#!/usr/bin/env python
# coding: utf-8

import sys
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
import os

# プロキシ環境変数をクリア
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

def make_get_request(url, headers):
    res = requests.get(url, headers=headers, verify=False, proxies={})
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))

    return res


def get_auth_token(user, password, base_url):
    headers = {"Content-Type": "application/json"}
    url = "https://{}/dna/system/api/v1/auth/token".format(base_url)
    res = requests.post(url, headers=headers, auth=(user, password), verify=False, proxies={})
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()["Token"]


def get_site_health(token, base_url):
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    url = "https://{}/dna/intent/api/v1/site-health".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()

def get_network_health(token, base_url):
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    url = "https://{}/dna/intent/api/v1/network-health".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()

def get_client_health(token, base_url):
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    url = "https://{}/dna/intent/api/v1/client-health".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()

def list_devices(token, base_url):
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    url = "https://{}/dna/intent/api/v1/network-device".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()

def get_advisory(token, base_url):
    headers = {
        "X-Auth-Token": token, 
        "Content-Type": "application/json"
    }
    url = "https://{}/dna/intent/api/v1/security-advisory/advisory".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()

def get_issues(token, base_url):
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    url = "https://{}/dna/intent/api/v1/issues".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()

def get_issue_details(token, base_url, entity_value):
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json",
        "entity_type": "issue_id",
        "entity_value": entity_value
    }
    url = "https://{}/dna/intent/api/v1/issue-enrichment-details".format(base_url)
    res = make_get_request(url, headers)
    if res.status_code != 200:
        sys.exit("Request failed: " + str(res.status_code))
    return res.json()
