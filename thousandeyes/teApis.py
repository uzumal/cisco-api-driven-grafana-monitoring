import sys
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Clear proxy environment variables
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

class ThousandEyesAPI:
    def __init__(self, base_url, bearer_token):
        self.base_url = base_url
        self.headers = {
            "Accept": "application/hal+json",
            "Authorization": f"Bearer {bearer_token}"
        }
        self.proxies = {
            "http": os.getenv("HTTP_PROXY", ""),
            "https": os.getenv("HTTPS_PROXY", "")
        }

    def get_tests(self):
        url = f"{self.base_url}/tests"
        response = requests.get(url, headers=self.headers, verify=False, proxies=self.proxies)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def get_http_server_test_results(self, test_id):
        url = f"{self.base_url}/test-results/{test_id}/http-server"
        response = requests.get(url, headers=self.headers, verify=False, proxies=self.proxies)
        if response.status_code != 200:
            sys.exit("Request failed: " + str(response.status_code))
        
        today = datetime.now().date()  # Get today's date
        filtered_results = []
        for result in response.json()['results']:
            result_date = datetime.strptime(result['date'], '%Y-%m-%dT%H:%M:%SZ').date()  # Get the date of the result
            if result_date == today:  # Add only if the result's date is today
                filtered_results.append(result)
        
        response_data = response.json()
        response_data['results'] = filtered_results  # Replace with filtered results
        return response_data