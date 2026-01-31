import cv2
import dlib
import serial
import time
from scipy.spatial import distance

# --- 1. CONFIGURATION ---
# Replace 'COM3' with your actual ESP32 port (e.g., '/dev/ttyUSB0' on Linux/Mac)
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200
EYE_AR_THRESH = 0.25      # Eye Aspect Ratio threshold
EYE_AR_CONSEC_FRAMES = 20 # Frames the eye must be closed to trigger alarm

# --- 2. INITIALIZE SERIAL ---
try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to ESP32 on {SERIAL_PORT}")
except Exception as e:
    print(f"Error: Could not connect to ESP32. {e}")
    esp32 = None

# --- 3. CORE LOGIC: EAR CALCULATION ---
def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the vertical eye landmarks
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    # Compute the euclidean distance between the horizontal eye landmark
    C = distance.euclidean(eye[0], eye[3])
    # EAR Formula
    ear = (A + B) / (2.0 * C)
    return ear

# --- 4. LOAD MODELS ---
# You must download 'shape_predictor_68_face_landmarks.dat' to this folder
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Indices for left and right eyes in the 68-point model
(lStart, lEnd) = (42, 48)
(rStart, rEnd) = (36, 42)

# --- 5. START VIDEO STREAM ---
print("Starting Camera...")
cap = cv2.VideoCapture(0)
COUNTER = 0

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        # Convert landmarks to coordinates
        coords = []
        for i in range(68):
            coords.append((shape.part(i).x, shape.part(i).y))
            
        leftEye = coords[lStart:lEnd]
        rightEye = coords[rStart:rEnd]
        
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        
        # Average the EAR for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # Check for Drowsiness
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if esp32: esp32.write(b'A') # Send ALERT to ESP32
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            COUNTER = 0
            if esp32: esp32.write(b'S') # Send SAFE to ESP32

        # Visual Feedback
        cv2.putText(frame, f"EAR: {ear:.2f}", (500, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Drowsiness Detector", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if esp32: esp32.close()
