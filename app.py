from functools import wraps
from auth import auth
from admin import admin
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
from recognition import process_image, process_video
from db import get_db_connection  # Import from db.py

app = Flask(__name__)
app.secret_key = '1111'  # Secret key for session management and security

# Authentication Blueprint
app.register_blueprint(auth, url_prefix='/auth')

# Register the admin blueprint
app.register_blueprint(admin, url_prefix='/admin')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create upload folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def get_db_connection():
#     """
#     Establishes a connection to the SQLite database.
#     """
#     conn = sqlite3.connect('site.db')
#     conn.row_factory = sqlite3.Row  # Allows accessing rows as dictionaries
#     return conn

def get_disease_details(disease_name):
    """
    Fetches disease details from the database based on the disease name.
    """
    conn = get_db_connection()
    disease = conn.execute('SELECT * FROM diseases WHERE class_name = ?', (disease_name,)).fetchone()
    conn.close()
    return disease

@app.route('/')
def index():
    """
    Renders the index page.
    """
    return render_template('index.html')  # This matches the 'Home' link in the navbar


def login_required(f):
    """
    Decorator to ensure that the user is logged in before accessing certain routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login if not authenticated
        return f(*args, **kwargs)
    return decorated_function

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serves the uploaded files from the 'uploads' directory.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    """
    Handles image upload and processing.
    """
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
            
            # Process the uploaded image
            result = process_image(file_path)
            
            if result["status"] == "success":
                disease_details = get_disease_details(result["disease_name"])
                # Pass only the filename (not full path)
                return render_template('result.html', result=result, disease=disease_details, image_filename=filename)
            else:
                flash(f'Error: {result["message"]}', 'danger')
                return redirect(url_for('index'))

    return render_template('index.html', preloader=True)

@app.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    """
    Handles video upload and processing.
    """
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
                # You can save the first frame or pass a frame as an image (if needed)
                frame_image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Assuming first frame or thumbnail is saved
                return render_template('result.html', result=result, disease=disease_details, image_url=frame_image_url)
            else:
                flash(f'Error: {result["message"]}', 'danger')
                return redirect(url_for('index'))

    return redirect(url_for('index'))

def allowed_file(filename):
    """
    Checks if the file extension is allowed.
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/about')
def about():
    """
    Renders the about page.
    """
    return render_template('about.html')  # Matches the 'About Us' link

if __name__ == '__main__':
    app.run(debug=True)  # Runs the Flask application in debug mode
