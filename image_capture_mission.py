import cv2
import time
import keyboard
import os
from pysimverse import Drone

# ------------------ Setup ------------------
drone = Drone()
drone.connect()
drone.take_off()

drone.streamon()
time.sleep(1)

# ------------------ Create Folder ------------------
folder = "Image Captured"
if not os.path.exists(folder):
    os.makedirs(folder)

# ------------------ Control Variables ------------------
SPEED = 50
rotation_SPEED = 5
img_count = 0
z_pressed_last = False  # for single capture per press

print("Controls:")
print("W/S = Forward/Backward")
print("A/D = Left/Right")
print("Up/Down = Up/Down")
print("Q/E = Yaw")
print("Z = Capture Image")
print("ESC = Land & Exit")

# ------------------ Main Loop ------------------
while True:

    # Get frame
    frame, is_success = drone.get_frame()

    if is_success:
        cv2.imshow("Drone Frame", frame)

    # ------------------ Reset Movement ------------------
    left_right = 0
    forward_backward = 0
    up_down = 0
    yaw = 0

    # ------------------ Keyboard Controls ------------------
    if keyboard.is_pressed('w'):
        forward_backward = SPEED
    if keyboard.is_pressed('s'):
        forward_backward = -SPEED

    if keyboard.is_pressed('d'):
        left_right = SPEED
    if keyboard.is_pressed('a'):
        left_right = -SPEED

    if keyboard.is_pressed('up'):
        up_down = SPEED
    if keyboard.is_pressed('down'):
        up_down = -SPEED

    if keyboard.is_pressed('e'):
        yaw = rotation_SPEED
    if keyboard.is_pressed('q'):
        yaw = -rotation_SPEED

    # ------------------ Snapshot (Z key) ------------------
    if is_success and keyboard.is_pressed('z'):
        if not z_pressed_last:
            img_name = f"{folder}/image_{img_count}.jpg"
            cv2.imwrite(img_name, frame)
            print(f"Captured: {img_name}")
            img_count += 1
            z_pressed_last = True
    else:
        z_pressed_last = False

    # ------------------ Send Drone Command ------------------
    drone.send_rc_control(left_right, forward_backward, up_down, yaw)

    # ------------------ Exit ------------------
    if keyboard.is_pressed('esc'):
        print("Landing...")
        drone.land()
        break

    # ------------------ Refresh ------------------
    cv2.waitKey(1)
    time.sleep(0.05)

# ------------------ Cleanup ------------------
cv2.destroyAllWindows()