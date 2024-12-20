from flask import Blueprint, render_template, request, session, redirect, url_for, flash, session, Response,make_response, current_app
from db import get_db_connection  # Import from db.py
import hashlib, datetime, csv, os
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__)

# Admin dashboard route
@admin.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    # Fetch some statistics from the database
    conn = get_db_connection()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_uploads = conn.execute('SELECT COUNT(*) FROM uploads').fetchone()[0]
    total_reports = conn.execute('SELECT COUNT(*) FROM diseases').fetchone()[0]
    recent_uploads = conn.execute('SELECT filename, upload_date, username, result FROM uploads ORDER BY upload_date DESC LIMIT 15').fetchall()
    conn.close()

    # Pass the data to the dashboard template
    return render_template('admin/admin_dashboard.html', total_users=total_users, total_reports=total_reports, total_uploads=total_uploads, recent_uploads=recent_uploads)

# Users route
# Define the allowed file extensions for profile pictures
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/manage_users')
def manage_users():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    # Fetch users from the database (including full_name and role)
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, full_name, role FROM users').fetchall()
    conn.close()

    return render_template('admin/manage_users.html', users=users)

@admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        nic = request.form.get('nic')
        address = request.form.get('address')

        # Handle profile picture upload
        file = request.files.get('profile_picture')
        profile_picture = user['profile_picture']  # Keep current profile picture by default

        # Check if a new file was uploaded and if it's allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)  # Ensure the directory exists
            profile_picture_path = os.path.join(upload_folder, filename)
            file.save(profile_picture_path)

            # Save only the relative path to the 'uploads' folder
            profile_picture = f'uploads/{filename}'

        # Validate and update user details
        if not username or not role or not full_name or not dob or not nic or not address:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        # Update the user record with or without the profile picture change
        conn.execute('''
            UPDATE users 
            SET username = ?, role = ?, full_name = ?, dob = ?, nic = ?, address = ?, profile_picture = ? 
            WHERE id = ?
            ''', (username, role, full_name, dob, nic, address, profile_picture, user_id))
        conn.commit()
        conn.close()

        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    conn.close()
    return render_template('admin/edit_user.html', user=user)

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash('User deleted successfully!', 'danger')
    return redirect(url_for('admin.manage_users'))

@admin.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        full_name = request.form['full_name']
        dob = request.form['dob']
        nic = request.form['nic']
        address = request.form['address']
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Handle profile picture
        profile_picture = request.files.get('profile_picture')
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Initialize the profile_picture_path to None
        profile_picture_path = None

        # Check if a profile picture was uploaded and validate the file
        if profile_picture and allowed_file(profile_picture.filename):
            # Secure the filename
            filename = secure_filename(profile_picture.filename)
            # Create a relative path for the profile picture (without 'static/')
            profile_picture_path = os.path.join('uploads', filename).replace('\\', '/')
            # Save the file to the static/profile directory
            profile_picture.save(os.path.join(current_app.root_path, 'static', profile_picture_path))
        else:
            flash('Invalid file type for profile picture. Please upload a valid image file (png, jpg, jpeg, gif).', 'danger')
            return redirect(url_for('admin.add_user'))

        # Insert new user into the database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO users (username, full_name, dob, nic, address, role, password, profile_picture) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, full_name, dob, nic, address, role, hashed_password, profile_picture_path))
        conn.commit()
        conn.close()

        flash('New user added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/add_user.html')


# Disease route
@admin.route('/disease_reports')
def disease_reports():
    conn = get_db_connection()
    diseases = conn.execute('SELECT * FROM diseases').fetchall()
    conn.close()

    return render_template('admin/disease_reports.html', diseases=diseases)

@admin.route('/edit_disease/<int:disease_id>', methods=['GET', 'POST'])
def edit_disease(disease_id):
    conn = get_db_connection()
    
    # Fetch the disease details for editing
    disease = conn.execute('SELECT * FROM diseases WHERE disease_id = ?', (disease_id,)).fetchone()

    if not disease:
        flash('Disease not found!', 'danger')
        return redirect(url_for('admin.disease_list'))  # Redirect to disease list if disease is not found

    if request.method == 'POST':
        # Retrieve updated data from the form
        class_name = request.form['class_name']
        symptoms = request.form['symptoms']
        recommendations = request.form['recommendations']
        details = request.form['details']

        # Update disease in the database
        conn.execute('UPDATE diseases SET class_name = ?, symptoms = ?, recommendations = ?, details = ? WHERE disease_id = ?',
                     (class_name, symptoms, recommendations, details, disease_id))
        conn.commit()
        conn.close()

        flash('Disease updated successfully!', 'success')
        return redirect(url_for('admin.disease_reports'))

    conn.close()
    return render_template('admin/edit_disease.html', disease=disease)

@admin.route('/delete_disease/<int:disease_id>', methods=['POST'])
def delete_disease(disease_id):
    conn = get_db_connection()
    
    # Delete the disease from the database
    conn.execute('DELETE FROM diseases WHERE disease_id = ?', (disease_id,))
    conn.commit()
    conn.close()

    flash('Disease deleted successfully!', 'success')
    return redirect(url_for('admin.disease_reports'))

@admin.route('/add_disease', methods=['GET', 'POST'])
def add_disease():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Retrieve form data
        class_name = request.form['class_name']
        symptoms = request.form['symptoms']
        recommendations = request.form['recommendations']
        details = request.form['details']

        # Insert the new disease into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO diseases (class_name, symptoms, recommendations, details) VALUES (?, ?, ?, ?)',
                     (class_name, symptoms, recommendations, details))
        conn.commit()
        conn.close()

        flash('New disease added successfully!', 'success')
        return redirect(url_for('admin.disease_reports'))

    return render_template('admin/add_disease.html')

# Upload logs route
@admin.route('/upload_logs')
def upload_logs():
    conn = get_db_connection()
    uploads = conn.execute('SELECT * FROM uploads').fetchall()
    conn.close()
    
    return render_template('admin/upload_logs.html', uploads=uploads)

@admin.route('/delete_log/<int:upload_id>', methods=['POST'])
def delete_log(upload_id):
    conn = get_db_connection()
    
    # Delete the disease from the database
    conn.execute('DELETE FROM uploads WHERE id = ?', (upload_id,))
    conn.commit()
    conn.close()

    flash('Log deleted successfully!', 'success')
    return redirect(url_for('admin.upload_logs'))

@admin.route('/filter_logs', methods=['GET'])
def filter_logs():
    # Get the filter parameters from the query string
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    username = request.args.get('username', '')

    # Establish a connection to the database
    conn = get_db_connection()

    # Query to get the upload logs based on filters
    query = "SELECT id, filename, upload_date, username, result FROM uploads WHERE 1=1"
    params = []

    # Filter by start date, end date, and username if provided
    if start_date:
        query += " AND upload_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND upload_date <= ?"
        params.append(end_date)
    if username:
        query += " AND username = ?"
        params.append(username)

    # Execute the query to get the filtered uploads
    uploads = conn.execute(query, params).fetchall()

    # Query to fetch all distinct usernames from the uploads table
    users = conn.execute("SELECT DISTINCT username FROM uploads").fetchall()

    # Close the database connection
    conn.close()

    # Render the template, passing the uploads and the list of distinct users
    return render_template('admin/upload_logs.html', uploads=uploads, users=users)

#  Route to generate PDF report
@admin.route('/generate_pdf_report', methods=['GET'])
def generate_pdf_report():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    username = request.args.get('username', '')

    conn = get_db_connection()
    query = "SELECT id, filename, upload_date, username, result FROM uploads WHERE 1=1"
    params = []

    if start_date:
        query += " AND upload_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND upload_date <= ?"
        params.append(end_date)
    if username:
        query += " AND username = ?"
        params.append(username)

    uploads = conn.execute(query, params).fetchall()
    conn.close()

    # Create the PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Upload Logs Report")
    
    # Add Title and Date
    pdf.drawString(100, 750, f"Upload Logs Report - {datetime.datetime.now().strftime('%Y-%m-%d')}")
    
    # Add Table Headers
    pdf.drawString(50, 700, "ID")
    pdf.drawString(100, 700, "Filename")
    pdf.drawString(250, 700, "Date Uploaded")
    pdf.drawString(400, 700, "Uploaded By")
    pdf.drawString(500, 700, "Result")
    
    # Add Table Rows
    y = 680
    for upload in uploads:
        pdf.drawString(50, y, str(upload['id']))
        pdf.drawString(100, y, upload['filename'])
        pdf.drawString(250, y, upload['upload_date'])
        pdf.drawString(400, y, upload['username'])
        pdf.drawString(500, y, upload['result'])
        y -= 20
    
    # Finish the PDF
    pdf.save()

    # Return the PDF as a downloadable file
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="upload_logs_{datetime.datetime.now().strftime("%Y-%m-%d")}.pdf"'
    return response

# Route to preview the report
@admin.route('/preview_report', methods=['POST'])
def preview_report():
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    username = request.form.get('username', '')

    conn = get_db_connection()
    query = "SELECT id, filename, upload_date, username, result FROM uploads WHERE 1=1"
    params = []

    if start_date:
        query += " AND upload_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND upload_date <= ?"
        params.append(end_date)
    if username:
        query += " AND username = ?"
        params.append(username)

    uploads = conn.execute(query, params).fetchall()
    users = conn.execute("SELECT DISTINCT username FROM uploads").fetchall()
    conn.close()

    return render_template('admin/upload_logs.html', uploads=uploads, users=users)