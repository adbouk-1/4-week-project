from picamera2 import Picamera2, Preview
from time import sleep
import uuid
from csv import DictWriter
import datetime
import os.path
import os
import time

def wait_for_file_unlock(filepath, timeout=300, interval=0.3):
    """
    Waits for a file to be unlocked before proceeding.
   
    :param filepath: Path to the file to check.
    :param timeout: Maximum time in seconds to wait for the file to be unlocked.
    :param interval: Time interval in seconds between checks.
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
    file_exists = os.path.isfile(filename)
    print(file_exists)
    # Open file in append mode
    wait_for_file_unlock(filename)
    with open(file_name, 'a', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = DictWriter(write_obj, fieldnames=list_of_elem.keys())
        # Add contents of list as last row in the csv file
        if write_obj.tell() == 0:
            csv_writer.writeheader()
        
        csv_writer.writerow(list_of_elem)
        
picam0 = Picamera2(0)
picam0.start_preview(Preview.QTGL)
picam0.start()
csv_path = "metadata.csv"
while True:
    filename = uuid.uuid4().hex
    filepath = filename + ".jpg"
    picam0.capture_file(filepath)
    sleep(5)
    #''.join(['{"fileName":"', filepath, '"}'])
    metadata = {'Image Name':filename, "Image": filepath, "Image URL": "", "Guess": "No Fault", "Actual":"n/a", "Confidence": 0.500, "Camera": 'Camera 2', "ApprovalStatus": 'Pending', "Timestamp": datetime.datetime.now()}
    
    append_list_as_row(csv_path, metadata)
        
picam0.stop()
picam0.stop_preview()
