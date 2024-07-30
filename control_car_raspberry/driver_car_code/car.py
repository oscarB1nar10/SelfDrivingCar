from gpiozero import Motor
import keyboard
import time
import os
from picamera2 import Picamera2
import cv2

# Ensure the data directory exists
data_directory = 'data'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

class Car:
    def __init__(self):
        # Initialize motors
        self.front_left = Motor(forward=6, backward=13, enable=12)
        self.front_right = Motor(forward=19, backward=26, enable=20)
        self.rear_left = Motor(forward=5, backward=0, enable=1)
        self.rear_right = Motor(forward=11, backward=9, enable=25)
        
        # Initialize camera
        self.picam2 = Picamera2()
        # Set the maximum resolution. This example assumes a Pi Camera V2.
        preview_config = self.picam2.create_preview_configuration(main={"size": (3280, 2464)})
        self.picam2.configure(preview_config)
        self.picam2.start()
        
    def capture_image(self):
        img = self.picam2.capture_array()
        #print(f"Initial capture dimensions and dtype: {img.shape}, {img.dtype}")  # Debug info
        height, width, _ = img.shape
        # cropping to get the lower half of the image
        img = img[int(height/2):,:,:]
        #print(f"Post-crop dimensions and dtype: {img.shape}, {img.dtype}")  # Debug info
        #img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)  # Nvidia model said it is best to use YUV color space
        #img = cv2.GaussianBlur(img, (3,3), 0) # to blur an image... The blurring of an image means smoothening of an image i.e., removing outlier pixels that may be noise in the image.????
        #img = cv2.resize(img, (200, 66)) # input image size (200,66) Nvidia model
        #print(f"Post-resize dimensions and dtype: {img.shape}, {img.dtype}")  # Debug info
        #img = img / 255
        #img = img[None, ...]
        #print(f"Final preprocessing dimensions and dtype: {img.shape}, {img.dtype}")  # Debug info

        return img 
    
    def log_data(self, image, fl_speed, fr_speed, rl_speed, rr_speed):
        timestamp = time.time()
        if image is not None:
            image_path = f'{data_directory}/{timestamp}_image.png'
            cv2.imwrite(image_path, image)
        with open(f'{data_directory}/log.csv', 'a') as file:
            file.write(f"{timestamp},{fl_speed},{fr_speed},{rl_speed},{rr_speed}\n")
    
    def stop(self):
        self.front_left.stop()
        self.front_right.stop()
        self.rear_left.stop()
        self.rear_right.stop()
    
    def forward(self, speed=0.7):
        self.front_left.forward(speed)
        self.front_right.forward(speed)
        self.rear_left.forward(speed)
        self.rear_right.forward(speed)
        image = self.capture_image()
        timestamp = time.time()
        #self.log_data(image, speed, speed, speed, speed)
        log = {"timestamp":timestamp,"fl_speed": speed, "fr_speed": speed, "rl_speed": speed, "rr_speed": speed}
        return image, log
    
    def backward(self, speed=0.7):
        self.front_left.backward(speed)
        self.front_right.backward(speed)
        self.rear_left.backward(speed)
        self.rear_right.backward(speed)
        image = self.capture_image()
        timestamp = time.time()
        #self.log_data(image, -speed, -speed, -speed, -speed)
        log = {"timestamp":timestamp,"fl_speed": -speed, "fr_speed": -speed, "rl_speed": -speed, "rr_speed": -speed}
        return image, log
    
    def turn_left(self, speed=0.5):
        self.front_right.backward(speed)
        self.rear_right.backward(speed)
        self.front_left.forward(speed)
        self.rear_left.forward(speed)
        image = self.capture_image()
        timestamp = time.time()
        #self.log_data(image, speed, -speed, speed, -speed)
        log = {"timestamp":timestamp,"fl_speed": speed, "fr_speed": -speed, "rl_speed": speed, "rr_speed": -speed}
        return image, log
        
    
    def turn_right(self, speed=0.5):
        self.front_left.backward(speed)
        self.rear_left.backward(speed)
        self.front_right.forward(speed)
        self.rear_right.forward(speed)
        image = self.capture_image()
        timestamp = time.time()
        #self.log_data(image, -speed, speed, -speed, speed)
        log = {"timestamp":timestamp,"fl_speed": -speed, "fr_speed": speed, "rl_speed": -speed, "rr_speed": speed}
        return image, log
    
    def shutdown(self):
        self.stop()
        self.picam2.stop()
        print("Motors stopped and camera released. Exiting program.")
    

