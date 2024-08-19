from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
import cv2
import numpy as np
import os

app = Flask(__name__)

# Load your pre-trained model here, if using TensorFlow or another framework
# from tensorflow.keras.models import load_model
# model = load_model('your_model.h5')

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
        # Check if the file is an image or a video
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension in ['.jpg', '.jpeg', '.png']:
            # Process image
            image = Image.open(file)
            image = np.array(image)

            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Resize image to the model's expected input size
            resized_image = cv2.resize(gray, (224, 224))  # Adjust size based on your model
            input_image = np.expand_dims(resized_image, axis=0)

            # Make prediction using the loaded model
            # prediction = model.predict(input_image)

            # Placeholder for prediction result
            prediction = "Healthy Skin"  # Replace with actual prediction logic

            return render_template('result.html', prediction=prediction)

        elif file_extension in ['.mp4', '.avi', '.mov']:
            # Save the uploaded video temporarily
            video_path = os.path.join('uploads', filename)
            file.save(video_path)

            # Process video
            cap = cv2.VideoCapture(video_path)
            frame_results = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert frame to grayscale
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Resize frame to the model's expected input size
                resized_frame = cv2.resize(gray_frame, (224, 224))  # Adjust size based on your model
                input_frame = np.expand_dims(resized_frame, axis=0)

                # Make prediction for each frame using the loaded model
                # frame_prediction = model.predict(input_frame)

                # Placeholder for frame prediction result
                frame_prediction = "Healthy Skin"  # Replace with actual prediction logic

                frame_results.append(frame_prediction)

            cap.release()

            # Determine the overall result based on frame predictions
            overall_result = max(set(frame_results), key=frame_results.count)

            return render_template('result.html', prediction=overall_result)

    return redirect(url_for('index'))

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
