from transformers import AutoModelForQuestionAnswering, AutoTokenizer, Trainer, TrainingArguments, EarlyStoppingCallback
from datasets import Dataset
import json

def load_datasets():
    # Load JSON files
    with open('merged_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Split data into train (80%) and validation (20%)
    total_docs = len(data['data'])
    split_point = int(total_docs * 0.8)
    
    train_data = {"data": data['data'][:split_point]}
    valid_data = {"data": data['data'][split_point:]}
    
    def flatten_data(data):
        flat_examples = []
        for doc in data['data']:
            for para in doc['paragraphs']:
                context = para['context']
                for qa in para['qas']:
                    flat_examples.append({
                        'context': context,
                        'question': qa['question'],
                        'answer_text': qa['answers'][0]['text'],
                        'answer_start': qa['answers'][0]['answer_start']
                    })
        return flat_examples
    
    train_examples = flatten_data(train_data)
    valid_examples = flatten_data(valid_data)
    
    print(f"Train examples: {len(train_examples)}")
    print(f"Validation examples: {len(valid_examples)}")
    
    return {
        'train': Dataset.from_list(train_examples),
        'validation': Dataset.from_list(valid_examples)
    }

# Load datasets
print("Loading datasets...")
dataset = load_datasets()
model_name = "dbmdz/bert-base-turkish-cased"
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def preprocess_function(examples):
    # Clean text
    questions = [q.strip() for q in examples['question']]
    contexts = [c.strip() for c in examples['context']]
    
    # Tokenize questions and contexts
    tokenized_examples = tokenizer(
        questions,
        contexts,
        truncation="only_second",
        max_length=384,
        stride=128,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )
    
    # Map character positions to token positions
    start_positions = []
    end_positions = []
    
    offset_mapping = tokenized_examples.pop("offset_mapping")
    sample_mapping = tokenized_examples.pop("overflow_to_sample_mapping")
    
    for i, offsets in enumerate(offset_mapping):
        sample_idx = sample_mapping[i]
        start_char = examples['answer_start'][sample_idx]
        answer_text = examples['answer_text'][sample_idx]
        end_char = start_char + len(answer_text)
        
        # Find token positions
        start_token = None
        end_token = None
        
        for idx, (start, end) in enumerate(offsets):
            if start <= start_char and end > start_char:
                start_token = idx
            if start < end_char and end >= end_char:
                end_token = idx
                break
        
        if start_token is None or end_token is None:
            start_token = 0
            end_token = 0
            
        start_positions.append(start_token)
        end_positions.append(end_token)
    
    tokenized_examples["start_positions"] = start_positions
    tokenized_examples["end_positions"] = end_positions
    
    return tokenized_examples

# Process datasets
print("Processing datasets...")
tokenized_train = dataset['train'].map(
    preprocess_function,
    batched=True,
    remove_columns=dataset['train'].column_names,
    batch_size=8
)

tokenized_valid = dataset['validation'].map(
    preprocess_function,
    batched=True,
    remove_columns=dataset['validation'].column_names,
    batch_size=8
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=5,              # Reduced from 15 to 5
    per_device_train_batch_size=8,   # Increased from 2 to 8
    per_device_eval_batch_size=8,    # Increased from 2 to 8
    gradient_accumulation_steps=4,   # Reduced from 16 to 4
    learning_rate=2e-5,             # Increased from 5e-6 to 2e-5
    warmup_ratio=0.1,               # Reduced from 0.2 to 0.1
    weight_decay=0.01,
    evaluation_strategy="steps",
    eval_steps=50,                  # Less frequent evaluation
    save_strategy="steps",
    save_steps=50,                  # Less frequent saving
    save_total_limit=2,             # Keep fewer checkpoints
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    logging_dir='./logs',
    logging_steps=25,
    report_to="none",
    fp16=True,
    max_grad_norm=1.0               # Increased from 0.5 to 1.0
)

# Add early stopping callback
early_stopping = EarlyStoppingCallback(
    early_stopping_patience=3,
    early_stopping_threshold=0.01
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_valid,
    tokenizer=tokenizer,
    callbacks=[early_stopping]
)

# Train the model
print("Starting training...")
trainer.train()

# Save the model
print("Saving model...")
model_path = "./fine_tuned_model"
trainer.save_model(model_path)
tokenizer.save_pretrained(model_path)