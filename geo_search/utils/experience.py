import requests


def user_details_api(email,occurrences):
    print("---called user details api---")
    api_url = "https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=experienced_service_user_details"
    print(email)
    print(occurrences)
    payload = {
        "email":email,
        "product_number":"UXLIVINGLAB004",
        "occurrences":occurrences
    }
    print("---payload gotten---")
    response = requests.post(api_url,json=payload)
    print(response)
    return response

def save_data(email,search_results):
    api_url = "https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=experienced_user_details" 
    print("---save data called---")
    print("this is res")
    print(search_results)
    payload = {

        "product_name":"LOCATION SPECIFIC SEARCH",
        "email":email,
        "experienced_data":search_results
    }
    
    print("gotten save data payload")
    response = requests.post(api_url,json=payload)
    print(response)
    return response

def update_user_usage(email,occurrences):
    api_url = f"https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=update_user_usage&product_number=UXLIVINGLAB004&email={email}&occurrences={occurrences}"
    response = requests.get(api_url)
    print(response)
    return response