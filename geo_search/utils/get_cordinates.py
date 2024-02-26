import requests
from django.conf import settings

def GetCoordinates(location):
    url = "https://100074.pythonanywhere.com/get-coords/"
    api_key = settings.DOWELL_API_KEY
    print("--Started--")

    payload = {
        "region": location,
        "api_key": api_key
    }
    print("--payload gotten--")
    try:
        response = requests.post(url, json=payload)
        print(response)
        if response.status_code == 200:
            data = response.json()
            print(data)
            # Access latitude and longitude within the 'location' key
            location_data = data.get('data', {}).get('location', {})
            latitude = location_data.get('lat')
            longitude = location_data.get('lng')
            
            return {'lat': latitude, 'lng': longitude}
        else:
            # Handle other status codes if needed
            print("Request failed with status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("Request exception:", e)
        return None
