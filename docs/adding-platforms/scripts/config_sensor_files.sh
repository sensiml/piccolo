#!/bin/bash

inputs=$1
# Other sensor configurations can be added, these can be removed as well.

sensor_plugin_name=`$1 | jq -r '.["sensor_plugin_name"]'`
sample_rate=`$1 | jq -r '.["sample_rate"]'`
accel_range=`$1 | jq -r '.["accelerometer_sensor_range"]'`
gyro_range=`$1 | jq -r '.["gyroscope_sensor_range"]'`

# switch to recognition mode (add to mqtt app as well for backwards compatibility. The app config is for SDK versions > 1.8)
if [[ ! -z $sample_rate ]]; then
echo "Changing Sample rate"
echo "$SML_APP_CONFIG_FILE"
sed -i "s/#define SNSR_SAMPLE_RATE\b.*/#define SNSR_SAMPLE_RATE $sample_rate/" $SML_APP_CONFIG_FILE
fi

if [[ ! -z $accel_range ]]; then
echo "Changing Accel Range"
sed -i "s/#define SNSR_ACCEL_RANGE\b.*/#define SNSR_ACCEL_RANGE $accel_range/" $SML_APP_CONFIG_FILE
fi
if [[ ! -z $gyro_range ]]; then
echo "Changing Gyro Range"
sed -i "s/#define SNSR_GYRO_RANGE\b.*/#define SNSR_GYRO_RANGE $gyro_range/" $SML_APP_CONFIG_FILE
fi
