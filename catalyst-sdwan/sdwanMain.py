import os
from dotenv import load_dotenv
from datetime import datetime
import json
from influxdb import InfluxDBClient
import sdwanApis

# load /.env
load_dotenv()

# Connect to the database
dbclient = InfluxDBClient(host='localhost', port=8086, database='CatSDWAN')

def write_to_influxdb(measurement, data, tags=None, client=dbclient):
    # Initialize measurement
    client.drop_measurement(measurement)
    client.write_points(data)

def calculate_health_ratio(data):
    """
    Calculate the health ratio based on the provided data.
    """
    total_count = data['count']
    error_count = data['statusList'][0]['count']
    healthy_count = total_count - error_count
    health_ratio = healthy_count / total_count if total_count > 0 else 0.0
    return health_ratio

def get_device_health(vmanage_host, jsessionId, token):
    # Get vManage health ratio
    vmanage_data = sdwanApis.get_data(vmanage_host, jsessionId, token, "/clusterManagement/health/summary")
    if vmanage_data:
        vmanage_data = vmanage_data['data'][0]
        vmanage_name = vmanage_data['name']
        vmanage_health_ratio = calculate_health_ratio(vmanage_data)

    # Get overall health ratio
    device_data = sdwanApis.get_data(vmanage_host, jsessionId, token, "/network/connectionssummary")
    if device_data:
        health_ratio_list = [(vmanage_name, vmanage_health_ratio)]
        for data in device_data['data']:
            device_name = data['name']
            health_ratio = calculate_health_ratio(data)
            health_ratio_list.append((device_name, health_ratio))
        
        json_body = []
        for item in health_ratio_list:
            json_body.append({
                "measurement": "DeviceHealth",
                "tags": {
                    "deviceType": item[0]
                },
                "fields": {
                    "healthRatio": item[1]
                }
            })
        
        write_to_influxdb("DeviceHealth", json_body)

def get_alarms(vmanage_host, jsessionId, token):
    query = {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": [
                        "24"
                    ],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "last_n_hours"
                },
                {
                    "value": [
                        "Critical",
                        "Major",
                        "Medium",
                        "Minor"
                    ],
                    "field": "severity",
                    "type": "string",
                    "operator": "in"
                },
                {
                    "value": [
                        "true"
                    ],
                    "field": "active",
                    "type": "string",
                    "operator": "in"
                },
            ]
        }
    }
    payload = json.dumps(query)
    alarm_data = sdwanApis.get_data(vmanage_host, jsessionId, token, "/alarms", method="POST", payload=payload)
    
    if alarm_data:
        alarms_list = []
        for alarm in alarm_data['data']:
            entry_time = alarm['entry_time']
            message = alarm['message']
            severity = alarm['severity']
            component = alarm['component']
            alarm_info = [entry_time, message, severity, component]
            alarms_list.append(alarm_info)
        
        for alarm in alarms_list:
            issue_time = datetime.fromtimestamp(alarm[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            issueJson = {
                "issue_time": issue_time,
                "issue_category": alarm[3],
                "issue_severity": alarm[2],
                "issue_description": alarm[1]
            }
            point = {
                "measurement": "issueDetails",
                "tags": {
                    "issueSource": "SDWAN"
                },
                "fields": {
                    "issueDescription": json.dumps(issueJson)
                }
            }
            dbclient.write_points([point])

if __name__ == "__main__":
    # vManage connection information
    vmanage_host = os.getenv("SDWAN_HOST")
    username = os.getenv("SDWAN_USERNAME")
    password = os.getenv("SDWAN_PASSWORD")

    # Get jsessionId and token
    sess, jsessionId = sdwanApis.get_jsession_id(vmanage_host, username, password)
    token = sdwanApis.get_token(vmanage_host, jsessionId)

    # Get device health and alarms
    get_device_health(vmanage_host, jsessionId, token)

    dbclient.drop_measurement('issueDetails')
    get_alarms(vmanage_host, jsessionId, token)

    # Close the session and database connection
    sess.close()
    dbclient.close()