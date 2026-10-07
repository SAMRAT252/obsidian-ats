def generate_recommendations(resume_data, jd_data, analysis_result):
    recommendations = []
    
    # 1. Check for missing keywords
    missing_kws = analysis_result.get('missing_keywords', [])
    if missing_kws:
        recommendations.append({
            'category': 'critical',
            'title': 'Add Missing Keywords',
            'description': f"Consider incorporating these keywords from the job description: {', '.join(missing_kws[:5])}",
            'section': 'Summary/Experience'
        })
        
    # 2. Check for missing skills
    missing_skills = analysis_result.get('missing_skills', [])
    if missing_skills:
        recommendations.append({
            'category': 'critical',
            'title': 'Address Missing Skills',
            'description': f"The JD requires these skills which are missing from your resume: {', '.join(missing_skills[:5])}",
            'section': 'Skills'
        })
        
    # 3. Check for section completeness
    sections = ['education', 'experience', 'skills', 'summary']
    for sec in sections:
        if not resume_data.get(sec) or resume_data.get(sec) == 'Not detected':
            recommendations.append({
                'category': 'important',
                'title': f'Add {sec.title()} Section',
                'description': f"Your resume is missing an explicit {sec} section, which is critical for ATS parsing.",
                'section': sec.title()
            })
            
    # 4. Check for quantifiable achievements (numbers in experience)
    exp_text = resume_data.get('experience', '')
    if exp_text and exp_text != 'Not detected':
        import re
        if not re.search(r'\d+', exp_text):
            recommendations.append({
                'category': 'optional',
                'title': 'Add Quantifiable Achievements',
                'description': "Use numbers and metrics to quantify your achievements in the experience section (e.g., 'improved performance by 20%').",
                'section': 'Experience'
            })
            
    # 5. Check for action verbs
    action_verbs = ['developed', 'managed', 'led', 'created', 'designed', 'implemented']
    if exp_text:
        exp_lower = exp_text.lower()
        found_verbs = [v for v in action_verbs if v in exp_lower]
        if len(found_verbs) < 2:
            recommendations.append({
                'category': 'optional',
                'title': 'Use Strong Action Verbs',
                'description': "Start your bullet points with strong action verbs like 'Developed', 'Managed', 'Led', 'Implemented'.",
                'section': 'Experience'
            })
            
    return recommendations
