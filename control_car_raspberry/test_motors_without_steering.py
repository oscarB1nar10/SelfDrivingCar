from gpiozero import Motor
import keyboard
import time
import os
from picamera2 import Picamera2, Preview
import cv2

# Ensure the data directory exists
data_directory = 'data'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Setup motors
front_left = Motor(forward=6, backward=13, enable=12)
front_right = Motor(forward=19, backward=26, enable=20)
rear_left = Motor(forward=5, backward=0, enable=1)
rear_right = Motor(forward=11, backward=9, enable=25)

# Initialize Picamera2
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (320, 240)})
picam2.configure(preview_config)
picam2.start()

# Function to capture image from Picamera2
def capture_image():
    image = picam2.capture_array()
    return image

# Function to log data
def log_data(image, fl_speed, fr_speed, rl_speed, rr_speed):
    timestamp = time.time()
    if image is not None:
        image_path = f'{data_directory}/{timestamp}_image.png'
        cv2.imwrite(image_path, image)  # Use cv2.imwrite to save the image
        #picam2.save(image, image_path)
    with open(f'{data_directory}/log.csv', 'a') as file:
        file.write(f"{timestamp},{fl_speed},{fr_speed},{rl_speed},{rr_speed}\n")

# Function to stop all motors
def stop():
    front_left.stop()
    front_right.stop()
    rear_left.stop()
    rear_right.stop()

# Updated movement functions with optional speed parameter and logging
def forward(speed=0.7):
    front_left.forward(speed)
    front_right.forward(speed)
    rear_left.forward(speed)
    rear_right.forward(speed)
    image = capture_image()
    log_data(image, speed, speed, speed, speed)

def backward(speed=0.7):
    front_left.backward(speed)
    front_right.backward(speed)
    rear_left.backward(speed)
    rear_right.backward(speed)
    image = capture_image()
    log_data(image, -speed, -speed, -speed, -speed)

def turn_left(speed=0.5):
    front_right.backward(speed)
    rear_right.backward(speed)
    front_left.forward(speed)
    rear_left.forward(speed)
    image = capture_image()
    log_data(image, speed, -speed, speed, -speed)

def turn_right(speed=0.5):
    front_left.backward(speed)
    rear_left.backward(speed)
    front_right.forward(speed)
    rear_right.forward(speed)
    image = capture_image()
    log_data(image, -speed, speed, -speed, speed)

try:
    print("Control the robot using 'w', 's', 'a', 'd' to move; Space to stop.")
    while True:
        stop()  # Ensure all motors are stopped unless a key is pressed
        if keyboard.is_pressed('w') and keyboard.is_pressed('a'):
            forward()
            turn_left()
            print('Moving forward and turning left.')
        elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):
            forward()
            turn_right()
            print('Moving forward and turning right.')
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
    picam2.stop()  # Stop the camera
    print("Motors stopped and camera released. Exiting program.")

# Command to run the code `sudo sdc_venv/bin/python /home/oscar/Desktop/sdc/drive_car.py`
# Steps to run the code more or less
# 1. sudo apt update
#    sudo apt upgrade
# 2. sudo apt install python3 python3-venv
# 3. python3 -m venv sdc_venv
# 4. pip install gpiozero
#    pip install keyboard
# 5. pip install lgpio


# To enable camera
# 1. sudo apt install -y libcamera-dev libcamera-apps
# 2. sudo nano /boot/firmware/config.txt
#    dtoverlay=imx219
# 3. sudo reboot
# 4. libcamera-hello
# 5. sudo apt-get install libcap-dev
# 6. pip install picamera2
# 7. python3 -m venv --system-site-packages myenv          (So important and not well undertood yet)
#    source myenv/bin/activate
# sudo myenv/bin/python /home/oscar/Desktop/sdc/drive_car.py


# Utils
# sudo rm -r data
