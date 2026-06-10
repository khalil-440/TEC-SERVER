#!/bin/bash

while true
do

CPU=$(mpstat 1 1 | awk '/Average/ && $NF ~ /[0-9.]+/ {print 100-$NF}')
RAM=$(free | awk '/Mem:/ {printf("%.2f"), $3/$2 * 100}')
DISK=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
SWAP=$(free | awk '/Swap:/ {if($2==0) print 0; else printf("%.2f"), $3/$2 * 100}')
USERS=$(who | wc -l)

mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway -e "
INSERT INTO monitoring_logs
(cpu_usage, ram_usage, disk_usage, swap_usage, active_users)
VALUES
($CPU, $RAM, $DISK, $SWAP, $USERS);
"

sleep 1

done
