from gpiozero import Motor
import keyboard
import time

# Setup motors
front_left = Motor(forward=6, backward=13, enable=12)
front_right = Motor(forward=19, backward=26, enable=20)
rear_left = Motor(forward=5, backward=0, enable=1)
rear_right = Motor(forward=11, backward=9, enable=25)

# Function to stop all motors
def stop():
    front_left.stop()
    front_right.stop()
    rear_left.stop()
    rear_right.stop()

# Updated movement functions with optional speed parameter
def forward(speed=0.7):
    front_left.forward(speed)
    front_right.forward(speed)
    rear_left.forward(speed)
    rear_right.forward(speed)

def backward(speed=0.7):
    front_left.backward(speed)
    front_right.backward(speed)
    rear_left.backward(speed)
    rear_right.backward(speed)

def turn_left(speed=0.5):
    front_right.backward(speed)
    rear_right.backward(speed)
    front_left.forward(speed)
    rear_left.forward(speed)

def turn_right(speed=0.5):
    front_left.backward(speed)
    rear_left.backward(speed)
    front_right.forward(speed)
    rear_right.forward(speed)

try:
    print("Control the robot using 'w', 's', 'a', 'd' to move; Space to stop.")
    while True:
        stop()  # Ensure all motors are stopped unless a key is pressed
        # Check multiple key presses for combined movements
        if keyboard.is_pressed('w') and keyboard.is_pressed('a'):
            forward()
            turn_left()
            print('moving forward and turning left.')
        elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):
            forward()
            turn_right()
            print('moving forward and turning right.')
        elif keyboard.is_pressed('w'):
            forward()
        elif keyboard.is_pressed('s'):
            backward()
        elif keyboard.is_pressed('a'):
            turn_left()
        elif keyboard.is_pressed('d'):
            turn_right()
        elif keyboard.is_pressed('space'):
            stop()
        time.sleep(0.1)  # Adding a small delay to reduce CPU usage

finally:
    stop()
    print("Motors stopped. Exiting program.")

