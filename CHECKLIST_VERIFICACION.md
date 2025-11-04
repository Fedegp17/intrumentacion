# Checklist de Verificacion

## ✅ Verificaciones Necesarias

### 1. Supabase - Tabla `sensor_data`
- [ ] Tabla creada/actualizada con todas las columnas:
  - `id` (bigint, Primary Key)
  - `temperature1` (real)
  - `humidity1` (real)
  - `temperature2` (real)
  - `humidity2` (real)
  - `soil_moisture1` (real)
  - `soil_moisture2` (real)
  - `timestamp` (text)

### 2. Vercel - Variables de Entorno
- [ ] `SUPABASE_URL` configurada
- [ ] `SUPABASE_ANON_KEY` configurada
- [ ] Deploy completado con las nuevas variables

### 3. ESP32 - Configuracion
- [ ] Codigo cargado en ESP32
- [ ] Sensores conectados:
  - DHT11 #1 en GPIO 2
  - DHT11 #2 en GPIO 4
  - Sensor suelo #1 en GPIO 35
  - Sensor suelo #2 en GPIO 36
- [ ] WiFi conectado
- [ ] URL del servidor: `https://intrumentacion-7fkz.vercel.app`

## 🔍 Como Verificar que Todo Funciona

### 1. Verificar Vercel
- Abre: https://intrumentacion-7fkz.vercel.app
- Deberias ver el dashboard con todos los sensores
- Si ves errores, revisa los logs en Vercel Dashboard

### 2. Verificar Supabase
- Ve a Supabase Dashboard → Table Editor → sensor_data
- Deberias poder ver la tabla (puede estar vacia inicialmente)
- Una vez que el ESP32 envie datos, apareceran nuevos registros

### 3. Verificar ESP32
- Abre Serial Monitor (115200 baud)
- Deberias ver mensajes de conexion WiFi
- Cada 5 minutos deberias ver: "Sending sensor data to server..."
- Deberias ver: "Sensor data sent successfully!"

### 4. Verificar Flujo Completo
1. ESP32 envia datos → Verifica en Serial Monitor
2. Servidor recibe datos → Verifica en Vercel logs
3. Datos guardados en Supabase → Verifica en Supabase Table Editor
4. Web muestra datos → Verifica en dashboard web

## 🐛 Problemas Comunes

### Si el ESP32 no envia datos:
- Verifica conexion WiFi
- Verifica URL del servidor en el codigo
- Revisa Serial Monitor para errores

### Si Vercel muestra error 500:
- Verifica que las variables de entorno esten configuradas
- Revisa logs en Vercel Dashboard
- Verifica que el deploy se completo correctamente

### Si Supabase no recibe datos:
- Verifica que la tabla tenga todas las columnas
- Verifica que las variables de entorno en Vercel sean correctas
- Revisa logs en Vercel para ver errores de Supabase

### Si la web no muestra datos:
- Espera 5 minutos para la primera actualizacion
- Verifica que Supabase tenga datos
- Revisa la consola del navegador (F12) para errores

## 📊 Datos Esperados

Una vez que todo funcione, deberias ver en Supabase registros como:

```json
{
  "id": 1,
  "temperature1": 23.5,
  "humidity1": 65.2,
  "temperature2": 24.1,
  "humidity2": 63.8,
  "soil_moisture1": 45.5,
  "soil_moisture2": 48.2,
  "timestamp": "2025-11-04 20:00:00"
}
```

Y en el dashboard web deberias ver todos estos valores actualizados cada 5 minutos.

