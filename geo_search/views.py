from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
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
import logging,json,tempfile
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.decorators import method_decorator



logging.basicConfig(level=logging.INFO)
@csrf_exempt
def homepage_view(request):
    serializer = LocationSerializer(Location.objects.all(), many=True)
    # Initialize as a list
    search_results = []
    
    if request.method == 'POST':
        # Deserialize the data using the serializer
        selected_location_ids = request.POST.getlist('location')  # Get a list of selected location IDs
        search_content = request.POST.get('search', '')
        num_results = request.POST.get('num_results')
        
        for location_id in selected_location_ids:
            try:
                selected_location = Location.objects.get(id=location_id)
                city = selected_location.name
                # Make a POST request to your APIView to set the Chrome instance
                response = requests.post('http://127.0.0.1:8080/api/geo_location/', data={
                    "city": city,
                    'search_content': search_content,
                    'num_results': num_results
                })
                if response.status_code == 200:
                    # Parse the JSON response from the Chromeview
                    # Inside your loop for multiple locations
                    response_data = response.json()
                    search_results.append({"city": city, "results": response_data.get('search_results', [])})
                    logging.info(f"Received results for {city}")
                else:
                    # Handle the case where the API request failed
                    error_message = f"API request for {city} failed."
                    return render(request, 'index.html', {'serializer': serializer, 'error_message': error_message})
            except Location.DoesNotExist:
                # Handle the case where the selected location doesn't exist
                error_message = f"Selected location with ID {location_id} does not exist."
                return render(request, 'index.html', {'serializer': serializer, 'error_message': error_message})

    else:
        # Create a serializer to render the form in the template
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)

    return render(request, 'index.html', {'serializer': serializer, 'search_results': search_results})

    

@method_decorator(csrf_exempt, name='dispatch')
class Chromeview(APIView):
    def post(self, request, format=None):
        search_content = request.data.get('search_content', '')  # Access search_content as a string
        num_results = request.data.get('num_results')

        # Extract the selected location
        city = request.data.get('city')
        logging.info(f"Received search_content: {search_content}")
        # Deserialize the data using the serializer
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            selected_location = serializer.validated_data
            # Perform the search and get the search results
            search_results = self.perform_search(city,search_content,num_results)
            logging.info("Performing search")
            # Return the search results as a JSON response
            return Response({"message": "Location set successfully", 'search_results': search_results}, status=status.HTTP_200_OK)

    # Perform the search feature in our app
    def perform_search(self, city, search_content, num_results):
        # Replace with your API key and search engine ID
        api_key = settings.GOOGLE_API_KEY  # Use the variable defined in your Django settings
        search_engine_id = settings.SEARCH_ENGINE_ID  # Use the variable defined in your Django settings
        # Get the location from the query parameters (e.g., /search/?location=New+York%2C+NY)
        location = city
        print(location)
        # Get the search query from the query parameters
        query = search_content + " in " + location
        if not location or not query:
            return JsonResponse({"error": "Both 'location' and 'query' parameters are required."}, status=400)
        
        # Initialize variables for pagination
        start_index = 1
        total_results = []
        
        # Convert num_results to an integer
        num_results = int(num_results)
        # Continue fetching results until we have the desired number or there are no more results
        while len(total_results) < num_results:
            # Calculate the number of results to fetch in this iteration (maximum of 10)
            results_to_fetch = min(num_results - len(total_results), 10)
            # Construct the URL for the Google Custom Search API with pagination
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&gl={location}&num={results_to_fetch}&start={start_index}"
            logging.info(f"API URL: {url}")  # Add this line to print the URL
            # Make the API request
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                try:
                    # Parse the JSON response
                    json_response = response.json()
                    # Extract the "items" field, which contains the search results
                    items = json_response.get("items", [])
                    # Extract the "title," "link," "snippet," and "pagemap" (which contains images) fields for each search result
                    search_results = [{"title": item["title"], "link": item["link"], "snippet": item.get("snippet", ""), "images": item.get("pagemap", {}).get("cse_image", [])} for item in items]
                    # Add the results to the total_results list
                    total_results.extend(search_results)
                    # If there are no more results, break out of the loop
                    if len(search_results) < results_to_fetch:
                        break
                    # Increment the start index for the next pagination
                    start_index += results_to_fetch
                except Exception as e:
                    # Handle any exceptions that may occur during JSON parsing or data extraction
                    return JsonResponse({"error": str(e)}, status=500)
            else:
                return JsonResponse({"error": "Google Custom Search API request failed."}, status=response.status_code)
        # Return the search results as a list of dictionaries
        return total_results





@method_decorator(csrf_exempt, name='dispatch')
class CityInfoView(APIView):
    def get_city_info(self, city, format=None):
        # Replace this hardcoded data with your actual data
        latitude = float(self.request.query_params.get('latitude'))
        longitude = float(self.request.query_params.get('longitude'))
        language =  self.request.query_params.get('language')
        state =  self.request.query_params.get('state')
        language_abbreviation = self.request.query_params.get('language_code')
        city_info = {
            "City": city,
            "Languages": language,  # Replace with the actual languages
            "LanguageAbbreviations": language_abbreviation,  # Replace with the actual abbreviations
            "State": state,
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

    