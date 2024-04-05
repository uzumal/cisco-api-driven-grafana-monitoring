import os
import json
from influxdb import InfluxDBClient

os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# Write data to InfluxDB
def write_influxdb(measurement, tag, fields):
  # Connect to the InfluxDB
  dbclient = InfluxDBClient(host='localhost', port=8086, database='Meraki')
  json_body = [
      {
          "measurement": measurement,
          "tag": tag,
          "fields": fields
      }
  ]
  print("Write points: {0}".format(json_body))
  dbclient.write_points(json_body)
  dbclient.close()
  return

# Create clientHealth fields for the InfluxDB
def create_fields_clientHealth(org, network, client):
  fields_clientHealth = {
    "org_name": org['name'],
    "network": network['name'],
    "mac": client['mac'],
    "clientId": client['clientId'],
    "performance_latest": client['performance']['latest'],
    "performance_currentConnection": client['performance']['currentConnection'],
    "onboarding": client['onboarding']['latest']
  }
  return fields_clientHealth

# Create deviceHealth fields for the InfluxDB
def create_fields_deviceHealth(org, network, device):
  fields_deviceHealth = {
    "org_name": org['name'],
    "network": network['name'],
    "serial": device['device']['serial'],
    "performance_latest": device['performance']['latest'],
    "onboarding_latest": device['onboarding']['latest']
  }
  return fields_deviceHealth

# Create deviceStatuses fields for the InfluxDB
def create_fields_deviceStatuses(org, deviceStatuses):
  fields_deviceStatuses = {
    "org_name": org['name'],
    "online": deviceStatuses['online'],
    "alerting": deviceStatuses['alerting'],
    "offline": deviceStatuses['offline'],
    "dormant": deviceStatuses['dormant']
  }
  return fields_deviceStatuses

# Create alert fields for the InfluxDB
def create_fields_alert(org, network, alert):
  fields_alert = {}
  fields_alert = {
    "org_name": org['name'],
    "network": network['name'],
    "occurredAt": alert["occurredAt"],
    "detail": json.dumps(alert), # Alertの内容によって内容が変わるため、json.dumps()で文字列に変換
  }
  #if "serial" in alert:
  #  fields_alert = {
  #    "org_name": org['name'],
  #    "network": network['name'],
  #    "occurredAt": alert["occurredAt"],
  #    "alertTypeId": alert["alertTypeId"],
  #    "alertType": alert["alertType"],
  #    "serial": alert["serial"],
  #    "model": alert["model"]
  #  }
  #else:
  #  fields_alert = {
  #    "org_name": org['name'],
  #    "network": network['name'],
  #    "occurredAt": alert["occurredAt"],
  #    "alertTypeId": alert["alertTypeId"],
  #    "alertType": alert["alertType"],
  #    "serial": alert["device"]["serial"],
  #    "model": alert["device"]["model"]
  #  }
  return fields_alert