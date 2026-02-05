#!/bin/bash

LOG_DIR="$HOME/sre-monitoring-suite/logs"
DISK_LOG="$LOG_DIR/disk_check.log"
MEMORY_LOG="$LOG_DIR/memory_check.log"
REPORT_FILE="$LOG_DIR/daily_report_$(date +%Y-%m-%d).txt"


echo "========================================" > $REPORT_FILE
echo "    REPORTE DIARIO DE MONITOREO" >> $REPORT_FILE
echo "    $(date '+%Y-%m-%d %H:%M:%S')" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE


# SECCIÓN: DISCO


echo "--- MONITOREO DE DISCO ---" >> $REPORT_FILE
echo "" >> $REPORT_FILE

if [ -f "$DISK_LOG" ]; then
    echo "Checks totales: $(grep -c 'Chequeando disco' $DISK_LOG)" >> $REPORT_FILE
    echo "OK: $(grep -c 'Estado actual: OK' $DISK_LOG)" >> $REPORT_FILE
    echo "Warnings: $(grep -c 'Estado actual: WARNING' $DISK_LOG)" >> $REPORT_FILE
    echo "Críticos: $(grep -c 'Estado actual: CRITICAL' $DISK_LOG)" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    echo "Última verificación:" >> $REPORT_FILE
    tail -n 3 $DISK_LOG >> $REPORT_FILE
else
    echo "No hay datos de disco disponibles" >> $REPORT_FILE
fi

echo "" >> $REPORT_FILE
echo "" >> $REPORT_FILE


# SECCIÓN: MEMORIA


echo "--- MONITOREO DE MEMORIA ---" >> $REPORT_FILE
echo "" >> $REPORT_FILE

if [ -f "$MEMORY_LOG" ]; then
    echo "Checks totales: $(grep -c 'Chequeando memoria' $MEMORY_LOG)" >> $REPORT_FILE
    echo "OK: $(grep -c 'Estado actual: OK' $MEMORY_LOG)" >> $REPORT_FILE
    echo "Warnings: $(grep -c 'Estado actual: WARNING' $MEMORY_LOG)" >> $REPORT_FILE
    echo "Críticos: $(grep -c 'Estado actual: CRITICAL' $MEMORY_LOG)" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    echo "Última verificación:" >> $REPORT_FILE
    tail -n 3 $MEMORY_LOG >> $REPORT_FILE
else
    echo "No hay datos de memoria disponibles" >> $REPORT_FILE
fi

echo "" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# ==========================================
# SECCIÓN: CPU
# ==========================================

echo "--- MONITOREO DE CPU ---" >> $REPORT_FILE
echo "" >> $REPORT_FILE

CPU_LOG="$LOG_DIR/cpu_check.log"

if [ -f "$CPU_LOG" ]; then
    echo "Checks totales: $(grep -c 'Chequeando CPU' $CPU_LOG)" >> $REPORT_FILE
    echo "OK: $(grep -c 'Estado actual: OK' $CPU_LOG)" >> $REPORT_FILE
    echo "Warnings: $(grep -c 'Estado actual: WARNING' $CPU_LOG)" >> $REPORT_FILE
    echo "Críticos: $(grep -c 'Estado actual: CRITICAL' $CPU_LOG)" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    echo "Última verificación:" >> $REPORT_FILE
    tail -n 3 $CPU_LOG >> $REPORT_FILE
else
    echo "No hay datos de CPU disponibles" >> $REPORT_FILE
fi

echo "" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE

cat $REPORT_FILE
