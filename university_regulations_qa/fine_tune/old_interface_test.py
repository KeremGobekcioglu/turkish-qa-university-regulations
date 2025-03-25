from transformers import AutoModelForQuestionAnswering, AutoTokenizer
from rank_bm25 import BM25Okapi
import numpy as np
import torch
import json
from nltk.tokenize import word_tokenize
import nltk
import re
nltk.download('punkt')

# Load model and tokenizer
print("Loading model and data...")
model = AutoModelForQuestionAnswering.from_pretrained("./fine_tuned_model")
tokenizer = AutoTokenizer.from_pretrained("./fine_tuned_model")

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[.,!?]', '', text)
    text = ' '.join(text.split())
    return text

def text_similarity(text1, text2):
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    if text1 == text2:
        return 1.0
    
    words1 = set(text1.split())
    words2 = set(text2.split())
    overlap = len(words1.intersection(words2))
    total = len(words1.union(words2))
    
    return overlap / total

def load_contexts_and_qa_pairs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    contexts = []
    qa_pairs = []
    
    for doc in data['data']:
        for para in doc['paragraphs']:
            contexts.append(para['context'])
            for qa in para['qas']:
                qa_pairs.append({
                    'question': qa['question'],
                    'answer': qa['answers'][0]['text'],
                    'context': para['context']
                })
    
    return contexts, qa_pairs

def create_bm25_index(contexts):
    tokenized_contexts = [word_tokenize(context.lower()) for context in contexts]
    return BM25Okapi(tokenized_contexts)

def get_answer(question, context, model, tokenizer):
    inputs = tokenizer(
        question,
        context,
        return_tensors="pt",
        max_length=512,
        truncation=True,
        padding="max_length"
    )

    with torch.no_grad():
        outputs = model(**inputs)

    start_scores = outputs.start_logits[0]
    end_scores = outputs.end_logits[0]
    
    start_index = torch.argmax(start_scores)
    end_index = torch.argmax(end_scores)
    
    if end_index < start_index:
        end_index = start_index + 1
    
    answer_tokens = inputs["input_ids"][0][start_index:end_index + 1]
    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
    
    confidence = (torch.max(start_scores) + torch.max(end_scores)).item() / 2
    
    return answer, confidence

def find_best_match(question, qa_pairs, threshold=0.8):
    normalized_question = normalize_text(question)
    best_match = None
    best_score = 0
    
    for qa in qa_pairs:
        score = text_similarity(normalized_question, qa['question'])
        if score > best_score and score >= threshold:
            best_score = score
            best_match = qa
    
    return best_match, best_score

def answer_question(question, contexts, bm25, model, tokenizer, qa_pairs):
    # Normalize question
    question = normalize_text(question)
    
    # 1. Try exact and similar matches
    best_match, match_score = find_best_match(question, qa_pairs)
    if best_match:
        print(f"Found match with score: {match_score}")
        return {
            'answer': best_match['answer'],
            'context': best_match['context'],
            'confidence': match_score * 10,  # Scale to 0-10
            'source': 'match'
        }
    
    # 2. Try BM25 + Model
    print("\nNo exact match found, trying BM25 + Model")
    tokenized_question = word_tokenize(question)
    bm25_scores = bm25.get_scores(tokenized_question)
    
    # Print top contexts
    print("\nTop 3 BM25 matches:")
    top_indices = np.argsort(bm25_scores)[-3:][::-1]
    for idx in top_indices:
        print(f"\nScore: {bm25_scores[idx]:.4f}")
        print(f"Context: {contexts[idx]}")
    
    best_answer = ""
    best_confidence = -float('inf')
    best_context = ""
    
    for idx in top_indices:
        if bm25_scores[idx] > 0:
            context = contexts[idx]
            answer, confidence = get_answer(question, context, model, tokenizer)
            
            print(f"\nTrying context {idx}:")
            print(f"Answer: {answer}")
            print(f"Confidence: {confidence}")
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_answer = answer
                best_context = context
    
    if best_confidence > 0:
        return {
            'answer': best_answer,
            'context': best_context,
            'confidence': best_confidence,
            'source': 'model'
        }
    
    return {
        'answer': "Üzgünüm, bu soru için güvenilir bir cevap bulamadım.",
        'context': "",
        'confidence': 0,
        'source': 'no_match'
    }

def test_specific_case():
    test_question = "eğitim-öğretim yılı kaç yarıyıldan oluşur?"
    test_context = "madde 11 – (1) öğretim yılı, güz ve bahar yarıyıllarından oluşur."
    
    print("\nTesting specific case:")
    print(f"Question: {test_question}")
    print(f"Expected context: {test_context}")
    
    # Test BM25 scoring
    tokenized_question = word_tokenize(test_question.lower())
    bm25_scores = bm25.get_scores(tokenized_question)
    
    # Find this context in our contexts
    context_idx = contexts.index(test_context) if test_context in contexts else -1
    if context_idx != -1:
        print(f"Context found at index {context_idx}")
        print(f"BM25 score: {bm25_scores[context_idx]}")
    else:
        print("Context not found in dataset!")
    
    # Get model answer
    answer, confidence = get_answer(test_question, test_context, model, tokenizer)
    print(f"\nDirect model answer: {answer}")
    print(f"Confidence: {confidence}")
    
    # Try through main function
    result = answer_question(test_question, contexts, bm25, model, tokenizer, qa_pairs)
    print("\nMain function result:")
    print(json.dumps(result, indent=2))

# Load data and initialize
contexts, qa_pairs = load_contexts_and_qa_pairs('train.json')
bm25 = create_bm25_index(contexts)

# Interactive testing
def interactive_qa():
    print("\nSoru Cevap Sistemi Hazır!")
    print("Çıkmak için 'quit' yazın")
    print("Test modu için 'test' yazın")
    
    while True:
        question = input("\nSorunuzu girin: ")
        if question.lower() == 'quit':
            break
        elif question.lower() == 'test':
            test_specific_case()
            continue
            
        result = answer_question(question, contexts, bm25, model, tokenizer, qa_pairs)
        
        print("\nCevap:", result['answer'])
        print("Güven Skoru:", result['confidence'])
        print("Kaynak:", result['source'])
        print("\nKullanılan Bağlam:", result['context'])
        print("-" * 80)

if __name__ == "__main__":
    interactive_qa()