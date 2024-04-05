import sys
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
import os

# プロキシ環境変数をクリア
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

def get_jsession_id(vmanage_host, username, password):
    vmanage_url = f"https://{vmanage_host}"
    auth_url = "/j_security_check"
    url = f"{vmanage_url}{auth_url}"
    payload = {"j_username": username, "j_password": password}

    sess = requests.session()
    res = sess.post(url, data=payload, verify=False)

    if res.status_code != 200:
        print(f"Login failed with status code {res.status_code}")
        print(res.text)
        sys.exit(1)

    if "Set-Cookie" in res.headers:
        cookies = res.headers["Set-Cookie"]
        jsession = cookies.split(";")
        jsessionId = jsession[0]
    else:
        print("Failed to get jsessionid from login response")
        print(res.text)
        sys.exit(1)

    return sess, jsessionId

def get_token(vmanage_host, jsessionId):
    base_url = f"https://{vmanage_host}/dataservice"
    token_url = "/client/token"
    url = f"{base_url}{token_url}"
    headers = {"Cookie": jsessionId}

    res = requests.get(url, headers=headers, verify=False)

    if res.status_code != 200:
        print(f"Failed to get token with status code {res.status_code}")
        print(res.text)
        sys.exit(1)

    if "<html>" in res.text:
        print("Failed to get token, received HTML response")
        print(res.text)
        sys.exit(1)

    return res.text

def get_data(vmanage_host, jsessionId, token, endpoint, method="GET", payload=None):
    base_url = f"https://{vmanage_host}/dataservice"
    url = f"{base_url}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Cookie": jsessionId,
        "X-XSRF-TOKEN": token
    }

    if method == "GET":
        res = requests.get(url, headers=headers, verify=False)
    elif method == "POST":
        res = requests.post(url, headers=headers, data=payload, verify=False)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    if res.status_code != 200:
        print(f"Failed to get data from {endpoint} with code {res.status_code}")
        print(res.text)
        return None

    return res.json()