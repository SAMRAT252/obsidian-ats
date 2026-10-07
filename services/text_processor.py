import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
from collections import Counter
import sys
import os

# Adjust path to import ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from ml.vectorizer import get_tfidf_scores
except ImportError:
    get_tfidf_scores = None

nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[^a-zA-Z0-9\s.,;-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text):
    if not text:
        return []
    return word_tokenize(text)

def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [t for t in tokens if t.lower() not in stop_words and len(t) > 1]

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = clean_text(text)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

def extract_keywords(text, top_n=30):
    if not text or not get_tfidf_scores:
        return []
    normalized = normalize_text(text)
    scores = get_tfidf_scores(normalized)
    return scores[:top_n]

def extract_ngrams(text, n=2, top_n=20):
    if not text:
        return []
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    n_grams = ngrams(tokens, n)
    n_grams_freq = Counter(n_grams)
    return [(' '.join(gram), count) for gram, count in n_grams_freq.most_common(top_n)]
