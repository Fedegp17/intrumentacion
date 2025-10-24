# 📁 Estructura del Proyecto IoT

## 🎯 **Archivos Principales (Producción)**

### **🐍 Servidor Flask**
- **`principal_code.py`** - Servidor principal en producción
  - Sistema completo con Supabase
  - Interfaz web profesional
  - Desplegado en Vercel
  - Funcionalidades completas del sistema IoT

### **🔧 Código Arduino**
- **`codigo_dht11/principal_code.ino`** - Código principal para ESP32
  - Conexión real con sensor DHT11
  - Comunicación con servidor de producción
  - Control de LED integrado
  - Envío de datos cada 15 minutos

---

## 🧪 **Archivos de Prueba (Testing)**

### **🐍 Servidor de Pruebas**
- **`test_server.py`** - Servidor de pruebas
  - Simula datos del sensor DHT11
  - Interfaz web para testing
  - Funcionalidades de prueba
  - Puerto 5001 (diferente al principal)

### **🔧 Código Arduino de Prueba**
- **`codigo_dht11/test_code.ino`** - Código de prueba para ESP32
  - Simula datos del sensor (sin DHT11 real)
  - Comunicación con servidor de pruebas
  - Envío de datos cada 10 segundos
  - Funciones de autodiagnóstico

---

## 🚀 **Cómo Usar**

### **📋 Para Desarrollo y Pruebas:**
1. **Servidor de Pruebas:**
   ```bash
   python test_server.py
   ```
   - Accede a: `http://localhost:5001`
   - Simula datos del sensor
   - Prueba funcionalidades sin hardware

2. **ESP32 de Prueba:**
   - Carga `codigo_dht11/test_code.ino` en el ESP32
   - Cambia la URL del servidor a puerto 5001
   - No necesita sensor DHT11 real

### **🌐 Para Producción:**
1. **Servidor Principal:**
   ```bash
   python principal_code.py
   ```
   - Accede a: `http://localhost:5000`
   - Conectado a Supabase
   - Desplegado en Vercel

2. **ESP32 Principal:**
   - Carga `codigo_dht11/principal_code.ino` en el ESP32
   - Conecta sensor DHT11 real
   - Comunicación con servidor de producción

---

## 🔧 **Configuración de Red**

### **🌐 URLs del Servidor:**
- **Producción:** `http://192.168.100.25:5000`
- **Pruebas:** `http://192.168.100.25:5001`

### **📡 WiFi (Ambos códigos):**
- **SSID:** `MEGACABLE-2.4G-F6A3`
- **Password:** `mKyUQGz295`

---

## 🧪 **Funcionalidades de Prueba**

### **📊 Test Server Features:**
- ✅ Simulación de datos del sensor
- ✅ Interfaz web de pruebas
- ✅ Control de LED simulado
- ✅ Generación de alertas
- ✅ Datos históricos simulados

### **🔧 Test Arduino Features:**
- ✅ Simulación de sensor DHT11
- ✅ Envío de datos cada 10 segundos
- ✅ Control de LED real
- ✅ Autodiagnóstico del sistema
- ✅ Generación de temperaturas altas para alertas

---

## 📋 **Comandos Útiles**

### **🐍 Servidor:**
```bash
# Servidor principal (producción)
python principal_code.py

# Servidor de pruebas
python test_server.py
```

### **🔧 Arduino:**
- **Principal:** Carga `principal_code.ino` para uso real
- **Pruebas:** Carga `test_code.ino` para testing

---

## 🎯 **Flujo de Desarrollo**

1. **🧪 Desarrollo:** Usa archivos `test_*` para probar funcionalidades
2. **✅ Testing:** Verifica que todo funcione correctamente
3. **🚀 Producción:** Usa archivos `principal_*` para despliegue real
4. **🌐 Deploy:** El servidor principal se despliega automáticamente en Vercel

---

## 📁 **Estructura de Archivos**

```
codigo_esp/
├── principal_code.py          # 🐍 Servidor principal
├── test_server.py             # 🧪 Servidor de pruebas
├── supabase_config.py         # 🗄️ Configuración Supabase
├── requirements.txt           # 📦 Dependencias Python
├── vercel.json               # 🌐 Configuración Vercel
├── supabase.env              # 🔐 Variables de entorno
├── codigo_dht11/
│   ├── principal_code.ino     # 🔧 Arduino principal
│   └── test_code.ino         # 🧪 Arduino de pruebas
└── README_ESTRUCTURA.md      # 📋 Este archivo
```

---

## 🎉 **¡Listo para Usar!**

- **🧪 Para pruebas:** Usa archivos `test_*`
- **🚀 Para producción:** Usa archivos `principal_*`
- **🌐 Despliegue:** Automático en Vercel
- **📊 Monitoreo:** Interfaz web profesional
