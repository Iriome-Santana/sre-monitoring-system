# Troubleshooting Guide

Documentación de problemas reales que encontré y cómo los resolví **sin IA**.

---

## Problem #1: Cron no ejecutaba los scripts

**Síntomas:**
- Scripts funcionaban manualmente con `python3 disk_check.py`
- Logs vacíos después de configurar cron
- No había errores visibles

**Proceso de debugging (paso a paso):**

1. **Verificar que cron está corriendo:**
```bash
   sudo service cron status
   # Output: active (running)
```
   ✅ Cron está activo

2. **Ver logs de cron:**
```bash
   grep CRON /var/log/syslog | tail -n 20
   # Output: No mention of my scripts
```
   ❌ Mis scripts no se están ejecutando

3. **Probar cron con comando simple:**
```bash
   # Añadí a crontab:
   * * * * * echo "test" >> /tmp/cron-test.log
   # Esperé 2 minutos
   cat /tmp/cron-test.log
   # Output: test test test
```
   ✅ Cron SÍ ejecuta comandos

4. **Hipótesis: problema con rutas relativas**
```bash
   # Cambié de:
   */5 * * * * python3 scripts/disk_check.py
   # A rutas absolutas:
   */5 * * * * python3 /home/iriom/sre/scripts/disk_check.py
```

5. **Resultado: Funcionó**
```bash
   tail -f logs/disk_check.log
   # Logs empezaron a aparecer
```

**Root Cause:** Cron ejecuta con directorio de trabajo diferente (`/home/iriom` en lugar de `/home/iriom/sre`). Rutas relativas no funcionan.

**Lección aprendida:** Siempre usar rutas absolutas en cron jobs.

**Tiempo de resolución:** 45 minutos

**¿ChatGPT/Claude me habría ayudado?** 
Tal vez me hubiera dado la respuesta directamente, pero NO habría aprendido el proceso de:
- Leer logs de sistema
- Probar hipótesis incrementalmente
- Entender cómo funciona cron internamente

---

## Problem #2: Alertas duplicadas en Discord

**Síntomas:**
- Recibía 10 alertas idénticas cada hora
- Todas decían "WARNING - Uso de disco: 45%"
- Discord se llenaba de spam

**Mi proceso:**

1. **Observar el patrón:**
   - 1 alerta cada 5 minutos
   - Todas con el mismo mensaje
   - Uso de disco NO estaba cambiando

2. **Revisar el código:**
```python
   # Código original:
   if use_percent >= warning_threshold:
       send_alert(...)  # ← ESTO se ejecuta SIEMPRE
```

3. **Hipótesis:** No estoy verificando si YA alerté antes

4. **Buscar soluciones (Google, no IA):**
   - "nagios avoid duplicate alerts"
   - "prometheus alertmanager deduplication"
   - Encontré el concepto de "state management"

5. **Diseñar la solución:**
```
   Guardar último estado → Comparar con actual → Alertar solo si cambió
```

6. **Implementar:**
```python
   last_state = load_last_state()
   current_state = determine_state()
   
   if last_state != current_state and current_state != "OK":
       send_alert(...)
   
   save_state(current_state)
```

7. **Probar:**
   - Forzar WARNING varias veces
   - ✅ Solo 1 alerta la primera vez
   - ✅ Silencio después
   - ✅ Nueva alerta cuando cambió a CRITICAL

**Root Cause:** Faltaba state management (patrón común en monitoring)

**Lección:** Sistemas de alertas profesionales siempre tienen deduplicación

**¿La IA me habría ayudado?** 
Sí, me habría dado el código. Pero:
- NO habría entendido por qué es necesario
- NO habría aprendido el patrón general
- NO habría podido explicarlo en una entrevista

---

## Problem #3: Script que avisaba en desarrollo pero no en cron al mover archivos

**Síntomas**
- Forzaba el cambio de estado y cuando esperaba a que cron me enviara el RECOVERY a Discord nunca llegaba

**Mi proceso**

1. **Observar el patrón:**
   - Forcé el WARNING para que el current state cambiara
   - Esperé a que el cron avisara del recovery
   - Nunca avisab

2. **Revisar el código:**

No veía ningún fallo en el código y me extrañaba

3. **Hipótesis:** No cambié la ruta de crontab

4. **Buscar soluciones:**
   - Con el comando crontab -e entré a crontab y revisé los paths y estaban desactualizados
   - Actualicé los paths a los actuales y arrgelé el problema
---

## Metodología de Troubleshooting

Mi proceso estándar (aprendido haciendo):

1. **Reproducir el problema** manualmente
2. **Aislar variables** (funciona en X pero no en Y)
3. **Formar hipótesis** específicas
4. **Probar hipótesis** una a una
5. **Documentar** lo que funcionó/no funcionó
6. **Entender el "por qué"** (no solo el fix)

**Esto NO se puede delegar a IA.**# Troubleshooting

## No se envían alertas
- Verificar DISCORD_WEBHOOK
- Verificar NOTIFICATIONS_ENABLED
- Probar ejecución manual

## Alertas repetidas
- Verificar permisos de /tmp
- Verificar escritura del archivo .state

## Diferencias entre ejecución manual y cron
- Cron no carga variables de entorno
- Solución: definirlas en el script o en crontab
