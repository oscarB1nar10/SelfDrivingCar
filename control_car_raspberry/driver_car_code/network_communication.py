from threading import Thread
import socket
import cv2
import io
import time
import json
import os

# Ensure the data directory exists
data_directory = 'data'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

def send_image_to_server_threaded(image, log_data):
    def send_image():
        try:
            log_car_data(image, log_data)
            send_image_to_server(image, log_data)
        except Exception as e:
            print(f"Failed to send image: {e}")

    thread = Thread(target=send_image)
    thread.start()
    
def log_car_data(image, log_data):
    timestamp = time.time()
    if image is not None:
        image_path = f'{data_directory}/{timestamp}_image.png'
        cv2.imwrite(image_path, image)
    with open(f'{data_directory}/log.csv', 'a') as file:
        file.write(f"{log_data['timestamp']},{log_data['fl_speed']},{log_data['fr_speed']},{log_data['rl_speed']},{log_data['rr_speed']}\n")
    
    
def send_image_to_server(image, log_data):
    try:
        #server_ip = '192.168.21.73'
        server_ip = '192.168.1.4'
        server_port = 12345
        #timestamp = time.time()
        print(f"log_data:{log_data['fl_speed']}")
        _, buffer = cv2.imencode('.jpg', image)
        image_data = io.BytesIO(buffer).getvalue()

        # Construct CSV string from log data
        csv_data = f"{log_data['timestamp']},{log_data['fl_speed']},{log_data['fr_speed']},{log_data['rl_speed']},{log_data['rr_speed']}\n"
        csv_data_bytes = csv_data.encode()
        csv_data_size = len(csv_data_bytes)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_ip, server_port))
            # Send CSV data size and CSV data
            sock.sendall(csv_data_size.to_bytes(4, 'big'))
            sock.sendall(csv_data_bytes)

            # Send image data size and image data
            image_data_size = len(image_data)
            sock.sendall(image_data_size.to_bytes(4, 'big'))
            sock.sendall(image_data)

    except Exception as e:
        print(f"Failed to send image: {e}")


