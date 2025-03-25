# # # import json
# # # import os
# # # # file_paths = ["dataset1.json", "dataset2.json", "dataset3.json"]  # Replace with your file names

# # # # for file_path in file_paths:
# # # #     with open(file_path, "r", encoding="utf-8") as f:
# # # #         data = json.load(f)
# # # #         merged_data["data"].extend(data["data"])
# # # filename = directory = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad'
# # # output_path = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad/merged_data.json'
    
# # # def merge_json_files(directory):
# # #     merged_data = {"data": []}
    
# # #     for filename in os.listdir(directory):
# # #         if filename.endswith('.json'):
# # #             file_path = os.path.join(directory, filename)
# # #             with open(file_path, 'r', encoding='utf-8') as f:
# # #                 data = json.load(f)
# # #                 merged_data["data"].extend(data["data"])
    
# # #     return merged_data

# # # merged_data = merge_json_files(filename)
# # # with open("merged_dataset.json", "w", encoding="utf-8") as f:
# # #     json.dump(merged_data, f, ensure_ascii=False, indent=4)

# # import os
# # import json

# # filename = directory = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad'
# # output_path = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad/merged_data.json'

# # def merge_json_files(directory):
# #     merged_data = {"data": []}
# #     current_id = 1  # Keep track of the current ID
    
# #     # Sort files to ensure consistent ordering
# #     json_files = sorted([f for f in os.listdir(directory) if f.endswith('.json')])
    
# #     for filename in json_files:
# #         file_path = os.path.join(directory, filename)
# #         with open(file_path, 'r', encoding='utf-8') as f:
# #             data = json.load(f)
# #             # Update IDs before extending
# #             for document in data["data"]:
# #                 for paragraph in document["paragraphs"]:
# #                     for qa in paragraph["qas"]:
# #                         qa["id"] = current_id  # or just current_id if you want integers
# #                         current_id += 1
# #             merged_data["data"].extend(data["data"])
    
# #     return merged_data

# # # Merge files
# # merged_data = merge_json_files(filename)

# # # Optional: Verify unique IDs
# # def verify_ids(data):
# #     ids = []
# #     for document in data["data"]:
# #         for paragraph in document["paragraphs"]:
# #             for qa in paragraph["qas"]:
# #                 ids.append(qa["id"])
    
# #     # Check for duplicates
# #     if len(ids) != len(set(ids)):
# #         print("Warning: Duplicate IDs found!")
# #         from collections import Counter
# #         duplicates = [item for item, count in Counter(ids).items() if count > 1]
# #         print(f"Duplicate IDs: {duplicates}")
# #     else:
# #         print(f"All IDs are unique. Total QA pairs: {len(ids)}")

# # # Save merged data
# # with open("merged_dataset.json", "w", encoding="utf-8") as f:
# #     json.dump(merged_data, f, ensure_ascii=False, indent=4)

# # # Verify the merged file
# # verify_ids(merged_data)
# import os
# import json
# from collections import OrderedDict

# def merge_json_files(directory):
#     merged_data = {"data": []}
#     current_id = 1
    
#     json_files = sorted([f for f in os.listdir(directory) if f.endswith('.json')])
    
#     for filename in json_files:
#         file_path = os.path.join(directory, filename)
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             for document in data["data"]:
#                 new_document = OrderedDict([
#                     ("title", document["title"]),
#                     ("paragraphs", [])
#                 ])
                
#                 for paragraph in document["paragraphs"]:
#                     new_paragraph = OrderedDict([
#                         ("context", paragraph["context"]),
#                         ("qas", [])
#                     ])
                    
#                     for qa in paragraph["qas"]:
#                         # Create QA pair with specific order
#                         new_qa = OrderedDict([
#                             ("question", qa["question"]),
#                             ("answers", qa["answers"]),
#                             ("id", current_id)
#                         ])
                        
#                         new_paragraph["qas"].append(new_qa)
#                         current_id += 1
                    
#                     new_document["paragraphs"].append(new_paragraph)
                
#                 merged_data["data"].append(new_document)
    
#     return merged_data

# # Main execution
# filename = directory = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad'
# output_path = 'merged_dataset.json'

# # Merge files
# merged_data = merge_json_files(filename)

# # Save with preserved order
# with open(output_path, "w", encoding="utf-8") as f:
#     json.dump(merged_data, f, ensure_ascii=False, indent=4)

# print(f"Merged data saved to {output_path} with preserved field order")
import os
import json
from collections import OrderedDict

def merge_json_files(directory):
    merged_data = {"data": []}
    current_id = 1
    processed_titles = set()  # Keep track of processed titles to avoid duplicates
    
    # Get unique JSON files
    json_files = sorted(set([f for f in os.listdir(directory) if f.endswith('.json')]))
    
    print(f"Found {len(json_files)} JSON files")
    
    for filename in json_files:
        file_path = os.path.join(directory, filename)
        print(f"Processing {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for document in data["data"]:
                # Skip if we've already processed this title
                if document["title"] in processed_titles:
                    print(f"Skipping duplicate title: {document['title']}")
                    continue
                
                processed_titles.add(document["title"])
                
                new_document = OrderedDict([
                    ("title", document["title"]),
                    ("paragraphs", [])
                ])
                
                for paragraph in document["paragraphs"]:
                    new_paragraph = OrderedDict([
                        ("context", paragraph["context"]),
                        ("qas", [])
                    ])
                    
                    for qa in paragraph["qas"]:
                        # Create QA pair with specific order
                        new_qa = OrderedDict([
                            ("question", qa["question"]),
                            ("answers", qa["answers"]),
                            ("id", current_id)
                        ])
                        
                        new_paragraph["qas"].append(new_qa)
                        current_id += 1
                    
                    new_document["paragraphs"].append(new_paragraph)
                
                merged_data["data"].append(new_document)
    
    return merged_data

def analyze_data(data, label=""):
    total_docs = len(data["data"])
    total_paragraphs = sum(len(doc["paragraphs"]) for doc in data["data"])
    total_qa = sum(len(para["qas"]) for doc in data["data"] for para in doc["paragraphs"])
    
    print(f"\n{label} Analysis:")
    print(f"Total documents: {total_docs}")
    print(f"Total paragraphs: {total_paragraphs}")
    print(f"Total QA pairs: {total_qa}")
    
    # Print titles
    print("\nDocuments:")
    for doc in data["data"]:
        print(f"- {doc['title']}: {sum(len(para['qas']) for para in doc['paragraphs'])} QA pairs")

# Main execution
directory = 'C:/Users/keko1/Desktop/nlphw2/normalized_squad'
output_path = 'merged_dataset.json'

# Merge files
print("Starting merge process...")
merged_data = merge_json_files(directory)

# Analyze before saving
analyze_data(merged_data, "Merged Dataset")

# Save with preserved order
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=4)

print(f"\nMerged data saved to {output_path}")

# Verify unique IDs
def verify_ids(data):
    ids = []
    questions = set()  # To track unique questions
    
    for document in data["data"]:
        for paragraph in document["paragraphs"]:
            for qa in paragraph["qas"]:
                ids.append(qa["id"])
                questions.add(qa["question"])
    
    print(f"\nVerification Results:")
    print(f"Total QA pairs: {len(ids)}")
    print(f"Unique questions: {len(questions)}")
    
    # Check for duplicates
    if len(ids) != len(set(ids)):
        print("Warning: Duplicate IDs found!")
        from collections import Counter
        duplicates = [item for item, count in Counter(ids).items() if count > 1]
        print(f"Duplicate IDs: {duplicates}")
    else:
        print("All IDs are unique.")

# Verify the merged file
verify_ids(merged_data)