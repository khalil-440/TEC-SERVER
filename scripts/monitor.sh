#!/bin/bash

while true
do

CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
RAM=$(free | awk '/Mem:/ {printf("%.2f"), $3/$2 * 100}')
DISK=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
SWAP=$(free | awk '/Swap:/ {if($2==0) print 0; else printf("%.2f"), $3/$2 * 100}')
USERS=$(who | wc -l)

mysql -u tecadmin -ptec123 monitoring_db -e "
INSERT INTO monitoring_logs
(cpu_usage, ram_usage, disk_usage, swap_usage, active_users)
VALUES
($CPU, $RAM, $DISK, $SWAP, $USERS);
"

sleep 5

done
