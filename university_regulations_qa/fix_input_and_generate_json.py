import unicodedata
import os
import json

def delete_empty_lines_and_normalize_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            normalized_line = unicodedata.normalize('NFKC', line).strip().lower()
            if normalized_line:  # Check if the line is not empty or just spaces
                f.write(normalized_line + '\n')

def delete_empty_lines_and_normalize_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            delete_empty_lines_and_normalize_in_file(file_path)
            print(f"Processed {file_path}")
def parse_blocks_from_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove lines that start with a number
    lines = [line for line in lines if not line.strip().isdigit()]
    
    content = ''.join(lines)
    print("Content after removing lines starting with a number:\n", content)
    
    # blocks = []
    # current_block = {}
    # for i, line in enumerate(lines):
    #     line = line.strip()
    #     if line.lower().startswith("context:"):
    #         if current_block:
    #             blocks.append(current_block)
    #             current_block = {}
    #         current_block["context"] = lines[i + 1].strip().strip('"')
    #     elif line.lower().startswith("question:"):
    #         current_block["question"] = lines[i + 1].strip()
    #     elif line.lower().startswith("answer:"):
    #         current_block["answer"] = lines[i + 1].strip().strip('"')
    blocks = []
    current_block = {}
    for line in lines:
        line = line.strip()
        if line.lower().startswith("context:"):
            if current_block:
                blocks.append(current_block)
                current_block = {}
            current_block["context"] = line[len("context:"):].strip().strip('"')
        elif line.lower().startswith("question:"):
            current_block["question"] = line[len("question:"):].strip()
        elif line.lower().startswith("answer:"):
            current_block["answer"] = line[len("answer:"):].strip().strip('"')
            blocks.append(current_block)
            current_block = {}
    
    if current_block:
        blocks.append(current_block)
    
    # Assign IDs to blocks
    for i, block in enumerate(blocks, start=1):
        block["id"] = i
    
    print("Parsed blocks:\n", blocks)
    return blocks
# def find(source, destination):
#     # Normalize the strings
#     source = unicodedata.normalize('NFKC', source).strip()
#     destination = unicodedata.normalize('NFKC', destination).strip()

#     # Convert both source and destination to lowercase for case-insensitive search
#     source_lower = source.lower()
#     destination_lower = destination.lower()
    
#     # First try Python's built-in find method
#     index = source_lower.find(destination_lower)
#     if index != -1:
#         return index

#     # Try to find the key parts of the answer in the source
#     key_parts = destination_lower.split()
#     for part in key_parts:
#         if len(part) > 3:  # Only look for significant words
#             index = source_lower.find(part)
#             if index != -1:
#                 return index

#     # If still no match found, try to find any significant substring
#     for i in range(len(destination_lower), 2, -1):
#         for j in range(len(destination_lower) - i + 1):
#             substring = destination_lower[j:j+i]
#             if len(substring) > 3:  # Only consider substantial substrings
#                 index = source_lower.find(substring)
#                 if index != -1:
#                     return index

#     return -1
def find(source, destination):
    # Normalize the strings
    source = unicodedata.normalize('NFKC', source).strip()
    destination = unicodedata.normalize('NFKC', destination).strip()

    # Convert both source and destination to lowercase for case-insensitive search
    source_lower = source.lower()
    destination_lower = destination.lower()
    
    # First try Python's built-in find method
    index = source_lower.find(destination_lower)
    if index != -1:
        return index

    # Remove punctuation from the end of destination if it exists
    if destination_lower.endswith('.'):
        destination_lower = destination_lower[:-1]
        index = source_lower.find(destination_lower)
        if index != -1:
            return index

    # Try finding without the last word if it's a common ending like "eder", "edilir", etc.
    common_endings = ['eder', 'edilir', 'olur', 'olunur', 'yapılır']
    dest_words = destination_lower.split()
    if any(dest_words[-1].endswith(ending) for ending in common_endings):
        modified_dest = ' '.join(dest_words[:-1])
        index = source_lower.find(modified_dest)
        if index != -1:
            return index

    # Try to find the longest matching sequence
    dest_words = destination_lower.split()
    for length in range(len(dest_words), 0, -1):
        for i in range(len(dest_words) - length + 1):
            phrase = ' '.join(dest_words[i:i+length])
            if len(phrase) > 10:  # Only consider substantial phrases
                index = source_lower.find(phrase)
                if index != -1:
                    return index

    return -1

def generate_squad_json(blocks):
    data = {"data": []}
    article = {"title": "Generated SQuAD Data", "paragraphs": []}
    
    for block in blocks:
        context = block.get("context", "")
        question = block.get("question", "")
        answer = block.get("answer", "")
        
        # Normalize and strip whitespace
        context = unicodedata.normalize('NFKC', context).strip()
        answer = unicodedata.normalize('NFKC', answer).strip()
        
        print("Answer: ", answer)
        print("Context: ", context)
        
        answer_start = find(context, answer)
        if answer_start == -1:
            print(f"Warning: Answer not found in context for block ID {block['id']}")
            print(f"Context: {context}")
            print(f"Answer: {answer}")
            answer_start = 0
        
        paragraph = {
            "context": context,
            "qas": [
                {
                    "question": question,
                    "answers": [
                        {
                            "text": answer,
                            "answer_start": answer_start
                        }
                    ],
                    "id": str(block["id"])  # Convert the id to a string
                }
            ]
        }
        
        article["paragraphs"].append(paragraph)
    
    data["data"].append(article)
    return data

def main():
    input_path = 'C:/Users/keko1/Desktop/nlphw2/input.txt'
    output_path = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad/generated_squad.json'
    # file = "input.txt"s
    delete_empty_lines_and_normalize_in_file(input_path)
    blocks = parse_blocks_from_text(input_path)
    squad_data = generate_squad_json(blocks)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(squad_data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated SQuAD JSON saved to {output_path}")

if __name__ == "__main__":
    main()