from database.db import get_db

def save_analysis(user_id, resume_id, job_description_id, ats_score, score_breakdown, matched_keywords, missing_keywords, matched_skills, missing_skills, recommendations, skill_gap_analysis):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO analyses 
           (user_id, resume_id, job_description_id, ats_score, score_breakdown, matched_keywords, missing_keywords, matched_skills, missing_skills, recommendations, skill_gap_analysis) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, resume_id, job_description_id, ats_score, score_breakdown, matched_keywords, missing_keywords, matched_skills, missing_skills, recommendations, skill_gap_analysis)
    )
    db.commit()
    return cursor.lastrowid

def get_analysis(analysis_id):
    db = get_db()
    analysis = db.execute(
        '''SELECT a.*, r.original_filename as resume_filename, j.title as job_title, j.company as job_company 
           FROM analyses a
           JOIN resumes r ON a.resume_id = r.id
           JOIN job_descriptions j ON a.job_description_id = j.id
           WHERE a.id = ?''', 
        (analysis_id,)
    ).fetchone()
    return dict(analysis) if analysis else None

def get_user_analyses(user_id):
    db = get_db()
    analyses = db.execute(
        '''SELECT a.*, r.original_filename as resume_filename, j.title as job_title, j.company as job_company 
           FROM analyses a
           JOIN resumes r ON a.resume_id = r.id
           JOIN job_descriptions j ON a.job_description_id = j.id
           WHERE a.user_id = ? ORDER BY a.created_at DESC''', 
        (user_id,)
    ).fetchall()
    return [dict(a) for a in analyses]

def delete_analysis(analysis_id):
    db = get_db()
    db.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
    db.commit()
    return True

def save_job_description(user_id, title, company, description, experience_required, parsed_data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO job_descriptions (user_id, title, company, description, experience_required, parsed_data) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, title, company, description, experience_required, parsed_data)
    )
    db.commit()
    return cursor.lastrowid

def get_job_description(jd_id):
    db = get_db()
    jd = db.execute(
        'SELECT * FROM job_descriptions WHERE id = ?', (jd_id,)
    ).fetchone()
    return dict(jd) if jd else None

def get_user_job_descriptions(user_id):
    db = get_db()
    jds = db.execute(
        'SELECT * FROM job_descriptions WHERE user_id = ? ORDER BY created_at DESC', (user_id,)
    ).fetchall()
    if not jds:
        ensure_benchmark_jobs(user_id)
        jds = db.execute(
            'SELECT * FROM job_descriptions WHERE user_id = ? ORDER BY created_at DESC', (user_id,)
        ).fetchall()
    return [dict(j) for j in jds]

def ensure_benchmark_jobs(user_id):
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM job_descriptions WHERE user_id = ?', (user_id,)).fetchone()[0]
    if count > 0:
        return
        
    import json
    from services import text_processor, skill_extractor
    
    benchmarks = [
        {
            'title': 'Senior Graphic & UI/UX Specialist',
            'company': 'Creative Design Studio',
            'experience': '3-5 years',
            'desc': 'Senior Graphic Designer and UI/UX Specialist with expertise in Adobe Creative Suite, Illustrator, Photoshop, InDesign, Figma, typography, branding, marketing collateral, presentation design, and web design (HTML, CSS). Strong creative direction, concept development, client presentation, and collaboration skills.'
        },
        {
            'title': 'AI & Machine Learning Engineer',
            'company': 'Obsidian AI Labs',
            'experience': '2-4 years',
            'desc': 'Machine Learning Engineer proficient in Python, PyTorch, TensorFlow, Scikit-learn, NLP, LLMs, computer vision, data analysis, SQL, Docker, and Git. Experience building and deploying machine learning pipelines, REST APIs, and model evaluation.'
        },
        {
            'title': 'Full-Stack Software Engineer',
            'company': 'Nexus Technologies',
            'experience': '3+ years',
            'desc': 'Full-Stack Software Engineer with expertise in Python, JavaScript, TypeScript, React, Node.js, SQL, PostgreSQL, Docker, Git, REST APIs, and CI/CD pipelines. Strong problem solving, software architecture, and agile team collaboration.'
        }
    ]
    
    for b in benchmarks:
        cleaned = text_processor.clean_text(b['desc'])
        skills = skill_extractor.extract_skills(cleaned)
        keywords = text_processor.extract_keywords(cleaned)
        parsed_data = json.dumps({'skills': skills, 'keywords': keywords, 'cleaned_text': cleaned})
        save_job_description(user_id, b['title'], b['company'], b['desc'], b['experience'], parsed_data)

