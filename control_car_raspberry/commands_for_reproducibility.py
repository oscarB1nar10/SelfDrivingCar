
# List of commands for project reproducibilitiy

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
# 4. libcamera-hello -t 0
# 5. sudo apt-get install libcap-dev
# 6. pip install picamera2
# 7. python3 -m venv --system-site-packages myenv          (So important and not well undertood yet)
#    source myenv/bin/activate
# sudo myenv/bin/python /home/oscar/Desktop/sdc/drive_car.py


# Utils
# sudo rm -r data
