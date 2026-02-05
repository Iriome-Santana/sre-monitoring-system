#!/usr/bin/env python3
"""
Módulo base para scripts de monitoreo.
Contiene lógica compartida: logging, state management, alertas.
"""

import logging
import sys
import os
from typing import Literal

# Añadir directorio al path para importar notifier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notifier import send_alert

# Tipos
State = Literal["OK", "WARNING", "CRITICAL"]

STATE_DIR = os.environ.get("STATE_DIR", "/tmp")



class BaseCheck:
    """
    Clase base para todos los checks de monitoreo.
    Maneja state management, logging y alertas.
    """
    
    def __init__(self, check_name: str):
        """
        Inicializa el check.
        
        Args:
            check_name: Nombre del check (disk, memory, cpu, etc.)
        """
        self.check_name = check_name
        self.state_file = f"{STATE_DIR}/{check_name}.state"
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def load_last_state(self) -> State:
        """
        Lee el último estado guardado.
        Si no existe, asume OK.
        """
        try:
            with open(self.state_file) as f:
                state = f.read().strip()
                # Validar que sea un estado válido
                if state in ("OK", "WARNING", "CRITICAL"):
                    return state
                return "OK"
        except FileNotFoundError:
            return "OK"
    
    def save_state(self, state: State) -> None:
        """
        Guarda el estado actual.
        """
        with open(self.state_file, "w") as f:
            f.write(state)
    
    def handle_state_change(
        self, 
        current_state: State, 
        metric_name: str, 
        metric_value: str
    ) -> int:
        """
        Maneja cambios de estado y envía alertas.
        
        Args:
            current_state: Estado actual (OK/WARNING/CRITICAL)
            metric_name: Nombre de la métrica (ej: "Uso de disco")
            metric_value: Valor de la métrica (ej: "85%")
        
        Returns:
            Exit code apropiado (0, 1, o 2)
        """
        last_state = self.load_last_state()
        
        logging.info(f"Estado anterior: {last_state}")
        logging.info(f"Estado actual: {current_state}")
        logging.info(f"{metric_name}: {metric_value}")
        
        # Detectar si debe alertar
        should_alert = (
            last_state != current_state and 
            current_state != "OK"
        )
        
        # Detectar recovery
        should_recovery = (
            last_state != "OK" and 
            current_state == "OK"
        )
        
        # Enviar alertas
        if should_alert:
            logging.info("DEBUG: entrando en send_alert (ALERTA)")
            send_alert(
                title=f"{current_state}: {metric_name}",
                message=f"{metric_name}: {metric_value}",
                level=current_state
            )
        
        if should_recovery:
            logging.info("DEBUG: entrando en send_alert (RECOVERY)")
            send_alert(
                title=f"RECOVERY: {self.check_name.title()} OK",
                message=f"{metric_name} normalizado: {metric_value}",
                level="OK"
            )
        
        # Guardar estado
        self.save_state(current_state)
        
        # Retornar exit code apropiado
        if current_state == "OK":
            return 0
        elif current_state == "WARNING":
            return 1
        else:  # CRITICAL
            return 2
    
    def validate_thresholds(
        self, 
        warning: int, 
        critical: int,
        inverted: bool = False
    ) -> None:
        """
        Valida que los thresholds sean correctos.
        
        Args:
            warning: Threshold de warning
            critical: Threshold de critical
            inverted: Si True, warning debe ser > critical (ej: memoria)
        """
        if inverted:
            if warning <= critical:
                logging.error(
                    f"WARNING ({warning}) debe ser mayor que "
                    f"CRITICAL ({critical}) para este check"
                )
                sys.exit(2)
        else:
            if warning >= critical:
                logging.error(
                    f"WARNING ({warning}) debe ser menor que "
                    f"CRITICAL ({critical}) para este check"
                )
                sys.exit(2)