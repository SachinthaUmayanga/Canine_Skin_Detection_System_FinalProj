from flask import Blueprint, request, render_template, redirect, url_for, session

auth = Blueprint('auth', __name__)

# Hardcoded credentials for testing purposes
HARDCODED_USERNAME = 'admin'
HARDCODED_PASSWORD = 'password'  # In production, NEVER store passwords in plain text

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check against hardcoded credentials
        if username == HARDCODED_USERNAME and password == HARDCODED_PASSWORD:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

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
