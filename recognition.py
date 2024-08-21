from PIL import Image
import cv2
import numpy as np
import os

def process_image(file):
    image = Image.open(file)
    image = np.array(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(gray, (224, 224))  # Adjust size based on your model
    input_image = np.expand_dims(resized_image, axis=0)

    # prediction = model.predict(input_image)
    prediction = "Healthy Skin"  # Replace with actual prediction logic

    return prediction

def process_video(file, filename):
    video_path = os.path.join('uploads', filename)
    file.save(video_path)

    cap = cv2.VideoCapture(video_path)
    frame_results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized_frame = cv2.resize(gray_frame, (224, 224))  # Adjust size based on your model
        input_frame = np.expand_dims(resized_frame, axis=0)

        # frame_prediction = model.predict(input_frame)
        frame_prediction = "Healthy Skin"  # Replace with actual prediction logic

        frame_results.append(frame_prediction)

    cap.release()

    overall_result = max(set(frame_results), key=frame_results.count)

    return overall_result
