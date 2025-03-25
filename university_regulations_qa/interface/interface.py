import os
import json
import torch
import webbrowser
from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk
from threading import Timer
import re
import numpy as np
nltk.download('punkt')
nltk.download('punkt_tab')
app = Flask(__name__)

# Global variables
model = None
tokenizer = None
contexts = None
qa_pairs = None
bm25 = None

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

def get_answer(question, context):
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

# def answer_question(question):
#     # Normalize question
#     question = normalize_text(question)
    
#     # 1. Try exact and similar matches
#     best_match, match_score = find_best_match(question, qa_pairs)
#     if best_match:
#         return {
#             'exact_match': {
#                 'answer': best_match['answer'],
#                 'confidence': match_score * 10,
#                 'source': 'Tam/Benzer Eşleşme'
#             },
#             'model_answer': None
#         }
    
#     # 2. Try BM25 + Model
#     tokenized_question = word_tokenize(question)
#     bm25_scores = bm25.get_scores(tokenized_question)
#     top_contexts_indices = np.argsort(bm25_scores)[-5:][::-1]
    
#     best_answer = ""
#     best_confidence = -float('inf')
    
#     for idx in top_contexts_indices:
#         context = contexts[idx]
#         if bm25_scores[idx] > 0:
#             answer, confidence = get_answer(question, context)
            
#             if confidence > best_confidence:
#                 best_confidence = confidence
#                 best_answer = answer

#     return {
#         'exact_match': None,
#         'model_answer': {
#             'answer': best_answer if best_confidence > 5.0 else "Üzgünüm, bu soru için güvenilir bir cevap bulamadım.",
#             'confidence': best_confidence,
#             'source': 'Model'
#         }
#     }
def answer_question(question):
    # Normalize question
    question = normalize_text(question)
    
    # 1. Try exact and similar matches
    best_match, match_score = find_best_match(question, qa_pairs)
    if best_match:
        return {
            'exact_match': {
                'answer': best_match['answer'],
                'confidence': match_score * 10,
                'source': 'Exact/Similar Match'
            },
            'model_answer': None
        }
    
    # 2. Try BM25 + Model
    tokenized_question = word_tokenize(question)
    bm25_scores = bm25.get_scores(tokenized_question)
    top_contexts_indices = np.argsort(bm25_scores)[-5:][::-1]
    
    best_answer = ""
    best_confidence = -float('inf')

    # Use BM25-ranked contexts to find the best model-generated answer
    for idx in top_contexts_indices:
        context = contexts[idx]
        if bm25_scores[idx] > 0:
            answer, confidence = get_answer(question, context)
            if confidence > best_confidence:
                best_confidence = confidence
                best_answer = answer

    # Fallback mechanism if no BM25 score is above 0
    if best_confidence < 0 or best_answer == "":
        fallback_context = " ".join(contexts)  # Concatenate all contexts as a fallback
        best_answer, best_confidence = get_answer(question, fallback_context)

    return {
        'exact_match': None,
        'model_answer': {
            'answer': best_answer,
            'confidence': best_confidence,
            'source': 'Model'
        }
    }

# Initialize function
def initialize():
    global model, tokenizer, contexts, qa_pairs, bm25
    
    print("Loading model and data...")
    
    model_path = "C:/Users/keko1/Desktop/200104004032_KEREM_GOBEKCIOGLU_CSE484_HW2/models/fine_tuned_model_0"
    model = AutoModelForQuestionAnswering.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    contexts, qa_pairs = load_contexts_and_qa_pairs("C:/Users/keko1/Desktop/200104004032_KEREM_GOBEKCIOGLU_CSE484_HW2/fine_tune/merged_dataset.json")
    bm25 = create_bm25_index(contexts)
    
    print("System initialized!")

# Initialize at startup
initialize()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>GTÜ Yönetmelik Soru-Cevap Sistemi</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f0f2f5;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .input-section {
                margin-bottom: 20px;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                background-color: #1a73e8;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #1557b0;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 4px;
                display: none;
            }
            .answer-section {
                background-color: #f8f9fa;
                padding: 15px;
                margin-top: 10px;
                border-radius: 4px;
            }
            .confidence {
                color: #666;
                font-size: 0.9em;
                margin-top: 5px;
            }
            .source {
                color: #1a73e8;
                font-weight: bold;
                margin-bottom: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>GTÜ Yönetmelik Soru-Cevap Sistemi</h1>
            <div class="input-section">
                <input type="text" id="question" placeholder="Sorunuzu buraya yazın...">
                <button onclick="getAnswer()">Cevapla</button>
            </div>
            <div id="result" class="result">
                <div id="exact-match" class="answer-section" style="display: none;">
                    <div class="source">Tam Eşleşme</div>
                    <div id="exact-match-answer"></div>
                    <div id="exact-match-confidence" class="confidence"></div>
                </div>
                <div id="model-answer" class="answer-section" style="display: none;">
                    <div class="source">Model Cevabı</div>
                    <div id="model-answer-text"></div>
                    <div id="model-confidence" class="confidence"></div>
                </div>
            </div>
        </div>

        <script>
        function getAnswer() {
            const question = document.getElementById('question').value;
            
            fetch('/answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question
                }),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').style.display = 'block';
                
                // Handle exact match
                const exactMatchDiv = document.getElementById('exact-match');
                if (data.exact_match) {
                    exactMatchDiv.style.display = 'block';
                    document.getElementById('exact-match-answer').textContent = data.exact_match.answer;
                    document.getElementById('exact-match-confidence').textContent = 
                        `Güven Skoru: ${(data.exact_match.confidence * 10).toFixed(2)}%`;
                } else {
                    exactMatchDiv.style.display = 'none';
                }
                
                // Handle model answer
                const modelAnswerDiv = document.getElementById('model-answer');
                if (data.model_answer) {
                    modelAnswerDiv.style.display = 'block';
                    document.getElementById('model-answer-text').textContent = data.model_answer.answer;
                    document.getElementById('model-confidence').textContent = 
                        `Güven Skoru: ${(data.model_answer.confidence * 10).toFixed(2)}%`;
                } else {
                    modelAnswerDiv.style.display = 'none';
                }
            });
        }
        </script>
    </body>
    </html>
    '''

@app.route('/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json()
        question = data['question']
        
        result = answer_question(question)
        return jsonify(result)
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your question.',
            'details': str(e)
        }), 500

@app.route('/status')
def status():
    return jsonify({
        'model_loaded': model is not None,
        'total_qa_pairs': len(qa_pairs) if qa_pairs else 0,
        'total_contexts': len(contexts) if contexts else 0
    })

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True)