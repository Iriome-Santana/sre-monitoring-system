# Design Decisions

Documentación de decisiones arquitectónicas y por qué las tomé.

---

## Decision #1: 3 Scripts Separados vs 1 Script Unificado

**Contexto:** 
Tenía código duplicado (logging, state management) en 3 scripts.

**Opciones consideradas:**

### Opción A: Un solo script `base_check.py --check disk`
**Pros:**
- Menos archivos
- DRY (código compartido en un lugar)

**Contras:**
- Exit codes confusos (¿qué devuelvo si corro `--check all`?)
- Logs mezclados
- Acoplamiento (bug en uno afecta a todos)
- Menos flexible en cron

### Opción B: 3 scripts + módulo base compartido
**Pros:**
- Separation of concerns
- Logs separados (más fácil debuggear)
- Scheduling flexible
- Fácil añadir checks nuevos
- Unix philosophy ("do one thing well")

**Contras:**
- Más archivos

**Decisión:** Opción B

**Razón:** 
En SRE real, prefieres **observabilidad** sobre **compactness**. 
Si `memory_check` falla, quiero saber EXACTAMENTE cuál falló sin parsear logs mezclados. 
Además, puedo ejecutar `disk_check` cada 5 min y `cpu_check` cada 1 min independientemente.

**Influencias:**
- Patrón usado en Datadog agents
- Nagios plugins
- Prometheus exporters

**¿La IA me habría ayudado?**
Me habría dado ambas opciones, pero NO me habría explicado las implicaciones operacionales reales.

---

## Decision #2: State Files en /tmp vs Base de Datos

**Contexto:**
Necesitaba guardar el último estado para evitar alertas duplicadas.

**Opciones:**

### A: SQLite database
**Pros:** 
- Más robusto
- Queries complejas posibles
- Histórico completo

**Contras:**
- Overkill para este caso
- Dependencia extra
- Puede corromperse

### B: Files en /tmp
**Pros:**
- Simple (read/write file)
- No dependencies
- Rápido (en memoria en muchos sistemas)
- Auto-cleanup en reboot

**Contras:**
- Pierde estado en reboot
- No histórico

**Decisión:** Opción B

**Razón:** 
Para este caso de uso (detectar cambios de estado), no necesito histórico. 
Si el servidor reinicia, es BUENO que el estado se resetee a "OK" (clean slate).
YAGNI principle: "You Aren't Gonna Need It" - no añadir complejidad innecesaria.

**Cuándo cambiaría:**
Si necesitara análisis de tendencias, migraría a Prometheus (que es el tool correcto para eso).

---

## Decision #3: Discord Webhooks vs PagerDuty

**Contexto:**
Necesitaba recibir alertas en tiempo real.

**Opciones:**

### A: PagerDuty / Opsgenie
**Pros:**
- Escalation policies
- On-call scheduling
- Acknowledge/resolve workflows
- Integraciones profesionales

**Contras:**
- Cuesta $$$ (después del trial)
- Overkill para un proyecto de aprendizaje

### B: Discord / Slack webhooks
**Pros:**
- Gratis
- Simple (un POST request)
- Móvil + desktop
- Fácil de reemplazar después

**Contras:**
- No tiene on-call management
- No tiene escalation

**Decisión:** Discord (por ahora)

**Razón:**
Este es un proyecto de aprendizaje. Discord me da 80% de lo que necesito (notificaciones) con 5% del esfuerzo.

**Upgrade path:**
Cuando tenga un equipo de 3+ personas, cambio a PagerDuty. El código está diseñado para que sea fácil:
```python
# Solo cambio esto:
send_alert() → send_pagerduty_incident()
```

**Lección:**
Usa la herramienta más simple que resuelva el problema AHORA. No sobre-ingenierices.# Technical Decisions

## Why idle CPU instead of load average?
El idle time refleja directamente la capacidad disponible
y es fácil de interpretar para alerting.

## Why variables de entorno?
Permiten modificar comportamiento sin cambiar código,
siguiendo principios 12-factor.

## Why state files en /tmp?
Simplicidad y persistencia entre ejecuciones
sin necesidad de base de datos.

## Why Discord?
Rápido, visual y suficiente para entornos pequeños.
