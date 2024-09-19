from flask import Blueprint, render_template, request, session, redirect, url_for, flash, session
from db import get_db_connection  # Import from db.py
import hashlib

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
    # total_uploads = conn.execute('SELECT COUNT(*) FROM uploads').fetchone()[0]
    total_reports = conn.execute('SELECT COUNT(*) FROM diseases').fetchone()[0]
    # recent_uploads = conn.execute('SELECT filename, upload_date, processed, result FROM uploads ORDER BY upload_date DESC LIMIT 5').fetchall()
    conn.close()

    # Pass the data to the dashboard template
    return render_template('admin/admin_dashboard.html', total_users=total_users, total_reports=total_reports)
# , total_uploads=total_uploads, recent_uploads=recent_uploads)

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

@admin.route('/disease_reports')
def disease_reports():
    conn = get_db_connection()
    diseases = conn.execute('SELECT * FROM diseases').fetchall()
    conn.close()

    return render_template('admin/disease_reports.html', diseases=diseases)