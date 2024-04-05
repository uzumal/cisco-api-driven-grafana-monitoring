# Description: This file contains the constant values used in the Meraki API scripts.

import os
from dotenv import load_dotenv

# load /.env
load_dotenv()

# Set your Meraki API key and base URL
api_key_devnet = os.getenv("MERAKI_DEVNET_API_KEY") # DevNet Sandbox
api_key_user = os.getenv("MERAKI_USER_API_KEY") # DevNet Sandbox
api_key_launchpad = os.getenv("MERAKI_API_KEY") # Meraki Launchpad's API key
#api_key = api_key_devnet
#api_key = api_key_keishima
api_key = api_key_launchpad
base_url = "https://api.meraki.com/api/v1"

headers = {
  "X-Cisco-Meraki-API-Key": api_key,
}

proxies = [
  "http://proxy.esl.cisco.com:80",
  "http://proxy-wsa.esl.cisco.com:80"
]

sleep_time = 3

status_code_custom = 499