import os
import requests


# Pass the 'request' object when you call this function from a view
def convert_currency(request, from_currency, to_currency, amount):
    # Get the API domain from environment variables or default to 'localhost:8000'
    api_domain = os.getenv('API_DOMAIN', 'localhost:8000')

    # Use the request scheme to determine if it's 'http' or 'https'
    protocol = request.scheme

    api_url = f"{protocol}://{api_domain}/conversion/{from_currency}/{to_currency}/{amount}"

    response = requests.get(api_url, verify=False)
    if response.status_code == 200:
        conversion_result = response.json()
        return conversion_result['converted_amount']
    else:
        raise ValueError(f"Failed to convert currency. API responded with status code {response.status_code}.")
