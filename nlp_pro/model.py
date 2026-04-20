import re
import math
from collections import Counter

# ─────────────────────────────────────────────
# Try to import HuggingFace pipeline (optional)
# Falls back to extractive summarizer if not available
# ─────────────────────────────────────────────
try:
    from transformers import pipeline
    _summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        revision="a4f8f3e"
    )
    TRANSFORMER_AVAILABLE = True
    print("✅ Transformer model loaded.")
except Exception as e:
    TRANSFORMER_AVAILABLE = False
    print(f"⚠️  Transformer not available ({e}). Using extractive fallback.")


# ─────────────────────────────────────────────
# Extractive Summarizer (fallback)
# ─────────────────────────────────────────────
STOP_WORDS = {
    'the','a','an','and','or','but','in','on','at','to','for',
    'of','with','by','from','up','about','into','through','during',
    'is','are','was','were','be','been','being','have','has','had',
    'do','does','did','will','would','could','should','may','might',
    'shall','can','need','this','that','these','those','it','its',
    'we','our','they','their','he','she','his','her','i','my','you',
    'your','all','also','as','if','so','such','than','then','there',
    'when','where','which','who','whom','how','what','any','each',
    'both','few','more','most','other','some','such','no','nor',
    'not','only','own','same','too','very','just','because','while'
}

def _sentence_score(sentence, word_freq):
    words = re.findall(r'\b[a-z]+\b', sentence.lower())
    score = sum(word_freq.get(w, 0) for w in words if w not in STOP_WORDS)
    return score / max(len(words), 1)

def extractive_summarize(text, num_sentences=6):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.split()) > 5]
    if len(sentences) <= num_sentences:
        return ' '.join(sentences)
    words = re.findall(r'\b[a-z]+\b', text.lower())
    word_freq = Counter(w for w in words if w not in STOP_WORDS)
    scored = [(s, _sentence_score(s, word_freq)) for s in sentences]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:num_sentences]
    # Preserve original order
    top_set = {s for s, _ in top}
    ordered = [s for s in sentences if s in top_set]
    return ' '.join(ordered)


# ─────────────────────────────────────────────
# Main summarization entry point
# ─────────────────────────────────────────────
def generate_summary(text):
    text = text.strip()
    if not text:
        return "No content available to summarize."

    if TRANSFORMER_AVAILABLE:
        try:
            # Split into chunks ≤ 1024 tokens (~3500 chars)
            chunks = _split_text(text, max_chars=3500)
            summaries = []
            for chunk in chunks[:3]:          # limit to 3 chunks for speed
                result = _summarizer(
                    chunk,
                    max_length=180,
                    min_length=60,
                    do_sample=False,
                    truncation=True
                )
                summaries.append(result[0]['summary_text'])
            return ' '.join(summaries)
        except Exception as e:
            print(f"Transformer error: {e}. Falling back to extractive.")

    return extractive_summarize(text, num_sentences=7)


def _split_text(text, max_chars=3500):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for sent in sentences:
        if len(current) + len(sent) > max_chars and current:
            chunks.append(current.strip())
            current = sent
        else:
            current += " " + sent
    if current.strip():
        chunks.append(current.strip())
    return chunks


# ─────────────────────────────────────────────
# Score calculation (0 – 100)
# ─────────────────────────────────────────────
RESEARCH_KEYWORDS = [
    'abstract','introduction','methodology','method','methods',
    'results','conclusion','conclusions','discussion','references',
    'literature','review','analysis','experiment','data',
    'hypothesis','research','study','findings','algorithm',
    'model','evaluation','performance','accuracy','dataset',
    'proposed','approach','framework','system','novel',
    'objective','contribution','future','work','limitation'
]

def calculate_score(text):
    if not text or len(text.split()) < 50:
        return 0.0

    words = text.lower().split()
    word_count = len(words)

    # 1. Length score (0-30) — sweet spot 3000-8000 words
    if word_count < 500:
        length_score = 10
    elif word_count < 1500:
        length_score = 18
    elif word_count < 3000:
        length_score = 24
    elif word_count <= 8000:
        length_score = 30
    else:
        length_score = 25

    # 2. Keyword score (0-35)
    text_lower = text.lower()
    hits = sum(1 for kw in RESEARCH_KEYWORDS if kw in text_lower)
    keyword_score = min(35, (hits / len(RESEARCH_KEYWORDS)) * 55)

    # 3. Structure score (0-20)
    sections = ['abstract', 'introduction', 'methodology',
                'results', 'conclusion', 'references']
    found = sum(1 for s in sections if s in text_lower)
    structure_score = (found / len(sections)) * 20

    # 4. Sentence quality (0-15) — avg sentence length 15-25 words is ideal
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if len(s.split()) > 3]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if 15 <= avg_len <= 25:
            quality_score = 15
        elif 10 <= avg_len < 15 or 25 < avg_len <= 35:
            quality_score = 10
        else:
            quality_score = 5
    else:
        quality_score = 0

    total = length_score + keyword_score + structure_score + quality_score
    return round(min(total, 100), 2)


# ─────────────────────────────────────────────
# Keyword extraction (top-N)
# ─────────────────────────────────────────────
def extract_keywords(text, top_n=10):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in STOP_WORDS]
    freq = Counter(filtered)
    top = freq.most_common(top_n * 2)

    # Prefer words that appear in our research vocab
    research_set = set(RESEARCH_KEYWORDS)
    boosted = sorted(top, key=lambda x: (x[0] in research_set, x[1]), reverse=True)
    keywords = [w for w, _ in boosted[:top_n]]
    return ', '.join(keywords)
