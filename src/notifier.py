#!/usr/bin/env python3
"""
Módulo de notificaciones para scripts de monitoreo.
Soporta múltiples canales: Discord, Slack, archivos.
"""

import requests
import json
import os
from datetime import datetime

class Notifier:
    """
    Clase para enviar notificaciones a diferentes canales.
    """
    
    def __init__(self):
        """
        Inicializa el notificador leyendo configuración.
        """
        # Leer webhook de Discord desde variable de entorno
        self.discord_webhook = os.environ.get("DISCORD_WEBHOOK", "")
        
        # Flag para habilitar/deshabilitar notificaciones
        self.enabled = os.environ.get("NOTIFICATIONS_ENABLED", "true").lower() == "true"
    
    def send_discord(self, title, message, level="INFO"):
        """
        Envía notificación a Discord.
        
        Args:
            title (str): Título de la alerta
            message (str): Mensaje detallado
            level (str): Nivel de severidad (INFO, WARNING, CRITICAL)
        """
        # Si no está habilitado o no hay webhook, no hacer nada
        if not self.enabled or not self.discord_webhook:
            print("WARNING: DISCORD_WEBHOOK no definido, no se enviará alerta")
            return False
        
        # Colores según severidad (en hexadecimal)
        colors = {
            "INFO": 3447003,      # Azul
            "OK": 3066993,        # Verde
            "WARNING": 16776960,  # Amarillo
            "CRITICAL": 15158332  # Rojo
        }
        
        # Emojis según severidad
        emojis = {
            "INFO": "ℹ️",
            "OK": "✅",
            "WARNING": "⚠️",
            "CRITICAL": "🔥"
        }
        
        # Construir el mensaje para Discord (formato embed)
        embed = {
            "title": f"{emojis.get(level, '📊')} {title}",
            "description": message,
            "color": colors.get(level, 3447003),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": f"Monitor SRE | {level}"
            }
        }
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            # Enviar POST request al webhook
            response = requests.post(
                self.discord_webhook,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Verificar si fue exitoso
            if response.status_code == 204:
                return True
            else:
                print(f"Error al enviar a Discord: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Excepción al enviar a Discord: {e}")
            return False
    
    def send_alert(self, title, message, level="INFO"):
        """
        Envía alerta a todos los canales configurados.
        
        Args:
            title (str): Título de la alerta
            message (str): Mensaje detallado
            level (str): Nivel de severidad
        """
        if not self.enabled:
            return
        
        # Enviar a Discord
        self.send_discord(title, message, level)
        
        # Aquí podrías añadir más canales en el futuro:
        # self.send_slack(title, message, level)
        # self.send_email(title, message, level)

# Función helper para uso rápido
def send_alert(title, message, level="INFO"):
    """
    Función de conveniencia para enviar alertas rápidamente.
    """
    notifier = Notifier()
    notifier.send_alert(title, message, level)