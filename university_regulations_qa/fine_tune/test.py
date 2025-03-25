from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch
import json
import numpy as np
from tqdm import tqdm
import os
from datetime import datetime
def load_test_data(file_path):
    """Load test data from your JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    test_cases = []
    for doc in data['data']:
        for para in doc['paragraphs']:
            context = para['context']
            for qa in para['qas']:
                test_cases.append({
                    'question': qa['question'],
                    'context': context,
                    'answer': qa['answers'][0]['text']
                })
    return test_cases

def calculate_f1(prediction, ground_truth):
    """Calculate F1 score between prediction and ground truth"""
    prediction_tokens = prediction.lower().split()
    ground_truth_tokens = ground_truth.lower().split()
    
    common = set(prediction_tokens) & set(ground_truth_tokens)
    
    if len(common) == 0:
        return 0
    
    precision = len(common) / len(prediction_tokens)
    recall = len(common) / len(ground_truth_tokens)
    
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1

def calculate_exact_match(prediction, ground_truth):
    """Calculate exact match score"""
    return int(prediction.lower().strip() == ground_truth.lower().strip())

def get_answer(question, context, model, tokenizer):
    """Get answer from model"""
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

    start_scores = outputs.start_logits
    end_scores = outputs.end_logits
    
    start_index = torch.argmax(start_scores)
    end_index = torch.argmax(end_scores)
    
    answer_tokens = inputs["input_ids"][0][start_index:end_index + 1]
    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
    
    confidence = (torch.max(start_scores) + torch.max(end_scores)).item() / 2
    
    return answer, confidence

def evaluate_model(model, tokenizer, test_cases):
    """Evaluate model on test cases"""
    total_em = 0
    total_f1 = 0
    results = []
    
    print("\nEvaluating model on test cases...")
    for test_case in tqdm(test_cases):
        predicted_answer, confidence = get_answer(
            test_case['question'],
            test_case['context'],
            model,
            tokenizer
        )
        
        em_score = calculate_exact_match(predicted_answer, test_case['answer'])
        f1_score = calculate_f1(predicted_answer, test_case['answer'])
        
        total_em += em_score
        total_f1 += f1_score
        
        results.append({
            'question': test_case['question'],
            'context': test_case['context'],
            'predicted': predicted_answer,
            'actual': test_case['answer'],
            'confidence': confidence,
            'exact_match': em_score,
            'f1_score': f1_score
        })
    
    num_examples = len(test_cases)
    avg_em = total_em / num_examples * 100
    avg_f1 = total_f1 / num_examples * 100
    
    return {
        'exact_match': avg_em,
        'f1_score': avg_f1,
        'detailed_results': results
    }

def print_evaluation_results(eval_results):
    """Print evaluation results with examples"""
    print("\nOverall Results:")
    print(f"Exact Match: {eval_results['exact_match']:.2f}%")
    print(f"F1 Score: {eval_results['f1_score']:.2f}%")
    
    print("\nDetailed Analysis:")
    results = eval_results['detailed_results']
    
    # Print some example predictions
    print("\nSample Predictions (first 5):")
    for i, result in enumerate(results[:5]):
        print(f"\nExample {i+1}:")
        print(f"Question: {result['question']}")
        print(f"Predicted: {result['predicted']}")
        print(f"Actual: {result['actual']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Exact Match: {'✓' if result['exact_match'] else '✗'}")
        print(f"F1 Score: {result['f1_score']:.2f}")
    
    # Analyze confidence scores
    confidences = [r['confidence'] for r in results]
    print("\nConfidence Analysis:")
    print(f"Average confidence: {np.mean(confidences):.2f}")
    print(f"Min confidence: {min(confidences):.2f}")
    print(f"Max confidence: {max(confidences):.2f}")
    
    # Find best and worst predictions
    sorted_by_f1 = sorted(results, key=lambda x: x['f1_score'])
    
    print("\nWorst Predictions (lowest F1 scores):")
    for result in sorted_by_f1[:3]:
        print(f"\nQuestion: {result['question']}")
        print(f"Predicted: {result['predicted']}")
        print(f"Actual: {result['actual']}")
        print(f"F1 Score: {result['f1_score']:.2f}")
    
    print("\nBest Predictions (highest F1 scores):")
    for result in sorted_by_f1[-3:]:
        print(f"\nQuestion: {result['question']}")
        print(f"Predicted: {result['predicted']}")
        print(f"Actual: {result['actual']}")
        print(f"F1 Score: {result['f1_score']:.2f}")

def return_model_name(model_path):
    base_name = os.path.basename(model_path)

    # Find the index of "fine_tuned_model_" and slice the string to get the model number
    prefix = "fine_tuned_model_"
    index = base_name.find(prefix)
    if index != -1:
        model_number = base_name[index + len(prefix):]
        return f"model_{model_number}"
    else:
        return base_name
    
def save_results(eval_results, model_name, base_dir='C:/Users/keko1/Desktop/nlphw2/final_results', base_filename='evaluation_results.json'):
    # Ensure the directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Always include the model name in the base filename
    base_filename = os.path.join(base_dir, f"evaluation_results_{model_name}.json")
    
    # Check if the file exists and create a unique filename if it does
    if os.path.exists(base_filename):
        version = 1
        while os.path.exists(base_filename):
            base_filename = os.path.join(base_dir, f"evaluation_results_{model_name}_v{version}.json")
            version += 1
    
    print("\nSaving detailed results...")
    with open(base_filename, 'w', encoding='utf-8') as f:
        json.dump(eval_results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {base_filename}")
# Main execution
def main():
    # Load model and tokenizer
    print("Loading model...")

# Slice the string up to the end of "fine_tuned"
    for i in range(0,6):
        model_path = f"C:/Users/keko1/Desktop/nlphw2/models/fine_tuned_model_{i}"  # Adjust path as needed
        model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        index = model_path.find("fine_tuned")
        result = return_model_name(model_path)
        # Load test data
        print("Loading test data...")
        test_cases = load_test_data('final_test.json')  # Or your validation set
        
        # Evaluate model
        eval_results = evaluate_model(model, tokenizer, test_cases)
        
        # Print results
        print_evaluation_results(eval_results)
        
        # # Save detailed results
        # print("\nSaving detailed results...")
        # with open('evaluation_results.json', 'w', encoding='utf-8') as f:
        #     json.dump(eval_results, f, ensure_ascii=False, indent=2)
        # print("Results saved to evaluation_results.json")
        save_results(eval_results,result)

if __name__ == "__main__":
    main()