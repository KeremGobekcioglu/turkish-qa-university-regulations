from transformers import AutoModelForQuestionAnswering, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("json", data_files={"train": "train.json", "validation": "valid.json"})

# Load the pre-trained Turkish model and tokenizer
model_name = "dbmdz/bert-base-turkish-cased"
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def preprocess_function(examples):
    questions = []
    contexts = []
    answers = []
    
    # Handle the nested structure
    for document in examples['data']:
        for paragraph in document['paragraphs']:
            context = paragraph['context']
            for qa in paragraph['qas']:
                questions.append(qa['question'])
                contexts.append(context)
                if qa['answers']:
                    answers.append({
                        'text': qa['answers'][0]['text'],
                        'answer_start': qa['answers'][0]['answer_start']
                    })
                else:
                    answers.append({'text': '', 'answer_start': 0})
    
    # Tokenize questions and contexts
    tokenized_examples = tokenizer(
        questions,
        contexts,
        truncation=True,
        max_length=512,
        padding="max_length",
        return_offsets_mapping=True,
        stride=128
    )
    
    # Map character positions to token positions
    start_positions = []
    end_positions = []
    
    offset_mapping = tokenized_examples.pop("offset_mapping")
    
    for i, (offset, answer) in enumerate(zip(offset_mapping, answers)):
        start_char = answer['answer_start']
        end_char = start_char + len(answer['text'])
        
        # Find token positions
        start_token = None
        end_token = None
        
        for idx, (start, end) in enumerate(offset):
            if start <= start_char and end > start_char:
                start_token = idx
            if start < end_char and end >= end_char:
                end_token = idx
                break
        
        # If answer is not fully within the context due to truncation, skip it
        if start_token is None or end_token is None:
            start_token = 0
            end_token = 0
            
        start_positions.append(start_token)
        end_positions.append(end_token)
    
    tokenized_examples["start_positions"] = start_positions
    tokenized_examples["end_positions"] = end_positions
    
    return tokenized_examples

# Process the datasets
tokenized_datasets = dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=dataset["train"].column_names,
    batch_size=2  # Process in smaller batches if memory is an issue
)

# Set up training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    save_steps=1000,
    save_total_limit=2,
    logging_dir='./logs',
    logging_steps=500,
    fp16=True,
    gradient_accumulation_steps=2,
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer
)

# Fine-tune the model
trainer.train()

# Save the fine-tuned model
trainer.save_model("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")