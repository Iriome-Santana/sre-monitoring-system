#!/usr/bin/env python3
"""
Script de monitoreo de CPU.
Autor: Iriome
Fecha: 02/02/2026
"""

import subprocess
import sys
import os
import re
import logging

from base_check import BaseCheck

# Configuración
WARNING_THRESHOLD = int(os.environ.get("WARNING", "20"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "10"))

def main():
    check = BaseCheck("cpu")
    
    # Validar (invertido: más idle = mejor)
    check.validate_thresholds(WARNING_THRESHOLD, CRITICAL_THRESHOLD, inverted=True)
    
    logging.info(
        f"Chequeando CPU "
        f"(warning={WARNING_THRESHOLD}% idle, "
        f"critical={CRITICAL_THRESHOLD}% idle)"
    )
    
    # Ejecutar top
    result = subprocess.run(
        ["top", "-bn1"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logging.error("Fallo al ejecutar top")
        logging.error(result.stderr.strip())
        sys.exit(2)
    
    # Buscar línea de CPU
    cpu_line = None
    for line in result.stdout.splitlines():
        if "Cpu(s)" in line:
            cpu_line = line
            break
    
    if cpu_line is None:
        logging.error("No se encontró información de CPU")
        sys.exit(2)
    
    # Extraer idle con regex
    match = re.search(r'(\d+\.?\d*)\s*id', cpu_line)
    
    if not match:
        logging.error("No se pudo extraer el valor idle")
        logging.error(f"Línea parseada: {cpu_line}")
        sys.exit(2)
    
    try:
        idle_percent = round(float(match.group(1)), 1)
    except ValueError:
        logging.error("Error al convertir idle a número")
        sys.exit(2)
    
    usage_percent = round(100 - idle_percent, 1)
    
    # Determinar estado
    if idle_percent >= WARNING_THRESHOLD:
        current_state = "OK"
    elif idle_percent >= CRITICAL_THRESHOLD:
        current_state = "WARNING"
    else:
        current_state = "CRITICAL"
    
    # Manejar estado
    exit_code = check.handle_state_change(
        current_state,
        "CPU idle",
        f"{idle_percent}% idle ({usage_percent}% uso)"
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()