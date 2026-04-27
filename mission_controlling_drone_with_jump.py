import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pysimverse import Drone

# ---------------- DRONE ----------------
drone = Drone()
drone.connect()

is_flying = False  # control state

# ---------------- MODEL ----------------
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

# ---------------- STATE ----------------
prev_time = time.time()
prev_hip_y = None
prev_ankle_y = None

state = "GROUND"
jump_triggered = False

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
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    timestamp += 33
    result = detector.detect_for_video(mp_image, timestamp)

    if result.pose_landmarks:
        lm = result.pose_landmarks[0]

        # Points
        hip_y = (lm[23].y + lm[24].y) / 2
        ankle_y = (lm[27].y + lm[28].y) / 2

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
                jump_triggered = True
                state = "GROUND"

        prev_hip_y = hip_y
        prev_ankle_y = ankle_y

    # ---------------- DRONE CONTROL ----------------
    if jump_triggered:
        if not is_flying:
            print("Drone TAKEOFF")
            drone.take_off()
            is_flying = True
        else:
            print("Drone LAND")
            drone.land()
            is_flying = False

        jump_triggered = False  # IMPORTANT: reset

    # Keep drone stable
    drone.send_rc_control(0, 0, 0, 0)

    # UI
    cv2.putText(frame, f"State: {state}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Jump → Drone Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()