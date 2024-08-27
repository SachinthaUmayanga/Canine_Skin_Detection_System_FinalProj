from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os

# Load the YOLOv8 model
try:
    model = YOLO('last.pt')  # Load the pre-trained YOLOv8 model
    class_names = ['allergic infection', 'bacterial infection', 'dermatosis', 'dog-skin', 'fungal infection']
except Exception as e:
    print(f"Error loading model: {e}")  # Print error if model loading fails
    model = None
    class_names = []

def process_image(file_path):
    """
    Process a single image file to detect the disease.

    Args:
        file_path (str): Path to the image file.

    Returns:
        dict: A dictionary containing the status of the operation,
              the predicted class, and the disease name.
    """
    try:
        if model is None:
            return {"status": "error", "message": "Model not loaded"}

        # Load image with PIL and convert to a numpy array
        image = Image.open(file_path)
        image = np.array(image)

        # Make a prediction using YOLOv8
        results = model.predict(source=image)

        # Get the most confident prediction (assuming single object detection per image)
        predicted_class = results[0].boxes.cls[0].item()

        return {"status": "success", "predicted_class": int(predicted_class), "disease_name": class_names[int(predicted_class)]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_video(file, filename, upload_folder):
    """
    Process a video file to detect the most common disease across all frames.

    Args:
        file (werkzeug.datastructures.FileStorage): The video file object.
        filename (str): The name of the video file.
        upload_folder (str): The folder path where the video file will be saved.

    Returns:
        dict: A dictionary containing the status of the operation,
              the most common prediction across frames, and the disease name.
    """
    try:
        if model is None:
            return {"status": "error", "message": "Model not loaded"}

        # Save the uploaded video file
        video_path = os.path.join(upload_folder, filename)
        file.save(video_path)

        cap = cv2.VideoCapture(video_path)
        frame_results = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Make a prediction using YOLOv8 for each frame
            results = model.predict(source=frame)
            
            # Get the most confident prediction for the frame
            predicted_class = results[0].boxes.cls[0].item()
            frame_results.append(predicted_class)

        cap.release()

        # Determine the overall result based on the most common prediction across frames
        overall_result = max(set(frame_results), key=frame_results.count)

        return {"status": "success", "overall_result": int(overall_result), "disease_name": class_names[int(overall_result)]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
