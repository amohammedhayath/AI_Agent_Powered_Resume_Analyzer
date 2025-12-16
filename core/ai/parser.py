import pypdf
import docx

def parse_resume(file_path):
    if file_path.endswith('.pdf'):
        return _parse_pdf(file_path)
    elif file_path.endswith('.docx'):
        return _parse_docx(file_path)
    return ""

def _parse_pdf(file_path):
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def _parse_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    if not text: return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks