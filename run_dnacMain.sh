#!/bin/bash

# Path to your script
DNAC_PATH="/home/copmock/COPOC/dnac-esxi-prod/dnacMain.py"

# Path to your python3
PYTHON_PATH="/usr/bin/python3"

while true
do
    $PYTHON_PATH $DNAC_PATH

    # Update the environment variables
    source change_env.sh
    # Get sleep time from environment variable
    Var_SLEEP_TIME="${SLEEP_TIME:-300}"
    echo "SLEEP_TIME: $Var_SLEEP_TIME"
    sleep $Var_SLEEP_TIME
done