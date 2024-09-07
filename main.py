import os
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
from datetime import datetime
import csv
from cvzone.SelfiSegmentationModule import SelfiSegmentation

app = FastAPI()

# Enable CORS to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize camera
camera_index = 1  # Camera index for your system
cap = cv2.VideoCapture(camera_index)
if not cap.isOpened():
    raise Exception(f"Unable to open camera with index {camera_index}")

# Load background image for segmentation
background_image_path = "bg_image.jpeg"
background_image = None
if os.path.exists(background_image_path):
    background_image = cv2.imread(background_image_path)
else:
    raise FileNotFoundError("Background image not found. Ensure 'bg_image.jpeg' exists.")

# Initialize background removal and face detection
segmentor = SelfiSegmentation()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')

# Save data to CSV
def save_to_csv(data, filename):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Emotion analysis
def analyze_face(face_roi):
    try:
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
    except Exception as e:
        print(f"Error analyzing face: {e}")
        return None

# FastAPI route to process video frames
@app.post("/process_frame")
async def process_frame(file: UploadFile = File(...)):
    try:
        # Read image file
        img_data = await file.read()
        np_img = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Ensure background image has the correct size
        resized_background = cv2.resize(background_image, (frame.shape[1], frame.shape[0]))

        # Apply background removal
        segmented_img = segmentor.removeBG(frame, resized_background)

        # Convert frame to grayscale for face detection
        gray_frame = cv2.cvtColor(segmented_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

        # Analyze emotions
        emotion_data = []
        for (x, y, w, h) in faces:
            face_roi = frame[y:y + h, x:x + w]
            emotion = analyze_face(face_roi)
            if emotion:
                emotion_data.append({
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'emotion': emotion
                })

        return emotion_data

    except Exception as e:
        print(f"Error in processing frame: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ensure camera cleanup on exit
@app.on_event("shutdown")
def cleanup():
    if cap.isOpened():
        cap.release()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
