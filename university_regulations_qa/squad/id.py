import json

def add_ids_to_qas(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    id_counter = 1
    for article in data['data']:
        for paragraph in article['paragraphs']:
            for qa in paragraph['qas']:
                qa['id'] = id_counter
                id_counter += 1
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    json_path = 'C:/Users/keko1/Desktop/nlphw2/squad/YN-0015 Yaz Öğretimi Yönetmeliği R1.json'
    add_ids_to_qas(json_path)
    print(f"Added integer IDs to qas in {json_path}")

if __name__ == "__main__":
    main()