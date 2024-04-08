def extract_test_data(tests):
    http_server_test_ids = []
    cpoc_test_ids = []
    for test in tests:
        if test["enabled"]:
            if test["type"] == "http-server":
                if "CPOC" in test["testName"]:
                    cpoc_test_ids.append(test["testId"])
                elif test["liveShare"]:
                    http_server_test_ids.append(test["testId"])
    return http_server_test_ids, cpoc_test_ids