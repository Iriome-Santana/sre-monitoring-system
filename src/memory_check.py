#!/usr/bin/env python3

"""Script para monitorear el uso y las fugas de memoria de la RAM.
Autor: Iriome
Fecha: 03/02/2026
"""

import subprocess
import sys
import os
import logging

from base_check import BaseCheck

WARNING_THRESHOLD = int(os.environ.get("WARNING", "20"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "10"))


def main():
    
    check = BaseCheck("memory")
    
    check.validate_thresholds(WARNING_THRESHOLD, CRITICAL_THRESHOLD, inverted=True)

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
    
    available_percent = round((available_mb / total_mb) * 100, 1)

    if available_percent >= WARNING_THRESHOLD:
        current_state= "OK"
    
    elif available_percent >= CRITICAL_THRESHOLD:
        current_state= "WARNING"
    
    else:
        current_state= "CRITICAL"

    exit_code = check.handle_state_change(
        current_state,
        "Memoria disponible",
        f"{available_percent}% ({available_mb}MB de {total_mb}MB)"

    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
    

