#Import the modules
import csv
import os
import time
from classifier.classifier import *
from sharepoint_upload.sharepoint_uploader import *


#All the information regarding the sharepoint
SHAREPOINT_URL = 'https://pilmembranesltd.sharepoint.com/' #Sharepoint URL
SHAREPOINT_SITE = 'https://pilmembranesltd.sharepoint.com/' #Sharepoint site URL if you are using a specific site (e.g. sites/Shoestring Project)
SHAREPOINT_LIST_FAULT = 'SP2 - Detected Faults' #Detected faults with high confidence will be sent to this list
SHAREPOINT_LIST_LOW_CONF = 'SP1 - Check Faults' #Any image with a low confidence will be sent to the list for verification
USERNAME = 'ShoeStringuser@pilmembranes.com' #username for signing in to sharepoint
PASSWORD = 'Baz15685' #password for signing in to sharepoint
IMAGE_UPLOAD_PATH = "/Shared Documents/Imgs" #folder path within sharepoint where the images themselves will be uploaded


#additional variables required for running the script
CNN_FOLDER_PATH = "/code/src/classifier/models/model.h5" #the path points to where the model will be stored in the docker container TODO: Place a working model in this path
METADATA_CSV_PATH = '/code/src/data/metadata.csv' #Where the metadata of all the images is stored
IMAGE_STORE_PATH = "/code/src/data/" #where the images will be stored in the docker container. The path will be mapped to a folder path on the raspberry pi as defined in the Docker Comopose YAML


#Load the trained cnn classifier model from the following path
# loaded_model = load_model_from_file(CNN_FOLDER_PATH) TODO: Uncomment once the model works and is downloaded onto the system
loaded_model = ""


#The context provides authentication to the sharepoint so that the images can be uploaded
context = get_sharepoint_context_using_user(SHAREPOINT_URL, USERNAME, PASSWORD)


#Find the target folder in the sharepoint and make sure it exists. This is again for the image upload process
target_folder = context.web.get_folder_by_server_relative_url(
        IMAGE_UPLOAD_PATH
    )

  
#Provide authentication for uploading to the sharepoint list. It requires seperate authentication to uploading to a regular folder
sp_site = authenticate(SHAREPOINT_URL,SHAREPOINT_SITE,USERNAME,PASSWORD) 


#Get the sharepoints lists and make sure they exist.  
sp_list_low_conf = get_sp_list(sp_site, SHAREPOINT_LIST_LOW_CONF)
sp_list_fault = get_sp_list(sp_site, SHAREPOINT_LIST_FAULT)


def process_new_row(sp_list_low_conf, sp_list_fault, loaded_model, row):
    """
    Process a new row from the metadata CSV file.

    :param sp_list_low_conf: The SharePoint list for low confidence images.
    :param sp_list_fault: The SharePoint list for detected faults.
    :param loaded_model: The loaded machine learning model.
    :param row: The row to be processed.
    """

    print("Processing new row:", row)

    file_path = IMAGE_STORE_PATH + row["Image Name"] + ".jpg" #file path of the image that will be uploaded to sharepoint

    #upload the image to sharepoint
    with open(file_path, "rb") as content_file:
        file_content = content_file.read()
        target_folder.upload_file(os.path.basename(file_path), file_content).execute_query()

    full_path = SHAREPOINT_URL + IMAGE_UPLOAD_PATH.replace(" ", "%20")[1:] + "/" + os.path.basename(file_path) #get the sharepoint path of the newly uploaded image

    #update the csv row with the new sharepoint path
    row["Image"] = full_path
    row["Image URL"] = full_path
    
    #put the image through the model to classify whether there is a fault or not TODO: Uncomment this whole block and delete the 3 rows below it once the model works and is installed in the correct location
    # predicted_class = predict_image(loaded_model, file_path) #the function will return a list of 2 numbers representing the probabilities of it being a fault/no fault

    # #update the csv with the classifier guess and prediction
    # if predicted_class[0] > predicted_class[1]:
    #     row["Guess"] = "Fault"
    #     row["Confidence"] = predicted_class[0]
    # else:
    #     row["Guess"] = "No Fault"
    #     row["Confidence"] = predicted_class[1]

    # #upload the final csv row to the relevant sharepoint list
    # if row["Guess"] == "Fault" and row["Confidence"] > 0.85:
    #     create_list_items(sp_list_fault, [row])
    # elif row["Confidence"] < 0.85:
    #     create_list_items(sp_list_low_conf, [row])

    row["Guess"] = "No Fault"
    row["Confidence"] = 0
    create_list_items(sp_list_low_conf, [row])

def archive_old_rows(filepath, max_rows=1000):
    """
    Archive old rows from the metadata CSV file and delete the corresponding images.

    :param filepath: Path to the CSV file.
    :param max_rows: Maximum number of rows allowed in the CSV file before archiving. Default is 1000.
    :return: The number of rows removed from the file.
    """

    #open and read the metadata csv as a dict
    with open(filepath, 'r', newline='') as file:
        rows = list(csv.DictReader(file))

    if len(rows) > max_rows:
        rows_to_remove = len(rows) - max_rows  # Calculate the number of rows to remove

        # delete the current files
        for i in range(1, rows_to_remove):
            current_dict = rows[i]
            os.remove(IMAGE_STORE_PATH + current_dict["Image"]) #remove the image 
            os.remove(IMAGE_STORE_PATH + current_dict["Image Name"]) #there is some parasitic file that gets generated when saving an image, remove that too
       
        # Write the last 'max_rows' rows to the original file
        with open(filepath, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows[-max_rows:])
       
        return rows_to_remove
    return 0


def monitor_csv_file(sp_list_low_conf, sp_list_fault, filepath, loaded_model, interval=5, max_rows=1000):
    """
    Monitors the metadata CSV file for new rows and processes them.

    :param sp_list_low_conf: The SharePoint list for low confidence images.
    :param sp_list_fault: The SharePoint list for detected faults.
    :param filepath: Path to the CSV file.
    :param loaded_model: The loaded machine learning model.
    :param interval: The interval in seconds between each check for new rows. Default is 5 seconds.
    :param max_rows: Maximum number of rows allowed in the CSV file before archiving. Default is 1000.
    """

    print(f"Monitoring {filepath} for new rows...")
    
    last_known_row = 0 #to track which rows have already been processed
   
   #have it continuously running
    while True:
        # Check and potentially archive old rows
        try:
            rows_removed = archive_old_rows(filepath, max_rows)
        except:
            rows_removed = 0
        
        #update the last known row
        if rows_removed > 0:
            last_known_row = max(last_known_row - rows_removed, 0)
       
        #read the csv as a dictionary and process each new row
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            current_rows = list(reader)
            if len(current_rows) > last_known_row:
                for row in current_rows[last_known_row:]:
                    process_new_row(sp_list_low_conf, sp_list_fault, loaded_model, row)
                last_known_row = len(current_rows)
       
        time.sleep(interval)

# Replace 'your_file.csv' and 'your_archive_path' with your actual file paths.
monitor_csv_file(sp_list_low_conf, sp_list_fault, METADATA_CSV_PATH, loaded_model, interval=5, max_rows=10)
