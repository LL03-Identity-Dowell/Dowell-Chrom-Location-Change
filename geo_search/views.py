from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from selenium import webdriver
import socket
import time
from selenium.webdriver.common.by import By
import requests
import pychrome
from contextlib import closing
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

class Chromeview(APIView):
    def __init__(self):
        self.hostname = "one.one.one.one"
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.22 Safari/537.36'
        self.options = Options()
        self.options.add_argument(f'user-agent={self.user_agent}')
        self.options.add_argument("--disable-renderer-backgrounding")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-features=VizDisplayCompositor")
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        # Call find_free_port without arguments
        self.port_number = self.find_free_port()
        self.port_url = f"--remote-debugging-port={self.port_number}"
        self.options.add_argument(self.port_url)
        self.driver = webdriver.Chrome( options=self.options)
        self.url = f"http://localhost:{self.port_number}"
        self.dev_tools = pychrome.Browser(url=self.url)
        self.tab = self.dev_tools.new_tab()
        self.tab.start()
        self.driver.get("https://www.google.com")

    def is_connected(self):
        try:
            response = requests.get(f"http://{self.hostname}", timeout=2)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
        
    def loop_connected(self):#This function is called to check the internet connection thruoghout the code which will call is_connected() 
        if self.is_connected(): #If internet connection is there, it will return True and remaining code will continue
            return True
        else:#If false, it will wait 10 seconds for internet connection and try again
            print("Internet Disabled")
            time.sleep(10)
            self.loop_connected()#Call itself again
    def find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", 0))
            _, port = sock.getsockname()
            return port
        finally:
            sock.close()


    def post(self, request, format=None):
        try:
            # Extract data from the request, for example, latitude and longitude
            latitude = float(request.data.get('latitude'))
            longitude = float(request.data.get('longitude'))
            # Initialize Chrome WebDriver
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            with closing(webdriver.Chrome(options=options)) as driver:
                #Simulate setting geolocation
                self.set_location(latitude, longitude)
                #Change browser language settings
                self.change_language_settings(driver, 'en')
                return Response({"message": "Location set successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def set_location(self, latitude, longitude):
        try:
            self.loop_connected()  # Check internet connection

            self.tab.call_method("Network.enable", _timeout=20)
            self.tab.call_method("Browser.grantPermissions", permissions=["geolocation"])

            # Set geolocation override
            self.tab.call_method(
                "Emulation.setGeolocationOverride",
                latitude=latitude,
                longitude=longitude,
                accuracy=100,
            )

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            body_element = self.driver.find_element(By.TAG_NAME, "body")
            body_text = body_element.text

            if "Use precise location" in body_text:
                self.driver.find_element(By.XPATH, "//a[text()='Use precise location']").click()
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
                return True
            elif "Update location" in body_text:
                self.driver.find_element(By.XPATH, "//a[text()='Update location']").click()
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
                return True
            else:
                print('Send mail')

        except NoSuchElementException:  # If page is not loaded properly
            self.loop_connected()
            self.driver.refresh()
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            body_element = self.driver.find_element(By.TAG_NAME, "body")
            body_text = body_element.text

            if "Use precise location" in body_text:
                self.driver.find_element(By.XPATH, "//a[text()='Use precise location']").click()
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
                return True
            elif "Update location" in body_text:
                self.driver.find_element(By.XPATH, "//a[text()='Update location']").click()
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
                return True
            else:
                print('Send email')  # Send mail
        except Exception as error:
            print(f'An exception occurred: {error}')
            return False



    def change_language_settings(self, driver, language):
        try:
            language_link = 'https://www.google.com/?hl='+str(language)#Values such as (en,hi,ta) is given
            self.driver.get(language_link)#Change the language
            print('language set successfully')
        except Exception as e:
            print(f"Error changing language settings: {str(e)}")

    def separate_alphabets(self, driver, letter):
        try:
            # Find the search field by its NAME attribute
            search_field = driver.find_element(By.NAME, "q")
            autocomplete_list = []  # Initialize a list to store autocomplete suggestions
            # Enter the letter in the search bar
            search_field.send_keys(str(letter))
            # Wait for autocomplete suggestions to appear (up to 10 seconds)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*/ul/li/div/div[2]/div[1]")))
            for loop in range(1, 11):  # Iterate through the first 10 autocomplete suggestions
                try:
                    # Find and extract the text of the autocomplete suggestion
                    li_item = driver.find_element(By.XPATH, f"//*/ul/li[{loop}]/div/div[2]/div[1]").text
                    autocomplete_list.append(li_item)  # Append the suggestion to the list
                except NoSuchElementException:
                    # If no more suggestions are found, append None and exit the loop
                    autocomplete_list.append(None)
                    break
            return autocomplete_list  # Return the list of autocomplete suggestions
        except Exception as e:
            print(f"Error separating alphabets: {str(e)}")  # Handle and log any exceptions


    def retrieving_alphabets(self, driver, alphabets):
        try:
            self.alphabets = alphabets  # Store the provided alphabets
            self.json_letters = {}  # Initialize an empty dictionary to store results
            for i in range(len(self.alphabets)):  # Iterate through each alphabet
                alphabet = self.alphabets[i]
                # Call the separate_alphabets function to retrieve autocomplete results
                autocomplete_results = self.separate_alphabets(driver, alphabet)
                # Store the results in the dictionary with the alphabet as the key
                self.json_letters[alphabet] = autocomplete_results
            return self.json_letters  # Return the dictionary containing autocomplete results

        except Exception as e:
            print(f"Error retrieving alphabets: {str(e)}")  # Handle and log any exceptions

