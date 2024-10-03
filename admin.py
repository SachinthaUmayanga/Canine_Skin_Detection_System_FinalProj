from flask import Blueprint, render_template, request, session, redirect, url_for, flash, session, Response
from db import get_db_connection  # Import from db.py
import hashlib
from datetime import datetime
import csv
from io import StringIO

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
    recent_uploads = conn.execute('SELECT filename, upload_date, username, result FROM uploads ORDER BY upload_date DESC LIMIT 10').fetchall()
    conn.close()

    # Pass the data to the dashboard template
    return render_template('admin/admin_dashboard.html', total_users=total_users, total_reports=total_reports, total_uploads=total_uploads, recent_uploads=recent_uploads)


# Users route
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

        # Validate and update user details
        if not username or not role or not full_name or not dob or not nic or not address:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        conn.execute('UPDATE users SET username = ?, role = ?, full_name = ?, dob = ?, nic = ?, address = ? WHERE id = ?',
                     (username, role, full_name, dob, nic, address, user_id))
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

        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin.add_user'))

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert new user into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, full_name, dob, nic, address, role, password) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (username, full_name, dob, nic, address, role, hashed_password))
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
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    username = request.args.get('username')

    conn = get_db_connection()

    query = 'SELECT * FROM uploads WHERE 1=1'
    params = []

    if start_date and end_date:
        query += ' AND upload_date BETWEEN ? AND ?'
        params.extend([start_date, end_date])

    if username:
        query += ' AND username = ?'
        params.append(username)

    query += ' ORDER BY upload_date DESC'

    uploads = conn.execute(query, tuple(params)).fetchall()
    users = conn.execute('SELECT DISTINCT username FROM uploads').fetchall()
    conn.close()

    return render_template('admin/upload_logs.html', uploads=uploads, users=users)

# Preview Report Route
@admin.route('/preview_report', methods=['POST'])
def preview_report():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    username = request.form.get('username')

    conn = get_db_connection()

    # Build the query dynamically based on filters
    query = 'SELECT * FROM uploads WHERE 1=1'
    params = []
    
    if start_date and end_date:
        query += ' AND upload_date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    
    if username:
        query += ' AND username = ?'
        params.append(username)

    uploads = conn.execute(query, tuple(params)).fetchall()
    users = conn.execute('SELECT DISTINCT username FROM uploads').fetchall()
    conn.close()

    # Render the report preview page with the filtered uploads
    return render_template('admin/upload_logs.html', uploads=uploads, users=users)

# Generate and Download Report Route
@admin.route('/generate_report', methods=['POST'])
def generate_report():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    username = request.form.get('username')

    conn = get_db_connection()

    # Build the query dynamically based on filters
    query = 'SELECT * FROM uploads WHERE 1=1'
    params = []
    
    if start_date and end_date:
        query += ' AND upload_date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    
    if username:
        query += ' AND username = ?'
        params.append(username)

    uploads = conn.execute(query, tuple(params)).fetchall()
    conn.close()

    # Generate CSV
    si = StringIO()
    csv_writer = csv.writer(si)

    # Add headers
    csv_writer.writerow(['ID', 'Filename', 'Upload Date', 'Uploaded By', 'Result'])

    # Add data rows
    for upload in uploads:
        csv_writer.writerow([upload['id'], upload['filename'], upload['upload_date'], upload['username'], upload['result']])

    # Create the CSV response
    output = si.getvalue()
    si.close()

    response = Response(output, mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=upload_logs_report.csv'

    return response