#!/usr/bin/env python3
"""
Script de monitoreo de uso de disco.
Autor: Iriome
Fecha: 02/02/2026
"""

import subprocess
import sys
import os
import logging
from base_check import *


DISK_PATH = os.environ.get("DISK_PATH", "/")
WARNING_THRESHOLD = int(os.environ.get("WARNING", "80"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "90"))

def main():
    # Crear instancia del check
    check = BaseCheck("disk")
    
    # Validar thresholds
    check.validate_thresholds(WARNING_THRESHOLD, CRITICAL_THRESHOLD)
    
    # Log inicio
    logging.info(
        f"Chequeando disco en '{DISK_PATH}' "
        f"(warning={WARNING_THRESHOLD}%, critical={CRITICAL_THRESHOLD}%)"
    )
    
    # Ejecutar comando df
    result = subprocess.run(
        ["df", "-h", DISK_PATH],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logging.error("Fallo al ejecutar df")
        logging.error(result.stderr.strip())
        sys.exit(2)
    
    # Parsear output
    lines = result.stdout.splitlines()
    
    if len(lines) < 2:
        logging.error("Salida inesperada de df")
        sys.exit(2)
    
    parts = lines[1].split()
    
    if len(parts) < 5:
        logging.error("No se pudo extraer Use%")
        sys.exit(2)
    
    # Extraer porcentaje
    use_percent_str = parts[4]
    
    try:
        use_percent = int(use_percent_str.strip('%'))
    except ValueError:
        logging.error(f"Valor inválido de uso de disco: {use_percent_str}")
        sys.exit(2)
    
    # Determinar estado
    if use_percent < WARNING_THRESHOLD:
        current_state = "OK"
    elif use_percent < CRITICAL_THRESHOLD:
        current_state = "WARNING"
    else:
        current_state = "CRITICAL"
    
    # Manejar estado y salir
    exit_code = check.handle_state_change(
        current_state,
        "Uso de disco",
        f"{use_percent}% en {DISK_PATH}"
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()