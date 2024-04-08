import requests
from fake_useragent import UserAgent
import logging
logging.basicConfig(level=logging.DEBUG)

def get_proxies_from_file():
    """
    Get proxies cached inside the proxies.txt file
    """
    import os
    if os.path.exists('proxies.txt'):
        with open('proxies.txt', 'r') as file:
            proxies = [i.removesuffix('\n') for i in file.readlines()]
            return proxies

def write_proxies_to_file(proxy=None):
    """
    Append a new proxy to the proxies.txt file
    """
    if proxy is not None:
        if proxy in get_proxies_from_file():
            return None
        with open('proxies.txt', 'a') as file:
            file.write(f'{proxy}\n')
            return True

def get_proxies(latitude:str=None, longitude:str=None, country:str=None):
    """
    Get a list of proxies for a specified location

    Args:
    - latitude (str): optional
    - longitude (str): optional
    - country (str): The ISO code of the country. 
    """
    url = f'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&country={country}&protocol=http,socks5&proxy_format=protocolipport&format=text&anonymity=Anonymous,Elite&timeout=819'
    response = requests.get(url)
    if response.status_code == 200:
        proxies = response.text.split('\n')
        proxies = [i.removesuffix('\r') for i in proxies]
        # print(proxies)
        return proxies
    return None

def get_content_with_proxy(url:str, proxies:list):
    """
    Get the content of a URL using a rotating list of proxies.

    Args:
    - url (str): The URL to retrieve content from.
    - proxies (list): A list of proxy dictionaries, each containing 'http' and 'https' keys.

    Returns:
    - str: The content of the URL.
    - None: If the request fails after exhausting all proxies.
    """
    
    # Create a user-agent generator
    user_agent = UserAgent()
    
    # Iterate through the list of proxies
    for index, proxy in enumerate(proxies):
        try:
            # Get a new user-agent string for each request
            headers = {'User-Agent': user_agent.random}
            
            logging.info(f'[+][{index+1}/{len(proxies)}] Making request to URL with {proxy}.\n')
            # Disclaimer: Set a timeout value else connection to proxy might led to lag in making the request to the server.
            response = requests.get(url, proxies=proxy, headers=headers, timeout=2, allow_redirects=False)
            
            # Check if the request was successful
            if response.status_code == 200:
                write_proxies_to_file(proxy['https'])
                # print(response.text)
                return response.text
            
            # If the request was unsuccessful, print the status code
            logging.info(f"[{proxy['https']}]: Request failed with status code {response.status_code}\n")
            
        except Exception as error:
            logging.debug(error)
    
    # If all proxies fail, return None
    return None


# Example usage:
# url = 'https://www.britbox.com' #Worked
# url = 'https://www.fubo.tv'
# url = 'https://www.sling.com' #Worked
# url = 'https://www.pandora.com' #Worked