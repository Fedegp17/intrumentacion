# Test Dummy Data - ESP32

## Descripcion

Este codigo envia datos dummy (simulados) al servidor de Vercel para probar la conexion:
- ESP32 -> Vercel -> Supabase

## Caracteristicas

- **No requiere sensores fisicos** - Genera datos aleatorios
- **Envio rapido** - Cada 30 segundos (para pruebas)
- **Mensajes detallados** - Muestra todo en Serial Monitor
- **Datos realistas** - Valores dentro de rangos normales

## Datos Dummy Generados

- **DHT11 Sensor 1**: Temperatura 23.5-28.5°C, Humedad 60-90%
- **DHT11 Sensor 2**: Temperatura 24.0-29.0°C, Humedad 58-93%
- **Soil Moisture 1**: 40-80%
- **Soil Moisture 2**: 45-80%
- **UV Index**: 2.0-10.0

## Configuracion

### 1. Actualizar Credenciales WiFi

Abre `test_dummy_data.ino` y actualiza las credenciales:

```cpp
const char* ssid = "TU_SSID";
const char* password = "TU_PASSWORD";
```

O usa las credenciales de `CREDENCIALES.txt`

### 2. Verificar URL del Servidor

Verifica que la URL sea correcta:

```cpp
const char* serverURL = "https://intrumentacion-7fkz.vercel.app";
```

## Uso

1. Abre el codigo en Arduino IDE
2. Selecciona tu ESP32 board
3. Sube el codigo
4. Abre Serial Monitor (115200 baud)
5. Observa los mensajes de envio

## Mensajes Esperados

### Exito:
```
HTTP Response Code: 200
SUCCESS! Data sent to server
Server response: {"status":"success",...}
```

### Error:
```
HTTP ERROR: 500
Response: {"message":"..."}
```

## Verificacion

### 1. Verificar en Vercel
- Ve a Vercel Dashboard
- Revisa los logs de la aplicacion
- Deberias ver requests POST a `/data`

### 2. Verificar en Supabase
- Ve a Supabase Dashboard
- Table Editor -> sensor_data
- Deberias ver nuevos registros cada 30 segundos

### 3. Verificar en Serial Monitor
- Deberias ver mensajes de exito
- Datos enviados correctamente
- Respuesta del servidor

## Troubleshooting

### WiFi no conecta
- Verifica credenciales en el codigo
- Verifica que el WiFi este disponible
- Revisa Serial Monitor para errores

### HTTP 500 Error
- Verifica que Vercel este desplegado
- Revisa logs de Vercel
- Verifica que Supabase este configurado

### HTTP 404 Error
- Verifica la URL del servidor
- Verifica que el endpoint `/data` exista

### Connection Failed
- Verifica conexion a internet
- Verifica que Vercel este activo
- Revisa que la URL sea HTTPS

## Notas

- Este codigo solo prueba la conexion, no usa sensores reales
- Los datos son generados aleatoriamente
- Intervalo de envio: 30 segundos (para pruebas rapidas)
- Para usar en produccion, cambiar intervalo a 5 minutos

