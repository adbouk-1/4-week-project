import sys 
import requests 
from bs4 import BeautifulSoup 
from shareplum.site import Version 
from shareplum import Site, Office365 
import csv
import os
import time
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import pandas as pd
import io
import errno

AUTHOR_PAGE_URL = 'https://www.mssqltips.com/sql-server-mssqltips-authors/' 
SHAREPOINT_URL = 'https://pilmembranesltd.sharepoint.com/' 
SHAREPOINT_SITE = 'https://pilmembranesltd.sharepoint.com/' 
SHAREPOINT_LIST = 'Fault Detection Image Dataset (Line 2)' 
USERNAME = 'ShoeStringuser@pilmembranes.com' 
PASSWORD = 'Baz15685'



def get_sharepoint_context_using_user(sharepoint_url):
    user_credentials = UserCredential("ShoeStringuser@pilmembranes.com", "Baz15685")
    ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)
    return ctx


sharepoint_url = 'https://pilmembranesltd.sharepoint.com/'
context = get_sharepoint_context_using_user(sharepoint_url)


folder_path = "/Shared Documents/Line 2 Fault Detection Images (Shoestring)"

target_folder = context.web.get_folder_by_server_relative_url(
        folder_path
    )

def authenticate(sp_url, sp_site, user_name, password): 
    """ 
    Takes a SharePoint url, site url, username and password to access the SharePoint site. 
    Returns a SharePoint Site instance if passing the authentication, returns None otherwise. 
    """ 
    site = None 
    try: 
        authcookie = Office365(SHAREPOINT_URL, username=USERNAME, password=PASSWORD).GetCookies() 
        site = Site(SHAREPOINT_SITE, version=Version.v365, authcookie=authcookie) 
    except: 
        # We should log the specific type of error occurred. 
        print('Failed to connect to SP site: {}'.format(sys.exc_info()[1])) 
    return site 
  
# Test the function 
sp_site = authenticate(SHAREPOINT_URL,SHAREPOINT_SITE,USERNAME,PASSWORD) 


def get_sp_list(sp_site, sp_list_name): 
    """ 
    Takes a SharePoint Site instance and invoke the "List" method of the instance. 
    Returns a SharePoint List instance. 
    """ 
    sp_list = None 
    try: 
        sp_list = sp_site.List(SHAREPOINT_LIST) 
    except: 
        # We should log the specific type of error occurred. 
        print('Failed to connect to SP list: {}'.format(sys.exc_info()[1])) 
    return sp_list 
  
# Test the function 
sp_list = get_sp_list(sp_site, SHAREPOINT_LIST)

def download_list_items(sp_list, view_name=None, fields=None, query=None, row_limit=0): 
    """ 
    Takes a SharePoint List instance, view_name, fields, query, and row_limit. 
    The rowlimit defaulted to 0 (unlimited) 
    Returns a list of dictionaries if the call succeeds; return a None object otherwise. 
    """ 
    sp_list_items = None 
    try: 
        sp_list_items = sp_list.GetListItems(view_name=view_name, fields=fields, query=query, row_limit=row_limit) 
    except: 
        # We should log the specific type of error occurred. 
        print('Failed to download list items {}'.format(sys.exc_info()[1])) 
        raise SystemExit('Failed to download list items {}'.format(sys.exc_info()[1])) 
    return sp_list_items 
  
# Test the function 
#sp_items_all = download_list_items(sp_list) 

#print(sp_items_all)

def create_list_items(sp_list, new_items): 
    """ 
    Takes a SharePoint List instance and a list of disctoraries. 
    The keys in the disctorary should match the list column. 
    """ 
    if len(new_items) > 0: 
        try: 
            sp_list.UpdateListItems(data=new_items, kind='New') 
        except: 
            # We should log the specific type of error occurred. 
            print('Failed to upload new list items: {}'.format(sys.exc_info()[1])) 


def process_new_row(sp_list, row):
    # Action performed on each new row
    print("Processing new row:", row)
    
    create_list_items(sp_list, [row])

def archive_old_rows(filepath, archive_path, max_rows=1000):
    """
    Archives rows if the CSV file exceeds a specified number of rows.
   
    :param filepath: Path to the CSV file.
    :param archive_path: Path to archive the old rows.
    :param max_rows: Maximum number of rows allowed in the CSV file before archiving.
    :returns: The number of rows removed during the archive process.
    """
    with open(filepath, 'r', newline='') as file:
        rows = list(csv.DictReader(file))

    if len(rows) > max_rows:
        # Calculate the number of rows to remove
        rows_to_remove = len(rows) - max_rows
        print(rows_to_remove)
        # Archive the current file
        for i in range(1, rows_to_remove):
            current_dict = rows[i]
            print(current_dict)
            os.remove(current_dict["FileName"] + ".jpg")
            os.remove(current_dict["FileName"])
        #copyfile(filepath, f"{archive_path}_{time.strftime('%Y%m%d%H%M%S')}.csv")
       
        # Write the last 'max_rows' rows to the original file
        print(rows[-max_rows:])
        with open(filepath, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows[-max_rows:])
       
        return rows_to_remove
    return 0

def monitor_csv_file(sp_list, filepath, archive_path, interval=5, max_rows=1000):
    """
    Monitors a CSV file for new rows, performs an action on each new row, and archives old rows.
   
    :param filepath: Path to the CSV file to monitor.
    :param archive_path: Path to archive the old rows.
    :param interval: Time interval (in seconds) to wait between checks.
    :param max_rows: Maximum number of rows allowed in the CSV file before archiving.
    """
    print(f"Monitoring {filepath} for new rows...")
    last_known_row = 0
   
    while True:
        # Check and potentially archive old rows
        #try:
        rows_removed = archive_old_rows(filepath, archive_path, max_rows)
        #except:
            #rows_removed = 0
        if rows_removed > 0:
            last_known_row = max(last_known_row - rows_removed, 0)
       
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            current_rows = list(reader)
            if len(current_rows) > last_known_row:
                for row in current_rows[last_known_row:]:
                    process_new_row(sp_list, row)
                last_known_row = len(current_rows)
       
        time.sleep(interval)

# Replace 'your_file.csv' and 'your_archive_path' with your actual file paths.
monitor_csv_file(sp_list, 'metadata.csv', '', interval=5, max_rows=10)

 