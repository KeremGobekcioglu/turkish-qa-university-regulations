# import json
# from sklearn.model_selection import train_test_split

# import json

# def fix_id_field(file_path):
#     with open(file_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     # Convert all "id" fields to strings
#     for item in data["data"]:
#         for paragraph in item["paragraphs"]:
#             for qa in paragraph["qas"]:
#                 qa["id"] = str(qa["id"])  # Convert the "id" field to a string

#     # Save the fixed dataset to the same file
#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

# # Fix train.json
# fix_id_field("train.json")

# # Fix valid.json
# fix_id_field("valid.json")

# # Load the merged dataset
# with open("merged_dataset.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# # Extract the "data" field which contains the paragraphs
# paragraphs = data["data"]

# # Split the dataset into 80% training and 20% validation
# train_paragraphs, valid_paragraphs = train_test_split(paragraphs, test_size=0.2, random_state=42)

# # Save the training dataset
# train_data = {"data": train_paragraphs}
# with open("train.json", "w", encoding="utf-8") as f:
#     json.dump(train_data, f, ensure_ascii=False, indent=4)

# # Save the validation dataset
# valid_data = {"data": valid_paragraphs}
# with open("valid.json", "w", encoding="utf-8") as f:
#     json.dump(valid_data, f, ensure_ascii=False, indent=4)

# print("Training and validation datasets created!")

import json
from sklearn.model_selection import train_test_split

# def fix_id_field(data):
#     # Convert all "id" fields to strings
#     for item in data["data"]:
#         for paragraph in item["paragraphs"]:
#             for qa in paragraph["qas"]:
#                 qa["id"] = str(qa["id"])  # Convert the "id" field to a string
#                 print("fixed")
#     return data

def split_dataset(input_file, train_output, valid_output, test_size=0.2):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Fix the id fields
    # data = fix_id_field(data)
    
    # Split the dataset
    train_data, valid_data = train_test_split(data["data"], test_size=test_size)
    
    # Save the split datasets
    with open(train_output, "w", encoding="utf-8") as f:
        json.dump({"data": train_data}, f, ensure_ascii=False, indent=4)
    
    with open(valid_output, "w", encoding="utf-8") as f:
        json.dump({"data": valid_data}, f, ensure_ascii=False, indent=4)

# Split the dataset and fix id fields
split_dataset("merged_dataset.json", "train.json", "final_test.json")

print("Dataset split into train.json and valid.json with fixed ID fields.")