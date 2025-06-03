from gpiozero import Motor

from tensorflow.keras.models import load_model

import numpy as np

import keyboard

import time

import os

from picamera2 import Picamera2

import cv2

import tensorflow as tf

from tensorflow.keras.preprocessing.image import load_img, img_to_array



# Ensure the data directory exists

data_directory = 'data'

if not os.path.exists(data_directory):

    os.makedirs(data_directory)

    

# Directory to save captured images

inference_image_directory = 'inference_images'

if not os.path.exists(inference_image_directory):

    os.makedirs(inference_image_directory)

    

DEFAULT_SPEED_FORWARD = 0.7

DEFAULT_SPEED_LATERALS = 1.0

SPEED_DECREMENT = 0.01



class Car:

    def __init__(self):

        # Initialize motors

        self.front_left = Motor(forward=6, backward=13, enable=12)

        self.front_right = Motor(forward=19, backward=26, enable=20)

        self.rear_left = Motor(forward=5, backward=0, enable=1)

        self.rear_right = Motor(forward=11, backward=9, enable=25)

        

        # Attributes to handle car's repetitive cycles

        self.default_speed_laterals = DEFAULT_SPEED_LATERALS

        self.moving_right_count = 0

        self.moving_left_count = 0

        self.one_cicle = False

        

        try:

            self.model = load_model("model/end_to_end.keras")

            print("Model loaded successfully.")

        except Exception as e:

            print(f"Failed to load model: {e}")

            self.model = None

        

        # Initialize camera

        self.picam2 = Picamera2()

        # Set the maximum resolution. This example assumes a Pi Camera V2.

        preview_config = self.picam2.create_preview_configuration(main={"size": (3280, 2464)})

        self.picam2.configure(preview_config)

        self.picam2.start()

        

        

    def preprocess_image(self, image):

        img = image[:, :, :3]  # Ensure three channels

        img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)  # RGB to YUV

        img = cv2.GaussianBlur(img, (3, 3), 0)      # Apply Gaussian blur

        img = img / 255.0                           # Normalize

        #img = cv2.resize(img, (200, 66))           # Resize to (200, 66)

        return img





    def capture_and_predict(self):

        # Step 1: Capture and save the image

        img = self.picam2.capture_array()

        temp_image_path = "temp_image.jpg"

        cv2.imwrite(temp_image_path, img)



        # Step 2: Use load_img and img_to_array for consistent preprocessing

        try:

            image = load_img(temp_image_path, color_mode='rgb', target_size=(66, 200))

            img_array  = img_to_array(image)  # Converts to numpy array

            print(f"Loaded image shape: {img_array.shape}")

        except Exception as e:

            print(f"Failed to load image: {e}")

            return None

            

        # Preprocess the image

        processed_img = self.preprocess_image(img_array )

        

        # Expand dimensions to match model input shape

        processed_img = np.expand_dims(processed_img, axis=0)

        print(f"Input tensor shape: {processed_img.shape}")



        # Step 4: Run prediction

        if self.model:

            # Run prediction

            start_time = time.time()

            prediction = self.model.predict(processed_img)

            inference_time = time.time() - start_time

            print(f"Inference time: {inference_time:.4f} seconds")

            print(f"Prediction: {prediction}")

            

            # Get predicted class and confidence

            direction = np.argmax(prediction, axis=-1)[0]

            confidence = np.max(prediction)

            print(f"Prediction: {prediction}")

            print(f"Predicted direction: {direction}, Confidence: {confidence:.4f}")



            if confidence > 0.4:

                return direction

            else:

                print("Low confidence in prediction. Stopping the car.")

                self.stop()

                return None

        else:

            print("Model not loaded.")

            return None





    def control_motors(self, direction):

        if direction == 0:  # "forward"

            self.forward()

        elif direction == 1:  # "right"

            self.handle_move_right()

        elif direction == 2:  # "left"

            self.handle_move_left()

        else:

            self.backward()

            #self.stop()  # Default to stop if unexpected value

    

    def handle_move_right(self):

        self.moving_right_count += 1

        if self.moving_right_count >= 2 and self.moving_left_count >= 1 :

            self.default_speed_laterals -= SPEED_DECREMENT

            self.turn_right(self.default_speed_laterals)

        else:

            # Reset default speed

            self.default_speed_laterals = DEFAULT_SPEED_LATERALS

            self.turn_right()

            

    def handle_move_left(self):

        self.moving_left_count += 1

        if self.moving_left_count >= 2 and self.moving_right_count >= 1 :

            self.default_speed_laterals -= SPEED_DECREMENT

            self.turn_left(self.default_speed_laterals)

        else:

            # Reset default speed

            self.default_speed_laterals = DEFAULT_SPEED_LATERALS

            self.turn_left()



    def capture_image(self):

        img = self.picam2.capture_array()

        height, width, _ = img.shape

        # cropping to get the lower half of the image

        img = img[int(height/2):,:,:]

        img = cv2.resize(img, (200, 66)) # input image size (200,66) Nvidia model

        return img 





    def log_data(self, image, fl_speed, fr_speed, rl_speed, rr_speed):

        timestamp = time.time()

        if image is not None:

            image_path = f'{data_directory}/{timestamp}_image.jpg'

            cv2.imwrite(image_path, image)



        with open(f'{data_directory}/log.csv', 'a') as file:

            file.write(f"{timestamp},{fl_speed},{fr_speed},{rl_speed},{rr_speed}\n")





    def stop(self):

        self.front_left.stop()

        self.front_right.stop()

        self.rear_left.stop()

        self.rear_right.stop()





    def forward(self, speed=DEFAULT_SPEED_FORWARD):

        image = self.capture_image()

        timestamp = time.time()

        steering_angle = self.calculate_steering_angle(speed,speed,speed,speed)



        #self.log_data(image, speed, speed, speed, speed)

        log = {

            "timestamp":timestamp,

            "fl_speed": speed,

            "fr_speed": speed,

            "rl_speed": speed,

            "rr_speed": speed,

            "steering": "forward",

            "steering_angle": steering_angle}



        

        self.front_left.forward(speed)

        self.front_right.forward(speed)

        self.rear_left.forward(speed)

        self.rear_right.forward(speed)



        return image, log





    def backward(self, speed=DEFAULT_SPEED_FORWARD):

        image = self.capture_image()

        timestamp = time.time()

        steering_angle = self.calculate_steering_angle(-speed,-speed,-speed,-speed)

        

        #self.log_data(image, -speed, -speed, -speed, -speed)

        log = {

            "timestamp":timestamp,

            "fl_speed": -speed,

            "fr_speed": -speed,

            "rl_speed": -speed,

            "rr_speed": -speed,

            "steering": "backward",

            "steering_angle": -1}



        self.front_left.backward(speed)

        self.front_right.backward(speed)

        self.rear_left.backward(speed)

        self.rear_right.backward(speed)



        return image, log



    

    def turn_left(self, speed=DEFAULT_SPEED_LATERALS):

        image = self.capture_image()

        timestamp = time.time()

        steering_angle = self.calculate_steering_angle(

            speed,

            -speed,

            speed,

            -speed)



        #self.log_data(image, speed, -speed, speed, -speed)

        log = {

            "timestamp":timestamp,

            "fl_speed": speed,

            "fr_speed": -speed,

            "rl_speed": speed,

            "rr_speed": -speed,

            "steering": "left",

            "steering_angle": steering_angle}

        

        self.front_right.backward(speed)

        self.rear_right.backward(speed)

        self.front_left.forward(speed)

        self.rear_left.forward(speed)



        return image, log



        



    def turn_right(self, speed=DEFAULT_SPEED_LATERALS):

        image = self.capture_image()

        timestamp = time.time()

        steering_angle = self.calculate_steering_angle(

            -speed,

            speed,

            -speed,

            speed)



        #self.log_data(image, -speed, speed, -speed, speed)

        log = {

            "timestamp":timestamp,

            "fl_speed": -speed,

            "fr_speed": speed,

            "rl_speed": -speed,

            "rr_speed": speed,

            "steering": "right",

            "steering_angle": steering_angle}



        self.front_left.backward(speed)

        self.rear_left.backward(speed)

        self.front_right.forward(speed)

        self.rear_right.forward(speed)

        

        return image, log



    



    def calculate_steering_angle(self, fl_speed, fr_speed, rl_speed, rr_speed):

        # Example constants for maximum steering angle

        max_steering_angle = 45  # degrees



        # Calculate differential on each side (simplified assumption)

        left_speed_avg = (fl_speed + rl_speed) / 2

        right_speed_avg = (fr_speed + rr_speed) / 2



        # Calculate speed difference and handle zero division

        speed_difference = left_speed_avg - right_speed_avg

        max_speed_difference = max(fl_speed, fr_speed, rl_speed, rr_speed) - min(fl_speed, fr_speed, rl_speed, rr_speed)



        # Check if max_speed_difference is zero to avoid division by zero

        if max_speed_difference == 0:

            steering_angle = 0  # No steering needed if all wheel speeds are equal

        else:

            # Normalize and calculate angle

            steering_angle = (speed_difference / max_speed_difference) * max_steering_angle



        # Ensure the steering angle is within bounds

        steering_angle = max(-max_steering_angle, min(max_steering_angle, steering_angle))



        return steering_angle



    

    def shutdown(self):

        self.stop()

        self.picam2.stop()

        print("Motors stopped and camera released. Exiting program.")
