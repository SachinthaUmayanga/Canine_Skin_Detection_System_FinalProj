import cv2
import numpy as np
import os
from ultralytics import YOLO

# Load the YOLOv8 model
try:
    model = YOLO('last.pt')  # Load the pre-trained YOLOv8 model
    class_names = ['allergic infection', 'bacterial infection', 'dermatosis', 'dog-skin', 'fungal infection']
except Exception as e:
    print(f"Error loading model: {e}")  # Print error if model loading fails
    model = None
    class_names = []

def process_image(image):
    """
    Process a single image (or video frame) to detect the disease.
    """
    try:
        if model is None:
            return {"status": "error", "message": "Model not loaded"}

        # Make a prediction using YOLOv8 on the image/frame directly
        results = model.predict(source=image)

        # Get the most confident prediction (assuming single object detection per image)
        predicted_class = results[0].boxes.cls[0].item()

        return {"status": "success", "predicted_class": int(predicted_class), "disease_name": class_names[int(predicted_class)]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_video(file, filename, upload_folder):
    """
    Process a video file to detect the most common disease across all frames.
    """
    try:
        if model is None:
            return {"status": "error", "message": "Model not loaded"}

        # Save the uploaded video file
        video_path = os.path.join(upload_folder, filename)
        file.save(video_path)

        cap = cv2.VideoCapture(video_path)
        frame_results = []
        frame_count = 0

        # Check if the video is successfully opened
        if not cap.isOpened():
            return {"status": "error", "message": "Cannot open video file"}

        print(f"Processing video: {video_path}")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print(f"End of video reached at frame {frame_count}")
                break

            frame_count += 1
            print(f"Processing frame {frame_count}")

            # Convert frame to RGB (YOLO model expects RGB format)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame directly
            result = process_image(frame_rgb)
            
            # Log the result for debugging
            if result["status"] == "success":
                print(f"Frame {frame_count}: Detected class {result['predicted_class']} ({result['disease_name']})")
                frame_results.append(result["predicted_class"])
            else:
                print(f"Frame {frame_count}: {result['message']}")
                frame_results.append(None)

        cap.release()

        # Filter out None values (frames where no object was detected)
        frame_results = [result for result in frame_results if result is not None]

        if len(frame_results) == 0:
            return {"status": "error", "message": "No disease detected in the video frames"}

        # Determine the overall result based on the most common prediction across frames
        overall_result = max(set(frame_results), key=frame_results.count)
        print(f"Overall result: {overall_result} ({class_names[int(overall_result)]})")

        return {"status": "success", "overall_result": int(overall_result), "disease_name": class_names[int(overall_result)]}

    except Exception as e:
        print(f"Error during video processing: {e}")
        return {"status": "error", "message": str(e)}
