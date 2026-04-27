import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from pysimverse import Drone
import time

# ---------------- DRONE SETUP ----------------
drone = Drone()
drone.connect()
drone.take_off()

# Movement variables
left_right = 0
forward_backward = 0
up_down = 0
yaw = 0

speed = 30   # adjust sensitivity

# ---------------- MEDIAPIPE SETUP ----------------
base_options = BaseOptions(model_asset_path=r"Models/hand_landmarker.task")

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

prev_zone = None  # for stability

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = detector.detect(mp_image)

    zone_text = "DEADZONE"

    # Zones
    left_boundary = w // 3
    right_boundary = 2 * w // 3

    cv2.line(frame, (left_boundary, 0), (left_boundary, h), (255, 0, 0), 2)
    cv2.line(frame, (right_boundary, 0), (right_boundary, h), (255, 0, 0), 2)

    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:

            # Draw hand
            for lm in hand_landmarks:
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            # Center of hand
            cx = int(sum(lm.x for lm in hand_landmarks) / len(hand_landmarks) * w)
            cy = int(sum(lm.y for lm in hand_landmarks) / len(hand_landmarks) * h)

            cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)

            # Zone detection
            if cx < left_boundary:
                zone_text = "LEFT"
            elif cx > right_boundary:
                zone_text = "RIGHT"
            else:
                zone_text = "DEADZONE"

    # ---------------- DRONE CONTROL ----------------
    if zone_text == "LEFT":
        left_right = -speed
    elif zone_text == "RIGHT":
        left_right = speed
    else:
        left_right = 0

    # Send command
    drone.send_rc_control(left_right, forward_backward, up_down, yaw)

    # Display
    cv2.putText(frame, zone_text, (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Drone Control", frame)

    # Small delay → VERY IMPORTANT
    time.sleep(0.05)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
drone.land()
cap.release()
cv2.destroyAllWindows()