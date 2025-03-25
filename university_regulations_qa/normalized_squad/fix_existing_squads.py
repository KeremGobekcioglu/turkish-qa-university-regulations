import json
import unicodedata
import os
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

#     # Remove punctuation from the end of destination if it exists
#     if destination_lower.endswith('.'):
#         destination_lower = destination_lower[:-1]
#         index = source_lower.find(destination_lower)
#         if index != -1:
#             return index

#     # Try finding without the last word if it's a common ending like "eder", "edilir", etc.
#     common_endings = ['eder', 'edilir', 'olur', 'olunur', 'yapılır']
#     dest_words = destination_lower.split()
#     if any(dest_words[-1].endswith(ending) for ending in common_endings):
#         modified_dest = ' '.join(dest_words[:-1])
#         index = source_lower.find(modified_dest)
#         if index != -1:
#             return index

#     # Try to find the longest matching sequence
#     dest_words = destination_lower.split()
#     for length in range(len(dest_words), 0, -1):
#         for i in range(len(dest_words) - length + 1):
#             phrase = ' '.join(dest_words[i:i+length])
#             if len(phrase) > 10:  # Only consider substantial phrases
#                 index = source_lower.find(phrase)
#                 if index != -1:
#                     return index

#     return -1

# def update_squad_json(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
    
#     for article in data['data']:
#         for paragraph in article['paragraphs']:
#             context = paragraph['context']
#             context = unicodedata.normalize('NFKC', context).strip().lower()
#             paragraph['context'] = context
            
#             for qa in paragraph['qas']:
#                 question = qa['question']
#                 question = unicodedata.normalize('NFKC', question).strip().lower()
#                 qa['question'] = question
                
#                 for answer in qa['answers']:
#                     answer_text = answer['text']
#                     answer_text = unicodedata.normalize('NFKC', answer_text).strip().lower()
#                     answer['text'] = answer_text
                    
#                     answer_start = find(context, answer_text)
#                     if answer_start == -1:
#                         print(f"Warning: Answer not found in context for QA ID {qa['id']}")
#                         print(f"Context: {context}")
#                         print(f"Answer: {answer_text}")
#                         answer_start = 0  # or handle it as needed
#                     answer['answer_start'] = answer_start
    
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
    
#     print(f"Updated SQuAD JSON saved to {file_path}")

# def main():
#     file_path = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad/YÖ-0002 Önlisans-Lisans İngilizce Hazırlık Eğitim-Öğretim ve Sınav Yönergesi R71.json'
#     update_squad_json(file_path)

# if __name__ == "__main__":
#     main()
import json
import unicodedata

from Levenshtein import ratio  # You'll need to: pip install python-Levenshtein

def find_with_levenshtein(source, destination):
    source = source.lower()
    destination = destination.lower()
    
    # First try exact match
    index = source.find(destination)
    if index != -1:
        return index
    
    # Use sliding window with Levenshtein
    dest_len = len(destination)
    best_ratio = 0
    best_pos = -1
    
    for i in range(len(source) - dest_len + 1):
        window = source[i:i + dest_len]
        current_ratio = ratio(window, destination)
        
        if current_ratio > best_ratio and current_ratio > 0.85:  # 85% similarity threshold
            best_ratio = current_ratio
            best_pos = i
    
    return best_pos if best_ratio > 0.85 else -1
# def find_gpt(source, destination):
#     # Normalize the strings
#     source = unicodedata.normalize('NFKC', source).strip()
#     destination = unicodedata.normalize('NFKC', destination).strip()

#     # Convert to lowercase for case-insensitive matching
#     source_lower = source.lower()
#     destination_lower = destination.lower()
    
#     # 1. Exact Match
#     index = source_lower.find(destination_lower)
#     if index != -1:
#         return index

#     # 2. Turkish-Specific Variations
#     variations = [
#         destination_lower.rstrip('.'),  # Remove trailing period
#         destination_lower.rstrip(','),  # Remove trailing comma
#         destination_lower.replace('i̇', 'i'),  # Handle Turkish 'i̇' vs 'i'
#     ]
#     for variant in variations:
#         index = source_lower.find(variant)
#         if index != -1:
#             return index

#     # 3. Partial Matching Using Substring Similarity
#     destination_words = destination_lower.split()
#     if len(destination_words) > 1:
#         for i in range(len(destination_words)):
#             # Create substrings by progressively removing words
#             partial_dest = ' '.join(destination_words[i:])
#             index = source_lower.find(partial_dest)
#             if index != -1:
#                 return index

#     # 4. Fuzzy Matching
#     max_ratio = 0
#     best_index = -1
#     dest_len = len(destination_lower)
#     threshold = 0.75  # Adjust similarity threshold as needed
    
#     # Sliding window for fuzzy matching
#     for i in range(len(source_lower) - dest_len + 1):
#         window = source_lower[i:i + dest_len]
#         ratio = SequenceMatcher(None, window, destination_lower).ratio()
#         if ratio > max_ratio and ratio >= threshold:
#             max_ratio = ratio
#             best_index = i

#     if best_index != -1:
#         return best_index

#     # 5. Significant Words Matching
#     significant_words = [word for word in destination_words if len(word) > 3]
#     for word in significant_words:
#         index = source_lower.find(word)
#         if index != -1:
#             # Check surrounding context for higher confidence
#             context_start = max(0, index - 50)
#             context_end = min(len(source_lower), index + len(word) + 50)
#             context = source_lower[context_start:context_end]
#             if SequenceMatcher(None, context, destination_lower).ratio() > 0.6:
#                 return index

#     # If no match is found
#     return -1

# def update_squad_json(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     count = 0
#     for article in data['data']:
#         for paragraph in article['paragraphs']:
#             context = paragraph['context']
#             context = unicodedata.normalize('NFKC', context).strip().lower()
#             paragraph['context'] = context
            
#             for qa in paragraph['qas']:
#                 question = qa['question']
#                 question = unicodedata.normalize('NFKC', question).strip().lower()
#                 qa['question'] = question
                
#                 for answer in qa['answers']:
#                     answer_text = answer['text']
#                     answer_text = unicodedata.normalize('NFKC', answer_text).strip().lower()
#                     answer['text'] = answer_text
                    
#                     answer_start = find_gpt(context, answer_text)
#                     if answer_start == -1:
#                         print(f"Warning: Answer not found in context for QA ID {qa['id']}")
#                         print(f"Context: {context}")
#                         print(f"Answer: {answer_text}")
#                         count += 1
#                         answer_start = 0  # or handle it as needed
#                     answer['answer_start'] = answer_start
                
#                 # Convert the "id" field to a string
#                 qa['id'] = int(qa['id'])
    
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#     return count
from difflib import SequenceMatcher
from difflib import get_close_matches

def find_last(source, destination):
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
# import unicodedata
from difflib import SequenceMatcher

def find_first(source, destination):
    # Normalize the strings
    source = unicodedata.normalize('NFKC', source).strip()
    destination = unicodedata.normalize('NFKC', destination).strip()

    # Convert to lowercase
    source_lower = source.lower()
    destination_lower = destination.lower()
    
    # 1. Exact match
    index = source_lower.find(destination_lower)
    if index != -1:
        return index

    # 2. Common Turkish text variations
    variations = [
        destination_lower,
        destination_lower.rstrip('.'),  # Remove trailing period
        destination_lower.rstrip(','),  # Remove trailing comma
        destination_lower.replace('i̇', 'i'),  # Handle Turkish i/İ
    ]
    
    for variant in variations:
        index = source_lower.find(variant)
        if index != -1:
            return index

    # 3. Handle common Turkish verb endings
    common_endings = {
        'eder': 'etmek',
        'edilir': 'edilmek',
        'olur': 'olmak',
        'olunur': 'olunmak',
        'yapılır': 'yapılmak',
        'verilir': 'verilmek',
        'alınır': 'alınmak',
        'bulunur': 'bulunmak'
    }
    
    dest_words = destination_lower.split()
    if len(dest_words) > 0:
        last_word = dest_words[-1]
        for ending, replacement in common_endings.items():
            if last_word.endswith(ending):
                modified_dest = ' '.join(dest_words[:-1] + [last_word.replace(ending, replacement)])
                index = source_lower.find(modified_dest)
                if index != -1:
                    return index

    # 4. Fuzzy matching for longer phrases
    if len(destination_lower) > 10:
        max_ratio = 0
        best_index = -1
        
        # Use sliding window approach for longer texts
        dest_len = len(destination_lower)
        for i in range(len(source_lower) - dest_len + 1):
            window = source_lower[i:i + dest_len]
            ratio = SequenceMatcher(None, window, destination_lower).ratio()
            
            if ratio > max_ratio and ratio > 0.8:  # 80% similarity threshold
                max_ratio = ratio
                best_index = i
        
        if best_index != -1:
            return best_index

    # 5. Try finding significant parts
    significant_words = [word for word in dest_words if len(word) > 3]
    if significant_words:
        for word in significant_words:
            index = source_lower.find(word)
            if index != -1:
                # Verify surrounding context
                context_start = max(0, index - 50)
                context_end = min(len(source_lower), index + len(word) + 50)
                context = source_lower[context_start:context_end]
                
                if SequenceMatcher(None, context, destination_lower).ratio() > 0.6:
                    return index

    return -1
def find_second(source, destination):
    # Normalize the strings
    source = unicodedata.normalize('NFKC', source).strip()
    destination = unicodedata.normalize('NFKC', destination).strip()

    # Convert to lowercase for case-insensitive matching
    source_lower = source.lower()
    destination_lower = destination.lower()

    # 1. Exact Match
    index = source_lower.find(destination_lower)
    if index != -1:
        return index

    # 2. Turkish-Specific Variations
    variations = [
        destination_lower.rstrip('.'),  # Remove trailing period
        destination_lower.rstrip(','),  # Remove trailing comma
        destination_lower.replace('i̇', 'i'),  # Handle Turkish 'i̇' vs 'i'
    ]
    for variant in variations:
        index = source_lower.find(variant)
        if index != -1:
            return index

    # 3. Partial Matching Using Substring Similarity
    destination_words = destination_lower.split()
    if len(destination_words) > 1:
        for i in range(len(destination_words)):
            # Create substrings by progressively removing words
            partial_dest = ' '.join(destination_words[i:])
            index = source_lower.find(partial_dest)
            if index != -1:
                return index

    # 4. Fuzzy Matching Using SequenceMatcher (with lowered threshold)
    max_ratio = 0
    best_index = -1
    dest_len = len(destination_lower)
    threshold = 0.6  # Lowered threshold for better matches
    
    # Sliding window for fuzzy matching
    for i in range(len(source_lower) - dest_len + 1):
        window = source_lower[i:i + dest_len]
        ratio = SequenceMatcher(None, window, destination_lower).ratio()
        if ratio > max_ratio and ratio >= threshold:
            max_ratio = ratio
            best_index = i

    if best_index != -1:
        return best_index

    # 5. Significant Words Matching
    significant_words = [word for word in destination_words if len(word) > 3]
    for word in significant_words:
        index = source_lower.find(word)
        if index != -1:
            # Check surrounding context for higher confidence
            context_start = max(0, index - 50)
            context_end = min(len(source_lower), index + len(word) + 50)
            context = source_lower[context_start:context_end]
            if SequenceMatcher(None, context, destination_lower).ratio() > 0.6:
                return index

    # If no match is found
    return -1
def update_squad_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    filename = file_path.split('/')[-1]
    wrong_txt_path = os.path.join(os.path.dirname(file_path), 'wrong.txt')
    with open(wrong_txt_path, 'a', encoding='utf-8') as wrong_txt:
        for article in data['data']:
            for paragraph in article['paragraphs']:
                context = paragraph['context']
                context = unicodedata.normalize('NFKC', context).strip().lower()
                paragraph['context'] = context
                
                for qa in paragraph['qas']:
                    question = qa['question']
                    question = unicodedata.normalize('NFKC', question).strip().lower()
                    qa['question'] = question
                    
                    for answer in qa['answers']:
                        answer_text = answer['text']
                        answer_text = unicodedata.normalize('NFKC', answer_text).strip().lower()
                        answer['text'] = answer_text
                        
                        answer_start = find_second(context, answer_text)
                        if answer_start == -1:
                            wrong_txt.write(filename + qa['id'])
                            wrong_txt.write(f"Warning: Answer not found in context for QA ID {qa['id']}\n")
                            wrong_txt.write(f"Context: {context}\n")
                            wrong_txt.write(f"Answer: {answer_text}\n\n")
                            answer_start = 0  # or handle it as needed
                        answer['answer_start'] = answer_start
                
                # Convert the "id" field to a string
                qa['id'] = str(qa['id'])
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated SQuAD JSON saved to {file_path}")
def main():
    directory = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad'
    filename = "final_test.json"
    update_squad_json(os.path.join(directory, filename))
    # for filename in os.listdir(directory):
    #     if filename.endswith('.json'):
    #         file_path = os.path.join(directory, filename)
    #         update_squad_json(file_path)
if __name__ == "__main__":
    main()