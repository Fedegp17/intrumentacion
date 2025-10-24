# 🤖 Modelo de Machine Learning para Predicción de Riego

## 📋 Descripción

Este módulo contiene el código de machine learning para predecir cuándo regar las plantas basado en datos de sensores IoT (temperatura, humedad, etc.).

## 🚀 Instalación

### 1. Instalar dependencias de ML:
```bash
pip install -r requirements_ml.txt
```

### 2. Dependencias principales:
- **pandas**: Análisis de datos
- **numpy**: Cálculos numéricos
- **scikit-learn**: Algoritmos de ML
- **joblib**: Guardar/cargar modelos

## 📊 Uso del Modelo

### Entrenar el modelo:
```python
from ModelML import train_irrigation_model

# Entrenar con datos existentes
train_irrigation_model('sensor_data.csv')
```

### Hacer predicciones:
```python
from ModelML import predict_irrigation_needs

# Datos de sensores
sensor_data = {
    'temperature': 28.5,
    'humidity': 45.0,
    'soil_moisture': 25.0,
    'uv_index': 7.2
}

# Predecir si necesita riego
prediction = predict_irrigation_needs(sensor_data)
print(prediction)
```

### Generar datos de muestra:
```python
from ModelML import generate_sample_data

# Generar 1000 registros de muestra
generate_sample_data(1000)
```

## 🧠 Algoritmo Utilizado

- **Random Forest Classifier**
- **Características**: temperatura, humedad, humedad del suelo, UV, hora, día
- **Etiqueta**: necesita riego (sí/no)
- **Regla de etiquetado**: humedad del suelo < 30%

## 📈 Características del Modelo

### Datos de Entrada:
- **Temperatura** (°C)
- **Humedad** (%)
- **Humedad del suelo** (%)
- **Índice UV**
- **Hora del día** (0-23)
- **Día de la semana** (0-6)

### Salida:
- **needs_irrigation**: Boolean (True/False)
- **confidence**: Nivel de confianza (0-1)
- **probability_irrigation**: Probabilidad de riego (0-1)

## 🔧 Funcionalidades

### 1. **Entrenamiento Automático**
```python
# Entrenar con datos reales
train_irrigation_model('dht11_data.csv')
```

### 2. **Predicción en Tiempo Real**
```python
# Usar en el servidor Flask
prediction = predict_irrigation_needs(current_sensor_data)
```

### 3. **Análisis de Importancia**
```python
# Ver qué características son más importantes
predictor = IrrigationPredictor()
predictor.load_model()
importance = predictor.get_feature_importance()
```

## 📊 Métricas de Evaluación

- **Precisión**: Exactitud del modelo
- **Reporte de Clasificación**: Precision, Recall, F1-Score
- **Importancia de Características**: Qué factores influyen más

## 🎯 Casos de Uso

### 1. **Sistema de Riego Automático**
- Predecir cuándo regar automáticamente
- Optimizar uso de agua
- Evitar riego excesivo

### 2. **Alertas Inteligentes**
- Notificar cuando las plantas necesitan agua
- Basado en condiciones ambientales
- Personalizado por tipo de planta

### 3. **Análisis Histórico**
- Entender patrones de riego
- Optimizar horarios de riego
- Ahorro de recursos

## 🔄 Integración con el Sistema IoT

### En el servidor Flask:
```python
# En server_dht11.py
from ModelML import predict_irrigation_needs

@app.route('/predict-irrigation')
def predict_irrigation():
    sensor_data = esp32_data['sensor_data']
    prediction = predict_irrigation_needs(sensor_data)
    return jsonify(prediction)
```

### En el ESP32:
```cpp
// En codigo_dht11.ino
// Enviar datos adicionales para ML
String jsonData = "{";
jsonData += "\"temperature\":" + String(temperature) + ",";
jsonData += "\"humidity\":" + String(humidity) + ",";
jsonData += "\"soil_moisture\":" + String(soilMoisture) + ",";
jsonData += "\"uv_index\":" + String(uvIndex);
jsonData += "}";
```

## 📁 Estructura de Archivos

```
├── ModelML.py              # Código principal de ML
├── requirements_ml.txt     # Dependencias de ML
├── ML_README.md           # Esta documentación
├── irrigation_model.pkl   # Modelo entrenado (generado)
└── sample_sensor_data.csv # Datos de muestra (generado)
```

## 🚀 Ejemplo Completo

```python
# 1. Generar datos de muestra
from ModelML import generate_sample_data, train_irrigation_model, predict_irrigation_needs

# Generar datos
generate_sample_data(1000)

# Entrenar modelo
train_irrigation_model('sample_sensor_data.csv')

# Hacer predicción
sensor_data = {
    'temperature': 30.0,
    'humidity': 35.0,
    'soil_moisture': 20.0,
    'uv_index': 8.5
}

result = predict_irrigation_needs(sensor_data)
print(f"¿Necesita riego? {result['needs_irrigation']}")
print(f"Confianza: {result['confidence']:.2f}")
```

## 🎓 Para Desarrolladores

### Extender el Modelo:
1. **Agregar más sensores**: pH, conductividad, etc.
2. **Mejorar etiquetado**: Usar reglas más sofisticadas
3. **Optimizar hiperparámetros**: Grid search, etc.
4. **Agregar validación cruzada**: Mejor evaluación

### Mejores Prácticas:
- **Datos balanceados**: Evitar sesgo en las etiquetas
- **Validación continua**: Re-entrenar con nuevos datos
- **Monitoreo**: Seguir métricas en producción
- **Backup**: Guardar versiones del modelo

¡El modelo está listo para usar! 🌱🤖
