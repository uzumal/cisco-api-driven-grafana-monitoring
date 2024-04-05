import const
import merakiApis
import influxdbApis
import time

# Data inserted into the InfluxDB
organizations = []
list_org_networks = [] # [[org, networks], ... , []]
list_org_network_clients = [] # [[org, network, clients], ... , []]
list_org_network_devices = [] # [[org, network, devices], ... , []]
list_org_network_alerts = [] # [[org, network, alerts], ... , []]
list_org_deviceStatuses = [] # [[org, deviceStatuses], ... , []]

# Make a GET request to retrieve the organizations
organizations = merakiApis.get_organizations(const.base_url, const.headers)
for org in organizations:
  #print(f"Organization Name: {org['name']}, ID: {org['id']}")
  time.sleep(const.sleep_time)

  networks = merakiApis.get_org_networks(const.base_url, const.headers, org['id'])
  for network in networks:
    list_org_networks.append([org, network])
    #print(f"  Network Name: {network['name']}, ID: {network['id']}")
    time.sleep(const.sleep_time)

    clients = merakiApis.get_network_wireless_clients_health(const.base_url, const.headers, network['id'])
    for client in clients:
      list_org_network_clients.append([org, network, client])
      #print(f"    Client MAC: {client['mac']}, Performance(latest): {client['performance']['latest']}, Performance(currentConnection): {client['performance']['currentConnection']}, Onboarding: {client['onboarding']}")
    time.sleep(const.sleep_time)

    devices = merakiApis.get_network_wireless_devices_health(const.base_url, const.headers, network['id'])
    for device in devices:
      list_org_network_devices.append([org, network, device])
      #print(f"    Device Serial: {device['device']['serial']}, Performance(latest): {device['performance']['latest']}, Onboarding(latest): {device['onboarding']}")
    time.sleep(const.sleep_time)

    alerts = merakiApis.get_network_alerts_history(const.base_url, const.headers, network['id'])
    for alert in alerts:
      list_org_network_alerts.append([org, network, alert])
      #print(f"  Alert: {alert}")
    time.sleep(const.sleep_time)

  device_statuses = merakiApis.get_org_devices_statuses(const.base_url, const.headers, org['id'])
  list_org_deviceStatuses.append([org, device_statuses])
  #print(f"  Devices Status->Online: {device_statuses['online']}, Alerting: {device_statuses['alerting']}, Offline: {device_statuses['offline']}, Dormant: {device_statuses['dormant']}")
  time.sleep(const.sleep_time)

# Write the lists to a log file
merakiApis.write_list_to_log_file(organizations, list_org_networks, list_org_network_clients, list_org_network_devices, list_org_network_alerts, list_org_deviceStatuses)
#print(f"{organizations}\n\n{list_org_networks}\n\n{list_org_network_clients}\n\n{list_org_network_devices}\n\n{list_org_network_alerts}\n\n{list_org_deviceStatuses}\n")

# Write clients health data to the InfluxDB
for org_network_clients in list_org_network_clients:
  clients = org_network_clients[2]
  for client in clients:
    fields_clientHealth = influxdbApis.create_fields_clientHealth(org=org_network_clients[0], network=org_network_clients[1], client=org_network_clients[2])
    influxdbApis.write_influxdb(measurement="clientHealth", tag={"clientHealth"}, fields=fields_clientHealth)

# Write devices health data to the InfluxDB
for org_network_devices in list_org_network_devices:
  devices = org_network_devices[2]
  for device in devices:
    fields_deviceHealth = influxdbApis.create_fields_deviceHealth(org=org_network_devices[0], network=org_network_devices[1], device=org_network_devices[2])
    influxdbApis.write_influxdb(measurement="deviceHealth", tag={"deviceHealth"}, fields=fields_deviceHealth)

# Write device statuses data to the InfluxDB
for org_deviceStatuses in list_org_deviceStatuses:
  fields_deviceStatuses = influxdbApis.create_fields_deviceStatuses(org=org_deviceStatuses[0], deviceStatuses=org_deviceStatuses[1])
  influxdbApis.write_influxdb(measurement="deviceStatuses", tag={"deviceStatuses"}, fields=fields_deviceStatuses)

# Write alerts data to the InfluxDB
for org_network_alerts in list_org_network_alerts:
  alerts = org_network_alerts[2]
  for alert in alerts:
    fields_alert = influxdbApis.create_fields_alert(org=org_network_alerts[0], network=org_network_alerts[1], alert=org_network_alerts[2])
    influxdbApis.write_influxdb(measurement="alerts", tag={"alerts"}, fields=fields_alert)