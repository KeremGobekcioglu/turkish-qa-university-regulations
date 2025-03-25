import os
import json

def update_title_with_filename(directory):
    json_files = sorted([f for f in os.listdir(directory) if f.endswith('.json')])
    
    for filename in json_files:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update the title with the filename (excluding the extension)
        title = os.path.splitext(filename)[0]
        for article in data["data"]:
            article["title"] = title
        
        # Save the updated JSON back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Updated title in file '{filename}' to '{title}'")

def main():
    directory = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad'
    update_title_with_filename(directory)

if __name__ == "__main__":
    main()