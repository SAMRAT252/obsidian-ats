import sys
import os

# Adjust path to import text_processor and skill_extractor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from text_processor import extract_keywords
    from skill_extractor import extract_skills
except ImportError:
    pass

def match_keywords(resume_keywords, jd_keywords):
    if not jd_keywords:
        return {'matched': [], 'missing': [], 'match_percentage': 0.0}
        
    res_kws_lower = {k.lower() for k in resume_keywords}
    jd_kws_lower = {k.lower() for k in jd_keywords}
    
    matched = list(res_kws_lower.intersection(jd_kws_lower))
    missing = list(jd_kws_lower.difference(res_kws_lower))
    
    percentage = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0.0
    
    return {
        'matched': matched,
        'missing': missing,
        'match_percentage': round(percentage, 2)
    }

def extract_jd_keywords(jd_text):
    if not jd_text:
        return []
        
    # Extract using TF-IDF
    tfidf_kws = extract_keywords(jd_text, top_n=40)
    keywords = [kw for kw, score in tfidf_kws]
    
    # Extract skills
    skills_dict = extract_skills(jd_text)
    
    # Combine and deduplicate
    all_kws = list(set(keywords + skills_dict['all']))
    
    return all_kws

def calculate_keyword_density(text, keywords):
    if not text or not keywords:
        return {}
        
    text_lower = text.lower()
    density = {}
    
    for kw in keywords:
        kw_lower = kw.lower()
        count = text_lower.count(kw_lower)
        if count > 0:
            density[kw] = count
            
    return density
