# 🔬 ResearchAI — AI-Based Publication Summary Generator

A full-stack Flask web application that lets **faculty** upload research papers (PDF),
automatically generates summaries using a Transformer NLP model, calculates quality
scores, and lets **students** browse the research library.

---

## 📁 Project Structure

```
project/
├── app.py              # Flask app — all routes
├── database.py         # SQLite helpers
├── model.py            # NLP summarizer + scorer + keyword extractor
├── utils.py            # PDF extraction + file utilities
├── requirements.txt
├── database.db         # Created automatically on first run
├── uploads/            # Uploaded PDFs stored here
├── static/
│   └── style.css       # Dark academic theme
└── templates/
    ├── base.html           # Shared layout + sidebar
    ├── login.html
    ├── register.html
    ├── faculty_dashboard.html
    ├── upload.html
    ├── result.html
    ├── student.html
    └── view_papers.html
```

---

## ⚡ Quick Start

### 1. Install Python dependencies

```bash
pip install flask werkzeug PyMuPDF pdfplumber PyPDF2
```

### 2. (Optional) Install AI model for better summaries

```bash
# CPU-only (smaller, faster)
pip install transformers torch --index-url https://download.pytorch.org/whl/cpu

# Or full PyTorch (if you have GPU)
pip install transformers torch
```

> ✅ **Without transformers** — the app still works using an extractive summarizer (no neural net needed).  
> 🚀 **With transformers** — uses `sshleifer/distilbart-cnn-12-6` for abstractive summaries (first run downloads ~1 GB).

### 3. Run the application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 👥 User Roles

| Role    | Capabilities |
|---------|-------------|
| Faculty | Register · Login · Upload PDFs · View summaries + scores · Manage papers |
| Student | Register · Login · Browse all papers · Search/filter · Read summaries |

---

## 🧠 AI Pipeline

```
PDF Upload → Text Extraction (PyMuPDF) → Text Cleaning
    → Abstractive Summarization (DistilBART / Extractive fallback)
    → Keyword Extraction (TF-IDF style)
    → Quality Score (0–100)
    → Stored in SQLite → Displayed in UI
```

### Score Breakdown

| Component | Max Points | Metric |
|-----------|-----------|--------|
| Paper Length | 30 | Word count sweet spot 3K–8K |
| Keywords Found | 35 | Research vocabulary coverage |
| Structure Quality | 20 | Sections (abstract, intro, methodology, etc.) |
| Sentence Quality | 15 | Average sentence length 15–25 words |

### Experience Levels

| Level | Requirements |
|-------|-------------|
| 🌱 New Faculty | 0 papers |
| 🔬 Researcher | 1 paper |
| 📚 Assistant Professor | 2+ papers |
| 🎓 Associate Professor | 5+ papers, avg ≥ 60% |
| 🏆 Distinguished Professor | 10+ papers, avg ≥ 70% |

---

## 🔐 Authentication

- Passwords hashed with **Werkzeug PBKDF2-SHA256**
- Flask session-based auth
- Role-based route protection (`@faculty_required`, `@student_required`)

---

## 🗄️ Database Schema

**users**
```sql
id | name | email | password | role | created_at
```

**papers**
```sql
id | faculty_id | title | summary | score | keywords | file_path | upload_date
```

---

## 🌐 API Endpoints (JSON)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/papers` | List papers (role-filtered) |
| GET | `/api/paper/<id>` | Single paper detail |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (custom dark theme), Vanilla JS |
| Backend | Python 3.10+, Flask 3.0 |
| Database | SQLite via `sqlite3` |
| PDF | PyMuPDF / pdfplumber / PyPDF2 |
| AI Model | HuggingFace `transformers` (DistilBART) |
| Auth | Werkzeug password hashing |
