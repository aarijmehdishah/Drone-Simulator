from pysimverse import Drone
import time
drone=Drone()
drone.connect()

drone.take_off(10)
drone.move_forward(500)
time.sleep(2)