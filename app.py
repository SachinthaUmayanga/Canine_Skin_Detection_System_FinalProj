from flask import Flask, render_template, request, redirect, url_for
import torch
from PIL import Image
import cv2
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='/mnt/data/last.pt')

def detect_skin_condition(image_path):
    # Load the image
    image = Image.open(image_path)
    
    # Perform detection
    results = model(image)
    
    # Return results
    return results.pandas().xyxy[0].to_dict(orient="records")

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    detections = []

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Save frame as image
        frame_path = f"frame_{i}.jpg"
        cv2.imwrite(frame_path, frame)
        
        # Detect on frame
        results = detect_skin_condition(frame_path)
        detections.append({"frame": i, "results": results})
        
        # Clean up frame image
        os.remove(frame_path)

    cap.release()
    return detections

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            if file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                results = detect_skin_condition(file_path)
                os.remove(file_path)
                return render_template('result.html', results=results, type='image')
            
            elif file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
                results = process_video(file_path)
                os.remove(file_path)
                return render_template('result.html', results=results, type='video')
            
            else:
                os.remove(file_path)
                return render_template('index.html', error="Unsupported file type")
    
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0')
