import json

def convert_id_to_int(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    count = 1
    for article in data['data']:
        for paragraph in article['paragraphs']:
            for qa in paragraph['qas']:
                # Convert the "id" field to an integer
                qa['id'] = int(qa['id'])
                count += 1
    print(count)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated IDs in SQuAD JSON saved to {file_path}")

def main():
    file_path = 'C:/Users/keko1/Desktop/nlphw2/fine_tune/merged_dataset.json'
    convert_id_to_int(file_path)

if __name__ == "__main__":
    main()