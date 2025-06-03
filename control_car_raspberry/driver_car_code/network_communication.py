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



def handle_captured_data(image, log_data):

    def send_image():

        try:

            log_car_data(image, log_data)

            #send_image_to_server(image, log_data)

        except Exception as e:

            print(f"Failed to send image: {e}")



    thread = Thread(target=send_image)

    thread.start()

    

def log_car_data(image, log_data):

    if image is not None:

        image_path = f"{data_directory}/{log_data['timestamp']}_image.jpg"

        cv2.imwrite(image_path, image)

    with open(f'{data_directory}/log.csv', 'a') as file:

        file.write(f"{log_data['timestamp']}_image.jpg,"+

                   f"{log_data['fl_speed']},"+

                   f"{log_data['fr_speed']},"+

                   f"{log_data['rl_speed']},"+

                   f"{log_data['rr_speed']},"+

                   f"{log_data['steering']},"+

                   f"{log_data['steering_angle']}\n")

                   

