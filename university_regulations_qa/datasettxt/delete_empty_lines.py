# import os

# def delete_empty_lines_in_file(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         lines = f.readlines()
    
#     with open(file_path, 'w', encoding='utf-8') as f:
#         for line in lines:
#             if line.strip():  # Check if the line is not empty or just spaces
#                 f.write(line)

# def delete_empty_lines_in_directory(directory):
#     for filename in os.listdir(directory):
#         if filename.endswith('.txt'):
#             file_path = os.path.join(directory, filename)
#             delete_empty_lines_in_file(file_path)
#             print(f"Processed {file_path}")

# def main():
#     directory = 'C:/Users/keko1/Desktop/nlphw2/datasettxt'
#     delete_empty_lines_in_directory(directory)

# if __name__ == "__main__":
#     main()import os
import unicodedata
import os
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

def main():
    directory = 'C:/Users/keko1/Desktop/nlphw2/datasettxt'
    delete_empty_lines_and_normalize_in_directory(directory)

if __name__ == "__main__":
    main()