from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from selenium import webdriver
import socket
import time
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import datetime
import time
from pymongo import MongoClient
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import pychrome
from rest_framework import generics, status,viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render,get_object_or_404
from .serializers import LocationSerializer,SearchSerializer
from .models import Location
from contextlib import closing
from django.views.decorators.csrf import csrf_exempt
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import logging
from django.utils.decorators import method_decorator



logging.basicConfig(level=logging.INFO)

@csrf_exempt
def homepage_view(request):
    serializer = LocationSerializer(Location.objects.all(), many=True)
    if request.method == 'POST':
        # Deserialize the data using the serializer
        selected_location_id = request.POST.get('location')  # Assuming 'location' is the name of the select input field

        try:
            selected_location = Location.objects.get(id=selected_location_id)
            latitude = selected_location.latitude
            longitude = selected_location.longitude
            city = selected_location.city

            language = selected_location.language.id

            # Make a POST request to your APIView to set the Chrome instance
            response = requests.post('http://127.0.0.1:8080/api/geo_location/', data={
                'latitude': latitude,
                'longitude': longitude,
                'language': language,
            })
            

            #make a get request to the search view
            url = f'http://127.0.0.1:8080/api/get_city/{city}/'
            response = requests.get(url, params={
                'latitude': latitude,
                'longitude': longitude,
            })


        except Location.DoesNotExist:
            # Handle the case where the selected location doesn't exist
            error_message = "Selected location does not exist."
            return render(request, 'index.html', {'serializer': serializer, 'error_message': error_message})

    else:
        # Create a serializer to render the form in the template
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)

    return render(request, 'index.html', {'serializer': serializer})
    
@method_decorator(csrf_exempt, name='dispatch')
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
            # Deserialize the data using the serializer
            serializer = LocationSerializer(data=request.data)
            if serializer.is_valid():
                selected_location = serializer.validated_data
                
                # Extract latitude and longitude from the selected location
                latitude = selected_location.get('latitude')
                longitude = selected_location.get('longitude')
                
                # Get the language code from the selected location
                language_code = selected_location.get('language', '')  # Use the language code from the selected location
                
                # Initialize Chrome WebDriver with language settings
                options = webdriver.ChromeOptions()
                options.add_argument(f'--lang={language_code}')  # Set the desired language code
                logging.info("Changing language")
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                driver = webdriver.Chrome(options=options)
                try:
                    # Simulate setting geolocation
                    self.set_location(driver, latitude, longitude)
                    logging.info("Changing location")
                    
                    return Response({"message": "Location set successfully", "latitude": latitude, "longitude": longitude}, status=status.HTTP_200_OK)
                finally:
                    driver.quit()
            else:
                errors = serializer.errors
                return Response({"message": "Invalid serializer data", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle exceptions and provide meaningful error messages
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def set_location(self, driver, latitude, longitude):
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

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            body_element = driver.find_element(By.TAG_NAME, "body")
            body_text = body_element.text

            if "Use precise location" in body_text:
                driver.find_element(By.XPATH, "//a[text()='Use precise location']").click()
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
            elif "Update location" in body_text:
                driver.find_element(By.XPATH, "//a[text()='Update location']").click()
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
            else:
                print('Send mail')

        except NoSuchElementException:  # If page is not loaded properly
            self.loop_connected()
            driver.refresh()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            body_element = driver.find_element(By.TAG_NAME, "body")
            body_text = body_element.text

            if "Use precise location" in body_text:
                driver.find_element(By.XPATH, "//a[text()='Use precise location']").click()
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
            elif "Update location" in body_text:
                driver.find_element(By.XPATH, "//a[text()='Update location']").click()
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print('Location set successfully')
            else:
                print('Send email')  # Send mail
        except Exception as error:
            raise Exception(f'An exception occurred: {error}')

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


@method_decorator(csrf_exempt, name='dispatch')
class CityInfoView(APIView):
    def get_city_info(self, city, format=None):
        # Replace this hardcoded data with your actual data
        latitude = float(self.request.query_params.get('latitude'))
        longitude = float(self.request.query_params.get('longitude'))
        city_info = {
            "City": city,
            "Languages": "English,Hindi,Spanish",  # Replace with the actual languages
            "LanguageAbbreviations": "en,hi,es",  # Replace with the actual abbreviations
            "State": "Delhi",
            "Latitude": latitude,
            "Longitude": longitude,
        }
        return city_info

    def get_city_languages(self, city):
        # Replace this hardcoded data with your actual data
        language_data = {
            "Language": ["English", "Hindi", "Spanish"],  # Replace with actual languages
            "English_binary": ["Yes", "No", "Yes"],  # Replace with actual data
            "Hindi_binary": ["Yes", "No", "Yes"],    # Replace with actual data
            "Spanish_binary": ["No", "Yes", "No"],   # Replace with actual data
        }

        # Create a DataFrame
        df = pd.DataFrame(language_data)

        return df

    def storing_in_mongodb(self, language, browser_language, autocomplete, id_of_object):
        # Replace this with your MongoDB storage logic
        pass

    def write(self, i, obj, combination, lat, log, id_of_object, city, data_frame):
        time.sleep(i)
        print(i, "---", obj, "---", combination)
        # Replace this with your actual implementation
        pass

    def get(self, request, city):
        # Retrieve information about the city
        city_info = self.get_city_info(city)

        # Retrieve language data for the city
        language_dataframe = self.get_city_languages(city)

        # Get latitude and longitude from city_info
        latitude, longitude = float(city_info['Latitude']), float(city_info['Longitude'])

        # Convert language and language abbreviation strings to lists
        languages = city_info['Languages'].split(',')
        languages_abbreviation = city_info['LanguageAbbreviations'].split(',')

        # Create combinations of languages and language abbreviations
        combinations = list(zip(languages, languages_abbreviation))

        # Simulate processing for each combination
        results = []
        for combination in combinations:
            result = {
                'Language': combination[0],
                'LanguageAbbreviation': combination[1],
                'SampleResult': f'Sample result for {combination[0]} in {city}',
            }
            results.append(result)

        return Response({'city_info': city_info, 'language_data': language_dataframe.to_dict(), 'results': results}, status=status.HTTP_200_OK)

    # def get(self, request, city):
    #     # Connect to MongoDB
    #     client = MongoClient("mongodb+srv://vaibhav:Password@cluster0.kfdbs.mongodb.net/test?retryWrites=true&w=majority")
    #     database_name = client.Autocomplete_results
    #     collection_name = database_name[city]

    #     # Retrieve information about the city
    #     city_info = self.get_city_info(city)

    #     # Retrieve language data for the city
    #     language_dataframe = self.get_city_languages(city)

    #     # Get latitude and longitude from city_info
    #     latitude, longitude = float(city_info['Latitude']), float(city_info['Longitude'])

    #     # Convert language and language abbreviation strings to lists
    #     languages = city_info['Languages'].split(',')
    #     languages_abbreviation = city_info['LanguageAbbreviations'].split(',')

    #     # Create combinations of languages and language abbreviations
    #     combinations = list(zip(languages, languages_abbreviation))

    #     # Create a list of numbers for synchronization
    #     list_of_numbers = list(range(0, len(combinations)))

    #     # Create instances of CityInfoView for each combination
    #     list_of_objects = [self for _ in range(len(combinations))]

    #     # Create a thread pool for parallel execution (replace with your implementation)
    #     pool = []

    #     # Create MongoDB document data
    #     rec = {
    #         "City": city,
    #         "Month": datetime.datetime.now().strftime("%b"),
    #         "Date": str(datetime.datetime.now()).split(' ')[0],
    #         "State": city_info['State']
    #     }

    #     # Insert a new MongoDB document and get its Object ID (replace with your MongoDB logic)
    #     object_id = collection_name.insert_one(rec).inserted_id

    #     # Use multi-threading to execute the write function for each combination (replace with your logic)
    #     for i, obj, combination in zip(list_of_numbers, list_of_objects, combinations):
    #         self.write(i, obj, combination, latitude, longitude, object_id, city, language_dataframe)

    #     # Close the MongoDB client (replace with your MongoDB logic)
    #     client.close()

    #     return Response({"message": "City info updated in MongoDB"})

