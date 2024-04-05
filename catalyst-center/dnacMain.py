import dnacApis
import os
from dotenv import load_dotenv
import json
import time
from datetime import datetime
from influxdb import InfluxDBClient

# .envファイルを読み込む
load_dotenv()

USER = os.getenv("DNAC_USERNAME")
PASSWORD = os.getenv("DNAC_PASSWORD")
BASE_URL = os.getenv("DNAC_HOST")

# Connect to the database
dbclient = InfluxDBClient(host='localhost', port=8086, database='CatC')

# Get DNA-API-KEY
token = dnacApis.get_auth_token(USER, PASSWORD, BASE_URL)

# Retrieve data from DNA Center
sites_health = dnacApis.get_site_health(token, BASE_URL)
network_health = dnacApis.get_network_health(token, BASE_URL)
client_health = dnacApis.get_client_health(token, BASE_URL)
issues_data = dnacApis.get_issues(token, BASE_URL)
advisories = dnacApis.get_advisory(token, BASE_URL)

def write_to_influxdb(measurement, data, tags=None, client=dbclient):
    # Initialize measurement
    client.drop_measurement(measurement)
    client.write_points(data)

def analyze_client_health(data):
    result = {}
    for site in data:
        for score_detail in site["scoreDetail"]:
            if score_detail["scoreCategory"]["scoreCategory"] == "CLIENT_TYPE":
                client_type = score_detail["scoreCategory"]["value"]
                if client_type not in result:
                    result[client_type] = {
                        "total": 0,
                        "POOR": 0,
                        "FAIR": 0,
                        "GOOD": 0,
                        "IDLE": 0,
                        "NEW": 0,
                        "NODATA": 0
                    }
                result[client_type]["total"] += score_detail["clientCount"]
                
                if "scoreList" in score_detail:
                    for score in score_detail["scoreList"]:
                        if score["scoreCategory"]["scoreCategory"] == "SCORE_TYPE":
                            score_type = score["scoreCategory"]["value"]
                            if score_type in result[client_type]:
                                result[client_type][score_type] += score["clientCount"]
    return result

def write_network_device_health_to_influxdb(data):
    json_body = []
    for item in data:
        json_body.append({
            "measurement": "networkDeviceHealth",
            "tags": {
                "entity": item["entity"]
            },
            "fields": {
                "healthScore": item["healthScore"],
                "totalCount": item["totalCount"],
                "goodCount": item["goodCount"],
                "noHealthCount": item["noHealthCount"],
                "fairCount": item["fairCount"],
                "badCount": item["badCount"],
                "maintenanceModeCount": item["maintenanceModeCount"]
            }
        })
    return json_body

def write_client_health_to_influxdb(data):
    json_body = []
    for client_type, values in data.items():
        json_body.append({
            "measurement": "clientHealth",
            "tags": {
                "clientType": client_type
            },
            "time": int(time.time_ns()),
            "fields": {
                "total": values["total"],
                "poor": values["POOR"],
                "fair": values["FAIR"],
                "good": values["GOOD"],
                "idle": values["IDLE"],
                "new": values["NEW"],
                "nodata": values["NODATA"]
            }
        })
    return json_body

def write_overall_health_to_influxdb(data):
    json_body = [
        {
            "measurement": "overallHealth",
            "tags": {
                "siteName": data[0].get("siteName")
            },
            "fields": {
                "networkHealth": data[0].get("networkHealthAverage"),
                "switchHealth": data[0].get("networkHealthSwitch"),
                "WLCHealth": data[0].get("networkHealthWLC"),
                "APHealth": data[0].get("networkHealthAP"),
                "wirelessHealth": data[0].get("networkHealthWireless"),
            }
        }
    ]
    return json_body

def write_advisory_to_influxdb(data):
    for advisory in data:
        point = {
            "measurement": "securityAdvisory",
            "time": int(time.time_ns()),
            "fields": {
                "deviceCount": advisory.get("deviceCount", 0),
                "cves": ",".join(advisory.get("cves", [])),
                "publicationUrl": advisory.get("publicationUrl", ""),
                "severity": advisory.get("sir", ""),
                "advisoryId": advisory.get("advisoryId", "")
            },
            "tags": {
                "advisoryId": advisory.get("advisoryId", "")
            }
        }
        dbclient.write_points([point])

def write_issue_details_to_influxdb(data):
    for issue_detail in data:
        for issue in issue_detail["issue"]:
            issue_time = datetime.fromtimestamp(issue["issueTimestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            issue_json = {
                "issue_time": json.dumps(issue_time),
                "issue_category": issue.get("issueCategory"),
                "issue_severity": issue.get("issueSeverity"),
                "issue_description": issue.get("issueDescription")
            }
            point = {
                "measurement": "issueDetails",
                "tags": {
                    "issueSource": issue["issueSource"]
                },
                "fields": {
                    "issueDetails": json.dumps(issue_json)
                }
            }
            dbclient.write_points([point])

if __name__ == "__main__":
    # Write data to InfluxDB
    write_to_influxdb("networkDeviceHealth", write_network_device_health_to_influxdb(network_health["response"]))
    analysis_result = analyze_client_health(client_health["response"])
    write_to_influxdb("clientHealth", write_client_health_to_influxdb(analysis_result))
    write_to_influxdb("overallHealth", write_overall_health_to_influxdb(sites_health["response"]))

    all_issue_details = []
    for issue in issues_data['response']:
        issue_details = dnacApis.get_issue_details(token, BASE_URL, issue["issueId"])
        all_issue_details.append(issue_details["issueDetails"])

    dbclient.drop_measurement('securityAdvisory')
    write_advisory_to_influxdb(advisories["response"])
    dbclient.drop_measurement('issueDetails')
    write_issue_details_to_influxdb(all_issue_details)

    dbclient.close()