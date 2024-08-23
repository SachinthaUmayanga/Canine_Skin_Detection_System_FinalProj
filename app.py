from flask import Flask, request, render_template, redirect, url_for, session
import os
from auth import auth
from recognition import process_image, process_video  # Import the recognition functions

app = Flask(__name__)
app.secret_key = '1111'

# Register the auth blueprint
app.register_blueprint(auth)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension in ['.jpg', '.jpeg', '.png']:
            prediction = process_image(file)
            return render_template('result.html', prediction=prediction)

        elif file_extension in ['.mp4', '.avi', '.mov']:
            prediction = process_video(file, filename)
            return render_template('result.html', prediction=prediction)

    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
