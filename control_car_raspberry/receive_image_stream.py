import socket
import time
import cv2
import numpy as np
import os

data_path = "C:/Users/osciv/Desktop/ml/Self_driving_car/SelfDrivingCar/control_car_raspberry/data"

def receive_images(port):
    # Ensure the save directory exists
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        
    log_file_path = os.path.join(data_path, "log_data.csv")  # Path for the log file

    # Setup server socket
    # socket.AF_INET: Specifies the address family for the socket `AF_INET` is used for IPV4 addresses
    # socket.SOCK_STREAM: This specifies the socket type `SOCK_STREAM` indicates that the socket is a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
         # Set the option on the socket
         # socket.SOL_SOCKET: Means the options are being set at the socket level
         # socket.SO_REUSEADDR: It allows the socket to be bound to an address (`port` in this case) that is already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # `bind()`: Binds the socket to a specific network interface and port number.
        sock.bind(('', port))  # Bind the socket to all interfaces on the given port
        # sock.listen(1): This tells the socket to begin listening for incoming connections. The argument '1' indicates the 
        # maximum number of queued connections (the size of connection backlog)
        sock.listen(1)  # Listen for incoming connections (1 client at a time)
        print("Server listening...")
        
        while True:
            conn, addr = sock.accept()  # Accept a connection; blocking call
            with conn:
                print('Connected by', addr)
                try:
                    while True:
                        # Receive and process CSV data
                        # conn.recv(4): This function call reads the first 4 bytes of data from the client through the connection `conn`.
                        # These 4 bytes are expected to represent the size of the upcoming CSV data, encoded in bytes.
                        # The `big` argument specifies that the byte order is big-endian, meaning the most significant byte is at the smallest address
                        csv_data_size = int.from_bytes(conn.recv(4), 'big')
                        csv_data_bytes = conn.recv(csv_data_size)
                        # Decodes the bytes into a string using UTF-8 encoding
                        csv_data = csv_data_bytes.decode()

                        # Process CSV data
                        # `strip()`: Is used to remove any leading an trailing whitespace characters from the `csv_data` string.
                        # `split(',')`: Divide the string into a list of substrings wherever a comma (`,`) is found
                        log_entries = csv_data.strip().split(',')
                        print(f"log_entries: {log_entries}")
                        timestamp = log_entries[0]
                        fl_speed = log_entries[1]
                        fr_speed = log_entries[2]
                        rl_speed = log_entries[3]
                        rr_speed = log_entries[4]
                        print(f"Received CSV data: Timestamp={timestamp}, FL={fl_speed}, FR={fr_speed}, RL={rl_speed}, RR={rr_speed}")
                        
                        # Append log data to the log file
                        # Opens a file specified by `log_file_path` in append mode (`"a"`)
                        # log_file.write(csv_data): Writes the string contained in the variable `csv_data` to the file referred to by `log_fileS`
                        with open(log_file_path, "a") as log_file:
                            log_file.write(csv_data)

                        # Receive and process image data
                        image_data_size = int.from_bytes(conn.recv(4), 'big')
                        image_data = b''
                        while len(image_data) < image_data_size:
                            packet = conn.recv(4096)
                            if not packet:
                                break
                            image_data += packet

                        if image_data:
                            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
                            image_filename = f"{data_path}/{timestamp}_received.jpg"
                            cv2.imwrite(image_filename, image)
                            print(f"Image saved to {image_filename}")
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    conn.close()

# Example usage
if __name__ == "__main__":
    receive_images(12345)
