# Funcionalidades del Servidor

## 🌐 Endpoints Disponibles

### 1. Dashboard Principal
- **URL:** `GET /`
- **Descripcion:** Pagina principal con dashboard web
- **Funcionalidad:**
  - Muestra datos de todos los sensores en tiempo real
  - Actualizacion automatica cada 5 minutos desde Supabase
  - Interfaz web responsive y moderna

### 2. Recibir Datos del ESP32
- **URL:** `POST /data`
- **Descripcion:** Endpoint para que el ESP32 envie datos de sensores
- **Body (JSON):**
```json
{
  "temperature1": 23.5,
  "humidity1": 65.2,
  "temperature2": 24.1,
  "humidity2": 63.8,
  "soil_moisture1": 45.5,
  "soil_moisture2": 48.2
}
```
- **Respuesta:**
```json
{
  "status": "success",
  "message": "Sensor data received and saved",
  "timestamp": "2025-11-04 19:50:00",
  "data": {
    "temperature1": 23.5,
    "humidity1": 65.2,
    ...
  }
}
```
- **Funcionalidad:**
  - Guarda datos en Supabase automaticamente
  - Actualiza el estado de conexion del ESP32
  - Retorna confirmacion de recepcion

### 3. Obtener Datos Actuales
- **URL:** `GET /data`
- **Descripcion:** Obtiene los datos actuales almacenados en memoria
- **Respuesta:**
```json
{
  "sensor_data": {
    "temperature1": 23.5,
    "humidity1": 65.2,
    "temperature2": 24.1,
    "humidity2": 63.8,
    "soil_moisture1": 45.5,
    "soil_moisture2": 48.2,
    "last_update": "2025-11-04 19:50:00"
  },
  "esp32_status": "connected",
  "led_status": "OFF",
  "led_state": "off"
}
```

### 4. Obtener Datos Mas Recientes desde Supabase
- **URL:** `GET /latest-data`
- **Descripcion:** Obtiene los datos mas recientes desde Supabase
- **Funcionalidad:**
  - Consulta la base de datos
  - Retorna el ultimo registro guardado
  - Usado por la pagina web para auto-refresh
- **Respuesta:**
```json
{
  "status": "success",
  "sensor_data": {
    "temperature1": 23.5,
    "humidity1": 65.2,
    "temperature2": 24.1,
    "humidity2": 63.8,
    "soil_moisture1": 45.5,
    "soil_moisture2": 48.2,
    "last_update": "2025-11-04 19:50:00"
  },
  "esp32_status": "connected"
}
```

### 5. Estado del LED
- **URL:** `GET /led-status`
- **Descripcion:** Obtiene el estado actual del LED del ESP32
- **Respuesta:**
```json
{
  "status": "success",
  "led_status": "OFF",
  "led_state": "off"
}
```

## 📊 Datos que Maneja el Servidor

### Sensores Monitoreados:

1. **DHT11 Sensor 1** (GPIO 2)
   - Temperatura (°C)
   - Humedad (%)

2. **DHT11 Sensor 2** (GPIO 4)
   - Temperatura (°C)
   - Humedad (%)

3. **Humedad de Suelo Sensor 1** (GPIO 35)
   - Humedad del suelo (%)

4. **Humedad de Suelo Sensor 2** (GPIO 36)
   - Humedad del suelo (%)

## 🔄 Funcionalidades Automaticas

### 1. Guardado Automatico en Supabase
- Cada vez que el ESP32 envia datos, se guardan automaticamente en Supabase
- No requiere intervencion manual
- Los datos se almacenan con timestamp

### 2. Actualizacion Automatica de la Web
- La pagina web se actualiza automaticamente cada 5 minutos
- Obtiene los datos mas recientes desde Supabase
- Muestra un contador regresivo de la proxima actualizacion

### 3. Manejo de Errores Robusto
- Si Supabase no esta disponible, el servidor sigue funcionando
- Los datos se mantienen en memoria
- No falla si faltan sensores o datos

## 🌐 Interfaz Web

### Caracteristicas:
- **Dashboard responsive** con tarjetas para cada sensor
- **Actualizacion automatica** cada 5 minutos
- **Indicadores visuales** de estado de conexion
- **Diseño moderno** con gradientes y animaciones
- **Compatible con dispositivos moviles**

### Elementos de la Interfaz:
1. **Tarjeta DHT11 Sensor 1** - Muestra temperatura y humedad
2. **Tarjeta DHT11 Sensor 2** - Muestra temperatura y humedad
3. **Tarjeta Humedad Suelo 1** - Muestra porcentaje de humedad
4. **Tarjeta Humedad Suelo 2** - Muestra porcentaje de humedad
5. **Tarjeta Estado de Conexion** - Estado del ESP32 y ultima actualizacion
6. **Contador Regresivo** - Muestra tiempo hasta proxima actualizacion

## 🚀 Como Usar el Servidor

### 1. El servidor esta desplegado en Vercel
- URL: `https://intrumentacion.vercel.app`
- Funciona 24/7 automaticamente
- No requiere mantenimiento

### 2. El ESP32 envia datos automaticamente
- Cada 5 minutos
- Formato JSON
- Se guardan en Supabase

### 3. La pagina web se actualiza sola
- Cada 5 minutos
- Obtiene datos desde Supabase
- Muestra informacion en tiempo real

### 4. Ver datos manualmente
- Abre: `https://intrumentacion.vercel.app`
- Veras todos los sensores actualizados
- Los datos se actualizan automaticamente

## 📈 Flujo de Datos

```
ESP32 (cada 5 min)
    ↓
POST /data
    ↓
Servidor Flask
    ↓
Guardar en Supabase
    ↓
Web (cada 5 min)
    ↓
GET /latest-data
    ↓
Obtener de Supabase
    ↓
Mostrar en Dashboard
```

## 🔧 Configuracion Actual

- **Intervalo de envio ESP32:** 5 minutos
- **Intervalo de actualizacion web:** 5 minutos
- **Base de datos:** Supabase
- **Almacenamiento:** Persistente en Supabase
- **Interfaz:** Dashboard web responsive

