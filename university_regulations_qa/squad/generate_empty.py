import os
import json

def generate_empty_json_files(source_directory, target_directory):
    # Create the target directory if it doesn't exist
    os.makedirs(target_directory, exist_ok=True)
    
    # Iterate over all files in the source directory
    for filename in os.listdir(source_directory):
        if filename.endswith('.txt'):
            # Create a corresponding JSON filename
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(target_directory, json_filename)
            
            # Create an empty JSON structure
            empty_json = {}
            
            # Write the empty JSON to the file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(empty_json, f, ensure_ascii=False, indent=2)
            
            print(f"Generated empty JSON file: {json_path}")

def main():
    source_directory = 'C:/Users/keko1/Desktop/nlphw2/datasettxt'
    target_directory = 'C:/Users/keko1/Desktop/nlphw2/squad'
    
    generate_empty_json_files(source_directory, target_directory)

if __name__ == "__main__":
    main()