import re

TECHNICAL_SKILLS = {
    'Programming Languages': ['python', 'java', 'javascript', 'typescript', 'c', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'r', 'matlab', 'scala', 'perl', 'dart', 'lua', 'shell', 'bash', 'powershell', 'sql', 'html', 'css'],
    'Web Technologies': ['react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'asp.net', 'next.js', 'nuxt.js', 'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'webpack', 'rest api', 'graphql', 'fastapi'],
    'Databases': ['mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'firebase', 'oracle', 'sql server', 'neo4j', 'mariadb'],
    'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'ci/cd', 'github actions', 'gitlab ci', 'heroku', 'nginx', 'apache', 'linux', 'git'],
    'Data Science & ML': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'nlp', 'computer vision', 'opencv', 'data analysis', 'data visualization', 'tableau', 'power bi', 'spark', 'hadoop', 'jupyter', 'statistics', 'neural networks', 'random forest', 'svm', 'regression', 'classification', 'clustering', 'natural language processing', 'transformers', 'bert', 'gpt', 'llm', 'generative ai', 'reinforcement learning', 'feature engineering', 'model deployment'],
    'Mobile Development': ['android', 'ios', 'react native', 'flutter', 'swift', 'kotlin', 'xamarin', 'ionic'],
    'UI/UX & Design': ['figma', 'adobe xd', 'photoshop', 'illustrator', 'indesign', 'creative suite', 'ui design', 'ux design', 'typography', 'branding', 'wireframing', 'prototyping', 'user research', 'dreamweaver'],
    'Tools & Platforms': ['git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'vs code', 'intellij', 'postman']
}

SOFT_SKILLS = ['leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking', 'time management', 'adaptability', 'creativity', 'collaboration', 'project management', 'analytical thinking', 'attention to detail', 'decision making', 'negotiation', 'presentation', 'mentoring', 'agile', 'scrum']

def extract_skills(text):
    if not text:
        return {'technical': [], 'soft': [], 'all': []}
    
    text_lower = text.lower()
    
    found_technical = []
    found_soft = []
    
    # Extract technical skills
    for category, skills in TECHNICAL_SKILLS.items():
        for skill in skills:
            escaped_skill = re.escape(skill)
            pattern = r'(?:^|\s|\b)' + escaped_skill + r'(?:$|\s|\b)'
            if re.search(pattern, text_lower):
                if skill not in found_technical:
                    found_technical.append(skill)
                    
    # Extract soft skills
    for skill in SOFT_SKILLS:
        escaped_skill = re.escape(skill)
        pattern = r'(?:^|\s|\b)' + escaped_skill + r'(?:$|\s|\b)'
        if re.search(pattern, text_lower):
            if skill not in found_soft:
                found_soft.append(skill)
                
    return {
        'technical': found_technical,
        'soft': found_soft,
        'all': found_technical + found_soft
    }

def categorize_skills(skills_list):
    categorized = {cat: [] for cat in TECHNICAL_SKILLS.keys()}
    categorized['Soft Skills'] = []
    
    skills_lower = [s.lower() for s in skills_list]
    
    for skill in skills_lower:
        found = False
        for category, cat_skills in TECHNICAL_SKILLS.items():
            if skill in cat_skills:
                categorized[category].append(skill)
                found = True
                break
        if not found and skill in SOFT_SKILLS:
            categorized['Soft Skills'].append(skill)
            
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}
