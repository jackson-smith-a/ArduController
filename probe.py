from arduino import Arduino
import time

ard = Arduino()

print(ard.set_position(-12048))
ard.set_pid(0.1, 0.008, 4.0, 5, 0, 100, 255, 40)
print("Starting...")
try:
	while 1:
		print(ard.request_encoder())

		time.sleep(0.3)
finally:
	ard.close()
