import os
import re
import unicodedata
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# ─────────────────────────────────────────────
# PDF Text Extraction
# ─────────────────────────────────────────────
def extract_text_from_pdf(filepath):
    """Extract text from a PDF file using PyMuPDF (fitz) or pdfplumber fallback."""
    text = ""

    # Try PyMuPDF first (fastest)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        if text.strip():
            return clean_text(text)
    except ImportError:
        pass
    except Exception as e:
        print(f"PyMuPDF error: {e}")

    # Fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return clean_text(text)
    except ImportError:
        pass
    except Exception as e:
        print(f"pdfplumber error: {e}")

    # Fallback to PyPDF2
    try:
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return clean_text(text)
    except ImportError:
        pass
    except Exception as e:
        print(f"PyPDF2 error: {e}")

    return ""


# ─────────────────────────────────────────────
# Text Cleaning
# ─────────────────────────────────────────────
def clean_text(text):
    """Clean and normalize extracted PDF text."""
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Remove control characters (keep newlines)
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove excessive punctuation
    text = re.sub(r'[_=\-]{3,}', ' ', text)

    # Remove page numbers and headers (standalone numbers)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    # Collapse multiple spaces / blank lines
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix broken sentences (single newlines within paragraphs)
    text = re.sub(r'(?<![.!?])\n(?=[a-z])', ' ', text)

    return text.strip()


# ─────────────────────────────────────────────
# File Helpers
# ─────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """Save uploaded file and return (secure_filename, full_path)."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    # Make filename unique by prepending an index
    base, ext = os.path.splitext(filename)
    counter = 1
    full_path = os.path.join(UPLOAD_FOLDER, filename)
    while os.path.exists(full_path):
        filename = f"{base}_{counter}{ext}"
        full_path = os.path.join(UPLOAD_FOLDER, filename)
        counter += 1
    file.save(full_path)
    return filename, full_path


def extract_title_from_text(text):
    """Heuristic: first meaningful line is usually the title."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:10]:
        word_count = len(line.split())
        if 3 <= word_count <= 20 and not line.endswith('.'):
            return line
    return lines[0] if lines else "Untitled Paper"


# ─────────────────────────────────────────────
# Score → Badge helper (used in templates via Jinja)
# ─────────────────────────────────────────────
def score_badge(score):
    if score >= 80:
        return ('Excellent', '#22c55e')
    elif score >= 60:
        return ('Good', '#3b82f6')
    elif score >= 40:
        return ('Fair', '#f59e0b')
    else:
        return ('Needs Work', '#ef4444')


# ─────────────────────────────────────────────
# Experience level based on paper count & avg score
# ─────────────────────────────────────────────
def get_experience_level(total_papers, avg_score):
    if avg_score is None:
        avg_score = 0
    if total_papers >= 10 and avg_score >= 70:
        return ('Distinguished Professor', '🏆', '#f59e0b')
    elif total_papers >= 5 and avg_score >= 60:
        return ('Associate Professor', '🎓', '#8b5cf6')
    elif total_papers >= 2:
        return ('Assistant Professor', '📚', '#3b82f6')
    elif total_papers == 1:
        return ('Researcher', '🔬', '#06b6d4')
    else:
        return ('New Faculty', '🌱', '#22c55e')
