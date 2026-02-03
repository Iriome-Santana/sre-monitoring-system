#!/usr/bin/env python3

"""Script para monitorear el uso y las fugas de memoria de la RAM.
Autor: Iriome
Fecha: 03/02/2026
"""

import subprocess
import logging
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

WARNING_THRESHOLD = int(os.environ.get("WARNING", "20"))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL", "10"))

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
    logging.info(
        f"OK - Memoria disponible: {available_percent}%"
        f"({available_percent}MB de {total_mb}%)"
    )
    sys.exit(0)
    
elif available_percent >= CRITICAL_THRESHOLD:
    logging.warning(
        f"WARNING - Memoria disponible: {available_percent}% "
        f"({available_mb}MB de {total_mb}MB)"
    )
    sys.exit(1)
    
else:
    logging.error(
        f"CRITICAL - Memoria disponible: {available_percent}% "
        f"({available_mb}MB de {total_mb}MB)"
    )
    sys.exit(2)
    

    

