#!/bin/bash

check_return_code() {
        #Check the return code of most recent calls.
        rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
}

inputs=$1

sensor_plugin_name=`$1 | jq -r '.["sensor_plugin_name"]'`
sample_rate=`$1 | jq -r '.["sample_rate"]'`

# switch to recognition mode (add to mqtt app as well for backwards compatibility. The app config is for SDK versions > 1.8)
if [[ ! -z $SML_APP_CONFIG_FILE ]]; then
  if [[ $sample_rate -ne null ]]; then
    echo "Changing Sample rate"
    echo "$SML_APP_CONFIG_FILE"
    sed -i "s/#define ODR_IMU\b.*/#define ODR_IMU $sample_rate/" $SML_APP_CONFIG_FILE
    check_return_code
  fi
  
fi
