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

# =========================
# PROCESS MONITORING
# =========================

mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway -e "
TRUNCATE TABLE processes;
"

ps -eo pid,user,ni,%cpu,%mem,comm --no-headers |
while read pid user nice cpu mem command
do

    [ "$nice" = "-" ] && nice=0

    mysql \
    -h zephyr.proxy.rlwy.net \
    -u root \
    -p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
    --port 34161 \
    railway -e "
    INSERT INTO processes
    (pid,user,cpu,mem,nice,command)
    VALUES
    ($pid,'$user',$cpu,$mem,$nice,'$command');
    " 2>> /tmp/process_error.log

done


# =========================
# KILL REQUEST HANDLER
# =========================

mysql \
-h zephyr.proxy.rlwy.net \
-u root \
-p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
--port 34161 \
railway -N -e "
SELECT id,pid
FROM kill_requests
WHERE status='pending';
" |
while read id pid
do

    if kill -9 "$pid" 2>/dev/null
    then

        mysql \
        -h zephyr.proxy.rlwy.net \
        -u root \
        -p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
        --port 34161 \
        railway -e "
        UPDATE kill_requests
        SET status='done'
        WHERE id=$id;
        "

    else

        mysql \
        -h zephyr.proxy.rlwy.net \
        -u root \
        -p'lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR' \
        --port 34161 \
        railway -e "
        UPDATE kill_requests
        SET status='failed'
        WHERE id=$id;
        "

    fi

done

echo "$(date)"
sleep 1

done
