# Arquitectura del Sistema - Flujo de Datos

## 📊 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         ESP32 (Hardware)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ DHT11 #1 │  │ DHT11 #2 │  │ Suelo #1 │  │ Suelo #2 │  UV    │
│  │  GPIO 2  │  │  GPIO 4  │  │  GPIO 35 │  │  GPIO 34 │  GPIO  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   33   │
│       │              │              │              │         │  │
│       └──────────────┴──────────────┴──────────────┴─────────┘
│                              │
│                    [Lectura cada 1 minuto]
│                              │
│                    ┌─────────▼──────────┐
│                    │  Procesamiento     │
│                    │  - Validacion      │
│                    │  - Formato JSON    │
│                    └─────────┬──────────┘
│                              │
│                    [Envio cada 5 minutos]
│                              │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ HTTPS POST
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Vercel (Servidor Web)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Flask Application (Python)                   │  │
│  │                                                            │  │
│  │  Endpoints:                                               │  │
│  │  - POST /data        → Recibe datos del ESP32            │  │
│  │  - GET  /data        → Retorna datos actuales            │  │
│  │  - GET  /latest-data → Obtiene datos de Supabase         │  │
│  │  - POST /led-control → Controla LED                      │  │
│  │  - GET  /led-status  → Estado LED + comandos            │  │
│  │  - GET  /            → Dashboard web                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                    ┌─────────▼──────────┐                      │
│                    │  Guardar en       │                      │
│                    │  Supabase          │                      │
│                    └─────────┬──────────┘                      │
│                              │                                   │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ HTTPS API
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supabase (Base de Datos)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Tabla: sensor_data                            │  │
│  │                                                            │  │
│  │  Columnas:                                                 │  │
│  │  - id (bigserial)                                         │  │
│  │  - temperature1 (real)                                    │  │
│  │  - humidity1 (real)                                       │  │
│  │  - temperature2 (real)                                    │  │
│  │  - humidity2 (real)                                       │  │
│  │  - soil_moisture1 (real)                                 │  │
│  │  - soil_moisture2 (real)                                 │  │
│  │  - uv_index (real)                                       │  │
│  │  - timestamp (text)                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │                                   │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ Consulta cada 5 min
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Dashboard Web (Vercel)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Interfaz Web (HTML/CSS/JS)                   │  │
│  │                                                            │  │
│  │  - Muestra datos de sensores                              │  │
│  │  - Auto-refresh cada 5 minutos                            │  │
│  │  - Botones de control                                     │  │
│  │  - Estado de conexion                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                    ┌─────────▼──────────┐                      │
│                    │  GET /latest-data  │                      │
│                    │  (Desde Supabase)  │                      │
│                    └─────────┬──────────┘                      │
│                              │                                   │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ Actualizacion
                               │
                               ▼
                         [Usuario Ve Datos]
```

## 🔄 Flujo de Datos Detallado

### 1. Lectura de Sensores (ESP32)

**Frecuencia:** Cada 1 minuto

**Proceso:**
```
ESP32 → readAllSensors()
  ├─→ readDHT11Sensor1()    → GPIO 2
  ├─→ readDHT11Sensor2()    → GPIO 4
  ├─→ readSoilMoistureSensor1() → GPIO 35 (ADC)
  ├─→ readSoilMoistureSensor2() → GPIO 34 (ADC)
  └─→ readUVSensor()        → GPIO 33 (ADC)

Resultado: Variables globales actualizadas
  - temperature1, humidity1
  - temperature2, humidity2
  - soilMoisture1, soilMoisture2
  - uvIndex
```

**Serial Monitor muestra:**
```
=== ALL SENSOR READINGS ===
DHT11 Sensor 1 (GPIO 2): Temperature=23.50C, Humidity=65.20%
DHT11 Sensor 2 (GPIO 4): Temperature=24.10C, Humidity=63.80%
Soil Moisture Sensor 1 (GPIO 35): 45.50%
Soil Moisture Sensor 2 (GPIO 34): 48.20%
UV Sensor (GPIO 33): UV Index=3.50
===========================
```

### 2. Envio de Datos al Servidor (ESP32 → Vercel)

**Frecuencia:** Cada 5 minutos (300000 ms)

**Proceso:**
```
ESP32 → sendSensorData()
  ├─→ Crea JSON con todos los datos
  ├─→ POST a https://intrumentacion.vercel.app/data
  └─→ Recibe respuesta del servidor
```

**JSON Enviado:**
```json
{
  "temperature1": 23.5,
  "humidity1": 65.2,
  "temperature2": 24.1,
  "humidity2": 63.8,
  "soil_moisture1": 45.5,
  "soil_moisture2": 48.2,
  "uv_index": 3.5
}
```

**Respuesta del Servidor:**
```json
{
  "status": "success",
  "message": "Sensor data received and saved",
  "timestamp": "2025-11-04 20:00:00",
  "data": { ... }
}
```

### 3. Procesamiento en Servidor (Vercel Flask)

**Cuando recibe POST /data:**

```
1. Recibe JSON del ESP32
2. Valida datos (temperature1, humidity1 requeridos)
3. Llama save_sensor_data()
   ├─→ Genera timestamp
   ├─→ Guarda en Supabase (si disponible)
   └─→ Actualiza esp32_data en memoria
4. Retorna confirmacion
```

**Funcion save_sensor_data():**
```python
save_sensor_data(t1, h1, t2, h2, sm1, sm2, uv)
  ├─→ insert_sensor_data() → Supabase
  └─→ Actualiza esp32_data['sensor_data']
```

### 4. Guardado en Supabase (Vercel → Supabase)

**Frecuencia:** Cada vez que ESP32 envia datos (cada 5 min)

**Proceso:**
```
Flask → supabase_config.insert_sensor_data()
  ├─→ Crea objeto data con todos los valores
  ├─→ supabase.table('sensor_data').insert(data)
  └─→ Retorna True/False
```

**Datos Insertados:**
```json
{
  "temperature1": 23.5,
  "humidity1": 65.2,
  "temperature2": 24.1,
  "humidity2": 63.8,
  "soil_moisture1": 45.5,
  "soil_moisture2": 48.2,
  "uv_index": 3.5,
  "timestamp": "2025-11-04 20:00:00"
}
```

### 5. Lectura desde Supabase (Vercel ← Supabase)

**Frecuencia:** 
- Al cargar la pagina web
- Cada 5 minutos (auto-refresh)
- Manualmente (boton "Actualizar Datos Ahora")

**Proceso:**
```
Dashboard Web → GET /latest-data
  ├─→ Flask llama load_latest_data_from_supabase()
  ├─→ supabase_config.get_latest_sensor_data()
  │   └─→ SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1
  ├─→ Actualiza esp32_data['sensor_data']
  └─→ Retorna JSON con datos actualizados
```

**Respuesta:**
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
    "uv_index": 3.5,
    "last_update": "2025-11-04 20:00:00"
  },
  "esp32_status": "connected"
}
```

### 6. Visualizacion en Dashboard Web

**Proceso:**
```
Usuario → Abre https://intrumentacion.vercel.app
  ├─→ Flask renderiza HTML con datos iniciales
  ├─→ JavaScript carga datos desde /latest-data
  ├─→ Actualiza valores en la pagina
  └─→ Auto-refresh cada 5 minutos
```

**JavaScript actualiza:**
```javascript
updateSensorData(sensorData)
  ├─→ temperature1-value
  ├─→ humidity1-value
  ├─→ temperature2-value
  ├─→ humidity2-value
  ├─→ soil1-value
  ├─→ soil2-value
  ├─→ uv-value
  └─→ last-update
```

### 7. Control LED (Dashboard → ESP32)

**Proceso:**
```
Usuario → Click "Probar LED - Parpadear"
  ├─→ JavaScript → POST /led-control {action: "blink"}
  ├─→ Flask guarda comando en led_command_queue
  └─→ Retorna confirmacion

ESP32 → checkServerCommands() (cada 10 segundos)
  ├─→ GET /led-status
  ├─→ Flask retorna comando si existe
  ├─→ ESP32 recibe {"led_command": "blink"}
  ├─→ controlLED("blink")
  └─→ LED empieza a parpadear
```

## ⏱️ Intervalos de Tiempo

| Accion | Intervalo | Descripcion |
|--------|-----------|-------------|
| Lectura sensores | 60 segundos | ESP32 lee todos los sensores |
| Envio datos | 300 segundos (5 min) | ESP32 envia a servidor |
| Consulta comandos LED | 10 segundos | ESP32 pregunta por comandos |
| Auto-refresh web | 300 segundos (5 min) | Pagina actualiza desde Supabase |
| Reconexion WiFi | 30 segundos | ESP32 intenta reconectar |

## 📡 Protocolos y Formatos

### HTTP/HTTPS
- **ESP32 → Servidor:** POST con JSON
- **Servidor → ESP32:** GET con JSON
- **Dashboard → Servidor:** GET/POST con JSON

### JSON Format
```json
{
  "temperature1": float,
  "humidity1": float,
  "temperature2": float,
  "humidity2": float,
  "soil_moisture1": float,
  "soil_moisture2": float,
  "uv_index": float
}
```

### Database Schema
```sql
CREATE TABLE sensor_data (
    id BIGSERIAL PRIMARY KEY,
    temperature1 REAL,
    humidity1 REAL,
    temperature2 REAL,
    humidity2 REAL,
    soil_moisture1 REAL,
    soil_moisture2 REAL,
    uv_index REAL,
    timestamp TEXT
);
```

## 🔐 Seguridad

### Variables de Entorno
- **Vercel:** `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- **ESP32:** WiFi credentials (en codigo)

### Row Level Security (RLS)
- **RLS habilitado** en tabla sensor_data
- **Politicas:** 
  - INSERT permitido para anon/authenticated
  - SELECT permitido para anon/authenticated

## 🎯 Puntos de Datos

### Almacenamiento
1. **Memoria ESP32:** Variables globales (temporal)
2. **Memoria Servidor:** `esp32_data` dict (temporal)
3. **Supabase:** Tabla `sensor_data` (persistente)

### Fuente de Verdad
- **Supabase** es la fuente de verdad principal
- Los datos en memoria del servidor se actualizan desde Supabase
- Si Supabase falla, el sistema sigue funcionando con datos en memoria

## 🔄 Flujo Completo Ejemplo

```
T=0:00  ESP32 lee sensores (cada minuto)
T=0:05  ESP32 envia datos → Vercel
        Vercel guarda → Supabase
        Dashboard muestra datos iniciales
T=0:10  ESP32 consulta comandos LED
        Usuario presiona "Probar LED"
        Comando se guarda en cola
T=0:20  ESP32 consulta comandos LED
        Recibe comando "blink"
        LED empieza a parpadear
T=0:30  ESP32 lee sensores de nuevo
T=5:00  ESP32 envia nuevos datos
        Dashboard auto-refresh desde Supabase
        Usuario ve datos actualizados
```

## 📊 Resumen de Servicios

| Servicio | Tecnologia | Funcion |
|----------|------------|---------|
| ESP32 | Arduino/C++ | Lectura sensores, envio datos |
| Vercel | Flask (Python) | API REST, Dashboard web |
| Supabase | PostgreSQL | Base de datos persistente |
| Dashboard | HTML/CSS/JS | Interfaz de usuario |

## 🔗 URLs y Endpoints

- **Dashboard:** https://intrumentacion.vercel.app
- **API Data:** https://intrumentacion.vercel.app/data
- **API Latest:** https://intrumentacion.vercel.app/latest-data
- **API LED:** https://intrumentacion.vercel.app/led-control
- **API LED Status:** https://intrumentacion.vercel.app/led-status

