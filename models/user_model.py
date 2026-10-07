from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, email, password, full_name=''):
    db = get_db()
    password_hash = generate_password_hash(password)
    try:
        cursor = db.execute(
            'INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, full_name)
        )
        db.commit()
        return cursor.lastrowid
    except db.IntegrityError:
        return None

def get_user_by_id(user_id):
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    return dict(user) if user else None

def get_user_by_username(username):
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    return dict(user) if user else None

def get_user_by_email(email):
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE email = ?', (email,)
    ).fetchone()
    return dict(user) if user else None

def update_user(user_id, **kwargs):
    db = get_db()
    if not kwargs:
        return False
    
    fields = []
    values = []
    for k, v in kwargs.items():
        if k == 'password':
            fields.append('password_hash = ?')
            values.append(generate_password_hash(v))
        else:
            fields.append(f'{k} = ?')
            values.append(v)
            
    query = f"UPDATE users SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    values.append(user_id)
    
    db.execute(query, values)
    db.commit()
    return True

def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    return True

def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)
