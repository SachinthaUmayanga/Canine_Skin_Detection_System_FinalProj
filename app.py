from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3
from recognition import process_image, process_video

app = Flask(__name__)
app.secret_key = '1111'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_disease_details(disease_name):
    conn = get_db_connection()
    disease = conn.execute('SELECT * FROM diseases WHERE class_name = ?', (disease_name,)).fetchone()
    conn.close()
    return disease

@app.route('/')
def index():
    return render_template('index.html')

# Authentication Blueprint
from auth import auth
app.register_blueprint(auth, url_prefix='/auth')

def login_required(f):
    """Decorator to require login for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            result = process_image(file_path)
            
            if result["status"] == "success":
                disease_details = get_disease_details(result["disease_name"])
                return render_template('result.html', result=result, disease=disease_details)
            else:
                flash(f'Error: {result["message"]}', 'danger')
                return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('index'))

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            result = process_video(file, filename, app.config['UPLOAD_FOLDER'])

            if result["status"] == "success":
                disease_details = get_disease_details(result["disease_name"])
                return render_template('result.html', result=result, disease=disease_details)
            else:
                flash(f'Error: {result["message"]}', 'danger')
                return redirect(url_for('index'))

    return redirect(url_for('index'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
