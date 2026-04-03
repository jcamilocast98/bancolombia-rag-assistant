import sys
from PyPDF2 import PdfReader

def read_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"--- PAGE {i+1} ---\n"
            text += page.extract_text() + "\n"
        with open('tmp_pdf_out.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Done")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        read_pdf(sys.argv[1])
    else:
        print("Provide PDF file path args")
