I deleted all the models that performed poorly because they did not meet the required accuracy and performance benchmarks.
I have wrote the Prerequisites below, you can check. I hope you do not get any error while testing.

Prerequisites:

Python 3.8 or higher
Required libraries (see requirements.txt)
Install Dependencies:
Run the following command:
pip install -r requirements.txt

Adjust File Paths:
Update paths in the initialize() function in interface.py (line 198). Replace:

model_path: Path to the fine-tuned model.
contexts and qa_pairs: Path to your dataset JSON file.
Example:
model_path = "C:/Users/YourUsername/Desktop/200104004032_KEREM_GOBEKCIOGLU_CSE484_HW2/models/fine_tuned_model_0"
contexts, qa_pairs = load_contexts_and_qa_pairs("C:/Users/YourUsername/Desktop/200104004032_KEREM_GOBEKCIOGLU_CSE484_HW2/fine_tune/merged_dataset.json")

Running the Application:

Web Interface:

Navigate to the project directory which is interface.
Run the command: python interface.py
Access the interface at http://127.0.0.1:5000 if it does not open by itself

Troubleshooting:

Path Issues: Ensure paths in interface.py are correctly set.
Missing Dependencies: Run pip install -r requirements.txt
