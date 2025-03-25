# Turkish Question Answering System for University Regulations

This project is a fine-tuned BERT-based question answering system designed specifically for understanding Turkish university regulations. It features a web interface where users can input natural language questions and receive context-based answers.

## 🧠 Project Summary

- Fine-tuned BERT model on a Turkish QA dataset derived from university regulation documents.
- A simple Flask web interface to test model predictions.
- Custom preprocessing pipeline to prepare QA pairs from context passages.

## 📄 Project Report

A detailed explanation of the project, including methodology, preprocessing, model training, and evaluation results, is available here:

📘 **[Turkish Question Answering System (PDF)](./Turkish%20Question%20Answering%20System.pdf)**

---

## 📦 Model File Not Included

The trained model (`model.safetensors`) is **not included in this repository** due to its large size (~420MB).  
To use the system:

- You can train a new model using the provided fine-tuning scripts, or  
- Contact the author for access to the original model.

---

## ✅ Prerequisites

- Python 3.8 or higher
- Required libraries (see `requirements.txt`)

### Install Dependencies

```bash
pip install -r requirements.txt
