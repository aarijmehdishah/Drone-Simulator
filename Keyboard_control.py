import time
import keyboard
from pysimverse import Drone

# ------------------ Drone Setup ------------------
drone = Drone()
drone.connect()
drone.take_off()

# ------------------ Control Variables ------------------
left_right = 0
forward_backward = 0
up_down = 0
yaw = 0

SPEED = 50
Rotation_Speed=5

print("Controls:")
print("W/S = Forward/Backward")
print("A/D = Left/Right")
print("Up/Down Arrows = Up/Down")
print("Q/E = Yaw Left/Right")
print("SPACE = Stop")
print("ESC = Land & Exit")

# ------------------ Main Loop ------------------
while True:

    # Reset values each frame (important for smooth control)
    left_right = 0
    forward_backward = 0
    up_down = 0
    yaw = 0

    # -------- Movement Controls --------
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
        yaw = Rotation_Speed
    if keyboard.is_pressed('q'):
        yaw = -Rotation_Speed

    # -------- Emergency Stop --------
    if keyboard.is_pressed('space'):
        left_right = 0
        forward_backward = 0
        up_down = 0
        yaw = 0

    # -------- Exit & Land --------
    if keyboard.is_pressed('esc'):
        print("Landing...")
        drone.land()
        break

    # -------- Send RC Command --------
    drone.send_rc_control(left_right, forward_backward, up_down, yaw)

    # Control loop rate (prevents overload)
    time.sleep(0.05)