import os
import json
import requests
import concurrent.futures
import threading
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
    print(country)
    url = f'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&country={country}&protocol=http,socks4&proxy_format=protocolipport&format=text&anonymity=Elite,Anonymous&timeout=20000'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            proxies = response.text.split('\n')
            proxies = [i.removesuffix('\r') for i in proxies]
            proxies.pop()
            print("Total Proxies:", len(proxies))
            return proxies
    except Exception as error:
        logging.info(f"[-] Proxies: {error}")
        return None

def make_request_with_proxy(url, country, proxy, results, success_flag):
    try:
        user_agent = UserAgent()
        headers = {'User-Agent': user_agent.random}

        if not success_flag.is_set():
            response = requests.get(url, proxies=proxy, headers=headers, allow_redirects=False, timeout=10)
            
            if response.status_code == 200:
                # print(f"\n\n{url}: {response.status_code}")
                results[proxy['https']] = response.status_code  # Store successful response in results dictionary
                write_proxies_to_file(country, proxy['https'])  # Write successful proxy to file for caching
                logging.info(f"[+]: [{proxy['https']}] --> Request successful")
                success_flag.set()
                return
            else:
                logging.info(f"[{proxy['https']}]: Request failed with status code {response.status_code}")
    except Exception as error:
        logging.debug(f"Error with proxy {proxy['https']}: {error}")

def get_content_with_proxy(url, country, proxies):
    """
    Get the content of a URL using a rotating list of proxies.

    Args:
    - url (str): The URL to retrieve content from.
    - country (str): Country name (for logging or other purposes).
    - proxies (list): A list of proxy dictionaries, each containing 'http' and 'https' keys.

    Returns:
    - list: A dictionary containing successful responses (key: proxy URL, value: response content).
    """
    # Dictionary to store results
    results = {}

    # Event flag to signal success
    success_flag = threading.Event()
    
    # List to store threads
    threads = []
    
    # Iterate through the list of proxies
    for index, proxy in enumerate(proxies):
        # logging.info(f'[+][{index+1}/{len(proxies)}] Making request to URL with {proxy}.')

        # Create a thread for each proxy request
        thread = threading.Thread(target=make_request_with_proxy, args=(url, country, proxy, results, success_flag))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        # Breaks out of the loop once a thread is successful
        if len(results) >= 1:
            break
        thread.join()
        
    # Return successful responses if it exist or None
    return list(results.values())[0] if len(results) >=1 else None


# For ProxiesView API Endpoint.
def make_request(url, proxy):
    try:
        user_agent = UserAgent()
        headers = {'User-Agent': user_agent.random}
        response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=10)
        if response.status_code == 200:
            # print(f"\n\n{url}: {response.status_code}\n\n")
            return url, response.content, "Success"
        else:
            return url, response.status_code, f"Failed (Status Code: {response.status_code})"
    except Exception as e:
        # print(f"\n\nFailed Request: {e}\n\n")
        return url, "500", f"Error: {e}"

def multiple_url_request(urls, proxies):
    results = []
    url_futures_map = {url: [] for url in urls}  # Map to track futures for each URL
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(proxies)) as executor:
        for url in urls:
            for proxy in proxies:
                future = executor.submit(make_request, url, proxy)
                url_futures_map[url].append(future)  # Store future for each URL

        for url in urls:
            success_obtained = False
            for future in concurrent.futures.as_completed(url_futures_map[url]):
                try:
                    result = future.result()
                    # print(f"\n\n{result}\n\n")
                    if result[2] == "Success":
                        if not success_obtained:
                            results.append(result)
                            success_obtained = True  # Mark success obtained for this URL
                            # Cancel all other pending requests for this URL
                            for other_future in url_futures_map[url]:
                                if other_future != future and not other_future.done():
                                    other_future.cancel()
                            break  # Exit the loop once successful response is obtained
                except Exception as e:
                    pass
    
    # print(results)
    return [result[1] for result in results]

# Example usage:
# url = 'https://www.britbox.com' #Worked
# url = 'https://www.fubo.tv'
# url = 'https://www.sling.com' #Worked
# url = 'https://www.pandora.com' #Worked