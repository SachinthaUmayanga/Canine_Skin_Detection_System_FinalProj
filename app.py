from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
import cv2
import numpy as np
# Import your model here, e.g., a TensorFlow or Scikit-learn model
# from tensorflow.keras.models import load_model
# model = load_model('your_model.h5')

app = Flask(__name__)

# Load your pre-trained model
# model = load_model('model.h5')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        # Open image using PIL
        image = Image.open(file)
        image = np.array(image)

        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Resize image to the model's expected input size
        resized_image = cv2.resize(gray, (224, 224))  # Adjust size based on your model
        input_image = np.expand_dims(resized_image, axis=0)

        # Make prediction using the loaded model
        # prediction = model.predict(input_image)

        # For demonstration, we'll just return a placeholder
        prediction = "Healthy Skin"  # Replace with actual prediction logic

        return render_template('result.html', prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
