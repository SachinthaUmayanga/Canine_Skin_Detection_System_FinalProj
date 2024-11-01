import sqlite3
from flask import Blueprint, current_app, request, render_template, redirect, url_for, session, flash
import hashlib, os
from db import get_db_connection  # Import from db.py
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash the password before checking
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check the username and password against the database
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user['username']
            session['role'] = user['role']  # Add the role to the session
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid Credentials. Please try again.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user signup. Checks if the username already exists, hashes the password, and stores new user details.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('signup.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('signup.html')

        # Hash the password before storing
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        session['user'] = username
        flash('Successfully signed up!', 'success')
        return redirect(url_for('index'))
    
    return render_template('signup.html')

# Route for logout
@auth.route('/logout')
def logout():
    """
    Logs out the current user by removing them from the session.
    """
    session.pop('user', None)
    flash('Successfully logged out.', 'success')
    return redirect(url_for('index'))

# Define allowed file extensions for the profile picture
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for change profile
@auth.route('/change_profile', methods=['GET', 'POST'])
def change_profile():
    """
    Allows the user to change their username, password, full name, DOB, NIC, and address.
    """
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Ensures that rows behave like dictionaries
    cursor = conn.cursor()

    current_username = session['user']  # This gets the current username from session

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        nic = request.form.get('nic')
        address = request.form.get('address')

        # Password validation
        if new_password and new_password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('change_profile.html', user={
                'username': current_username,
                'full_name': full_name,
                'dob': dob,
                'nic': nic,
                'address': address
            })

        # Update password if provided
        if new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, current_username))
            flash('Password successfully changed!', 'success')

        # Update username if provided and is different from current
        if new_username and new_username != current_username:
            cursor.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, current_username))
            session['user'] = new_username  # Update session username
            current_username = new_username  # Update the current variable
            flash('Username successfully changed!', 'success')

        # Update full name, DOB, NIC, and address
        cursor.execute('UPDATE users SET full_name = ?, dob = ?, nic = ?, address = ? WHERE username = ?',
                       (full_name, dob, nic, address, session['user']))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # Retrieve user info to populate the form
    user = cursor.execute('SELECT * FROM users WHERE username = ?', (current_username,)).fetchone()
    conn.close()

    return render_template('change_profile.html', user=user)

