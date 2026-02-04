# Arquitectura del Sistema

## Diagrama de Flujo
```
┌─────────────────────────────────────────────────────────────┐
│                    CRON SCHEDULER                            │
│                  (Cada 5 minutos)                            │
└────────────────┬────────────┬────────────┬──────────────────┘
                 │            │            │
                 ▼            ▼            ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │disk_check  │ │memory_check│ │ cpu_check  │
        │   .py      │ │   .py      │ │   .py      │
        └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌────────────────┐
                    │  notifier.py   │
                    │  (send_alert)  │
                    └────────┬───────┘
                             │
                    ┌────────▼────────┐
                    │ Discord Webhook │
                    │  (POST request) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Discord Server │
                    │ #alertas-sistema│
                    └─────────────────┘
```

## Componentes

### 1. Scripts de Monitoreo

**disk_check.py**
- Lee uso de disco con `df -h`
- Compara contra thresholds
- Detecta cambios de estado
- Alerta si necesario

**memory_check.py**
- Lee memoria con `free -m`
- Calcula % disponible
- State management
- Alertas de memoria baja

**cpu_check.py**
- Lee CPU con `top -bn1`
- Extrae % idle con regex
- Detecta sobrecarga
- Alerta en cambios

### 2. Sistema de Notificaciones

**notifier.py**
- Clase `Notifier` con métodos:
  - `send_discord()` - Envía embed a Discord
  - `send_alert()` - Wrapper público
- Función helper `send_alert()` para uso rápido
- Colores según severidad (azul, amarillo, rojo)
- Timestamps UTC

### 3. State Management

Almacena último estado en `/tmp/<check>.state`:
```
/tmp/
├── disk.state     → "OK" | "WARNING" | "CRITICAL"
├── memory.state   → "OK" | "WARNING" | "CRITICAL"
└── cpu.state      → "OK" | "WARNING" | "CRITICAL"
```

**Lógica de alertas:**
- Alerta: `last_state != current_state AND current_state != "OK"`
- Recovery: `last_state != "OK" AND current_state == "OK"`

### 4. Logging

Todos los scripts logean a:
- `~/sre/logs/disk_check.log`
- `~/sre/logs/memory_check.log`
- `~/sre/logs/cpu_check.log`

Formato: `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`

## Decisiones de Diseño

### ¿Por qué Python + Bash?

- **Python**: Para lógica compleja (parsing, HTTP, regex)
- **Bash**: Para glue code y scripts de utilidad

### ¿Por qué state files en /tmp?

- Rápido (en memoria)
- No requiere DB
- Auto-limpieza en reboot (reset limpio)

### ¿Por qué Discord?

- Gratis
- Webhooks simples (un POST)
- Notificaciones móviles incluidas
- Fácil de reemplazar con Slack/PagerDuty después

### ¿Por qué cron en lugar de systemd timers?

- Más simple para empezar
- Familiar para la mayoría
- Funciona en cualquier Linux

**Mejora futura:** Migrar a systemd timers para mejor logging y control.

## Flujo de una Alerta
```
1. Cron ejecuta disk_check.py
2. Script lee uso actual: 85%
3. Lee last_state: "OK"
4. Determina current_state: "WARNING" (85% > 80%)
5. Detecta cambio: "OK" → "WARNING"
6. Llama send_alert(title, message, level="WARNING")
7. notifier.py construye embed JSON
8. POST a Discord webhook
9. Discord muestra alerta amarilla ⚠️
10. Guarda state: "WARNING" en /tmp/disk.state
11. Exit code 1 (WARNING)
```

## Escalabilidad

### Para 1 servidor: ✅ Perfecto así
### Para 10 servidores: 
- Centralizar logs en ELK o Loki
- Dashboard con Grafana

### Para 100+ servidores:
- Prometheus + Grafana
- Alertmanager para routing
- PagerDuty para escalamiento