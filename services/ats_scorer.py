WEIGHTS = {
    'keyword_match': 0.30,
    'skills_match': 0.25,
    'semantic_similarity': 0.20,
    'experience': 0.15,
    'education': 0.05,
    'structure': 0.05
}

def _score_experience(resume_data, jd_data):
    exp_text = resume_data.get('experience', '')
    if not exp_text or exp_text == 'Not detected':
        return 0.0
    
    score = 50.0
    words = len(exp_text.split())
    if words > 100:
        score += 25.0
    if words > 200:
        score += 25.0
        
    return min(100.0, score)

def _score_education(resume_data, jd_data):
    edu_text = resume_data.get('education', '')
    if not edu_text or edu_text == 'Not detected':
        return 0.0
    
    score = 50.0
    edu_text_lower = edu_text.lower()
    if 'bachelor' in edu_text_lower or 'b.s' in edu_text_lower or 'b.a' in edu_text_lower or 'degree' in edu_text_lower:
        score += 25.0
    if 'master' in edu_text_lower or 'm.s' in edu_text_lower or 'phd' in edu_text_lower:
        score += 25.0
        
    return min(100.0, score)

def _score_structure(resume_data):
    sections_present = 0
    total_sections = 7
    sections = ['email', 'phone', 'education', 'skills', 'experience', 'summary', 'projects']
    
    for sec in sections:
        val = resume_data.get(sec, '')
        if val and val != 'Not detected':
            sections_present += 1
            
    return (sections_present / total_sections) * 100.0

def calculate_ats_score(resume_data, jd_data, similarity_score, keyword_match_result, skill_match_result):
    keyword_score = keyword_match_result.get('match_percentage', 0.0)
    
    skills_matched = len(skill_match_result.get('matched', []))
    skills_missing = len(skill_match_result.get('missing', []))
    total_skills = skills_matched + skills_missing
    skill_score = (skills_matched / total_skills * 100.0) if total_skills > 0 else 0.0
    
    semantic_score = similarity_score * 100.0
    
    exp_score = _score_experience(resume_data, jd_data)
    edu_score = _score_education(resume_data, jd_data)
    struct_score = _score_structure(resume_data)
    
    total_score = (
        keyword_score * WEIGHTS['keyword_match'] +
        skill_score * WEIGHTS['skills_match'] +
        semantic_score * WEIGHTS['semantic_similarity'] +
        exp_score * WEIGHTS['experience'] +
        edu_score * WEIGHTS['education'] +
        struct_score * WEIGHTS['structure']
    )
    
    category = 'Poor'
    if total_score >= 90:
        category = 'Excellent'
    elif total_score >= 75:
        category = 'Good'
    elif total_score >= 60:
        category = 'Fair'
        
    strengths = []
    weaknesses = []
    
    if keyword_score > 80:
        strengths.append("Strong keyword match with job description.")
    elif keyword_score < 50:
        weaknesses.append("Low keyword overlap. Add more relevant keywords.")
        
    if skill_score > 80:
        strengths.append("Excellent skills match.")
    elif skill_score < 50:
        weaknesses.append("Missing several required skills.")
        
    if struct_score > 80:
        strengths.append("Good resume structure with all key sections.")
    else:
        weaknesses.append("Missing important sections (e.g., summary, skills, or experience).")
        
    if exp_score < 50:
        weaknesses.append("Experience section could be more detailed.")
        
    return {
        'total_score': round(total_score, 2),
        'breakdown': {
            'keyword_match': round(keyword_score, 2),
            'skills_match': round(skill_score, 2),
            'semantic_similarity': round(semantic_score, 2),
            'experience': round(exp_score, 2),
            'education': round(edu_score, 2),
            'structure': round(struct_score, 2)
        },
        'category': category,
        'strengths': strengths,
        'weaknesses': weaknesses
    }
