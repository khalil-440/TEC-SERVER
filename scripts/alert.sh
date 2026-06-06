CPU=$(mysql -u tecadmin -ptec123 monitoring_db -N -e "
SELECT cpu_usage
FROM monitoring_logs
ORDER BY id DESC
LIMIT 1;
")

RAM=$(mysql -u tecadmin -ptec123 monitoring_db -N -e "
SELECT ram_usage
FROM monitoring_logs
ORDER BY id DESC
LIMIT 1;
")

DISK=$(mysql -u tecadmin -ptec123 monitoring_db -N -e "
SELECT disk_usage
FROM monitoring_logs
ORDER BY id DESC
LIMIT 1;
")

echo "CPU=$CPU"
echo "RAM=$RAM"
echo "DISK=$DISK"

if (( $(echo "$CPU > 80" | bc -l) ))
then

mysql -u tecadmin -ptec123 monitoring_db -e "
INSERT INTO alerts(type,value,status)
VALUES('CPU','$CPU','WARNING');
"

fi
