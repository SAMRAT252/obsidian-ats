from database.db import get_db

def save_resume(user_id, filename, original_filename, file_path, file_type):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO resumes (user_id, filename, original_filename, file_path, file_type) 
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, filename, original_filename, file_path, file_type)
    )
    db.commit()
    return cursor.lastrowid

def get_resume(resume_id):
    db = get_db()
    resume = db.execute(
        'SELECT * FROM resumes WHERE id = ?', (resume_id,)
    ).fetchone()
    return dict(resume) if resume else None

def get_user_resumes(user_id):
    db = get_db()
    resumes = db.execute(
        'SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC', (user_id,)
    ).fetchall()
    return [dict(r) for r in resumes]

def update_resume(resume_id, extracted_text=None, parsed_data=None):
    db = get_db()
    updates = []
    values = []
    
    if extracted_text is not None:
        updates.append('extracted_text = ?')
        values.append(extracted_text)
    
    if parsed_data is not None:
        updates.append('parsed_data = ?')
        values.append(parsed_data)
        
    if not updates:
        return False
        
    query = f"UPDATE resumes SET {', '.join(updates)} WHERE id = ?"
    values.append(resume_id)
    
    db.execute(query, values)
    db.commit()
    return True

def delete_resume(resume_id):
    db = get_db()
    db.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
    db.commit()
    return True
