# 🚀 Despliegue del Modelo ML en Render

## 📋 Descripción

Este documento explica cómo desplegar el modelo de Machine Learning para predicción de riego en Render.

## 🛠️ Archivos Necesarios

### **1. `ml_api.py` - API Flask Principal**
- ✅ API REST para el modelo ML
- ✅ Endpoints para predicción, entrenamiento y monitoreo
- ✅ Manejo de errores y validación de datos
- ✅ Soporte para predicciones en lote

### **2. `requirements_ml_render.txt` - Dependencias**
```
Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
gunicorn==21.2.0
```

### **3. `render.yaml` - Configuración de Render**
- ✅ Configuración automática del servicio
- ✅ Comandos de build y start
- ✅ Variables de entorno

## 🌐 Endpoints de la API

### **🏠 Home**
```
GET /
```
**Respuesta:**
```json
{
  "message": "🌱 IoT Irrigation Prediction API",
  "version": "1.0.0",
  "status": "active",
  "model_loaded": true,
  "endpoints": {...}
}
```

### **🔍 Health Check**
```
GET /health
```
**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-23T18:30:00",
  "model_loaded": true
}
```

### **📊 Model Info**
```
GET /model-info
```
**Respuesta:**
```json
{
  "status": "success",
  "model_type": "RandomForestClassifier",
  "n_estimators": 100,
  "max_depth": 10,
  "feature_importance": {
    "temperature": 0.25,
    "humidity": 0.20,
    "soil_moisture": 0.35,
    "uv_index": 0.10,
    "hour": 0.05,
    "day_of_week": 0.05
  }
}
```

### **🔮 Predicción Individual**
```
POST /predict
```
**Datos de entrada:**
```json
{
  "temperature": 28.5,
  "humidity": 45.0,
  "soil_moisture": 25.0,
  "uv_index": 7.2
}
```
**Respuesta:**
```json
{
  "status": "success",
  "prediction": {
    "needs_irrigation": true,
    "confidence": 0.85,
    "probability_irrigation": 0.85
  },
  "input_data": {...},
  "timestamp": "2024-10-23T18:30:00"
}
```

### **📦 Predicciones en Lote**
```
POST /batch-predict
```
**Datos de entrada:**
```json
{
  "sensor_data": [
    {
      "temperature": 28.5,
      "humidity": 45.0,
      "soil_moisture": 25.0,
      "uv_index": 7.2
    },
    {
      "temperature": 30.0,
      "humidity": 40.0,
      "soil_moisture": 20.0,
      "uv_index": 8.5
    }
  ]
}
```

### **🌱 Entrenar Modelo**
```
POST /train
```
**Respuesta:**
```json
{
  "status": "success",
  "message": "Model trained successfully",
  "model_loaded": true,
  "timestamp": "2024-10-23T18:30:00"
}
```

## 🚀 Pasos para Desplegar en Render

### **1. Preparar el Repositorio**
```bash
# Agregar archivos al repositorio
git add ml_api.py requirements_ml_render.txt render.yaml
git commit -m "Add ML API for Render deployment"
git push origin main
```

### **2. Crear Cuenta en Render**
1. Ve a [render.com](https://render.com)
2. Regístrate con GitHub
3. Conecta tu repositorio

### **3. Crear Nuevo Servicio Web**
1. **New** → **Web Service**
2. **Connect Repository** → Selecciona tu repo
3. **Configure:**
   - **Name:** `ml-irrigation-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements_ml_render.txt`
   - **Start Command:** `gunicorn ml_api:app`
   - **Plan:** Free

### **4. Variables de Entorno (Opcional)**
```
PYTHON_VERSION=3.11.0
```

### **5. Desplegar**
- Click **Create Web Service**
- Render construirá y desplegará automáticamente
- Obtendrás una URL como: `https://ml-irrigation-api.onrender.com`

## 🔧 Configuración Avanzada

### **Usar render.yaml (Recomendado)**
1. Agrega `render.yaml` al repositorio
2. Render detectará automáticamente la configuración
3. Despliegue automático con la configuración especificada

### **Configuración Manual**
Si prefieres configurar manualmente:
- **Build Command:** `pip install -r requirements_ml_render.txt`
- **Start Command:** `gunicorn ml_api:app`
- **Python Version:** 3.11.0

## 📊 Uso de la API

### **Ejemplo con cURL:**
```bash
# Health check
curl https://tu-api.onrender.com/health

# Predicción
curl -X POST https://tu-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 28.5,
    "humidity": 45.0,
    "soil_moisture": 25.0,
    "uv_index": 7.2
  }'
```

### **Ejemplo con Python:**
```python
import requests

# URL de tu API en Render
api_url = "https://tu-api.onrender.com"

# Hacer predicción
data = {
    "temperature": 28.5,
    "humidity": 45.0,
    "soil_moisture": 25.0,
    "uv_index": 7.2
}

response = requests.post(f"{api_url}/predict", json=data)
result = response.json()

print(f"¿Necesita riego? {result['prediction']['needs_irrigation']}")
print(f"Confianza: {result['prediction']['confidence']:.2f}")
```

## 🔄 Integración con el Sistema IoT

### **En el ESP32:**
```cpp
// Enviar datos al modelo ML
String jsonData = "{";
jsonData += "\"temperature\":" + String(temperature) + ",";
jsonData += "\"humidity\":" + String(humidity) + ",";
jsonData += "\"soil_moisture\":" + String(soilMoisture) + ",";
jsonData += "\"uv_index\":" + String(uvIndex);
jsonData += "}";

// Enviar a la API de Render
http.begin("https://tu-api.onrender.com/predict");
http.addHeader("Content-Type", "application/json");
int httpResponseCode = http.POST(jsonData);
```

### **En el Servidor Principal:**
```python
import requests

def get_irrigation_prediction(sensor_data):
    """Obtener predicción del modelo ML en Render"""
    try:
        response = requests.post(
            "https://tu-api.onrender.com/predict",
            json=sensor_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['prediction']
        else:
            return None
            
    except Exception as e:
        print(f"Error calling ML API: {e}")
        return None
```

## 📈 Monitoreo y Logs

### **Logs en Render:**
- Ve a tu servicio en Render Dashboard
- Click en **Logs** para ver logs en tiempo real
- Monitorea el rendimiento y errores

### **Métricas:**
- **Uptime:** Tiempo de actividad del servicio
- **Response Time:** Tiempo de respuesta de la API
- **Memory Usage:** Uso de memoria
- **CPU Usage:** Uso de CPU

## 🎯 Beneficios del Despliegue en Render

### **✅ Ventajas:**
- **Gratis:** Plan gratuito disponible
- **Automático:** Deploy automático desde GitHub
- **Escalable:** Fácil escalamiento
- **Monitoreo:** Logs y métricas integradas
- **HTTPS:** Certificado SSL automático
- **Global:** CDN global para mejor rendimiento

### **🔄 Flujo de Trabajo:**
1. **Desarrollo:** Trabaja en local
2. **Commit:** `git commit` y `git push`
3. **Deploy:** Render detecta cambios automáticamente
4. **Testing:** Prueba la API desplegada
5. **Integración:** Conecta con tu sistema IoT

## 🚨 Troubleshooting

### **Problemas Comunes:**

#### **1. Error de Dependencias:**
```
Error: No module named 'pandas'
```
**Solución:** Verifica que `requirements_ml_render.txt` esté correcto

#### **2. Timeout en Build:**
```
Build timeout
```
**Solución:** Reduce las dependencias o usa un plan superior

#### **3. Error de Memoria:**
```
Out of memory
```
**Solución:** Optimiza el modelo o usa un plan superior

#### **4. Modelo no se carga:**
```
Model not loaded
```
**Solución:** Verifica que el entrenamiento se complete correctamente

¡Tu modelo ML estará listo para usar en producción! 🌱🤖
