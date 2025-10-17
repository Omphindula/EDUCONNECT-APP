from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from datetime import datetime
from database import get_db_connection
from models import User

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

# Edit a comment
@app.route('/forum/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    new_message = request.form.get('message')
    if not new_message:
        flash('Message cannot be empty.', 'error')
        return redirect(url_for('forum'))
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only allow editing own comment
    cursor.execute("SELECT user_id FROM comments WHERE id = %s", (comment_id,))
    row = cursor.fetchone()
    if not row or row[0] != current_user.id:
        cursor.close()
        conn.close()
        flash('You can only edit your own comment.', 'error')
        return redirect(url_for('forum'))
    cursor.execute("UPDATE comments SET message = %s WHERE id = %s", (new_message, comment_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Comment updated!', 'success')
    return redirect(url_for('forum'))

# Edit a discussion post
@app.route('/forum/post/<int:post_id>/edit', methods=['POST'])
@login_required
def edit_post(post_id):
    new_topic = request.form.get('topic')
    new_message = request.form.get('message')
    if not new_topic or not new_message:
        flash('Topic and message cannot be empty.', 'error')
        return redirect(url_for('forum'))
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only allow editing own post
    cursor.execute("SELECT user_id FROM discussions WHERE id = %s", (post_id,))
    row = cursor.fetchone()
    if not row or row[0] != current_user.id:
        cursor.close()
        conn.close()
        flash('You can only edit your own post.', 'error')
        return redirect(url_for('forum'))
    cursor.execute("UPDATE discussions SET topic = %s, message = %s WHERE id = %s", (new_topic, new_message, post_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Post updated!', 'success')
    return redirect(url_for('forum'))
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from datetime import datetime
from database import get_db_connection
from models import User

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        # user_data is a tuple: (id, name, email, password, role, date_joined)
        return User(user_data[0], user_data[1], user_data[2], user_data[4])
    return None

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        if not name or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already registered!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
        
        # Hash password and insert user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role, date_joined) VALUES (%s, %s, %s, %s, %s)",
            (name, email, hashed_password, role, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2], user_data[4])
            login_user(user)
            flash('Login successful!', 'success')
            if user_data[4] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Teacher routes
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM lessons WHERE teacher_id = %s ORDER BY created_at DESC",
        (current_user.id,)
    )
    lessons = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    processed = []
    for row in lessons:
        l = dict(zip(columns, row))
        if isinstance(l['created_at'], str):
            try:
                l['created_at'] = datetime.fromisoformat(l['created_at'])
            except Exception:
                pass
        processed.append(l)
    cursor.close()
    conn.close()
    return render_template('teacher_dashboard.html', lessons=processed)

@app.route('/teacher/lesson/create', methods=['GET', 'POST'])
@login_required
def create_lesson():
    if current_user.role != 'teacher':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title or not description:
            flash('Title and description are required!', 'error')
            return redirect(url_for('create_lesson'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lessons (title, description, teacher_id, created_at) VALUES (%s, %s, %s, %s)",
            (title, description, current_user.id, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('create_lesson.html')

@app.route('/teacher/resource/upload', methods=['GET', 'POST'])
@login_required
def upload_resource():
    if current_user.role != 'teacher':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        lesson_id = request.form.get('lesson_id')
        file = request.files.get('file')
        
        if not lesson_id or not file:
            flash('Lesson and file are required!', 'error')
            return redirect(url_for('upload_resource'))
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO resources (lesson_id, file_path, uploaded_by, uploaded_at) VALUES (%s, %s, %s, %s)",
            (lesson_id, filename, current_user.id, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Resource uploaded successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM lessons WHERE teacher_id = %s", (current_user.id,))
    lessons_raw = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    lessons = [dict(zip(columns, row)) for row in lessons_raw]
    cursor.close()
    conn.close()
    return render_template('upload_resource.html', lessons=lessons)

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get all lessons
    cursor.execute("SELECT l.*, u.name as teacher_name FROM lessons l JOIN users u ON l.teacher_id = u.id ORDER BY l.created_at DESC")
    lessons_raw = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    lessons = [dict(zip(columns, row)) for row in lessons_raw]
    # Get student progress
    cursor.execute("SELECT lesson_id, status FROM progress WHERE student_id = %s", (current_user.id,))
    progress_data = cursor.fetchall()
    # progress_data is a list of tuples (lesson_id, status)
    progress = {p[0]: p[1] for p in progress_data}
    cursor.close()
    conn.close()
    return render_template('student_dashboard.html', lessons=lessons, progress=progress)

@app.route('/student/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    if current_user.role != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get lesson details
    cursor.execute("SELECT l.*, u.name as teacher_name FROM lessons l JOIN users u ON l.teacher_id = u.id WHERE l.id = %s", (lesson_id,))
    lesson_row = cursor.fetchone()
    lesson = None
    if lesson_row:
        columns = [desc[0] for desc in cursor.description]
        lesson = dict(zip(columns, lesson_row))
        if isinstance(lesson['created_at'], str):
            try:
                lesson['created_at'] = datetime.fromisoformat(lesson['created_at'])
            except Exception:
                pass
    # Get resources for this lesson
    cursor.execute("SELECT * FROM resources WHERE lesson_id = %s", (lesson_id,))
    resources_raw = cursor.fetchall()
    resource_columns = [desc[0] for desc in cursor.description]
    resources = [dict(zip(resource_columns, row)) for row in resources_raw]
    cursor.close()
    conn.close()
    if not lesson:
        flash('Lesson not found!', 'error')
        return redirect(url_for('student_dashboard'))
    return render_template('view_lesson.html', lesson=lesson, resources=resources)

@app.route('/student/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    if current_user.role != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if progress exists
    cursor.execute("SELECT id FROM progress WHERE student_id = %s AND lesson_id = %s", (current_user.id, lesson_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            "UPDATE progress SET status = 'completed', updated_at = %s WHERE student_id = %s AND lesson_id = %s",
            (datetime.now(), current_user.id, lesson_id)
        )
    else:
        cursor.execute(
            "INSERT INTO progress (student_id, lesson_id, status, updated_at) VALUES (%s, %s, 'completed', %s)",
            (current_user.id, lesson_id, datetime.now())
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Lesson marked as completed!', 'success')
    return redirect(url_for('student_dashboard'))

# Discussion forum routes
@app.route('/forum')
@login_required
def forum():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch discussions
    cursor.execute(
        "SELECT d.*, u.name as user_name, u.role FROM discussions d JOIN users u ON d.user_id = u.id ORDER BY d.created_at DESC"
    )
    discussion_columns = [desc[0] for desc in cursor.description]
    discussions_raw = cursor.fetchall()
    discussions = [dict(zip(discussion_columns, row)) for row in discussions_raw]

    # Fetch all comments for these discussions
    discussion_ids = [d['id'] for d in discussions]
    comments = []
    if discussion_ids:
        format_strings = ','.join(['%s'] * len(discussion_ids))
        cursor.execute(
            f"SELECT c.*, u.name as user_name, u.role FROM comments c JOIN users u ON c.user_id = u.id WHERE c.discussion_id IN ({format_strings}) ORDER BY c.created_at ASC",
            tuple(discussion_ids)
        )
        comment_columns = [desc[0] for desc in cursor.description]
        comments_raw = cursor.fetchall()
        comments = [dict(zip(comment_columns, row)) for row in comments_raw]

    # Organize comments by discussion_id and parent_id
    comments_by_discussion = {}
    for c in comments:
        comments_by_discussion.setdefault(c['discussion_id'], []).append(c)

    cursor.close()
    conn.close()
    return render_template('forum.html', discussions=discussions, comments_by_discussion=comments_by_discussion)

# Route to post a comment
@app.route('/forum/comment', methods=['POST'])
@login_required
def post_comment():
    discussion_id = request.form.get('discussion_id')
    message = request.form.get('message')
    parent_id = request.form.get('parent_id') or None
    if not discussion_id or not message:
        flash('Comment message is required!', 'error')
        return redirect(url_for('forum'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comments (discussion_id, user_id, parent_id, message, created_at) VALUES (%s, %s, %s, %s, %s)",
        (discussion_id, current_user.id, parent_id, message, datetime.now())
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash('Comment posted!', 'success')
    return redirect(url_for('forum'))

@app.route('/forum/post', methods=['POST'])
@login_required
def post_discussion():
    topic = request.form.get('topic')
    message = request.form.get('message')
    
    if not topic or not message:
        flash('Topic and message are required!', 'error')
        return redirect(url_for('forum'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO discussions (topic, message, user_id, created_at) VALUES (%s, %s, %s, %s)",
        (topic, message, current_user.id, datetime.now())
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Discussion posted successfully!', 'success')
    return redirect(url_for('forum'))

# Progress tracking route
@app.route('/student/progress')
@login_required
def student_progress():
    if current_user.role != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    from datetime import datetime
    cursor.execute(
        """SELECT l.title, p.status, p.updated_at 
           FROM progress p 
           JOIN lessons l ON p.lesson_id = l.id 
           WHERE p.student_id = %s 
           ORDER BY p.updated_at DESC""",
        (current_user.id,)
    )
    progress_raw = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    processed = []
    for row in progress_raw:
        item = dict(zip(columns, row))
        if isinstance(item['updated_at'], str):
            try:
                item['updated_at'] = datetime.fromisoformat(item['updated_at'])
            except Exception:
                pass
        processed.append(item)
    cursor.close()
    conn.close()
    return render_template('progress.html', progress=processed)

if __name__ == '__main__':
    app.run(debug=True)
