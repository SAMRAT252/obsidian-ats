import os
import uuid
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from config import Config
from database import db
from models.user_model import (
    create_user, get_user_by_id, get_user_by_username, 
    get_user_by_email, update_user, verify_password
)
from models.resume_model import (
    save_resume, get_resume, get_user_resumes, 
    update_resume, delete_resume
)
from models.analysis_model import (
    save_analysis, get_analysis, get_user_analyses, delete_analysis,
    save_job_description, get_job_description, get_user_job_descriptions
)

# Services and ML modules
from services import (
    resume_parser, text_processor, skill_extractor,
    keyword_matcher, ats_scorer, recommendation_engine
)
from ml import matcher, vectorizer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance and upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

    db.init_app(app)

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_id') is None:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    @app.before_request
    def before_request():
        if not hasattr(app, '_db_initialized'):
            with app.app_context():
                db.init_db()
            app._db_initialized = True

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def _parse_analysis_record(analysis):
        """Helper to safely parse JSON strings stored in an analysis record."""
        if not analysis:
            return None
        parsed = dict(analysis)
        for field in ['score_breakdown', 'skill_gap_analysis']:
            val = parsed.get(field)
            if isinstance(val, str):
                try:
                    parsed[field] = json.loads(val)
                except Exception:
                    parsed[field] = {}
            elif val is None:
                parsed[field] = {}

        for field in ['matched_keywords', 'missing_keywords', 'matched_skills', 'missing_skills', 'recommendations']:
            val = parsed.get(field)
            if isinstance(val, str):
                try:
                    parsed[field] = json.loads(val)
                except Exception:
                    parsed[field] = []
            elif val is None:
                parsed[field] = []
        return parsed

    def _parse_resume_record(resume):
        """Helper to safely parse JSON strings stored in a resume record."""
        if not resume:
            return None
        parsed = dict(resume)
        val = parsed.get('parsed_data')
        if isinstance(val, str):
            try:
                parsed['parsed_data'] = json.loads(val)
            except Exception:
                parsed['parsed_data'] = {}
        elif val is None:
            parsed['parsed_data'] = {}
        return parsed

    # Context processor to inject user into templates
    @app.context_processor
    def inject_user():
        if session.get('user_id'):
            return dict(current_user={'id': session['user_id'], 'username': session.get('username'), 'full_name': session.get('full_name')})
        return dict(current_user=None)

    # Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if session.get('user_id'):
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            login_identifier = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            # Allow logging in with either username OR email
            user = get_user_by_username(login_identifier)
            if not user and '@' in login_identifier:
                user = get_user_by_email(login_identifier)
                
            if user and verify_password(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                flash('Logged in successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username/email or password.', 'danger')
                
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if session.get('user_id'):
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            full_name = request.form.get('full_name', '').strip()
            
            if not username or not email or not password:
                flash('Please fill in all required fields.', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('register.html')
                
            if get_user_by_username(username):
                flash('Username already exists.', 'danger')
                return render_template('register.html')
                
            if get_user_by_email(email):
                flash('Email already registered.', 'danger')
                return render_template('register.html')
                
            user_id = create_user(username, email, password, full_name)
            if user_id:
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('An error occurred during registration.', 'danger')
                
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        session.clear()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        raw_analyses = get_user_analyses(session['user_id'])
        analyses = []
        for a in raw_analyses:
            item = _parse_analysis_record(a)
            # Add formatted fields for template display
            item['resume_name'] = item.get('resume_filename', f"Resume #{item['resume_id']}")
            item['job_title'] = item.get('job_title', 'General Target Role')
            item['date'] = str(item.get('created_at', ''))[:10]
            analyses.append(item)
        return render_template('dashboard.html', analyses=analyses)

    @app.route('/upload-resume', methods=['GET', 'POST'])
    @login_required
    def upload_resume():
        if request.method == 'POST':
            if 'resume' not in request.files:
                flash('No file part selected.', 'danger')
                return redirect(request.url)
            file = request.files['resume']
            if file.filename == '':
                flash('No file selected.', 'danger')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                original_filename = secure_filename(file.filename) or file.filename
                extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                try:
                    extracted_text = resume_parser.extract_text(file_path, extension)
                    parsed_data = resume_parser.parse_resume(extracted_text)
                    parsed_data_json = json.dumps(parsed_data)
                except Exception as e:
                    print(f"Error parsing resume: {e}")
                    extracted_text = ""
                    parsed_data_json = "{}"
                
                resume_id = save_resume(session['user_id'], unique_filename, original_filename, file_path, extension)
                if resume_id:
                    update_resume(resume_id, extracted_text=extracted_text, parsed_data=parsed_data_json)
                    
                    target_jd_id = request.form.get('job_description_id')
                    if not target_jd_id:
                        jds = get_user_job_descriptions(session['user_id'])
                        if jds:
                            target_jd_id = jds[0]['id']
                            
                    if target_jd_id:
                        try:
                            analysis_id = _run_ats_pipeline(session['user_id'], int(resume_id), int(target_jd_id))
                            if analysis_id:
                                flash('Resume uploaded and ATS analysis generated successfully!', 'success')
                                return redirect(url_for('analysis_view', analysis_id=analysis_id))
                        except Exception as e:
                            print(f"Auto-analysis on upload failed: {e}")
                            
                    flash('Resume uploaded and parsed successfully.', 'success')
                else:
                    flash('Failed to save resume record.', 'danger')
                return redirect(url_for('upload_resume'))
            else:
                flash('Invalid file type. Only PDF and DOCX files are allowed.', 'danger')
                
        resumes = get_user_resumes(session['user_id'])
        job_descriptions = get_user_job_descriptions(session['user_id'])
        return render_template('upload.html', resumes=resumes, job_descriptions=job_descriptions)

    @app.route('/job-description', methods=['GET', 'POST'])
    @login_required
    def job_description():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            company = request.form.get('company', '').strip()
            experience_required = request.form.get('experience_required', '').strip()
            description = request.form.get('description', '').strip()
            
            if not title or not description:
                flash('Title and description are required.', 'danger')
                return redirect(request.url)
                
            try:
                cleaned_text = text_processor.clean_text(description)
                jd_skills = skill_extractor.extract_skills(cleaned_text)
                jd_keywords = text_processor.extract_keywords(cleaned_text)
                parsed_data = {
                    'skills': jd_skills,
                    'keywords': jd_keywords,
                    'cleaned_text': cleaned_text
                }
                parsed_data_json = json.dumps(parsed_data)
            except Exception as e:
                print(f"Error parsing JD: {e}")
                parsed_data_json = "{}"
            
            jd_id = save_job_description(session['user_id'], title, company, description, experience_required, parsed_data_json)
            if jd_id:
                flash('Job description saved successfully.', 'success')
            else:
                flash('Failed to save job description.', 'danger')
            return redirect(url_for('job_description'))
            
        job_descriptions = get_user_job_descriptions(session['user_id'])
        return render_template('job_description.html', job_descriptions=job_descriptions)

    def _run_ats_pipeline(user_id, resume_id, job_description_id):
        resume = get_resume(resume_id)
        jd = get_job_description(job_description_id)
        if not resume or resume['user_id'] != user_id or not jd or jd['user_id'] != user_id:
            return None

        # 1. Ensure Resume text and parsed data exist
        res_text = resume.get('extracted_text') or ''
        res_parsed = {}
        if resume.get('parsed_data'):
            try:
                res_parsed = json.loads(resume['parsed_data'])
            except Exception:
                res_parsed = {}

        if not res_text or not res_parsed:
            res_text = resume_parser.extract_text(resume['file_path'], resume['file_type'])
            res_parsed = resume_parser.parse_resume(res_text)
            update_resume(resume_id, extracted_text=res_text, parsed_data=json.dumps(res_parsed))
            
        # 2. Ensure JD is parsed
        jd_parsed = {}
        if jd.get('parsed_data'):
            try:
                jd_parsed = json.loads(jd['parsed_data'])
            except Exception:
                jd_parsed = {}

        if not jd_parsed:
            cleaned_jd = text_processor.clean_text(jd['description'])
            jd_parsed = {
                'skills': skill_extractor.extract_skills(cleaned_jd),
                'keywords': text_processor.extract_keywords(cleaned_jd),
                'cleaned_text': cleaned_jd
            }
        
        # 3. Keyword Matching
        resume_keywords = text_processor.extract_keywords(text_processor.clean_text(res_text))
        jd_keywords = jd_parsed.get('keywords', [])
        jd_keywords_only = [kw[0] if isinstance(kw, (tuple, list)) else kw for kw in jd_keywords]
        resume_keywords_only = [kw[0] if isinstance(kw, (tuple, list)) else kw for kw in resume_keywords]
        
        keyword_match_res = keyword_matcher.match_keywords(resume_keywords_only, jd_keywords_only)
        matched_keywords = keyword_match_res.get('matched', [])
        missing_keywords = keyword_match_res.get('missing', [])
        
        # 4. Skill Gap Analysis
        resume_skills = skill_extractor.extract_skills(res_text)
        jd_skills_all = jd_parsed.get('skills', {}).get('all', [])
        resume_skills_all = resume_skills.get('all', [])
        
        matched_skills = list(set(jd_skills_all).intersection(set(resume_skills_all)))
        missing_skills = list(set(jd_skills_all) - set(resume_skills_all))
        
        strong_skills = matched_skills[:6]
        moderate_skills = [s for s in resume_skills_all if s not in matched_skills][:6]
        
        learning_recs = []
        for s in missing_skills[:4]:
            learning_recs.append(f"Consider taking a certification or completing a hands-on project featuring {s.title()}.")
        if not learning_recs:
            learning_recs.append("Great alignment! Continue strengthening your core engineering fundamentals.")

        skill_gap_analysis = {
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
            "strong_skills": strong_skills,
            "moderate_skills": moderate_skills,
            "missing_skills": missing_skills,
            "recommendations": learning_recs
        }
        
        # 5. Semantic Similarity (Cosine Similarity via TF-IDF)
        similarity_score = matcher.calculate_similarity(res_text, jd['description'])
        
        # 6. ATS Score calculation
        skill_match_res = {
            'matched': matched_skills,
            'missing': missing_skills
        }
        score_res = ats_scorer.calculate_ats_score(
            res_parsed, 
            jd_parsed, 
            similarity_score, 
            keyword_match_res, 
            skill_match_res
        )
        
        # 7. Actionable Recommendations
        recommendations_input = {
            'missing_keywords': missing_keywords,
            'missing_skills': missing_skills
        }
        recommendations = recommendation_engine.generate_recommendations(res_parsed, jd_parsed, recommendations_input)
        
        # 8. Persist Analysis
        analysis_id = save_analysis(
            user_id,
            resume_id,
            job_description_id,
            score_res.get('total_score', 0),
            json.dumps(score_res.get('breakdown', {})),
            json.dumps(matched_keywords),
            json.dumps(missing_keywords),
            json.dumps(matched_skills),
            json.dumps(missing_skills),
            json.dumps(recommendations),
            json.dumps(skill_gap_analysis)
        )
        return analysis_id

    @app.route('/analyze', methods=['POST'])
    @login_required
    def analyze():
        resume_id = request.form.get('resume_id')
        job_description_id = request.form.get('job_description_id')
        
        # If user clicked quick-analyze without selecting a resume, use their most recent resume
        if not resume_id:
            user_resumes = get_user_resumes(session['user_id'])
            if user_resumes:
                resume_id = user_resumes[0]['id']
            else:
                flash('Please upload a resume first before analyzing.', 'warning')
                return redirect(url_for('upload_resume'))
        
        if not job_description_id:
            jds = get_user_job_descriptions(session['user_id'])
            if jds:
                job_description_id = jds[0]['id']
            else:
                flash('Please select or create a target job description.', 'danger')
                return redirect(url_for('job_description'))
                
        try:
            analysis_id = _run_ats_pipeline(session['user_id'], int(resume_id), int(job_description_id))
            if analysis_id:
                flash('ATS analysis generated successfully!', 'success')
                return redirect(url_for('analysis_view', analysis_id=analysis_id))
            else:
                flash('Invalid resume or job description selection.', 'danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Analysis error: {e}")
            flash(f'An error occurred during analysis: {str(e)}', 'danger')
            return redirect(url_for('dashboard'))

    @app.route('/analysis/<int:analysis_id>')
    @login_required
    def analysis_view(analysis_id):
        raw_analysis = get_analysis(analysis_id)
        if not raw_analysis or raw_analysis['user_id'] != session['user_id']:
            flash('Analysis not found.', 'danger')
            return redirect(url_for('dashboard'))

        analysis = _parse_analysis_record(raw_analysis)
        raw_resume = get_resume(analysis['resume_id'])
        resume = _parse_resume_record(raw_resume)
        jd = get_job_description(analysis['job_description_id'])

        return render_template('analysis.html', analysis=analysis, resume=resume, job_description=jd)

    @app.route('/ats-score/<int:analysis_id>')
    @login_required
    def ats_score(analysis_id):
        raw_analysis = get_analysis(analysis_id)
        if not raw_analysis or raw_analysis['user_id'] != session['user_id']:
            flash('Analysis not found.', 'danger')
            return redirect(url_for('dashboard'))
        
        analysis = _parse_analysis_record(raw_analysis)
        score = analysis.get('ats_score', 0)
        if score >= 90:
            analysis['category'] = 'Excellent'
        elif score >= 75:
            analysis['category'] = 'Good'
        elif score >= 60:
            analysis['category'] = 'Fair'
        else:
            analysis['category'] = 'Poor'
        return render_template('ats_score.html', analysis=analysis)

    @app.route('/keywords/<int:analysis_id>')
    @login_required
    def keywords(analysis_id):
        raw_analysis = get_analysis(analysis_id)
        if not raw_analysis or raw_analysis['user_id'] != session['user_id']:
            flash('Analysis not found.', 'danger')
            return redirect(url_for('dashboard'))
        analysis = _parse_analysis_record(raw_analysis)
        return render_template('keywords.html', analysis=analysis)

    @app.route('/skill-gap/<int:analysis_id>')
    @login_required
    def skill_gap(analysis_id):
        raw_analysis = get_analysis(analysis_id)
        if not raw_analysis or raw_analysis['user_id'] != session['user_id']:
            flash('Analysis not found.', 'danger')
            return redirect(url_for('dashboard'))
        analysis = _parse_analysis_record(raw_analysis)
        return render_template('skill_gap.html', analysis=analysis)

    @app.route('/suggestions/<int:analysis_id>')
    @login_required
    def suggestions(analysis_id):
        raw_analysis = get_analysis(analysis_id)
        if not raw_analysis or raw_analysis['user_id'] != session['user_id']:
            flash('Analysis not found.', 'danger')
            return redirect(url_for('dashboard'))
        analysis = _parse_analysis_record(raw_analysis)
        return render_template('suggestions.html', analysis=analysis)

    @app.route('/compare', methods=['GET', 'POST'])
    @login_required
    def compare():
        raw_analyses = get_user_analyses(session['user_id'])
        analyses = [_parse_analysis_record(a) for a in raw_analyses]

        if request.method == 'POST':
            a1_id = request.form.get('analysis_id_1')
            a2_id = request.form.get('analysis_id_2')
            
            if not a1_id or not a2_id:
                flash('Please select two analyses to compare.', 'danger')
                return render_template('compare.html', analyses=analyses)
                
            raw_a1 = get_analysis(a1_id)
            raw_a2 = get_analysis(a2_id)
            
            if not raw_a1 or not raw_a2 or raw_a1['user_id'] != session['user_id'] or raw_a2['user_id'] != session['user_id']:
                flash('Invalid selection for comparison.', 'danger')
                return render_template('compare.html', analyses=analyses)
                
            a1 = _parse_analysis_record(raw_a1)
            a2 = _parse_analysis_record(raw_a2)
            return render_template('compare.html', analyses=analyses, analysis1=a1, analysis2=a2)
            
        return render_template('compare.html', analyses=analyses)

    @app.route('/history')
    @login_required
    def history():
        raw_analyses = get_user_analyses(session['user_id'])
        analyses = []
        for a in raw_analyses:
            item = _parse_analysis_record(a)
            item['resume_name'] = item.get('resume_filename', f"Resume #{item['resume_id']}")
            item['job_title'] = item.get('job_title', 'General Target Role')
            item['date'] = str(item.get('created_at', ''))[:10]
            analyses.append(item)
        return render_template('history.html', analyses=analyses)

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user = get_user_by_id(session['user_id'])
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            
            updates = {}
            if full_name and full_name != user.get('full_name'):
                updates['full_name'] = full_name
            if email and email != user.get('email'):
                existing = get_user_by_email(email)
                if existing and existing['id'] != user['id']:
                    flash('Email already in use by another account.', 'danger')
                else:
                    updates['email'] = email
                    
            if current_password and new_password:
                if verify_password(user['password_hash'], current_password):
                    updates['password'] = new_password
                else:
                    flash('Current password is incorrect.', 'danger')
                    
            if updates:
                update_user(user['id'], **updates)
                if 'full_name' in updates:
                    session['full_name'] = updates['full_name']
                flash('Profile updated successfully.', 'success')
                
            return redirect(url_for('profile'))
            
        # Telemetry and stats for Career Profile
        resumes = get_user_resumes(session['user_id'])
        jds = get_user_job_descriptions(session['user_id'])
        analyses = get_user_analyses(session['user_id'])
        
        avg_score = round(sum(a['ats_score'] for a in analyses) / len(analyses), 1) if analyses else 0
        last_date = str(analyses[0]['created_at'])[:10] if analyses else 'None'
        
        stats = {
            'resumes_count': len(resumes),
            'job_descriptions_count': len(jds),
            'analyses_count': len(analyses),
            'average_score': avg_score,
            'last_analysis_date': last_date,
            'skills_improved': min(len(resumes) * 2 + 1, 15) if resumes else 0
        }
        
        latest_id = analyses[0]['id'] if analyses else None
        return render_template('profile.html', user=user, stats=stats, latest_analysis_id=latest_id)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/help')
    def help_page():
        return render_template('help.html')

    @app.route('/api/dashboard-stats')
    @login_required
    def api_dashboard_stats():
        resumes = get_user_resumes(session['user_id'])
        jds = get_user_job_descriptions(session['user_id'])
        analyses = get_user_analyses(session['user_id'])
        
        avg_score = round(sum(a['ats_score'] for a in analyses) / len(analyses), 1) if analyses else 0.0

        dist = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        recent = []
        for a in analyses[:5]:
            score = a['ats_score']
            if score >= 90:
                dist['excellent'] += 1
            elif score >= 75:
                dist['good'] += 1
            elif score >= 60:
                dist['fair'] += 1
            else:
                dist['poor'] += 1
            recent.append({
                'date': str(a.get('created_at', ''))[:10],
                'score': score
            })

        return jsonify({
            'resumes_count': len(resumes),
            'job_descriptions_count': len(jds),
            'analyses_count': len(analyses),
            'average_score': avg_score,
            'score_distribution': dist,
            'recent_analyses': recent
        })

    @app.route('/api/resumes')
    @login_required
    def api_resumes():
        resumes = get_user_resumes(session['user_id'])
        return jsonify(resumes)

    @app.route('/api/job-descriptions')
    @login_required
    def api_job_descriptions():
        jds = get_user_job_descriptions(session['user_id'])
        return jsonify(jds)

    @app.route('/delete-analysis/<int:analysis_id>', methods=['POST'])
    @login_required
    def delete_analysis_route(analysis_id):
        analysis = get_analysis(analysis_id)
        if analysis and analysis['user_id'] == session['user_id']:
            delete_analysis(analysis_id)
            flash('Analysis deleted successfully.', 'success')
        else:
            flash('Analysis not found.', 'danger')
        return redirect(url_for('history'))

    @app.route('/delete-resume/<int:resume_id>', methods=['POST'], endpoint='delete_resume')
    @login_required
    def delete_resume_route(resume_id):
        resume = get_resume(resume_id)
        if resume and resume['user_id'] == session['user_id']:
            try:
                if os.path.exists(resume['file_path']):
                    os.remove(resume['file_path'])
            except Exception:
                pass
            delete_resume(resume_id)
            flash('Resume deleted successfully.', 'success')
        else:
            flash('Resume not found.', 'danger')
        return redirect(url_for('upload_resume'))

    # Backward-compatible route endpoint alias
    app.add_url_rule('/delete-resume/<int:resume_id>', endpoint='delete_resume_route', view_func=delete_resume_route, methods=['POST'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
