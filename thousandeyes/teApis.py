import sys
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
import os
from dotenv import load_dotenv

# load /.env file
load_dotenv()

# clear export env
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
        return response.json()