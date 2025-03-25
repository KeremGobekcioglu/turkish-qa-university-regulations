import os
import json
import unicodedata
from difflib import SequenceMatcher

# Define your find_* functions here (find_first, find_last, find_second)
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
def update_squad_json(file_path, find_function, result_file):
    """
    Updates the SQuAD JSON file with the given find function and logs mismatches.
    
    Args:
        file_path (str): Path to the SQuAD JSON file.
        find_function (function): The function to use for finding `answer_start`.
        result_file (str): Path to the result file for logging mismatches.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Prepare the result file
    with open(result_file, 'w', encoding='utf-8') as result_txt:
        mismatch_count = 0

        for article in data['data']:
            for paragraph in article['paragraphs']:
                context = unicodedata.normalize('NFKC', paragraph['context']).strip().lower()
                paragraph['context'] = context
                
                for qa in paragraph['qas']:
                    question = unicodedata.normalize('NFKC', qa['question']).strip().lower()
                    qa['question'] = question
                    
                    for answer in qa['answers']:
                        answer_text = unicodedata.normalize('NFKC', answer['text']).strip().lower()
                        answer['text'] = answer_text
                        
                        # Use the specified find function
                        answer_start = find_function(context, answer_text)
                        if answer_start == -1:
                            mismatch_count += 1
                            result_txt.write(f"Mismatch in QA ID: {qa['id']}\n")
                            result_txt.write(f"Context: {context}\n")
                            result_txt.write(f"Answer: {answer_text}\n\n")
                            answer_start = 0  # Default value for unfound answers
                        answer['answer_start'] = answer_start
                
                # Convert the "id" field to a string
                qa['id'] = str(qa['id'])

        result_txt.write(f"Total mismatches: {mismatch_count}\n")
    
    # Save the updated JSON file
    updated_file_path = file_path.replace('.json', f'_{find_function.__name__}_updated.json')
    with open(updated_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated JSON saved to {updated_file_path}")
    print(f"Mismatches logged to {result_file}")


def compare_find_functions(file_path, output_dir):
    """
    Compares all find functions on the same JSON file and generates results.
    
    Args:
        file_path (str): Path to the JSON file to test.
        output_dir (str): Directory to save the result files.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # List of find functions to test
    find_functions = [find_first, find_last, find_second]

    # Dictionary to store mismatch counts for comparison
    mismatch_counts = {}

    # Run each function and generate result files
    for find_function in find_functions:
        result_file = os.path.join(output_dir, f"{find_function.__name__}_result.txt")
        update_squad_json(file_path, find_function, result_file)

        # Read the mismatch count from the result file
        with open(result_file, 'r', encoding='utf-8') as result_txt:
            for line in result_txt:
                if line.startswith("Total mismatches:"):
                    mismatch_counts[find_function.__name__] = int(line.split(":")[1].strip())

    # Write a comparison result file
    comparison_file = os.path.join(output_dir, "comparison_result.txt")
    with open(comparison_file, 'w', encoding='utf-8') as comp_file:
        comp_file.write("Comparison of Find Functions:\n")
        comp_file.write("=" * 30 + "\n")
        for func_name, mismatch_count in mismatch_counts.items():
            comp_file.write(f"{func_name}: {mismatch_count} mismatches\n")
        comp_file.write("=" * 30 + "\n")
        best_function = min(mismatch_counts, key=mismatch_counts.get)
        comp_file.write(f"Best performing function: {best_function} (least mismatches)\n")

    print(f"Comparison results saved to {comparison_file}")


if __name__ == "__main__":
    # Set the file to test and output directory
    file_to_test = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad/YÖ-0011 Uluslararası Öğrencilerin Lisans Programlarına Başvuru, Kabul ve Kayıt Yönergesi R7.json'
    output_directory = 'C:/Users/keko1/Desktop/nlphw2/results'

    # Run the comparison
    compare_find_functions(file_to_test, output_directory)
