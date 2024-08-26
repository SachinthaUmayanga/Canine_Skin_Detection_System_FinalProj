from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os

# Load the YOLOv8 model
try:
    model = YOLO('last.pt')  # Load the pre-trained YOLOv8 small model
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def process_image(file, model):
    try:
        # Load image with PIL and convert to numpy array
        image = Image.open(file)
        image = np.array(image)

        # Make a prediction using YOLOv8
        results = model.predict(source=image)

        # Get the most confident prediction
        predicted_class = results[0].boxes.cls[0].item()

        return {"status": "success", "predicted_class": int(predicted_class)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_video(file, filename, model):
    try:
        video_path = os.path.join('uploads', filename)
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

        # Determine the overall result based on the most common prediction
        overall_result = max(set(frame_results), key=frame_results.count)

        return {"status": "success", "overall_result": int(overall_result)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

