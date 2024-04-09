import os
import json
import requests
from fake_useragent import UserAgent
import logging
logging.basicConfig(level=logging.DEBUG)

def get_proxies_from_file(country:str=None):
    """
    Get proxies cached inside the proxies.json file
    """
    if os.path.exists('proxies.json'):
        with open('proxies.json', 'r') as file:
            data = json.load(file)
            proxies = data.get(country)
            return proxies

def write_proxies_to_file(country:str=None, proxy=None):
    """
    Append a new proxy to the proxies.json file
    """
    try:
        with open('proxies.json', 'r') as file:
            data = json.load(file)
            proxies = data.get(country)
            if proxies is not None:
                proxies.append(proxy)
                proxies = set(proxies) # Eliminate duplicates
                data[country] = list(proxies)
                with open('proxies.json', 'w') as file:
                    file.write(json.dumps(data))
            else:
                data[country] = [proxy]
                with open('proxies.json', 'w') as file:
                    file.write(json.dumps(data))
    except FileNotFoundError as e:
        with open('proxies.json', 'w') as file:
            file.write(json.dumps({country: [proxy]}))
            
def get_proxies(latitude:str=None, longitude:str=None, country:str=None):
    """
    Get a list of proxies for a specified location

    Args:
    - latitude (str): optional
    - longitude (str): optional
    - country (str): The ISO code of the country. 
    """
    url = f'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&country={country}&protocol=http&proxy_format=protocolipport&format=text&timeout=20000'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            proxies = response.text.split('\n')
            proxies = [i.removesuffix('\r') for i in proxies]
            proxies.pop()
            # print(proxies)
            return proxies
    except Exception as error:
        logging.info(f"[-] Proxies: {error}")
        return None

def get_content_with_proxy(url:str, country:str, proxies:list):
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
            
            logging.info(f'[+][{index+1}/{len(proxies)}] Making request to URL with {proxy}.')
            # Disclaimer: Set a timeout value else connection to proxy might led to lag in making the request to the server.
            response = requests.get(url, proxies=proxy, headers=headers, allow_redirects=False)
            
            # Check if the request was successful
            if response.status_code == 200:
                write_proxies_to_file(country, proxy['https'])
                print(response.text)
                return response.text
            
            # If the request was unsuccessful, print the status code
            logging.info(f"[{proxy['https']}]: Request failed with status code {response.status_code}\n")
            
        except Exception as error:
            print(f'[-]: {error}\n')
            logging.debug(error)
    
    # If all proxies fail, return None
    return None


# Example usage:
# url = 'https://www.britbox.com' #Worked
# url = 'https://www.fubo.tv'
# url = 'https://www.sling.com' #Worked
# url = 'https://www.pandora.com' #Worked