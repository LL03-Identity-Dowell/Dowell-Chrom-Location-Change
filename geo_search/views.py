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
from .serializers import LocationSerializer,CountrySerializer
from .models import Location,Country
from django.views.decorators.csrf import csrf_exempt
import logging,json,tempfile
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
logging.basicConfig(level=logging.INFO)



@method_decorator(csrf_exempt, name='dispatch')
class HomepageView(View):
    def get(self, request):
        # Attempt to get countries from cache
        countries = cache.get('cached_countries')
        search_results = []
        if countries is not None:
            print("Cache hit: Using cached countries")
        else:
            print("Cache miss: Fetching countries from the API")


        if countries is None:
            # If not found in cache, make an API request to get the list of countries
            dowell_api_key = settings.DOWELL_API_KEY
            dowell_testing_api_key = settings.DOWELL_TESTING_API_KEY

            country_api_url = f'https://100074.pythonanywhere.com/get-countries-v3/?api_key={dowell_api_key}'
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
                else:
                    # Handle the case where the API request failed
                    error_message = "Failed to retrieve country data from the API."
                    return render(request, 'index.html', {'search_results': search_results, 'error_message': error_message})
            else:
                # Handle the case where the API request failed
                error_message = "Failed to retrieve country data from the API."
                return render(request, 'index.html', {'search_results': search_results, 'error_message': error_message})

        # Use the cached or fetched countries
        return render(request, 'index.html', {'countries': countries, 'search_results': search_results})
    def post(self, request):
        dowell_api_key = settings.DOWELL_API_KEY
        dowell_testing_api_key = settings.DOWELL_TESTING_API_KEY
        search_results = []  # Initialize as an empty list

        # Attempt to get countries from cache
        countries = cache.get('cached_countries')

        if countries is not None:
            print("Cache hit: Using cached countries")
        else:
            print("Cache miss: Fetching countries from the API")
        

        if countries is None:
            # If not found in cache, make an API request to get the list of countries
            country_api_url = f'https://100074.pythonanywhere.com/get-countries-v3/?api_key={dowell_api_key}'
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
                else:
                    # Handle the case where the API request failed
                    error_message = "Failed to retrieve country data from the API."
                    return render(request, 'index.html', {'search_results': search_results, 'error_message': error_message})
            else:
                # Handle the case where the API request failed
                error_message = "Failed to retrieve country data from the API."
                return render(request, 'index.html', {'search_results': search_results, 'error_message': error_message})

        # Continue with the rest of your post method logic using the cached or fetched countries
        location = request.POST.getlist('location', [])
        search_content = request.POST.get('search', '')
        num_results = request.POST.get('num_results')

        try:
            for city in location:  # Loop through selected locations
                response = requests.post('https://geopositioning.uxlivinglab.online/api/geo_location', data={
                    "city": city,
                    'search_content': search_content,
                    'num_results': num_results
                })

                if response.status_code == 200:
                    response_data = response.json()
                    search_results.append({"city": city, "results": response_data.get('search_results', [])})
                    logging.info(f"Received results for {city}")
                else:
                    error_message = f"API request for {city} failed."
                    return render(request, 'index.html', {'countries': countries,'error_message': error_message})
        except Location.DoesNotExist:
            error_message = f"Selected location does not exist."
            return render(request, 'index.html', {'countries': countries,'error_message': error_message})

        request.session['search_results'] = search_results

        return render(request, 'index.html', {'countries': countries, 'search_results': search_results})


    
@method_decorator(csrf_exempt, name='dispatch')
class Chromeview(APIView):
    def post(self, request, format=None):
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
    

@csrf_exempt
def download_csv(request):
    # Get the search results from the session
    search_results = request.session.get('search_results', [])

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

        location_data = {}

        for country in selected_countries:
            # Define the cache key based on the selected country
            cache_key = f'locations_{country}'
            cached_data = cache.get(cache_key)

            if cached_data:
                location_data[country] = cached_data
            else:
                # Fetch location data from the external API
                api_key = settings.DOWELL_API_KEY
                api_url = f'https://100074.pythonanywhere.com/get-coords-v3/?api_key={api_key}'
                
                data = {
                    'country': country,
                    'query': 'all'
                }
                try:
                    response = requests.post(api_url,json=data)
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
    
