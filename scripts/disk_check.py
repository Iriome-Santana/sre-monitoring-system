#!/usr/bin/env python3
"""
Script de monitoreo de uso de disco.
Autor: Iriome
Fecha: 02/02/2026
"""
    
import subprocess
import sys
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Leer configuración
DISK_PATH = os.environ.get("DISK_PATH", "/")
WARNING_THRESHOLD = os.environ.get("WARNING", "80")
CRITICAL_THRESHOLD = os.environ.get("CRITICAL", "90")

STATE_DIR = "/tmp"
CHECK_NAME = "disk"

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

try:
    warning_threshold = int(WARNING_THRESHOLD)
    critical_threshold = int(CRITICAL_THRESHOLD)
except ValueError:
    logging.error("Los umbrales deben ser números enteros")
    sys.exit(2)

if warning_threshold >= critical_threshold:
    logging.error("WARNING debe ser menor que CRITICAL")
    sys.exit(2)

logging.info(
    f"Chequeando disco en '{DISK_PATH}' "
    f"(warning={warning_threshold}%, critical={critical_threshold}%)"
)

result = subprocess.run(
    ["df", "-h", DISK_PATH],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    logging.error("Fallo al ejecutar df")
    logging.error(result.stderr.strip())
    sys.exit(2)

lines = result.stdout.splitlines()

if len(lines) < 2:
    logging.error("Salida inesperada de df")
    sys.exit(2)

parts = lines[1].split()

if len(parts) < 5:
    logging.error("No se pudo extraer Use%")
    sys.exit(2)

use_percent_str = parts[4]

try:
    use_percent = int(use_percent_str.strip('%'))
except ValueError:
    logging.error(f"Valor inválido de uso de disco: {use_percent_str}")
    sys.exit(2)

if use_percent < warning_threshold:
    current_state = "OK"
elif use_percent < critical_threshold:
    current_state = "WARNING"
else:
    current_state = "CRITICAL"
    
last_state = load_last_state(CHECK_NAME)

logging.info(f"Estado anterior: {last_state}")
logging.info(f"Estado actual: {current_state}")
logging.info(f"Uso de disco: {use_percent}%")
    
should_alert = last_state != current_state and current_state != "OK"
should_recovery = last_state != "OK" and current_state == "OK"

if should_alert:
    send_alert(
        title=f"{current_state}: Uso de disco",
        message=f"Uso de disco en {DISK_PATH}: {use_percent}%",
        level=current_state
    )

if should_recovery:
    send_alert(
        title="RECOVERY: Disco OK",
        message=f"Uso de disco normalizado: {use_percent}%",
        level="OK"
    )
    
save_state(CHECK_NAME, current_state)

if current_state == "OK":
    sys.exit(0)
elif current_state == "WARNING":
    sys.exit(1)
else:
    sys.exit(2)


