import cv2
from pysimverse import Drone
import time

drone=Drone()
drone.connect()
drone.take_off()
drone.streamon()
time.sleep(1)

while True:
    frame,is_success = drone.get_frame()
    cv2.imshow("Drone Frame",frame)
    cv2.waitKey(0)