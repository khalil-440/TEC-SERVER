#!/bin/bash

while true
do

CPU=$(mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway \
-N -e "
SELECT cpu_usage
FROM monitoring_logs
ORDER BY id DESC
LIMIT 1;
")

RAM=$(mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway \
-N -e "
SELECT ram_usage
FROM monitoring_logs
ORDER BY id DESC
LIMIT 1;
")

DISK=$(mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway \
-N -e "
SELECT disk_usage
FROM monitoring_logs
ORDER BY id DESC
LIMIT 1;
")

echo "CPU=$CPU"
echo "RAM=$RAM"
echo "DISK=$DISK"

if (( $(echo "$CPU > 0" | bc -l) ))
then

mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway -e "
INSERT INTO alerts(type,value,status)
VALUES('CPU','$CPU','WARNING');
"

mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway -e "
INSERT INTO activity_logs(action,admin)
VALUES(
'EMAIL SENT : CPU usage reached $CPU%',
'SYSTEM'
);
"

fi

sleep 1

done
