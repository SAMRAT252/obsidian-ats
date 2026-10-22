import re
try:
    import pypdf as PyPDF2
except ImportError:
    try:
        import PyPDF2
    except ImportError:
        PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

def extract_text_from_pdf(file_path):
    text = ""
    if not PyPDF2:
        print("Warning: Neither pypdf nor PyPDF2 is installed.")
        return text
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text.strip()

def extract_text(file_path, file_type):
    if file_type.lower() == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type.lower() in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    return ""

def parse_resume(text):
    if not text or not text.strip():
        return {
            'name': 'Not detected',
            'email': 'Not detected',
            'phone': 'Not detected',
            'linkedin': 'Not detected',
            'github': 'Not detected',
            'education': 'Not detected',
            'skills': 'Not detected',
            'experience': 'Not detected',
            'projects': 'Not detected',
            'certifications': 'Not detected',
            'achievements': 'Not detected',
            'summary': 'Not detected'
        }

    parsed = {
        'name': 'Not detected',
        'email': 'Not detected',
        'phone': 'Not detected',
        'linkedin': 'Not detected',
        'github': 'Not detected',
        'education': 'Not detected',
        'skills': 'Not detected',
        'experience': 'Not detected',
        'projects': 'Not detected',
        'certifications': 'Not detected',
        'achievements': 'Not detected',
        'summary': 'Not detected'
    }

    # Regex patterns
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?'
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?'

    # Extract basic info
    emails = re.findall(email_pattern, text)
    if emails:
        parsed['email'] = emails[0]
        
    phones = re.findall(phone_pattern, text)
    if phones:
        parsed['phone'] = phones[0]
        
    linkedins = re.findall(linkedin_pattern, text)
    if linkedins:
        parsed['linkedin'] = linkedins[0]
        
    githubs = re.findall(github_pattern, text)
    if githubs:
        parsed['github'] = githubs[0]
        
    # Extract name (smart heuristic: first non-header, non-contact line)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:12]:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        if '@' in cleaned_line or '.com' in cleaned_line or 'http' in cleaned_line or 'www.' in cleaned_line:
            continue
        if re.search(r'\d{3}[-.\s]?\d{3}', cleaned_line) or re.search(r'\(\d{3}\)', cleaned_line):
            continue
        if any(kw in cleaned_line.upper() for kw in ['RESUME', 'CURRICULUM', 'VITAE', 'CONTACT', 'ABOUT', 'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROFILE']):
            continue
        words = cleaned_line.split()
        if 1 <= len(words) <= 4 and len(cleaned_line) <= 35:
            parsed['name'] = cleaned_line
            break
            
    if parsed['name'] == 'Not detected' and lines:
        parsed['name'] = lines[0]
        
    # Section extraction patterns (both standard words and compact representations)
    section_targets = {
        'education': ['EDUCATION', 'ACADEMICS', 'QUALIFICATIONS', 'ACADEMICBACKGROUND'],
        'skills': ['SKILLS', 'TECHNOLOGIES', 'TECHNICALSKILLS', 'CORECOMPETENCIES', 'EXPERTISE'],
        'experience': ['EXPERIENCE', 'WORKEXPERIENCE', 'PROFESSIONALEXPERIENCE', 'EMPLOYMENT', 'WORKHISTORY'],
        'projects': ['PROJECTS', 'PERSONALPROJECTS', 'KEYPROJECTS'],
        'certifications': ['CERTIFICATIONS', 'COURSES', 'LICENSES'],
        'achievements': ['ACHIEVEMENTS', 'AWARDS', 'HONORS'],
        'summary': ['SUMMARY', 'OBJECTIVE', 'PROFILE', 'ABOUT', 'PROFESSIONALSUMMARY', 'ABOUTME', 'BIO']
    }
    
    current_section = None
    section_content = {k: [] for k in section_targets.keys()}
    
    for line in lines:
        upper_line = line.upper().strip()
        compact_line = re.sub(r'[^A-Za-z]', '', line).upper()
        found_section = False
        
        # Check standard and compact headings for lines <= 35 chars
        if len(line) <= 35:
            for sec_name, targets in section_targets.items():
                for target in targets:
                    if compact_line == target or upper_line == target or upper_line.startswith(target + ':') or upper_line.startswith(target + ' -'):
                        current_section = sec_name
                        found_section = True
                        break
                if found_section:
                    break
        
        if not found_section:
            for sec_name, targets in section_targets.items():
                for target in targets:
                    if re.search(r'\b' + re.escape(target) + r'\b', upper_line):
                        current_section = sec_name
                        found_section = True
                        break
                if found_section:
                    break
        
        if found_section:
            continue
            
        if current_section:
            section_content[current_section].append(line)
            
    for sec_name, content in section_content.items():
        if content:
            parsed[sec_name] = '\n'.join(content)
            
    # Auto-extract recognized skills as a list
    try:
        from services.skill_extractor import extract_skills
        extracted = extract_skills(text)
        if extracted.get('all'):
            parsed['skills'] = extracted.get('all')
    except Exception as e:
        print(f"Skill auto-extraction warning: {e}")
            
    return parsed
