from picamera2 import Picamera2, Preview
from time import sleep
import uuid
from csv import DictWriter
import datetime
import os.path
import os
import time

csv_path = "metadata.csv" #where the metadata will be stored
raspi_name = 'Camera 2' #name of the raspberry pi
capture_interval = 5 #how often a picture will be taken in seconds

def wait_for_file_unlock(filepath, timeout=300, interval=0.3):
    """
    Waits for a file to be unlocked before proceeding with further operations.

    Parameters:
    - filepath (str): The path of the file to wait for.
    - timeout (int, optional): The maximum time (in seconds) to wait for the file to be unlocked. Defaults to 300.
    - interval (float, optional): The interval (in seconds) between each attempt to check if the file is unlocked. Defaults to 0.3.

    Returns:
    None

    Raises:
    None

    Notes:
    - This function attempts to open the file in append mode to check for both read and write access.
    - If a permission error is encountered, indicating that the file is locked, the function will wait for the specified interval before retrying.
    - If the timeout is exceeded while waiting for the file to be unlocked, a timeout message will be printed and the function will exit.

    """

    start_time = time.time()
    while True:
        # Attempt to open the file in append mode
        try:
            # Using 'a+' mode to check for both read and write access
            with open(filepath, 'a+'):
                print(f"File {filepath} is accessible and ready for writing.")
                break  # Exit the loop if the file is accessible
        except PermissionError:
            # If a permission error is encountered, the file is likely locked
            print(f"File {filepath} is currently locked, retrying in {interval} seconds.")
            time.sleep(interval)
        except Exception as e:
            # Handle any other exceptions
            print(f"An unexpected error occurred: {e}")
            break
       
        # Check if the timeout has been exceeded
        if time.time() - start_time > timeout:
            print(f"Timeout exceeded while waiting for file {filepath} to be unlocked.")
            break

def append_list_as_row(file_name, list_of_elem):
    """
    Append a list of elements as a row to a CSV file.

    Parameters:
    - file_name (str): The name of the CSV file.
    - list_of_elem (list): The list of elements to be appended as a row.

    Returns:
    None

    Raises:
    None

    Notes:
    - This function checks if the file exists before opening it in append mode.
    - It waits for the file to be unlocked before proceeding with the append operation.
    - The function uses the 'DictWriter' class from the 'csv' module to write the list of elements as a row in the CSV file.
    - If the CSV file is empty, the function writes the header row before appending the list of elements.
    """

    file_exists = os.path.isfile(filename)
    
    if file_exists:
        wait_for_file_unlock(filename)

    # Open file in append mode
    with open(file_name, 'a', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = DictWriter(write_obj, fieldnames=list_of_elem.keys())

        #If the file is new, add the column names before writing the new row
        if write_obj.tell() == 0:
            csv_writer.writeheader()
        
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

#Start the raspi camera
picam0 = Picamera2(0)
picam0.start_preview(Preview.QTGL)
picam0.start()

#Have the programme continuously running
while True:

    #create a unique id for the image
    filename = uuid.uuid4().hex
    filepath = filename + ".jpg" #save the image as a jpeg
    picam0.capture_file(filepath) #save the image

    sleep(capture_interval) #how often to take the pictures

    metadata = {'Image Name':filename, "Image": filepath, "Image URL": "", "Guess": "No Fault", "Actual":"n/a", "Confidence": 0.0, "Camera": raspi_name, "ApprovalStatus": 'Pending', "Timestamp": datetime.datetime.now()}
    
    append_list_as_row(csv_path, metadata)
        
picam0.stop()
picam0.stop_preview()