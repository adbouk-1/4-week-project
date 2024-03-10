#Import the modules
import sys 
from shareplum.site import Version 
from shareplum import Site, Office365 
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

def get_sharepoint_context_using_user(sharepoint_url, username, password):
    """
    Get a SharePoint context using user credentials.

    This function creates a SharePoint context object using the provided SharePoint URL, username, and password. It uses the UserCredential class from the office365.runtime.auth.user_credential module to authenticate the user.

    Parameters:
    - sharepoint_url (str): The URL of the SharePoint site.
    - username (str): The username of the user.
    - password (str): The password of the user.

    Returns:
    - ctx (ClientContext): The SharePoint context object.

    Example:
    ```python
    sharepoint_url = "https://example.sharepoint.com"
    username = "john.doe@example.com"
    password = "password123"
    ctx = get_sharepoint_context_using_user(sharepoint_url, username, password)
    """

    user_credentials = UserCredential(username, password)
    ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)
    return ctx

def authenticate(sp_url, sp_site, user_name, password): 
    """
    Authenticate to a SharePoint site using user credentials.

    This function takes in the SharePoint URL, SharePoint site name, username, and password as parameters. It uses the Office365 class from the shareplum package to authenticate the user and obtain the authentication cookie. The authentication cookie is then used to create a Site object from the shareplum package.

    Parameters:
    - sp_url (str): The URL of the SharePoint site.
    - sp_site (str): The name of the SharePoint site.
    - user_name (str): The username of the user.
    - password (str): The password of the user.

    Returns:
    - site (Site): The SharePoint site object.

    Example:
    ```python
    sp_url = "https://example.sharepoint.com"
    sp_site = "MySite"
    user_name = "john.doe@example.com"
    password = "password123"
    site = authenticate(sp_url, sp_site, user_name, password)
    """
    
    site = None 
    try: 
        authcookie = Office365(sp_url, username=user_name, password=password).GetCookies() 
        site = Site(sp_site, version=Version.v365, authcookie=authcookie) 
    except: 
        # log the specific type of error occurred. 
        print('Failed to connect to SP site: {}'.format(sys.exc_info()[1])) 
    return site 

def get_sp_list(sp_site, sp_list_name): 
    """
    This function takes in two parameters: sp_site and sp_list_name.
    It attempts to connect to a SharePoint list using the sp_site and sp_list_name parameters.
    If the connection is successful, it returns the SharePoint list object.
    If the connection fails, it logs the specific type of error that occurred and returns None.

    Parameters:
    - sp_site: The SharePoint site object.
    - sp_list_name: The name of the SharePoint list.

    Returns:
    - sp_list: The SharePoint list object if the connection is successful, None otherwise.
    """

    sp_list = None 
    try: 
        sp_list = sp_site.List(sp_list_name) 
    except: 
        # We should log the specific type of error occurred. 
        print('Failed to connect to SP list: {}'.format(sys.exc_info()[1])) 
    return sp_list 

def download_list_items(sp_list, view_name=None, fields=None, query=None, row_limit=0): 
    """
    Download list items from a SharePoint list.

    Parameters:
    - sp_list (object): The SharePoint list object.
    - view_name (str, optional): The name of the view to retrieve items from. Defaults to None.
    - fields (list, optional): The list of fields to retrieve for each item. Defaults to None.
    - query (str, optional): The query string to filter items. Defaults to None.
    - row_limit (int, optional): The maximum number of items to retrieve. Defaults to 0 (retrieve all items).

    Returns:
    - sp_list_items (object): The list items retrieved from the SharePoint list.

    Raises:
    - SystemExit: If an error occurs while downloading list items.
    """

    sp_list_items = None 
    try: 
        sp_list_items = sp_list.GetListItems(view_name=view_name, fields=fields, query=query, row_limit=row_limit) 
    except: 
        #log the specific type of error occurred. 
        print('Failed to download list items {}'.format(sys.exc_info()[1])) 
        raise SystemExit('Failed to download list items {}'.format(sys.exc_info()[1])) 
    return sp_list_items 
  

def create_list_items(sp_list, new_items): 
    """
    This function updates a SharePoint list with new items.

    Parameters:
    - sp_list (object): The SharePoint list object to update.
    - new_items (list): A list of new items to upload to the SharePoint list.

    Returns:
    None

    Raises:
    - Exception: If there is an error updating the SharePoint list.
    """

    if len(new_items) > 0: 
        try: 
            sp_list.UpdateListItems(data=new_items, kind='New') 
        except: 
            #log the specific type of error occurred. 
            print('Failed to upload new list items: {}'.format(sys.exc_info()[1])) 