# Test Code - Sensor UV GUVA-S12SD

## 📋 Descripción
Código de prueba específico para el sensor UV GUVA-S12SD. Este código permite probar únicamente el sensor UV y verificar que funciona correctamente antes de integrarlo al sistema principal.

## 🔌 Conexiones del Sensor UV

### Sensor GUVA-S12SD → ESP32
```
VCC del sensor UV  →  3.3V del ESP32
GND del sensor UV  →  GND del ESP32  
OUT del sensor UV  →  GPIO 34 del ESP32
```

## ⚙️ Configuración

### Serial Monitor
- **Baud Rate**: 115200
- **Configuración**: Sin terminación de línea

### Parámetros del Sensor
- **Pin**: GPIO 34 (ADC1_CH6)
- **Resolución ADC**: 12 bits (4096 niveles)
- **Voltaje de referencia**: 3.3V
- **Sensibilidad**: 0.1 V por unidad de UV Index

## 📊 Qué muestra el código

### Información inicial:
- Configuración del sensor
- Parámetros de calibración
- Prueba inicial (5 lecturas)

### Lecturas continuas (cada 2 segundos):
- Valor ADC crudo
- Voltaje convertido
- UV Index calculado
- Nivel de UV (Bajo/Moderado/Alto/etc.)
- Indicador visual en consola
- Color sugerido para UI

## 🎯 Interpretación de resultados

### UV Index Scale:
```
0-2:   Bajo (Verde)     - Protección mínima
3-5:   Moderado (Amarillo) - Protección requerida
6-7:   Alto (Naranja)   - Protección extra
8-10:  Muy Alto (Rojo)  - Evitar exposición prolongada
11+:   Extremo (Morado) - Evitar exposición
```

### Ejemplo de salida:
```
--- LECTURA SENSOR UV ---
Valor ADC crudo: 1024
Voltaje: 0.825V
UV Index: 8.3
Nivel UV: Muy Alto (8-10)
Indicador: ████████████░░░░░░░░ 8.3
Color sugerido: Rojo
------------------------
```

## 🔧 Calibración

Si los valores no parecen correctos:

1. **Verificar conexiones**:
   - VCC a 3.3V (no 5V)
   - GND común
   - OUT a GPIO 34

2. **Ajustar sensibilidad**:
   ```cpp
   #define UV_SENSITIVITY 0.1  // Cambiar este valor
   ```

3. **Calibrar con medidor profesional**:
   - Comparar con medidor UV comercial
   - Ajustar fórmula de conversión

## 🚀 Cómo usar

1. **Conectar el sensor** según el diagrama
2. **Abrir Arduino IDE**
3. **Cargar el código** `test_uv_sensor.ino`
4. **Configurar Serial Monitor** a 115200 baud
5. **Subir el código** al ESP32
6. **Observar las lecturas** en Serial Monitor

## ⚠️ Notas importantes

- El sensor debe estar **expuesto a la luz** para funcionar
- Los valores pueden variar según la **posición del sensor**
- La **calibración** puede necesitar ajustes según el sensor específico
- **No exponer** el sensor a luz UV extrema por períodos prolongados

## 🔍 Troubleshooting

### Problema: Valores siempre en 0
- **Solución**: Verificar conexión VCC y GND

### Problema: Valores muy altos
- **Solución**: Verificar que VCC esté en 3.3V (no 5V)

### Problema: Lecturas erráticas
- **Solución**: Verificar conexión del pin OUT

### Problema: No hay lecturas
- **Solución**: Verificar que el sensor esté expuesto a la luz
