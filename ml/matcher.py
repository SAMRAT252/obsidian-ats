from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        # Calculate cosine similarity between the two documents
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except ValueError:
        return 0.0

def calculate_section_similarity(resume_sections, jd_sections):
    if not resume_sections or not jd_sections:
        return {}
        
    similarities = {}
    for section_name, resume_text in resume_sections.items():
        jd_text = jd_sections.get(section_name, '')
        
        if resume_text and resume_text != 'Not detected' and jd_text:
            sim = calculate_similarity(resume_text, jd_text)
            similarities[section_name] = sim
        else:
            similarities[section_name] = 0.0
            
    return similarities
