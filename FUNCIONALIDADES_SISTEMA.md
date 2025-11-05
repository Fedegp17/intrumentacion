# Funcionalidades del Sistema IoT

## Resumen General
Sistema completo de monitoreo IoT con ESP32 que recopila datos de sensores ambientales y los transmite a un servidor web para visualizacion en tiempo real y almacenamiento en base de datos.

---

## 1. Sensores Implementados

### DHT11 Sensor 1 (GPIO 2)
- **Temperatura**: Rango -40°C a 80°C
- **Humedad**: Rango 20% a 90% RH
- **Actualizacion**: Cada 1 minuto
- **Precision**: ±2°C, ±5% RH

### DHT11 Sensor 2 (GPIO 4)
- **Temperatura**: Rango -40°C a 80°C
- **Humedad**: Rango 20% a 90% RH
- **Actualizacion**: Cada 1 minuto
- **Precision**: ±2°C, ±5% RH

### Sensor de Humedad de Suelo 1 (GPIO 35)
- **Rango**: 0% a 100%
- **Tipo**: Analogico (ADC)
- **Resolucion**: 12-bit (4096 niveles)
- **Actualizacion**: Cada 1 minuto

### Sensor de Humedad de Suelo 2 (GPIO 34)
- **Rango**: 0% a 100%
- **Tipo**: Analogico (ADC)
- **Resolucion**: 12-bit (4096 niveles)
- **Actualizacion**: Cada 1 minuto

### Sensor UV (GUVA-S12SD) (GPIO 33)
- **UV Index**: Rango 0 a 15
- **Tipo**: Analogico (ADC)
- **Sensibilidad**: 0.1V por unidad de UV Index
- **Actualizacion**: Cada 1 minuto

---

## 2. Funcionalidades del ESP32

### Lectura de Sensores
- ✅ Lectura automatica de todos los sensores cada 1 minuto
- ✅ Validacion de datos (verifica valores NaN)
- ✅ Mensajes de error detallados en Serial Monitor si falla una lectura
- ✅ Muestra todas las lecturas en Serial Monitor con formato claro

### Comunicacion WiFi
- ✅ Conexion automatica a WiFi al iniciar
- ✅ Reconexion automatica si se pierde la conexion (cada 30 segundos)
- ✅ Indicadores visuales durante la conexion
- ✅ Muestra IP asignada y URL del servidor

### Envio de Datos
- ✅ Envio automatico de datos al servidor cada 5 minutos
- ✅ Formato JSON con todos los datos de sensores
- ✅ Incluye: temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, uv_index
- ✅ Manejo de errores HTTP con mensajes descriptivos
- ✅ Timeout de 10 segundos para evitar bloqueos

### Verificacion de Conexion
- ✅ Verifica conexion con el servidor cada 10 segundos
- ✅ Muestra estado en Serial Monitor: "Server: CONNECTED" o "Server: DISCONNECTED"
- ✅ Actualiza estado interno de conexion

### Prueba de Comunicacion
- ✅ Consulta comandos del servidor cada 10 segundos
- ✅ Cuando recibe solicitud de prueba, imprime ">>> CONECTADO <<<" en Serial Monitor
- ✅ Envia confirmacion de vuelta al servidor
- ✅ Permite verificar comunicacion bidireccional

### Funcionamiento Autonomo
- ✅ Funciona completamente sin conexion serial
- ✅ No requiere intervencion manual
- ✅ Operacion continua 24/7
- ✅ Recuperacion automatica de errores

---

## 3. Funcionalidades del Servidor (Vercel)

### Endpoints Disponibles

#### `GET /` - Dashboard Web
- ✅ Interfaz web completa con diseño moderno
- ✅ Muestra datos de todos los sensores en tiempo real
- ✅ Tarjetas individuales para cada sensor con iconos
- ✅ Actualizacion automatica cada 5 minutos
- ✅ Muestra ultima actualizacion de cada sensor

#### `POST /data` - Recepcion de Datos
- ✅ Recibe datos JSON del ESP32
- ✅ Valida datos requeridos (temperature1, humidity1)
- ✅ Guarda automaticamente en Supabase
- ✅ Actualiza estado de conexion del ESP32
- ✅ Retorna confirmacion con datos recibidos
- ✅ Manejo de errores robusto

#### `GET /latest-data` - Ultimos Datos
- ✅ Obtiene los datos mas recientes de Supabase
- ✅ Actualiza datos en memoria del servidor
- ✅ Retorna JSON con todos los valores de sensores
- ✅ Incluye estado de conexion del ESP32

#### `GET /connection-status` - Estado de Conexion
- ✅ Verifica si el ESP32 esta realmente conectado
- ✅ Calcula tiempo desde ultimo dato recibido
- ✅ Marca como desconectado si han pasado mas de 7 minutos
- ✅ Retorna informacion detallada:
  - `connected`: boolean
  - `connection_status`: string
  - `last_data_received`: timestamp
  - `seconds_since_last_data`: numero

#### `GET/POST /communication-test` - Prueba de Comunicacion
- ✅ **GET**: El ESP32 consulta si hay solicitud de prueba
- ✅ **POST (desde web)**: Envia solicitud de prueba al ESP32
- ✅ **POST (desde ESP32)**: Recibe confirmacion "conectado"
- ✅ Actualiza timestamp del ultimo contacto
- ✅ Sistema de cola para comandos

---

## 4. Funcionalidades de la Interfaz Web

### Visualizacion de Datos
- ✅ Dashboard con diseño responsivo y moderno
- ✅ Tarjetas individuales para cada sensor:
  - DHT11 Sensor 1 (Temperatura y Humedad)
  - DHT11 Sensor 2 (Temperatura y Humedad)
  - Humedad de Suelo 1
  - Humedad de Suelo 2
  - Sensor UV (UV Index)
- ✅ Valores numericos con formato (1 decimal)
- ✅ Iconos visuales para cada tipo de sensor
- ✅ Colores diferenciados por tipo de sensor

### Panel de Control
- ✅ **Boton "Actualizar Datos Ahora"**: Actualiza datos inmediatamente desde Supabase
- ✅ **Boton "Prueba de Comunicacion"**: Envia solicitud de prueba al ESP32
  - El ESP32 respondera con ">>> CONECTADO <<<" en Serial Monitor
  - Actualiza estado de conexion en tiempo real

### Estado de Conexion
- ✅ Tarjeta dedicada mostrando estado del ESP32
- ✅ Indicador visual (verde/rojo/amarillo):
  - **Verde**: Conectado (datos recibidos en ultimos 7 minutos)
  - **Rojo**: Desconectado (mas de 7 minutos sin datos)
  - **Amarillo**: Verificando...
- ✅ Muestra texto del estado: "Conectado" o "Desconectado"
- ✅ Muestra timestamp de ultima verificacion
- ✅ Actualizacion automatica cada 10 segundos

### Actualizaciones Automaticas
- ✅ Actualiza datos de sensores cada 5 minutos
- ✅ Actualiza estado de conexion cada 10 segundos
- ✅ Sin necesidad de recargar la pagina

---

## 5. Funcionalidades de Supabase

### Almacenamiento de Datos
- ✅ Guarda automaticamente todos los datos recibidos
- ✅ Tabla `sensor_data` con columnas:
  - `id`: Auto-incremental
  - `temperature1`: REAL
  - `humidity1`: REAL
  - `temperature2`: REAL
  - `humidity2`: REAL
  - `soil_moisture1`: REAL
  - `soil_moisture2`: REAL
  - `uv_index`: REAL
  - `timestamp`: TEXT (formato: YYYY-MM-DD HH:MM:SS)

### Recuperacion de Datos
- ✅ Obtiene el registro mas reciente ordenado por timestamp
- ✅ Carga automatica en la interfaz web
- ✅ Historial completo de todas las mediciones

### Seguridad
- ✅ Row Level Security (RLS) habilitado
- ✅ Politicas configuradas para INSERT y SELECT
- ✅ Autenticacion mediante Anon Key

---

## 6. Caracteristicas Tecnicas

### ESP32
- **Plataforma**: ESP32 (Arduino Framework)
- **Librerias**:
  - WiFi.h (conexion WiFi)
  - HTTPClient.h (comunicacion HTTP)
  - ArduinoJson.h (manejo JSON)
  - DHT.h (sensores DHT11)
- **GPIOs Utilizados**:
  - GPIO 2: DHT11 Sensor 1
  - GPIO 4: DHT11 Sensor 2
  - GPIO 33: Sensor UV (ADC1_CH5)
  - GPIO 34: Humedad Suelo 2 (ADC1_CH6)
  - GPIO 35: Humedad Suelo 1 (ADC1_CH7)
- **Intervalos**:
  - Lectura sensores: 60 segundos (1 minuto)
  - Envio datos: 300 segundos (5 minutos)
  - Verificacion conexion: 10 segundos
  - Consulta comandos: 10 segundos

### Servidor
- **Plataforma**: Vercel (Serverless)
- **Framework**: Flask (Python)
- **Base de Datos**: Supabase (PostgreSQL)
- **Endpoints**: 5 rutas principales
- **Manejo de Errores**: Logging detallado con sys.stderr

### Interfaz Web
- **Tecnologia**: HTML5, CSS3, JavaScript vanilla
- **Iconos**: Font Awesome 6.0
- **Diseño**: Responsive, moderno, gradientes
- **Actualizaciones**: Fetch API con setInterval

---

## 7. Flujo de Datos

```
ESP32 → WiFi → Vercel Server → Supabase Database
                          ↓
                    Web Dashboard
```

1. **ESP32** lee sensores cada 1 minuto
2. **ESP32** envia datos a Vercel cada 5 minutos
3. **Vercel** recibe datos y los guarda en Supabase
4. **Vercel** actualiza estado de conexion
5. **Web Dashboard** consulta datos cada 5 minutos
6. **Web Dashboard** verifica conexion cada 10 segundos

---

## 8. Monitoreo y Diagnostico

### Serial Monitor (ESP32)
- ✅ Mensajes detallados de inicializacion
- ✅ Lecturas de todos los sensores con valores numericos
- ✅ Estado de conexion WiFi
- ✅ Resultados de envio de datos
- ✅ Estado de conexion con servidor
- ✅ Mensaje ">>> CONECTADO <<<" cuando se prueba comunicacion
- ✅ Mensajes de error descriptivos

### Logs del Servidor (Vercel)
- ✅ Errores de Supabase con detalles
- ✅ Warnings cuando falla el guardado
- ✅ Traceback completo en caso de excepciones
- ✅ Mensajes de estado de conexion

### Estado de Conexion
- ✅ Verificacion automatica basada en tiempo real
- ✅ Calculo preciso de tiempo desde ultimo contacto
- ✅ Actualizacion dinamica en interfaz web
- ✅ Indicadores visuales claros

---

## 9. Capacidades de Escalabilidad

### Recursos del ESP32
- ✅ 5 sensores funcionando simultaneamente
- ✅ RAM suficiente para operacion continua
- ✅ GPIOs disponibles: Aun quedan muchos GPIOs libres
- ✅ Capacidad para agregar mas sensores

### Servidor
- ✅ Serverless (escala automaticamente)
- ✅ Sin limites de conexiones simultaneas
- ✅ Base de datos escalable (Supabase)

---

## 10. Seguridad y Robustez

### Validacion de Datos
- ✅ Verifica valores NaN en sensores
- ✅ Valida datos requeridos antes de guardar
- ✅ Conversiones de tipo seguras (float)

### Manejo de Errores
- ✅ Try-catch en todas las operaciones criticas
- ✅ Reconexion automatica en caso de fallos
- ✅ Logging de errores para diagnostico
- ✅ Timeouts en conexiones HTTP

### Recuperacion Automatica
- ✅ Reconexion WiFi automatica
- ✅ Reintentos de envio de datos
- ✅ Continuacion del funcionamiento tras errores

---

## Resumen de Capacidades

### El sistema puede:
✅ Monitorear 5 sensores diferentes simultaneamente
✅ Transmitir datos cada 5 minutos de forma autonoma
✅ Almacenar historial completo en base de datos
✅ Visualizar datos en tiempo real en web dashboard
✅ Verificar estado de conexion en tiempo real
✅ Probar comunicacion bidireccional ESP32-Servidor
✅ Funcionar 24/7 sin intervencion manual
✅ Recuperarse automaticamente de errores
✅ Mostrar datos historicos desde Supabase
✅ Actualizar interfaz web automaticamente

### El sistema NO puede:
❌ Controlar actuadores (solo lectura de sensores)
❌ Enviar alertas por email/SMS (no implementado)
❌ Generar graficas historicas (solo ultimos datos)
❌ Configurar intervalos desde web (hardcoded en codigo)
❌ Múltiples dispositivos ESP32 (un solo dispositivo)

---

## Uso Tipico

1. **Encender ESP32**: Se conecta automaticamente a WiFi
2. **Lectura continua**: Lee sensores cada minuto
3. **Transmision**: Envia datos al servidor cada 5 minutos
4. **Visualizacion**: Usuario accede a dashboard web
5. **Monitoreo**: Ve estado de conexion y datos en tiempo real
6. **Prueba**: Puede probar comunicacion desde web
7. **Historial**: Datos guardados en Supabase para analisis futuro

---

**Fecha de actualizacion**: 2025-11-04
**Version**: Sistema completo funcional

