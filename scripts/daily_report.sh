#!/bin/bash

LOG_FILE=$HOME/sre/logs/disk_check.log
REPORT_FILE=$HOME/sre/logs/daily_report_$(date +%Y-%m-%d).txt

echo "=== Reporte de Disco - $(date +%Y-%m-%d) ====" > $REPORT_FILE

echo "" >> $REPORT_FILE
echo "Checks Totales:" >> $REPORT_FILE
grep -c "Chequeando disco" $LOG_FILE >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "OK detectados" >> $REPORT_FILE
grep -c "OK" $LOG_FILE >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "Warning detectados" >> $REPORT_FILE
grep -c "WARNING" $LOG_FILE >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "Critical detectados" >> $REPORT_FILE
grep -c "CRITICAL" $LOG_FILE >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "Última verificación" >> $REPORT_FILE
tail -n 2 $LOG_FILE >> $REPORT_FILE


cat $REPORT_FILE
