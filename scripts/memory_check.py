#!/usr/bin/env python3

"""Script para monitorear el uso y las fugas de memoria de la RAM.
Autor: Iriome
Fecha: 03/02/2026
"""

import subprocess
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

WARNING_THRESHOLD = int(os.environ.get("WARNING", "20"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "10"))

STATE_DIR = "/tmp"
CHECK_NAME= "memory"

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
    logging.error("WARNING debe ser mayor que critical (Son % disponible)")
    sys.exit(2)

logging.info(
    f"Chequeando memoria "
    f"(warning={WARNING_THRESHOLD}% disponible, "
    f"critical={CRITICAL_THRESHOLD}% disponible)"
)

result= subprocess.run(
    ["free", "-m"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    logging.error("Fallo al ejecutar free (el comando)")
    logging.error(result.stderr.strip())
    sys.exit(2)
    
lines = result.stdout.splitlines()

if len(lines) < 2:
    logging.error("Salida inesperada de free")
    sys.exit(2)
    
mem_line = lines[1].split()

if len(mem_line) < 7:
    logging.error("No se puedo parsear la salida")
    sys.exit(2)
    
try:
    total_mb = int(mem_line[1])
    available_mb = int(mem_line[6])
except (ValueError, IndexError):
    logging.error("Error en convertir los valores de la memoria")
    sys.exit(2)
    
available_percent = (available_mb / total_mb) * 100
available_percent = round(available_percent, 1)

if available_percent >= WARNING_THRESHOLD:
    current_state= "OK"
    
elif available_percent >= CRITICAL_THRESHOLD:
    current_state= "WARNING"
    
else:
    current_state= "CRITICAL"
    
last_state= load_last_state(CHECK_NAME)

logging.info(f"Estado anterior: {last_state}")
logging.info(f"Estado actual: {current_state}")
logging.info(f"Uso de memoria: {available_percent}%")

should_alert = last_state != current_state and current_state != "OK"
should_recovery = last_state != "OK" and current_state == "OK"

if should_alert:
    send_alert(
        title=f"{current_state}: Uso de memoria",
        message=f"Memoria disponible : {available_percent}%",
        level=current_state
    )

if should_recovery:
    send_alert(
        title="RECOVERY: Disco OK",
        message=f"Memoria disponible normalizado: {available_percent}%",
        level="OK"
    )
    
save_state(CHECK_NAME, current_state)

if current_state == "OK":
    sys.exit(0)
elif current_state == "WARNING":
    sys.exit(1)
else:
    sys.exit(2)
    

    

