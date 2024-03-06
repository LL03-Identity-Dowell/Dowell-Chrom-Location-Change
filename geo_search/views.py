from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework import generics, status,viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render,get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import logging,json,tempfile
from bs4 import BeautifulSoup
from django.conf import settings
from selenium import webdriver
from django.core.cache import cache
from django.utils.decorators import method_decorator
logging.basicConfig(level=logging.INFO)
from .utils.get_cordinates import GetCoordinates
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import logging
import requests
from threading import Thread
from .utils.experience import user_details_api,save_data,update_user_usage
from threading import Lock
occurrences_lock = Lock()  # Define a lock for occurrences


class GetCountries(APIView):
    def get(self,request):
        # Attempt to get countries from cache
        countries = cache.get('cached_countries')
        if countries is not None:
            print("Cache hit: Using cached countries")
        else:
            print("Cache miss: Fetching countries from the API")


        if countries is None:
            # If not found in cache, make an API request to get the list of countries
            dowell_api_key = settings.DOWELL_API_KEY
            dowell_testing_api_key = settings.DOWELL_TESTING_API_KEY

            country_api_url = f'https://100074.pythonanywhere.com/get-countries-v3/?api_key={dowell_testing_api_key}'
            print(country_api_url)
            response = requests.post(country_api_url)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    countries = data['data'][0].get('countries', [])
                    
                    if countries:
                        # Sort the list of countries alphabetically
                        countries = sorted(countries)
                        # Store the countries in the cache with a timeout
                        cache.set('cached_countries', countries, 86400)
        return Response({
            "success":True,
            "countries":countries
        })



@method_decorator(csrf_exempt, name='dispatch')
class HomepageView(APIView):
    def post(self, request):
        search_results = []  # Initialize as an empty list

        # Extract data from the request
        location = request.data.get('location', [])
        search_content = request.data.get('search', '')
        num_results = request.data.get('num_results')

        try:
            for city in location:  # Loop through selected locations
                response = requests.post('https://geopositioning.uxlivinglab.online/api/geo_location', data={
                    "city": city,
                    'search_content': search_content,
                    'num_results': num_results
                })
                print(response.json())
                if response.status_code == 200:
                    response_data = response.json()
                    search_results.append({
                        "city": city,
                        "search_content": search_content,
                        "results": response_data.get('search_results', [])
                    })
                    logging.info(f"Received results for {city}")
                else:
                    error_message = f"API request for {city} failed."
                    return Response({
                        "success": False,
                        "message": error_message
                    })
        except:
            error_message = f"Selected location does not exist."
            return Response({
                "success": False,
                "message": error_message
            })

        request.session['search_results'] = search_results

        # Call the function to hit an API with user details
        email = request.data.get('email')
        occurrences = request.data.get('occurrences')

        def execute_threaded_tasks(email, occurrences,search_results):
            api_response = user_details_api(email, occurrences)
            print("---got api response---")
            api_response_data = api_response.json()
            if "success" in api_response_data and api_response_data["success"]:
                print("---returning response---")
                # Run functions in threads
                print("this is res from view")
                with occurrences_lock:
                    occurrences += 1
                experienced_date = Thread(target=save_data, args=(email, search_results))
                experienced_date.daemon = True
                experienced_date.start()
                print("adding")
                print(occurrences)
                print("added")
                experienced_reduce = Thread(target=update_user_usage, args=(email, occurrences))
                experienced_reduce.daemon = True
                experienced_reduce.start()
                # Return PPP calculation response to the frontend
                print("---everything worked---")

        threading_tasks_thread = Thread(target=execute_threaded_tasks, args=(email, occurrences,search_results))
        threading_tasks_thread.daemon = True
        threading_tasks_thread.start()

        return Response({
            'success': True,
            'search_results': search_results
        })




    
@method_decorator(csrf_exempt, name='dispatch')
class Chromeview(APIView):
    def post(self, request, format=None):
        print("called")
        search_content = request.data.get('search_content', '')  # Access search_content as a string
        num_results = request.data.get('num_results')

        # Extract the selected location
        city = request.data.get('city')
        logging.info(f"Received search_content: {search_content}")
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
    


class DownloadCSV(APIView):

    def post(self, request):
        # Get the search results from the session
        search_results = request.data.get('search_results', [])
        print(search_results)
        # Create a CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="search_results.csv"'

        # Create a CSV writer
        csv_writer = csv.writer(response)
        # Write the header row
        csv_writer.writerow(['City', 'Title', 'Link', 'Snippet'])

        # Write the search results to the CSV file
        for city_data in search_results:
            city = city_data.get('city', '')  # Handle the case where 'city' is missing
            results = city_data.get('results', [])

            for result in results:
                title = result.get('title', '')  # Handle the case where 'title' is missing
                link = result.get('link', '')  # Handle the case where 'link' is missing
                snippet = result.get('snippet', '')  # Handle the case where 'snippet' is missing

                # Write the data to the CSV file
                csv_writer.writerow([city, title, link, snippet])

        return response



class GetLocations(APIView):
    def post(self, request):
        selected_countries = request.data.get('selectedCountries', [])
        offset = request.data.get("offset")
        limit = request.data.get("limit")

        location_data = {}

        for country in selected_countries:
            # Define the cache key based on the selected country, offset, and limit
            cache_key = f'locations_{country}_offset_{offset}_limit_{limit}'
            cached_data = cache.get(cache_key)

            if cached_data:
                location_data[country] = cached_data
            else:
                # Fetch location data from the external API
                api_key = settings.DOWELL_API_KEY
                api_url = f'https://100074.pythonanywhere.com/get-coords-v3/?api_key={api_key}'
                
                data = {
                    'country': country,
                    'query': 'all',
                    'offset': offset,
                    'limit': limit
                }
                try:
                    response = requests.post(api_url, json=data)
                    print("called")
                    response.raise_for_status()
                    data = response.json()
                    print(data)
                    location_data[country] = data
                    # Cache the location data for future use
                    cache.set(cache_key, location_data[country], timeout=86400)  # Cache indefinitely
                except requests.exceptions.RequestException as e:
                    # Handle API request errors
                    print(f"API request error for {country}: {e}")
                    location_data[country] = []

        return Response(location_data, status=status.HTTP_200_OK)

    

class LaunchBrowser(APIView):
    def post(self, request):
        print(request.data)
        url = request.data.get('url')
        locations = request.data.get('location', [])
        print(url)
        print(locations)  # Changed variable name to 'locations' for consistency
        
        # Validate 'url' and 'location' inputs (add your validation logic)
        if not url or not locations:  # Updated variable name to 'locations'
            return Response({'error': 'Invalid URL or Location data provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        for location in locations:  # Loop through each location
            print(location)
            coordinates = GetCoordinates(location)
            print(coordinates)
            
            if coordinates:
                try:
                    latitude = coordinates.get('lat')
                    longitude = coordinates.get('lng')
    
                    driver = webdriver.Chrome()
    
                    # Construct the JavaScript function to set the location
                    script = f"navigator.geolocation.getCurrentPosition = function(success) {{ success({{ coords: {{ latitude: {latitude}, longitude: {longitude} }} }}); }};"
                    
                    # Execute the JavaScript to set the location
                    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                        "source": script
                    })
                    
                    # Navigate to the URL
                    driver.get(url)
                    
                    # Keep the browser open until explicitly closed
                    input("Press Enter to close the browser...")  # This waits for user input to close the browser
                    
                    driver.quit()  # Close the browser explicitly
                    
                except Exception as e:
                    print(f"Error setting browser location for {location}: {e}")
                    # Handling individual location errors, you might want to customize this response
                    
            else:
                print(f"Failed to get coordinates for {location}")
                # Handling individual location coordinate retrieval failures

        return Response({'message': 'All locations processed successfully'}, status=status.HTTP_200_OK)
