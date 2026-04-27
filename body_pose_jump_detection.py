import cv2
import time
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ---------------- MODEL SETUP ----------------
base_options = python.BaseOptions(
    model_asset_path="Models/pose_landmarker_heavy.task"
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1
)

detector = vision.PoseLandmarker.create_from_options(options)

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

# ---------------- STATE VARIABLES ----------------
prev_time = time.time()
prev_hip_y = None
prev_ankle_y = None

state = "GROUND"

# Thresholds (tune these)
VEL_UP = 0.15
VEL_DOWN = -0.2
ANKLE_LIFT = 0.04

timestamp = 0

# ---------------- MAIN LOOP ----------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    timestamp += 33  # approx for 30 FPS

    result = detector.detect_for_video(mp_image, timestamp)

    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]

        # Get key points
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]

        hip_y = (left_hip.y + right_hip.y) / 2
        ankle_y = (left_ankle.y + right_ankle.y) / 2

        current_time = time.time()
        dt = current_time - prev_time
        prev_time = current_time

        if prev_hip_y is not None:
            vel = (prev_hip_y - hip_y) / dt
            ankle_lift = prev_ankle_y - ankle_y

            # -------- STATE MACHINE --------
            if state == "GROUND":
                if vel > VEL_UP and ankle_lift > ANKLE_LIFT:
                    state = "UP"

            elif state == "UP":
                if vel > 0:
                    state = "AIR"

            elif state == "AIR":
                if vel < VEL_DOWN:
                    state = "LAND"

            elif state == "LAND":
                print("JUMP DETECTED!")
                state = "GROUND"

            # Display state
            cv2.putText(frame, f"State: {state}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        prev_hip_y = hip_y
        prev_ankle_y = ankle_y

        # Draw points manually (since Tasks API doesn’t auto draw)
        for lm in landmarks:
            h, w, _ = frame.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

    cv2.imshow("Jump Detection (Tasks API)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()