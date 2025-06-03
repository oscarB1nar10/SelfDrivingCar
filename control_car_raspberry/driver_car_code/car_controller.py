from car import Car

import network_communication as net_com

import keyboard

import time



class CarController:

    def __init__(self, car):

        self.car = car

        self.server_ip = '192.168.1.14'

        self.server_port = '12345'

        self.autonomous_mode = False



    def control_loop(self):

        print("Control the robot using 'w', 's', 'a', 'd' to move; 'm' for autonomous, Space to stop.")

        try:

            while True:

                

                # Toggle autonomous mode

                if keyboard.is_pressed('m'):

                    self.autonomous_mode = not self.autonomous_mode

                    print("Autonomous mode:", "ON" if self.autonomous_mode else "OFF")

                    time.sleep(2)  # Delay to prevent multiple toggles from one press



                if self.autonomous_mode:

                    # Autonomous mode: capture image, predict direction, and control motors

                    direction = self.car.capture_and_predict()

                    if direction is not None:

                        self.car.control_motors(direction)

                        print(f"Autonomously moving: {['Forward', 'Left', 'Right', 'Backward'][direction]}")

                    else:

                        print("No valid direction predicted. Stopping the car.")

                        self.car.stop()

                    # Allow the car to move for 1 second

                    time.sleep(0.5)

                    # Stop the car briefly before the next cycle

                    self.car.stop()

                    time.sleep(1)

                else:

                    # Manual mode: control the car with keyboard input

                    self.car.stop()  # Ensure all motors are stopped unless a key is pressed

                    if keyboard.is_pressed('w') and keyboard.is_pressed('a'):

                        image,log = self.car.forward()

                        net_com.handle_captured_data(image, log)

                        image,log = self.car.turn_left()

                        net_com.handle_captured_data(image, log)

                        print('Moving forward and turning left.')

                    elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):

                        image,log = self.car.forward()

                        net_com.handle_captured_data(image, log)

                        image,log = self.car.turn_right()

                        net_com.handle_captured_data(image, log)

                        print('Moving forward and turning right.')

                    elif keyboard.is_pressed('w'):

                        image,log = self.car.forward()

                        net_com.handle_captured_data(image, log)

                        print('Moving forward')

                    elif keyboard.is_pressed('s'):

                        image,log = self.car.backward()

                        net_com.handle_captured_data(image, log)

                        print('Moving backward')

                    elif keyboard.is_pressed('a'):

                        image,log = self.car.turn_left()

                        net_com.handle_captured_data(image, log)

                        print('Moving left')

                    elif keyboard.is_pressed('d'):

                        image,log = self.car.turn_right()

                        net_com.handle_captured_data(image, log)

                        print('Moving right')

                    elif keyboard.is_pressed('space'):

                        self.car.stop()

                        print('stop car')

                        #self.car.stop()

                    time.sleep(0.1)  # Adding a small delay to reduce CPU usage

        except KeyboardInterrupt:

            pass

        finally:

            self.car.shutdown()



if __name__ == "__main__":

    car = Car()

    controller = CarController(car)

    controller.control_loop()

