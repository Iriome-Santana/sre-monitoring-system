#!/usr/bin/env python3
"""
Script de monitoreo de uso de CPU.
Autor: Iriome
Fecha: 02/02/2026
"""

import subprocess
import sys
import logging
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

WARNING_THRESHOLD = int(os.environ.get("WARNING", "20"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "10"))

STATE_DIR= "/tmp"
CHECK_NAME= "cpu"

def load_last_state(check_name: str) -> str:
    """
    Lee el último estado guardado.
    Si no existe, asumimos OK.
    """
    try:
        with open(f"{STATE_DIR}/{check_name}.state") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "OK"


def save_state(check_name: str, state: str) -> None:
    """
    Guarda el estado actual para el siguiente run.
    """
    with open(f"{STATE_DIR}/{check_name}.state", "w") as f:
        f.write(state)

if WARNING_THRESHOLD <= CRITICAL_THRESHOLD:
    logging.error("WARNING debe ser mayor que CRITICAL")
    sys.exit(2)
    
logging.info(
    f"Chequeando CPU "
    f"(warning={WARNING_THRESHOLD}% idle, "
    f"critical={CRITICAL_THRESHOLD}% idle)"
)

result = subprocess.run(
    ["top", "-bn1"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    logging.error("Fallo al ejecutar top")
    logging.error(result.stderr.strip())
    sys.exit(2)
    
cpu_line = None
for line in result.stdout.splitlines():
    if "Cpu(s)" in line:
        cpu_line=line
        break
    
if cpu_line is None:
    logging.error("No se encontró información de CPU")
    sys.exit(2)
    

match = re.search(r'(\d+\.?\d*)\s*id', cpu_line)

if not match:
    logging.error("No se pudo extraer el valor idle")
    logging.error(f"Línea parseada: {cpu_line}")
    sys.exit(2)
    
try:
    idle_percent = float(match.group(1))
except ValueError:
    logging.error("Error al convertir idle a número")
    sys.exit(2)
    
idle_percent = round(idle_percent, 1)

usage_percent = round(100 - idle_percent, 1)

if idle_percent >= WARNING_THRESHOLD:
    current_state= "OK"
    
elif idle_percent >= CRITICAL_THRESHOLD:
    current_state= "WARNING"
    
else:
    current_state= "CRITICAL"
    
last_state= load_last_state(CHECK_NAME)

logging.info(f"Estado anterior: {last_state}")
logging.info(f"Estado actual: {current_state}")
logging.info(f"CPU disponible: {idle_percent}")

should_alert = last_state != current_state and current_state != "OK"
should_recovery = last_state != "OK" and current_state == "OK"

if should_alert:
    send_alert(
        title=f"{current_state}: Uso de CPU",
        message=f"CPU disponible : {idle_percent}",
        level=current_state
    )

if should_recovery:
    send_alert(
        title="RECOVERY: Disco OK",
        message=f"CPU disponible normalizada: {idle_percent}",
        level="OK"
    )
    
save_state(CHECK_NAME, current_state)

if current_state == "OK":
    sys.exit(0)
elif current_state == "WARNING":
    sys.exit(1)
else:
    sys.exit(2)