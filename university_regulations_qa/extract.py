from pdfminer.high_level import extract_text as extract_text_from_pdf
import docx
import os

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(docx_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}")
        return ""

def extract_texts_from_directory(directory):
    """Extract text from all PDF and DOCX files in a directory."""
    texts = {}
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            text = extract_text_from_pdf(pdf_path)
            texts[filename] = text
        elif filename.endswith('.docx'):
            docx_path = os.path.join(directory, filename)
            text = extract_text_from_docx(docx_path)
            texts[filename] = text
    return texts

def main():
    pdf_directory = 'nlpdataset'
    output_directory = 'datasettxt'
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    texts = extract_texts_from_directory(pdf_directory)
    for filename, text in texts.items():
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(output_directory, txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Extracted text from {filename} and saved to {txt_filename}")

if __name__ == "__main__":
    main()