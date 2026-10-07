# AI-Powered ATS Resume Screening & Job Matching System

A multi-page web application built with **Flask**, **Scikit-Learn**, **NLTK**, **Pandas**, and **Chart.js** that simulates a modern enterprise Applicant Tracking System (ATS). It extracts text from PDF/DOCX resumes, carries out NLP preprocessing, extracts structured domain skills, performs TF-IDF vectorization and cosine similarity calculations, computes an ATS compatibility score, detects keyword/skill gaps, and renders interactive analytics dashboards.

---

## 🌟 Key Highlights & Engineering Features

- **Genuine AI/ML Pipeline**: TF-IDF Vectorization, Cosine Similarity matrix evaluation, Tokenization, Lemmatization, Stop-word removal, and N-gram extraction.
- **Section & Skill Extraction**: Recognizes education, experience, skills, certifications, and links from resumes. Evaluates over 200+ technical and soft skills.
- **Configurable ATS Scoring Model**: Transparent weighted scoring breakdown:
  - Keyword Match (30%)
  - Skills Match (25%)
  - Semantic Similarity (20%)
  - Experience Depth (15%)
  - Education Relevance (5%)
  - Structure & Completeness (5%)
- **Multi-Page Architecture**: 16 dedicated templates with tailored UI themes (Futuristic Dark AI landing, SaaS dashboard, AI Laboratory analysis, Split Comparison, Career Growth gap view).
- **Interactive Data Visualizations**: Radial ATS gauges, animated score breakdown progress bars, Chart.js doughnut distributions, bar charts, and side-by-side radar comparison graphs.
- **Full User Session Isolation**: Secure SQLite database storage with parameterized SQL queries, password hashing via Werkzeug, and authenticated workflows.

---

## 🏗️ System Architecture

```
User Resume (.pdf / .docx)
          │
          ▼
   [Resume Parser] ──(PyPDF2 / docx / Regex)──► [Extracted Entities & Sections]
          │                                              │
          ▼                                              ▼
[Text Preprocessor] ──(NLTK / Lemmatization)──► [Cleaned Tokens & N-Grams]
          │
          ├────────────────────────┬────────────────────────┐
          ▼                        ▼                        ▼
  [Skill Extractor]      [Keyword Matcher]        [TF-IDF Vectorizer]
(200+ Ontology Match)     (Jaccard & Density)     (Scikit-Learn TF-IDF)
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                        [Cosine Similarity & Matcher]
                                   │
                                   ▼
                          [ATS Scorer Engine]
                 ┌─────────────────────────────────┐
                 │ Keyword Match           (30%)   │
                 │ Skill Match             (25%)   │
                 │ Semantic Similarity     (20%)   │
                 │ Experience Relevance    (15%)   │
                 │ Education Relevance     (5%)    │
                 │ Structure Quality       (5%)    │
                 └─────────────────────────────────┘
                                   │
                                   ▼
                       [Recommendation Engine]
                                   │
                                   ▼
      [Multi-Page Dashboard & Visualizations (Chart.js / CSS3)]
```

---

## 📁 Project Directory Structure

```
ats-resume-system/
│
├── app.py                      # Core Flask application & controller routes
├── config.py                   # App configurations, secrets, upload quotas
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation & viva guide
│
├── database/
│   ├── db.py                   # SQLite database connections & lifecycle hooks
│   └── schema.sql              # Relational schema (users, resumes, JDs, analyses)
│
├── models/
│   ├── user_model.py           # User authentication & profile management
│   ├── resume_model.py         # Resume persistence & CRUD
│   └── analysis_model.py       # Job description & analysis storage
│
├── services/
│   ├── resume_parser.py        # PDF & DOCX extraction with section regexes
│   ├── text_processor.py       # NLTK tokenization, normalization & TF-IDF keywords
│   ├── skill_extractor.py      # 200+ skill ontology matching & categorization
│   ├── keyword_matcher.py      # Match percentage, density & gap detection
│   ├── ats_scorer.py           # Multi-factor weighted ATS score calculation
│   └── recommendation_engine.py# Actionable categorized resume suggestions
│
├── ml/
│   ├── vectorizer.py           # Scikit-learn TF-IDF vectorizer logic
│   └── matcher.py              # Cosine similarity calculations
│
├── templates/
│   ├── base.html               # Shared layout, navigation, flash messages
│   ├── index.html              # Futuristic AI landing page
│   ├── login.html              # Clean authentication login
│   ├── register.html           # Registration portal
│   ├── dashboard.html          # SaaS user dashboard with KPI widgets
│   ├── upload.html             # Document workspace & drag-and-drop zone
│   ├── job_description.html    # Recruitment JD manager
│   ├── analysis.html           # AI Laboratory extracted sections report
│   ├── ats_score.html          # Circular gauge & component breakdown
│   ├── keywords.html           # Matched & missing keyword chips + chart
│   ├── skill_gap.html          # Strong, moderate & missing skill matrix
│   ├── suggestions.html        # Critical, important & optional recommendations
│   ├── compare.html            # Split-screen dual resume radar comparison
│   ├── history.html            # Historical timeline of past screenings
│   ├── profile.html            # User account settings
│   ├── about.html              # Editorial about page
│   └── help.html               # Technical FAQ & guide
│
├── static/
│   ├── css/
│   │   ├── global.css          # Design system, CSS variables & typography
│   │   ├── home.css            # Dark AI hero & gradient animations
│   │   ├── auth.css            # Glassmorphism auth cards
│   │   ├── dashboard.css       # Sidebar scaffolding & widget styling
│   │   └── analysis.css        # Score ring, chips, bars & radar styling
│   │
│   └── js/
│       ├── main.js             # Mobile toggles, flash dismissals & interactions
│       ├── dashboard.js        # KPI cards & distribution charts
│       ├── upload.js           # Drag & drop file validation & progress
│       ├── analysis.js         # Circular gauge count-up & radar charts
│       └── charts.js           # Shared Chart.js utilities
│
├── uploads/                    # Secure storage for uploaded resumes
└── instance/
    └── ats.db                  # Local SQLite database
```

---

## 💻 Installation & Setup (Windows)

### 1. Prerequisites
- Python 3.10+ installed
- Pip package manager

### 2. Setup Virtual Environment
Open PowerShell or Command Prompt in the project directory:

```powershell
cd C:\Users\gupta\.gemini\antigravity\scratch\ats-resume-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
python app.py
```

### 5. Access the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🛠️ Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| `'python' is not recognized` | Python is not added to system PATH | Reinstall Python with "Add python.exe to PATH" checked, or specify full path `C:\Users\<user>\AppData\Local\Programs\Python\Python3xx\python.exe`. |
| `ModuleNotFoundError: No module named 'pypdf'` | Missing package in environment | Run `pip install pypdf python-docx scikit-learn nltk` inside the active virtual environment. |
| `sqlite3.OperationalError: no such table` | Database uninitialized | Delete `instance/ats.db` and re-run `python app.py` (the application automatically executes `schema.sql` on startup). |
| `Port 5000 already in use` | Another process is holding port 5000 | In PowerShell, run `Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process` or specify `port=5050` in `app.run()`. |
| `NLTK Resource punkt not found` | Offline network during first run | Run `python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"` |

---

## 🔬 NLP & AIML Methodology

1. **Text Normalization**:
   - Lowercasing and striping non-alphanumeric noise using regular expressions.
   - Word tokenization and stop-word filtering using standard English vocabularies.
   - Lemmatization via NLTK WordNet to reduce inflected forms (e.g., *analyzing* $\rightarrow$ *analyze*).
2. **Term Frequency-Inverse Document Frequency (TF-IDF)**:
   - Measures how important a term is to a resume relative to the job description corpus:
   $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
3. **Cosine Similarity**:
   - Compares the high-dimensional angle between the resume TF-IDF vector $\vec{u}$ and JD vector $\vec{v}$:
   $$\text{Cosine Similarity} = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \frac{\sum_{i=1}^n u_i v_i}{\sqrt{\sum_{i=1}^n u_i^2} \sqrt{\sum_{i=1}^n v_i^2}}$$
4. **Transparent Scoring Formula**:
   $$\text{ATS Score} = 0.30 \cdot S_{\text{kw}} + 0.25 \cdot S_{\text{skills}} + 0.20 \cdot S_{\text{cosine}} + 0.15 \cdot S_{\text{exp}} + 0.05 \cdot S_{\text{edu}} + 0.05 \cdot S_{\text{struct}}$$

---

## 🎓 Viva Voce Preparation (30 Questions & Answers)

### A. NLP & Machine Learning

**Q1: What is an ATS and how does it screen candidates?**
> **Answer**: An Applicant Tracking System (ATS) is an enterprise application that filters, organizes, and scores candidate resumes against target job specifications using keyword extraction, section parsing, and semantic matching algorithms.

**Q2: Why do we use TF-IDF instead of simple word frequency?**
> **Answer**: Simple frequency biases common words (e.g., "experience", "work"). TF-IDF balances Term Frequency with Inverse Document Frequency, giving higher weights to rare, domain-specific technical terms like "Kubernetes" or "PyTorch".

**Q3: How does Cosine Similarity evaluate resume match?**
> **Answer**: It calculates the cosine of the angle between two normalized vectors in multi-dimensional space. A value of 1 represents identical keyword distributions, while 0 indicates no shared terms. Because it relies on angles rather than vector lengths, it is immune to resume length bias.

**Q4: What is the purpose of text tokenization and stop-word removal?**
> **Answer**: Tokenization divides raw text strings into distinct linguistic units (words/tokens). Stop-word removal filters out syntactical noise words ("is", "the", "at") that contain no semantic signal for job qualifications.

**Q5: What is Lemmatization and how is it different from Stemming?**
> **Answer**: Stemming simply chops off word endings using heuristic rules (e.g., "studies" $\rightarrow$ "studi"). Lemmatization uses vocabulary and morphological analysis to return the true root word or lemma ("studies" $\rightarrow$ "study").

**Q6: What are N-Grams and why are they important in resume analysis?**
> **Answer**: N-Grams are contiguous sequences of $n$ words. Bi-grams and tri-grams capture multi-word technical concepts like "machine learning", "deep learning", or "REST API" that would lose context if split into single tokens.

**Q7: How are skills extracted from unstructured resume text?**
> **Answer**: We utilize regular expression boundary matching against a comprehensive ontology of over 200 categorized technical and soft skills, cross-referencing extracted tokens against both technical classifications and job requirements.

**Q8: Can Cosine Similarity alone act as a full ATS score?**
> **Answer**: No. Cosine similarity only measures textual co-occurrence. A comprehensive ATS score must also evaluate section structure, experience depth, skill coverage, and education level.

**Q9: What happens if a resume has images or multi-column layouts?**
> **Answer**: Many traditional ATS parsers break on multi-column layouts. Our parser uses stream-based text extraction to reconstruct contiguous text buffers, while recommending clean, single-column formatting.

**Q10: Why didn't you use hard-coded scores?**
> **Answer**: Hard-coded scores provide zero diagnostic value. Our system computes scores on real mathematical vector projections and token overlaps derived from the user's specific inputs.

---

### B. Architecture, Backend & Database

**Q11: Why did you choose Flask over Django for this project?**
> **Answer**: Flask is lightweight, micro-architectural, and modular. It gives full transparency over routing, allows direct integration with scientific Python libraries like Scikit-Learn and NLTK, and avoids unnecessary boilerplate.

**Q12: How are passwords secured in your application?**
> **Answer**: Passwords are never stored in plaintext. They are hashed using PBKDF2/SHA-256 with random salting via Werkzeug's `generate_password_hash` and verified with `check_password_hash`.

**Q13: How is user data isolated between accounts?**
> **Answer**: Session cookies track the authenticated `user_id`. Every SQL query joins or filters by `WHERE user_id = ?`, ensuring candidates only ever access their own resumes and analyses.

**Q14: Explain the role of SQLite in this application.**
> **Answer**: SQLite provides a serverless, zero-configuration relational database with full ACID compliance, parameterized query support to prevent SQL injection, and foreign key cascading.

**Q15: How does the application prevent SQL Injection?**
> **Answer**: All database interactions use parameterized placeholders (`?`), ensuring user inputs are treated strictly as data literals rather than executable SQL commands.

**Q16: How do you handle file upload security?**
> **Answer**: We validate file extensions against a strict whitelist (`.pdf`, `.docx`), sanitize filenames using `secure_filename`, assign unique UUID prefixes, and enforce a 16MB file limit.

**Q17: What is the purpose of the `@login_required` decorator?**
> **Answer**: It wraps view functions to inspect active session variables. If an unauthenticated user attempts to access private routes, it redirects them to the login screen with a warning flash message.

**Q18: What is Jinja2 template inheritance and why is it used?**
> **Answer**: It allows child templates to extend a common `base.html` structure. This enforces DRY (Don't Repeat Yourself) design for headers, navigation, flash notifications, and stylesheets while enabling unique per-page content.

**Q19: How are complex analysis results persisted in the database?**
> **Answer**: Structured analytical objects (breakdowns, skill lists, recommendations) are serialized as JSON strings in dedicated columns and deserialized upon retrieval.

**Q20: Why is the backend structured into modular service folders?**
> **Answer**: Separation of concerns: `models/` manages persistence, `services/` encapsulates business logic and parsing, `ml/` houses vector models, and `app.py` acts strictly as the HTTP controller.

---

### C. ATS Scoring & System Engineering

**Q21: Walk through the weighted scoring formula.**
> **Answer**: The ATS score combines Keyword Match (30%), Skills Match (25%), Semantic Similarity (20%), Experience (15%), Education (5%), and Structure (5%).

**Q22: How does the system evaluate the Experience section?**
> **Answer**: It verifies the presence of an identifiable work experience block and inspects lexical density, length, and the presence of quantifiable impact metrics and action verbs.

**Q23: How does the system evaluate Education?**
> **Answer**: It scans for academic keywords (Bachelor's, B.S., Master's, Ph.D., Degree) within the detected education section and evaluates alignment with role prerequisites.

**Q24: How does the Skill Gap feature determine recommendations?**
> **Answer**: It performs set-difference operations between the job description's extracted skills and the resume's skills: $\text{Missing} = \text{Skills}_{\text{JD}} \setminus \text{Skills}_{\text{Resume}}$.

**Q25: How are suggestions categorized into Critical, Important, and Optional?**
> **Answer**: Missing required skills and core keywords are classified as **Critical**; missing standard sections (like Education or Experience) are **Important**; and stylistic improvements (action verbs, quantifiable metrics) are **Optional**.

**Q26: How does the resume comparison feature work?**
> **Answer**: The user selects two historical analyses. The system extracts their component scores and renders a side-by-side card breakdown accompanied by a multi-axis Chart.js radar visualization.

**Q27: How does the system handle corrupted or unreadable resumes?**
> **Answer**: File operations are wrapped in `try/except` blocks. If text cannot be parsed, default fallback objects ("Not detected") are returned without crashing the web process.

**Q28: What is the client-server data flow during analysis?**
> **Answer**: The user submits the form via HTTP POST $\rightarrow$ Flask processes files $\rightarrow$ NLP/ML pipeline computes scores $\rightarrow$ results are stored in SQLite $\rightarrow$ server responds with a redirect to `/analysis/<id>` $\rightarrow$ client renders Jinja template and initializes Chart.js scripts.

**Q29: What are the current limitations of the system?**
> **Answer**: OCR is not included for scanned image PDFs, and the skill database requires periodic updates to incorporate emerging frameworks.

**Q30: What is the future scope of this project?**
> **Answer**: Integrating transformer-based contextual embeddings (like BERT/RoBERTa), adding an OCR module (Tesseract) for scanned resumes, and introducing Generative AI for real-time bullet point re-writing.

---

## 🎤 2-Minute Project Presentation Script

> *"Good morning, respected evaluators.*
> 
> *Today, I am proud to present my project: **AI-Powered ATS Resume Screening & Job Matching System**.*
> 
> *In today’s recruitment landscape, over 75% of resumes are screened by automated Applicant Tracking Systems before a human recruiter ever sees them. Many qualified candidates are rejected simply because their resumes lack targeted keywords, fail parsing checks, or lack semantic alignment with the job description.*
> 
> *To solve this, I designed and built an enterprise-grade, multi-page AI application that provides candidates with complete transparency into how ATS engines evaluate their resumes.*
> 
> *Our technical pipeline works in distinct stages:*
> *First, we extract clean textual data from uploaded PDF and DOCX files.*
> *Second, using **NLTK**, we tokenize, remove stop words, and lemmatize the text into normalized linguistic tokens.*
> *Third, our domain extractor evaluates the resume against a comprehensive 200+ skill ontology.*
> *Fourth, using **Scikit-Learn**, we generate TF-IDF vector representations and calculate the cosine similarity between the candidate's resume and the target job description.*
> 
> *Unlike trivial projects with arbitrary numbers, our system computes an **authentic, multi-factor ATS score** based on 6 weighted components: keyword overlap, skill match, semantic similarity, experience depth, education relevance, and resume structure.*
> 
> *The user experience is delivered across 16 responsive, themed pages — featuring a SaaS dashboard, circular score gauges, keyword gap visualizers, actionable recommendations, and a dual-resume radar comparison tool powered by **Chart.js**.*
> 
> *In summary, this project bridges the gap between job seekers and automated recruitment engines using genuine AI and modern full-stack web engineering. Thank you, and I look forward to your questions."*
