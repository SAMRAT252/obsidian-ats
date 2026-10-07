from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def vectorize_texts(texts):
    if not texts:
        return None, []
        
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    return tfidf_matrix, feature_names.tolist()

def get_tfidf_scores(text):
    if not text:
        return []
        
    vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get scores for the first document
        scores = tfidf_matrix.toarray()[0]
        
        # Create list of (word, score) tuples
        word_scores = [(feature_names[i], float(scores[i])) for i in range(len(feature_names))]
        
        # Sort by score descending
        word_scores.sort(key=lambda x: x[1], reverse=True)
        return word_scores
    except ValueError:
        # Happens if text contains no valid words after stopword removal
        return []
