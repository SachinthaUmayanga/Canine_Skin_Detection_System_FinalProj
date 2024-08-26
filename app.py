from flask import Flask, request, render_template, redirect, url_for, session
import os
from auth import auth
from recognition import process_image, process_video  # Import the recognition functions
from ultralytics import YOLO

app = Flask(__name__)
app.secret_key = '1111'

# Load the YOLOv8 model and handle potential loading errors
try:
    model = YOLO('last.pt')  # Load the YOLOv8 small model
except Exception as e:
    print(f"Error loading model: {e}")
    model = None  # Fallback if model loading fails

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

    if model is None:
        return render_template('error.html', message="Model failed to load. Please contact support.")

    try:
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension in ['.jpg', '.jpeg', '.png']:
            result = process_image(file, model)  # Pass the model to the function
            if result["status"] == "success":
                return render_template('result.html', prediction=result["predicted_class"])
            else:
                return render_template('error.html', message=f"Image processing failed: {result['message']}")

        elif file_extension in ['.mp4', '.avi', '.mov']:
            result = process_video(file, filename, model)  # Pass the model to the function
            if result["status"] == "success":
                return render_template('result.html', prediction=result["overall_result"])
            else:
                return render_template('error.html', message=f"Video processing failed: {result['message']}")

    except Exception as e:
        return render_template('error.html', message=f"An error occurred during file processing: {str(e)}")

    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
