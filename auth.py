from flask import Blueprint, request, render_template, redirect, url_for, session
import sqlite3
import hashlib  # For password hashing

auth = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

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
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            error = 'Passwords do not match. Please try again.'
            return render_template('signup.html', error=error)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            error = 'Username already exists. Please choose a different one.'
            return render_template('signup.html', error=error)

        # Hash the password before storing
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        session['user'] = username
        return redirect(url_for('index'))
    
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


# Uncomment and implement the profile change route if needed
# @auth.route('/change_profile', methods=['GET', 'POST'])
# def change_profile():
#     if 'user' not in session:
#         return redirect(url_for('auth.login'))

#     if request.method == 'POST':
#         # Handle profile change logic
#         pass

#     return render_template('change_profile.html')
