#!/bin/bash

echo "=== Probando memory_check.py ==="
echo ""

echo "1. Check normal (umbrales por defecto)"
python3 ~/sre/scripts/memory_check.py
echo "Exit code: $?"
echo ""

echo "2. Check con umbrales altos (forzar warning):"
WARNING=95 CRITICAL=90 python3 ~/sre/scripts/memory_check.py
echo "Exit code: $?"


