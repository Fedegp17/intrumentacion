# Guia de Verificacion de Conexiones

## Objetivo
Verificar que Python, Vercel y Supabase estan correctamente conectados y funcionando.

## Paso 1: Verificar Python

### 1.1 Verificar instalacion de Python
```bash
python --version
# o
python3 --version
```
**Debe mostrar:** Python 3.x.x

### 1.2 Instalar dependencias
```bash
pip install requests
# o
pip3 install requests
```

### 1.3 Verificar instalacion
```bash
python -c "import requests; print('OK')"
# o
python3 -c "import requests; print('OK')"
```
**Debe mostrar:** OK

## Paso 2: Verificar Vercel

### 2.1 Verificar que el servidor este desplegado
1. Abre tu navegador
2. Ve a: https://intrumentacion-7fkz.vercel.app
3. **Debe mostrar:** La pagina del dashboard (o al menos responder sin error 404)

### 2.2 Verificar endpoint de datos
1. Abre tu navegador
2. Ve a: https://intrumentacion-7fkz.vercel.app/data
3. **Debe mostrar:** JSON con datos o mensaje de error (no 404)

### 2.3 Verificar logs de Vercel
1. Ve a Vercel Dashboard
2. Selecciona tu proyecto
3. Ve a "Logs" o "Deployments"
4. **Debe mostrar:** Logs de la aplicacion activa

## Paso 3: Verificar Supabase

### 3.1 Verificar tabla en Supabase
1. Ve a Supabase Dashboard
2. Table Editor → `sensor_data`
3. **Debe mostrar:** La tabla con todas las columnas:
   - id
   - temperature1, humidity1
   - temperature2, humidity2
   - soil_moisture1, soil_moisture2
   - uv_index
   - timestamp

### 3.2 Verificar variables de entorno en Vercel
1. Ve a Vercel Dashboard
2. Tu proyecto → Settings → Environment Variables
3. **Debe tener:**
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

### 3.3 Verificar RLS (Row Level Security)
1. Ve a Supabase Dashboard
2. SQL Editor
3. Ejecuta:
```sql
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5;
```
4. **Debe mostrar:** Los ultimos 5 registros (o tabla vacia si no hay datos)

## Paso 4: Ejecutar Script de Prueba

### 4.1 Preparar el script
```bash
# Verificar que el archivo existe
ls test_dummy_data.py

# O en Windows
dir test_dummy_data.py
```

### 4.2 Ejecutar el script
```bash
python test_dummy_data.py
# o
python3 test_dummy_data.py
```

### 4.3 Verificar salida
**Debe mostrar:**
```
============================================================
ESP32 DUMMY DATA TEST - Python Script
============================================================
PRUEBA DE CONEXION
============================================================
Servidor: https://intrumentacion-7fkz.vercel.app
Endpoint: /data
------------------------------------------------------------
✓ Conexion al servidor: OK (Status: 200)

>>> Envio #1
============================================================
Enviando datos dummy al servidor...
HTTP Status Code: 200
✓ SUCCESS! Datos enviados correctamente
```

## Paso 5: Verificar Datos en Supabase

### 5.1 Despues de ejecutar el script
1. Espera 30 segundos (o deten el script con Ctrl+C)
2. Ve a Supabase Dashboard
3. Table Editor → `sensor_data`
4. Click en "Refresh" o recarga la pagina
5. **Debe mostrar:** Nuevos registros con datos dummy

### 5.2 Verificar estructura de datos
Cada registro debe tener:
- `temperature1`, `humidity1` (valores numericos)
- `temperature2`, `humidity2` (valores numericos)
- `soil_moisture1`, `soil_moisture2` (valores numericos)
- `uv_index` (valor numerico)
- `timestamp` (fecha y hora)

## Paso 6: Verificar Logs de Vercel

### 6.1 Durante la ejecucion del script
1. Ve a Vercel Dashboard
2. Tu proyecto → Logs
3. **Debe mostrar:** Requests POST a `/data`
4. **Debe mostrar:** Mensajes de exito o errores

### 6.2 Verificar errores
Si hay errores en los logs:
- **500 Error:** Problema con Supabase (revisa variables de entorno)
- **404 Error:** Endpoint no existe (revisa el codigo del servidor)
- **Connection Error:** Servidor no disponible

## Checklist de Verificacion

### Python
- [ ] Python instalado y funcionando
- [ ] Libreria `requests` instalada
- [ ] Script se ejecuta sin errores de importacion

### Vercel
- [ ] Servidor responde en el navegador
- [ ] Endpoint `/data` existe
- [ ] Logs muestran actividad
- [ ] Variables de entorno configuradas

### Supabase
- [ ] Tabla `sensor_data` existe
- [ ] Todas las columnas estan presentes
- [ ] RLS esta configurado correctamente
- [ ] Variables de entorno en Vercel estan configuradas

### Flujo Completo
- [ ] Script Python envia datos
- [ ] Vercel recibe datos (HTTP 200)
- [ ] Vercel guarda en Supabase
- [ ] Datos aparecen en Supabase Table Editor

## Troubleshooting

### Error: "No module named 'requests'"
**Solucion:**
```bash
pip install requests
```

### Error: "Connection refused" o "Connection failed"
**Solucion:**
- Verifica que Vercel este desplegado
- Verifica la URL del servidor
- Verifica tu conexion a internet

### Error: HTTP 500
**Solucion:**
- Revisa logs de Vercel
- Verifica variables de entorno de Supabase
- Verifica que RLS este configurado

### Error: HTTP 404
**Solucion:**
- Verifica que el endpoint `/data` exista en tu servidor
- Verifica la URL completa

### No aparecen datos en Supabase
**Solucion:**
- Verifica que RLS permita INSERT
- Verifica variables de entorno en Vercel
- Revisa logs de Vercel para errores

## Prueba Rapida

Para una prueba rapida, ejecuta:

```bash
# 1. Verificar Python
python -c "import requests; print('Python OK')"

# 2. Verificar conexion al servidor
python -c "import requests; r = requests.get('https://intrumentacion-7fkz.vercel.app'); print(f'Vercel: {r.status_code}')"

# 3. Ejecutar script completo
python test_dummy_data.py
```

## Siguiente Paso

Una vez que todo este verificado:
1. Los datos se envian desde Python ✓
2. Vercel recibe y procesa los datos ✓
3. Supabase almacena los datos ✓
4. Puedes usar el ESP32 real para enviar datos reales

