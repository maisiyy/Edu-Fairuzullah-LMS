from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'lms.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads') 
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'ppt', 'pptx', 'doc', 'docx'}

app = Flask(__name__)
application = app  # REQUIRED FOR AWS
app.secret_key = 'edu_fairuzullah_secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DATABASE SETUP ---
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses 
                 (id INTEGER PRIMARY KEY, title TEXT, content TEXT, 
                  educator_id INTEGER, resource_filename TEXT, meeting_link TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS enrollments 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(course_id) REFERENCES courses(id))''')
    try:
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('teacher', 'pass', 'educator')")
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('student', 'pass', 'learner')")
        conn.commit()
    except: pass
    conn.close()

init_db()

# --- AUTH ROUTES (USER CRUD: CREATE, READ) ---
@app.route('/')
def home():
    if 'user_id' in session:
        if session['role'] == 'educator': return redirect(url_for('educator_dashboard'))
        return redirect(url_for('learner_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash("Invalid Login", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST']) # USER CRUD: CREATE
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role'] # 'educator' or 'learner'
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except:
            flash("Username already exists.", "danger")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST']) # USER CRUD: UPDATE & READ
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        new_password = request.form['password']
        conn.execute("UPDATE users SET password=? WHERE id=?", (new_password, session['user_id']))
        conn.commit()
        flash("Password updated successfully!", "success")
    
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/delete_account') # USER CRUD: DELETE
def delete_account():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    # Delete user and their enrollments/courses
    conn.execute("DELETE FROM enrollments WHERE user_id=?", (session['user_id'],))
    conn.execute("DELETE FROM courses WHERE educator_id=?", (session['user_id'],))
    conn.execute("DELETE FROM users WHERE id=?", (session['user_id'],))
    conn.commit()
    conn.close()
    session.clear()
    flash("Account deleted.", "info")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- EDUCATOR ROUTES (COURSE CRUD: CREATE, READ, UPDATE, DELETE) ---
@app.route('/educator')
def educator_dashboard():
    if session.get('role') != 'educator': return redirect(url_for('login'))
    conn = get_db_connection()
    courses = conn.execute("SELECT * FROM courses WHERE educator_id=?", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('educator.html', courses=courses)

@app.route('/add_course', methods=['POST'])
def add_course():
    if session.get('role') != 'educator': return redirect(url_for('login'))
    title = request.form['title']
    content = request.form['content']
    meeting_link = request.form.get('meeting_link')
    file = request.files.get('file')
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db_connection()
    conn.execute("INSERT INTO courses (title, content, educator_id, resource_filename, meeting_link) VALUES (?, ?, ?, ?, ?)", 
                 (title, content, session['user_id'], filename, meeting_link))
    conn.commit()
    conn.close()
    return redirect(url_for('educator_dashboard'))

@app.route('/edit_course/<int:id>', methods=['GET', 'POST']) # COURSE CRUD: UPDATE
def edit_course(id):
    if session.get('role') != 'educator': return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        meeting_link = request.form['meeting_link']
        conn.execute("UPDATE courses SET title=?, content=?, meeting_link=? WHERE id=?", (title, content, meeting_link, id))
        conn.commit()
        conn.close()
        return redirect(url_for('educator_dashboard'))
    
    course = conn.execute("SELECT * FROM courses WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit_course.html', course=course)

@app.route('/delete_course/<int:id>')
def delete_course(id):
    if session.get('role') != 'educator': return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute("DELETE FROM courses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('educator_dashboard'))

# --- LEARNER ROUTES ---
@app.route('/learner')
def learner_dashboard():
    if session.get('role') != 'learner': return redirect(url_for('login'))
    conn = get_db_connection()
    my_courses = conn.execute('''SELECT courses.* FROM courses JOIN enrollments ON courses.id = enrollments.course_id WHERE enrollments.user_id = ?''', (session['user_id'],)).fetchall()
    
    if my_courses:
        enrolled_ids = [c['id'] for c in my_courses]
        placeholders = ','.join('?' for _ in enrolled_ids)
        all_courses = conn.execute(f"SELECT * FROM courses WHERE id NOT IN ({placeholders})", enrolled_ids).fetchall()
    else:
        all_courses = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()
    return render_template('learner.html', my_courses=my_courses, available_courses=all_courses)

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if session.get('role') != 'learner': return redirect(url_for('login'))
    conn = get_db_connection()
    exists = conn.execute("SELECT * FROM enrollments WHERE user_id=? AND course_id=?", (session['user_id'], course_id)).fetchone()
    if not exists:
        conn.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (session['user_id'], course_id))
        conn.commit()
    conn.close()
    return redirect(url_for('learner_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)