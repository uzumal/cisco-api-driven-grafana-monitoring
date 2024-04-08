from teApis import ThousandEyesAPI
from data_processing import extract_test_data
import json
from datetime import datetime
from dotenv import load_dotenv
from influxdb import InfluxDBClient

# Connect to the database
dbclient = InfluxDBClient(host='localhost', port=8086, database='TE', timeout=30)

# .envファイルを読み込む
load_dotenv()

TOKEN = os.getenv("TE_TOKEN")

def store_test_results_in_influxdb(test_results, test_name, is_cpoc):
    json_body = []
    for result in test_results:
        agent_name = result['agent']['agentName']
        timestamp = datetime.strptime(result['date'], '%Y-%m-%dT%H:%M:%SZ')
        response_code = result['responseCode']
        
        if is_cpoc:
            total_time = result['totalTime']
            data_point = {
                "measurement": "http_server_test_results_cpoc",
                "tags": {
                    "test_name": test_name,
                    "agent_name": agent_name
                },
                "time": timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "response_code": response_code,
                    "total_time": total_time
                }
            }
        else:
            num_redirects = result['numRedirects']
            response_time = result.get('responseTime', 0)  # Use get() method with default value 0
            data_point = {
                "measurement": f"http_server_test_{test_name}",
                "tags": {
                    "agent_name": agent_name
                },
                "time": timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "response_code": response_code,
                    "num_redirects": num_redirects,
                    "response_time": response_time
                }
            }
        
        json_body.append(data_point)
    
    print(f"Writing {len(json_body)} data points to InfluxDB...")
    # print(json.dumps(json_body, indent=4))
    dbclient.write_points(json_body)

def main():
    base_url = "https://api.thousandeyes.com/v7"
    bearer_token = TOKEN

    api = ThousandEyesAPI(base_url, bearer_token)
    response_data = api.get_tests()

    tests = response_data["tests"]
    http_server_test_ids, cpoc_test_ids = extract_test_data(tests)

    print(f"CPOC Test IDs: {cpoc_test_ids}")
    print(f"HTTP Server Test IDs: {http_server_test_ids}")

    for test_id in cpoc_test_ids:
        print(f"Processing CPOC Test ID: {test_id}")
        http_server_results = api.get_http_server_test_results(test_id)
        test_name = http_server_results['test']['testName']
        test_results = http_server_results['results']
        store_test_results_in_influxdb(test_results, test_name, is_cpoc=True)

    for test_id in http_server_test_ids:
        print(f"Processing HTTP Server Test ID: {test_id}")
        http_server_results = api.get_http_server_test_results(test_id)
        test_name = http_server_results['test']['testName']
        test_results = http_server_results['results']

        # Microsoft Office 365 Login のテストだけを処理する
        if test_name == "Microsoft Office 365 Login":
            store_test_results_in_influxdb(test_results, test_name, is_cpoc=False)

    dbclient.close()

if __name__ == "__main__":
    main()