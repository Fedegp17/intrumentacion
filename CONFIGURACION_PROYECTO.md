# 🌡️ ESP32 DHT11 Monitor - Configuración del Proyecto

## 📋 Información del Proyecto
- **Nombre:** ESP32 DHT11 Temperature & Humidity Monitor
- **Fecha:** Enero 2024
- **Propósito:** Monitoreo de temperatura y humedad con ESP32 y DHT11

## 🔐 Credenciales WiFi
```
SSID: MEGACABLE-2.4G-F6A3
Password: mKyUQGz295
```

## 🌐 Configuración de Red
- **IP del Servidor (PC):** 192.168.15.39
- **Puerto del Servidor:** 5000
- **URL Completa:** http://192.168.15.39:5000

## 🔧 Configuración del Hardware

### ESP32
- **Modelo:** ESP32 DevKit
- **LED Status:** Pin 2 (LED interno)

### DHT11 Sensor
- **Pin de Datos:** GPIO4
- **Tipo:** DHT11
- **Alimentación:** 3.3V o 5V
- **Rango de Temperatura:** 0-50°C
- **Rango de Humedad:** 20-90% RH

### Conexiones
```
ESP32    DHT11
VCC  →   Pin 1 (VCC - 3.3V)
GND  →   Pin 4 (GND)
GPIO4 → Pin 2 (Data)
```

## 📁 Archivos del Proyecto

### Código ESP32
- **`codigo_dht11.ino`** - Código principal del ESP32
- **Librerías necesarias:**
  - WiFi
  - HTTPClient
  - ArduinoJson
  - DHT sensor library

### Servidor Flask
- **`server_dht11.py`** - Servidor web con Flask
- **Dependencias:** Flask, pandas, numpy

## ⚙️ Configuración de Intervalos

### ESP32
- **Lectura de sensores:** Cada 1 minuto
- **Envío de datos:** Cada 30 minutos
- **Reintento de conexión WiFi:** Cada 30 segundos

### Servidor
- **Auto-refresh web:** Cada 30 segundos
- **Puerto:** 5000
- **Modo debug:** Activado

## 📊 Funcionalidades

### ESP32
- ✅ Conexión automática a WiFi
- ✅ Lectura de DHT11 cada minuto
- ✅ Envío de datos JSON al servidor
- ✅ Indicador LED de estado
- ✅ Reconexión automática
- ✅ Logs detallados en Serial

### Servidor Web
- ✅ Interfaz web responsive
- ✅ Gráficas en tiempo real
- ✅ Almacenamiento en CSV
- ✅ Datos históricos (últimos 20 registros)
- ✅ Generación de datos de prueba
- ✅ Auto-refresh de la página

## 🚀 Instrucciones de Uso

### 1. Preparar ESP32
```cpp
// En codigo_dht11.ino ya están configuradas las credenciales:
const char* ssid = "MEGACABLE-2.4G-F6A3";
const char* password = "mKyUQGz295";
const char* serverURL = "http://192.168.15.39:5000";
```

### 2. Conectar Hardware
- Conectar DHT11 al ESP32 según el esquema
- Alimentar ESP32 (USB o fuente externa)

### 3. Subir Código
- Abrir Arduino IDE
- Instalar librerías necesarias
- Seleccionar board ESP32
- Subir código al ESP32

### 4. Ejecutar Servidor
```bash
cd C:\Users\jfede\OneDrive\Documentos\Maestria\Instrumentacion\codigo_esp
python server_dht11.py
```

### 5. Ver Datos
- Abrir navegador en: http://localhost:5000
- O desde otro dispositivo: http://192.168.15.39:5000

## 📈 Formato de Datos

### JSON Enviado por ESP32
```json
{
  "temperature": 25.3,
  "humidity": 65.2
}
```

### CSV Guardado en Servidor
```csv
timestamp,temperature,humidity
2024-01-15 10:30:00,25.3,65.2
2024-01-15 11:00:00,26.1,63.8
```

## 🔍 Troubleshooting

### Problemas Comunes
1. **ESP32 no se conecta a WiFi**
   - Verificar credenciales
   - Verificar señal WiFi
   - Revisar monitor serial

2. **Servidor no recibe datos**
   - Verificar IP del servidor
   - Verificar firewall
   - Revisar logs del servidor

3. **DHT11 no lee datos**
   - Verificar conexiones
   - Verificar alimentación
   - Probar con otro sensor

### Logs Importantes
- **ESP32 Serial:** 115200 baud
- **Servidor:** Consola de Python
- **Navegador:** F12 para debug

## 📝 Notas de Seguridad
- ⚠️ Las credenciales WiFi están en texto plano en el código
- ⚠️ No compartir este documento públicamente
- ⚠️ Cambiar credenciales si se compromete la seguridad

## 🔄 Próximas Mejoras
- [ ] Encriptación de datos
- [ ] Autenticación en servidor
- [ ] Base de datos en lugar de CSV
- [ ] Notificaciones por email
- [ ] App móvil

---
**Creado por:** Asistente AI
**Fecha:** Enero 2024
**Versión:** 1.0

