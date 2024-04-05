#!/usr/bin/env python
# coding: utf-8

import requests
import urllib3
from requests.models import Response
import random
import os
import datetime
import const

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a response object for error situations that can't be handled
def create_response_object(e):
  response = Response()
  response.status_code = const.status_code_custom
  response._content = str(e).encode()
  return response

# Return proxies for the requests
def get_randomProxies():
  proxy = random.choice(const.proxies)
  return {
    "http": proxy,
    "https": proxy
  }

# Write lists to a log file
def write_list_to_log_file(*lists):
  # Get current date and time
  now = datetime.datetime.now()

  ## Mkdir logs if it doesn't exist
  log_dir = "logs"
  if not os.path.exists(log_dir):
    os.mkdir(log_dir)
  log_file_path = f"{log_dir}/log_{now.strftime('%Y%m%d_%H%M%S')}.log"

  with open(log_file_path, mode='w') as f:
    for list in lists:
      f.write(f"{list}\n\n")


# Make a GET request
def make_get_request(base_url, headers):
  try:
    response = requests.get(base_url, headers=headers, verify=False, proxies=get_randomProxies())
    return response
  except Exception as e:
    # Return response as None with error if there is an exception
    return create_response_object(e)


# Get the organizations
# https://developer.cisco.com/meraki/api/get-organizations/
def get_organizations(base_url, headers):
  response = make_get_request(f"{base_url}/organizations", headers)
  if response.status_code != 200:
    print(f"Error(get_organizations): {response.status_code} - {response.text}")
    return []
  return response.json()

# Get the networks for an organization
# https://developer.cisco.com/meraki/api/get-organization-networks/
def get_org_networks(base_url, headers, org_id):
  response = make_get_request(f"{base_url}/organizations/{org_id}/networks", headers)
  if response.status_code != 200:
    print(f"Error(get_org_networks): {response.status_code} - {response.text}")
    return []
  return response.json()

# Get the wireless clients health scores for a network
# https://developer.cisco.com/meraki/api/get-network-wireless-clients-health-scores/
def get_network_wireless_clients_health(base_url, headers, network_id):
  response = make_get_request(f"{base_url}/networks/{network_id}/wireless/clients/healthScores", headers)
  if response == None:
    print(f"Error(get_network_wireless_clients_health): Response is None from Network {network_id}")
    return []
  elif response.status_code != 200:
    print(f"Error(get_network_wireless_clients_health): {response.status_code} - {response.text}")
    return []
  return response.json()

# Get the wireless devices health scores for a network
# https://developer.cisco.com/meraki/api/get-network-wireless-devices-health-scores/
def get_network_wireless_devices_health(base_url, headers, network_id):
  response = make_get_request(f"{base_url}/networks/{network_id}/wireless/devices/healthScores", headers)
  if response == None:
    print(f"Error(get_network_wireless_devices_health): Response is None from Network {network_id}")
    return []
  elif response.status_code != 200:
    print(f"Error(get_network_wireless_devices_health): {response.status_code} - {response.text}")
    return []
  return response.json()

# Get the device statuses for an organization
# https://developer.cisco.com/meraki/api/get-organization-devices-statuses-overview/
def get_org_devices_statuses(base_url, headers, org_id):
  response = make_get_request(f"{base_url}/organizations/{org_id}/devices/statuses/overview", headers)
  if response.status_code != 200:
    print(f"Error(get_org_devices_statuses): {response.status_code} - {response.text}")
    return []
  return response.json()['counts']['byStatus']

# Get the network alerts history
# https://developer.cisco.com/meraki/api/get-network-alerts-history/
def get_network_alerts_history(base_url, headers, network_id):
  response = make_get_request(f"{base_url}/networks/{network_id}/alerts/history", headers)
  if response.status_code != 200:
    print(f"Error(get_network_alerts_history): {response.status_code} - {response.text}")
    return[]
  return response.json()