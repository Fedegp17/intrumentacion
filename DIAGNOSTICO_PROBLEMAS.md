# Diagnostico de Problemas

## Problemas Identificados y Soluciones

### 1. No se actualiza en Supabase

#### Posibles causas:
- Variables de entorno no configuradas en Vercel
- Tabla en Supabase no tiene todas las columnas
- Errores silenciados en el codigo

#### Soluciones implementadas:
- ✅ Logging agregado para ver errores
- ✅ Verificacion de que todas las columnas existen
- ✅ Manejo de errores mejorado

#### Como verificar:
1. Revisa los logs de Vercel para ver mensajes de error
2. Verifica que las variables de entorno esten configuradas:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
3. Verifica en Supabase que la tabla tenga todas las columnas:
   - `temperature1`, `humidity1`
   - `temperature2`, `humidity2`
   - `soil_moisture1`, `soil_moisture2`
   - `uv_index`
   - `timestamp`

### 2. LED no hace blink

#### Problema:
El servidor solo guardaba el comando en memoria pero no lo enviaba al ESP32.

#### Solucion implementada:
- ✅ Sistema de cola de comandos (`led_command_queue`)
- ✅ El ESP32 consulta `/led-status` cada 10 segundos
- ✅ El servidor envia el comando cuando el ESP32 lo solicita
- ✅ El comando se limpia despues de enviarlo

#### Como funciona:
1. Usuario presiona boton en la pagina web
2. Comando se guarda en `led_command_queue`
3. ESP32 consulta `/led-status` cada 10 segundos
4. Servidor devuelve el comando si existe
5. ESP32 ejecuta el comando y limpia la cola

### 3. Pagina no muestra ultima lectura

#### Problema:
La pagina solo mostraba datos cuando se actualizaba desde Supabase, pero no mostraba valores iniciales.

#### Solucion implementada:
- ✅ La pagina ahora muestra datos iniciales al cargar
- ✅ Los datos se actualizan desde Supabase automaticamente
- ✅ Los datos se muestran incluso si Supabase falla

#### Como funciona:
1. Al cargar la pagina, se muestran datos del servidor
2. Inmediatamente se hace fetch desde Supabase
3. Los datos se actualizan cada 5 minutos automaticamente
4. El boton "Actualizar Datos Ahora" permite actualizar manualmente

## Verificaciones Necesarias

### 1. Verificar Supabase
```sql
-- Verificar que la tabla existe y tiene todas las columnas
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sensor_data';

-- Verificar ultimos datos
SELECT * FROM sensor_data 
ORDER BY timestamp DESC 
LIMIT 5;
```

### 2. Verificar Variables de Entorno en Vercel
- Ve a Vercel Dashboard
- Settings → Environment Variables
- Verifica que existan:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`

### 3. Verificar Logs
- Revisa logs de Vercel para ver errores
- Busca mensajes que empiecen con "ERROR" o "WARNING"
- Verifica que los datos se esten guardando

### 4. Verificar ESP32
- Abre Serial Monitor (115200 baud)
- Verifica que el ESP32 este conectado a WiFi
- Verifica que este enviando datos cada 5 minutos
- Verifica que este consultando `/led-status` cada 10 segundos

## Testing

### Test 1: Guardar en Supabase
1. Envia datos desde ESP32
2. Revisa logs de Vercel
3. Verifica en Supabase que aparezca el nuevo registro

### Test 2: LED Blink
1. Presiona "Probar LED - Parpadear" en la pagina
2. Espera maximo 10 segundos
3. El LED del ESP32 deberia empezar a parpadear
4. Revisa Serial Monitor para ver el mensaje

### Test 3: Mostrar Datos
1. Carga la pagina web
2. Deberias ver los valores iniciales inmediatamente
3. Espera 5 minutos o presiona "Actualizar Datos Ahora"
4. Los datos deberian actualizarse desde Supabase

## Troubleshooting

### Si Supabase no guarda:
1. Verifica variables de entorno
2. Verifica que la tabla tenga todas las columnas
3. Revisa logs de Vercel para errores especificos
4. Verifica que `uv_index` este en la tabla

### Si LED no funciona:
1. Verifica que el ESP32 este consultando `/led-status`
2. Revisa Serial Monitor para ver si recibe comandos
3. Verifica que el LED este en GPIO 13
4. Prueba con comandos "on" y "off" primero

### Si la pagina no muestra datos:
1. Abre la consola del navegador (F12)
2. Busca errores en la consola
3. Verifica que `/latest-data` retorne datos
4. Verifica que Supabase tenga datos

