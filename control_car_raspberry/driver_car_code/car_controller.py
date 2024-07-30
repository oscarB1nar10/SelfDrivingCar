from drive_car import Car
import network_communication as net_com
import keyboard
import time

class CarController:
    def __init__(self, car):
        self.car = car
        self.server_ip = '192.168.1.14'
        self.server_port = '12345'

    def control_loop(self):
        print("Control the robot using 'w', 's', 'a', 'd' to move; Space to stop.")
        try:
            while True:
                self.car.stop()  # Ensure all motors are stopped unless a key is pressed
                if keyboard.is_pressed('w') and keyboard.is_pressed('a'):
                    image,log = self.car.forward()
                    net_com.send_image_to_server_threaded(image, log)
                    image,log = self.car.turn_left()
                    net_com.send_image_to_server_threaded(image, log)
                    print('Moving forward and turning left.')
                elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):
                    image,log = self.car.forward()
                    net_com.send_image_to_server_threaded(image, log)
                    image,log = self.car.turn_right()
                    net_com.send_image_to_server_threaded(image, log)
                    print('Moving forward and turning right.')
                elif keyboard.is_pressed('w'):
                    image,log = self.car.forward()
                    net_com.send_image_to_server_threaded(image, log)
                    print('Moving forward')
                elif keyboard.is_pressed('s'):
                    image,log = self.car.backward()
                    net_com.send_image_to_server_threaded(image, log)
                    print('Moving backward')
                elif keyboard.is_pressed('a'):
                    image,log = self.car.turn_left()
                    net_com.send_image_to_server_threaded(image, log)
                    print('Moving left')
                elif keyboard.is_pressed('d'):
                    image,log = self.car.turn_right()
                    net_com.send_image_to_server_threaded(image, log)
                    print('Moving right')
                elif keyboard.is_pressed('space'):
                    self.car.shutdown()
                    print('shutdown car')
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

