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


# Ensure the data directory existswwaa

data_directory = "data"

if not os.path.exists(data_directory):
    os.makedirs(data_directory)


# Directory to save captured images
inference_image_directory = "inference_images"

if not os.path.exists(inference_image_directory):
    os.makedirs(inference_image_directory)


IMAGE_SIZE = (200, 66)  # (width, height) expected by the model
CROP_Y_START_RATIO = 0.33  # 0 = keep whole frame, 0.5 = keep bottom half
DEFAULT_SPEED_FORWARD = 0.65
DEFAULT_SPEED_LATERALS = 0.55  # 0.55
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
        self.stopping_cycles = 0

        try:
            self.model = load_model("model/end_to_end.keras")
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None

        # Initialize camera
        self.picam2 = Picamera2()
        # Set the maximum resolution (Pi Camera V2 assumed)
        preview_config = self.picam2.create_preview_configuration(
            main={"size": (3280, 2464)}
        )
        self.picam2.configure(preview_config)
        self.picam2.start()

    # ---------------------------------------------------------------------

    # Vision helpers

    # ---------------------------------------------------------------------
    def preprocess_image(self, image):
        # Make preprocessing identical to training
        # Optional: discard alpha if camera ever outputs 4-channel frames
        if image.shape[2] == 4:
            image = image[:, :, :3]
        h = image.shape[0]
        y_start = int(h * CROP_Y_START_RATIO)
        image = image[y_start:, :, :]  # bottom 2/3
        image = cv2.resize(image, IMAGE_SIZE)  # (200, 66)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        image = cv2.GaussianBlur(image, (3, 3), 0)  # Gaussian blur
        image = image / 255.0  # Normalize

        return image

    def capture_and_predict(self):
        # Step 1 â€“ capture and save
        img = self.picam2.capture_array()
        temp_image_path = "temp_image.jpg"
        temp_image_path2 = "temp_image2.jpg"
        cv2.imwrite(temp_image_path, img)

        # Step 2 â€“ preprocess
        try:
            image = load_img(temp_image_path, color_mode="rgb", target_size=(66, 200))
            img_array = img_to_array(image)
            print(f"Loaded image shape: {img_array.shape}")
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None

        processed_img = self.preprocess_image(img_array)
        processed_img = np.expand_dims(processed_img, axis=0)
        cv2.imwrite(temp_image_path2, processed_img)
        print(f"Input tensor shape: {processed_img.shape}")

        # Step 3 â€“ predict
        if self.model:
            start_time = time.time()
            prediction = self.model.predict(processed_img)
            print(f"Inference time: {time.time() - start_time:.4f}s")

            direction = np.argmax(prediction, axis=-1)[0]
            confidence = np.max(prediction)
            print(f"Predicted dir: {direction}, conf: {confidence:.4f}")

            if confidence >= 0.60:
                return direction
            else:
                return 3
        else:
            print("Model not loaded.")

        return None

    # ---------------------------------------------------------------------

    # Motion control â€“ highâ€‘level dispatcher

    # ---------------------------------------------------------------------
    def control_motors(self, direction):
        if direction == 0:  # forward
            self.forward()
            self._reset_stopping_cycles()

        elif direction == 1:  # right
            self.handle_move_right()
            self._reset_stopping_cycles()

        elif direction == 2:  # left
            self.handle_move_left()
            self._reset_stopping_cycles()

        else:
            self.stopping_cycles += 1
            print(f"self.stopping_cycles: {self.stopping_cycles}")
            if self.stopping_cycles >= 3:
                print(f"self.stopping_cycles: {self.stopping_cycles}")
                # 5th consecutive low-confidence frame back up

                # self._reset_stopping_cycles()           # reset counter after corrective action

                # self.backward()                     # start moving backward immediately

                self.backward()  # corrective action
                self._reset_stopping_cycles()

            else:
                # Low confidence, just stop and increment the counter
                self.stop()

    # ---------------------------------------------------------------------

    # Oscillationâ€‘aware helpers

    # ---------------------------------------------------------------------
    def handle_move_right(self):
        self.moving_right_count += 1
        if self.moving_right_count >= 2 and self.moving_left_count >= 1:
            self.default_speed_laterals -= SPEED_DECREMENT
            self.turn_right(self.default_speed_laterals)

        else:
            self.default_speed_laterals = DEFAULT_SPEED_LATERALS
            self.turn_right()

    def handle_move_left(self):
        self.moving_left_count += 1
        if self.moving_left_count >= 2 and self.moving_right_count >= 1:
            self.default_speed_laterals -= SPEED_DECREMENT
            self.turn_left(self.default_speed_laterals)

        else:
            self.default_speed_laterals = DEFAULT_SPEED_LATERALS
            self.turn_left()

    # ---------------------------------------------------------------------

    # Lowâ€‘level motion primitives

    # ---------------------------------------------------------------------
    """Grabs current frame, crops ROI, and rescales to IMAGE_SIZE."""
    
    def capture_image(self):
        """Grabs current frame, crops ROI, and rescales to IMAGE_SIZE."""
        img = self.picam2.capture_array()
        h, _, _ = img.shape
        y_start = int(h * CROP_Y_START_RATIO)
        img = img[y_start:, :, :]  # keep bottom part incl. some horizon
        return cv2.resize(img, IMAGE_SIZE)  # (width, height)

    def log_data(self, image, fl, fr, rl, rr):
        ts = time.time()
        if image is not None:
            cv2.imwrite(f"{data_directory}/{ts}_image.jpg", image)

        with open(f"{data_directory}/log.csv", "a") as f:
            f.write(f"{ts},{fl},{fr},{rl},{rr}\n")

    def stop(self):
        self.front_left.stop()
        self.front_right.stop()
        self.rear_left.stop()
        self.rear_right.stop()

    def _reset_lateral_state(self):
        """Reset lateral speed and oscillation counters."""
        self.default_speed_laterals = DEFAULT_SPEED_LATERALS
        self.moving_left_count = 0
        self.moving_right_count = 0

    def _reset_stopping_cycles(self):
        self.stopping_cycles = 0

    def forward(self, speed=DEFAULT_SPEED_FORWARD):
        self._reset_lateral_state()
        image = self.capture_image()
        ts = time.time()
        angle = self.calculate_steering_angle(speed, speed, speed, speed)

        log = dict(
            timestamp=ts,
            fl_speed=speed,
            fr_speed=speed,
            rl_speed=speed,
            rr_speed=speed,
            steering="forward",
            steering_angle=angle,
        )

        self.front_left.forward(speed)
        self.front_right.forward(speed)
        self.rear_left.forward(speed)
        self.rear_right.forward(speed)

        return image, log

    def backward(self, speed=0.55):
        self._reset_lateral_state()
        image = self.capture_image()
        ts = time.time()
        angle = self.calculate_steering_angle(-speed, -speed, -speed, -speed)

        log = dict(
            timestamp=ts,
            fl_speed=-speed,
            fr_speed=-speed,
            rl_speed=-speed,
            rr_speed=-speed,
            steering="backward",
            steering_angle=-1,
        )

        self.front_left.backward(speed)
        self.front_right.backward(speed)
        self.rear_left.backward(speed)
        self.rear_right.backward(speed)

        return image, log

    def turn_left(self, speed=DEFAULT_SPEED_LATERALS):
        image = self.capture_image()
        ts = time.time()
        angle = self.calculate_steering_angle(speed, -speed, speed, -speed)

        log = dict(
            timestamp=ts,
            fl_speed=speed,
            fr_speed=-speed,
            rl_speed=speed,
            rr_speed=-speed,
            steering="left",
            steering_angle=angle,
        )

        self.front_right.backward(speed)
        self.rear_right.backward(speed)
        self.front_left.forward(speed)
        self.rear_left.forward(speed)

        return image, log

    def turn_right(self, speed=DEFAULT_SPEED_LATERALS):
        image = self.capture_image()
        ts = time.time()
        angle = self.calculate_steering_angle(-speed, speed, -speed, speed)

        log = dict(
            timestamp=ts,
            fl_speed=-speed,
            fr_speed=speed,
            rl_speed=-speed,
            rr_speed=speed,
            steering="right",
            steering_angle=angle,
        )

        self.front_left.backward(speed)
        self.rear_left.backward(speed)
        self.front_right.forward(speed)
        self.rear_right.forward(speed)

        return image, log

    # ---------------------------------------------------------------------

    # Utility

    # ---------------------------------------------------------------------
    def calculate_steering_angle(self, fl, fr, rl, rr):
        max_angle = 45  # degrees
        left_avg = (fl + rl) / 2
        right_avg = (fr + rr) / 2
        diff = left_avg - right_avg
        max_diff = max(fl, fr, rl, rr) - min(fl, fr, rl, rr)

        if max_diff == 0:
            return 0

        angle = (diff / max_diff) * max_angle
        return max(-max_angle, min(max_angle, angle))

    def shutdown(self):
        self.stop()
        self.picam2.stop()
        print("Motors stopped and camera released. Exiting program.")
    

