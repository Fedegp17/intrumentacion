"""
Script local para predecir riego usando scikit-learn completo
Obtiene datos de Supabase, hace predicción y guarda resultado
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import requests
import json

# Cargar variables de entorno
load_dotenv()
load_dotenv('supabase.env')

try:
    from supabase import create_client, Client
    
    # Obtener credenciales de Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("ERROR: SUPABASE_URL y SUPABASE_ANON_KEY deben estar en supabase.env")
        sys.exit(1)
    
    # Crear cliente de Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Conectado a Supabase")
    
except ImportError:
    print("ERROR: Instala supabase: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: No se pudo conectar a Supabase: {e}")
    sys.exit(1)

# Coeficientes del modelo entrenado (del último entrenamiento)
MODEL_COEFFICIENTS = {
    'intercept': 0.0267,
    'uv_index': -0.0333,
    'temperature2': 0.0041,
    'humidity2': 0.0299,
    'soil_moisture1': 0.0944,
    'soil_moisture2': -0.0309
}

THRESHOLD = 0.5

def get_latest_sensor_data():
    """Obtiene los últimos datos del sensor desde Supabase"""
    try:
        result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(1).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"ERROR obteniendo datos: {e}")
        return None

def create_prediction_model():
    """Crea el modelo de regresión lineal con scikit-learn"""
    # Crear pipeline con scaler y regresor
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', LinearRegression())
    ])
    
    # Crear datos dummy para inicializar el scaler
    # (los coeficientes ya están entrenados, solo necesitamos la estructura)
    dummy_X = np.array([[0, 0, 0, 0, 0], [1, 1, 1, 1, 1]])
    dummy_y = np.array([0, 1])
    
    # Entrenar el modelo (solo para inicializar)
    model.fit(dummy_X, dummy_y)
    
    # Establecer los coeficientes entrenados
    model.named_steps['regressor'].coef_ = np.array([
        MODEL_COEFFICIENTS['uv_index'],
        MODEL_COEFFICIENTS['temperature2'],
        MODEL_COEFFICIENTS['humidity2'],
        MODEL_COEFFICIENTS['soil_moisture1'],
        MODEL_COEFFICIENTS['soil_moisture2']
    ])
    model.named_steps['regressor'].intercept_ = MODEL_COEFFICIENTS['intercept']
    
    return model

def predict_irrigation(sensor_data):
    """
    Hace una predicción de riego usando scikit-learn
    
    Args:
        sensor_data: dict con los datos del sensor
    
    Returns:
        dict: Resultado de la predicción
    """
    try:
        # Crear el modelo
        model = create_prediction_model()
        
        # Preparar los datos en el orden correcto
        features = np.array([[
            float(sensor_data.get('uv_index', 0)),
            float(sensor_data.get('temperature2', 0)),
            float(sensor_data.get('humidity2', 0)),
            float(sensor_data.get('soil_moisture1', 0)),
            float(sensor_data.get('soil_moisture2', 0))
        ]])
        
        # Hacer la predicción
        score = model.predict(features)[0]
        
        # Determinar si se debe regar
        prediction = "Regar" if score >= THRESHOLD else "No regar"
        
        # Calcular confianza
        distance_from_threshold = abs(score - THRESHOLD)
        confidence = min(100.0, max(0.0, (1.0 - distance_from_threshold) * 100.0))
        
        return {
            'prediction': prediction,
            'score': float(score),
            'confidence': round(confidence, 2),
            'threshold': THRESHOLD,
            'status': 'success'
        }
    except Exception as e:
        return {
            'prediction': 'Error',
            'score': 0.0,
            'confidence': 0.0,
            'error': str(e),
            'status': 'error'
        }

def save_prediction_to_supabase(prediction_result, sensor_data):
    """Guarda el resultado de la predicción en Supabase"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Intentar insertar en tabla irrigation_predictions
        # Si la tabla no existe, se creará manualmente
        data = {
            'timestamp': timestamp,
            'prediction': prediction_result['prediction'],
            'score': prediction_result['score'],
            'confidence': prediction_result['confidence'],
            'uv_index': sensor_data.get('uv_index'),
            'temperature2': sensor_data.get('temperature2'),
            'humidity2': sensor_data.get('humidity2'),
            'soil_moisture1': sensor_data.get('soil_moisture1'),
            'soil_moisture2': sensor_data.get('soil_moisture2')
        }
        
        result = supabase.table('irrigation_predictions').insert(data).execute()
        
        if result.data:
            print(f"✅ Predicción guardada en Supabase: {prediction_result['prediction']}")
            return True
        else:
            print("⚠️ No se pudo guardar la predicción (tabla puede no existir)")
            return False
            
    except Exception as e:
        print(f"⚠️ Error guardando predicción: {e}")
        print("💡 Nota: Necesitas crear la tabla 'irrigation_predictions' en Supabase")
        return False

def send_prediction_to_vercel(prediction_result, sensor_data, vercel_url=None):
    """
    Envía la predicción directamente a Vercel (opcional)
    
    Args:
        prediction_result: Resultado de la predicción
        sensor_data: Datos del sensor utilizados
        vercel_url: URL de Vercel (opcional, se puede obtener de env)
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        # Obtener URL de Vercel
        if not vercel_url:
            vercel_url = os.getenv('VERCEL_URL', 'https://intrumentacion-7fkz.vercel.app')
        
        # Crear payload para enviar a Vercel
        payload = {
            'prediction': prediction_result['prediction'],
            'score': prediction_result['score'],
            'confidence': prediction_result['confidence'],
            'threshold': prediction_result['threshold'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sensor_data_used': {
                'uv_index': sensor_data.get('uv_index'),
                'temperature2': sensor_data.get('temperature2'),
                'humidity2': sensor_data.get('humidity2'),
                'soil_moisture1': sensor_data.get('soil_moisture1'),
                'soil_moisture2': sensor_data.get('soil_moisture2')
            }
        }
        
        # Enviar a Vercel (si hay un endpoint para recibir predicciones)
        # Por ahora, esto es opcional ya que Vercel lee de Supabase
        # Pero podemos agregar un endpoint en Vercel si se necesita
        
        print(f"💡 Nota: Vercel leerá la predicción de Supabase automáticamente")
        print(f"🌐 URL de Vercel: {vercel_url}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error enviando a Vercel: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🌱 Sistema de Predicción de Riego Local")
    print("=" * 60)
    print()
    
    # Obtener últimos datos del sensor
    print("📡 Obteniendo últimos datos de Supabase...")
    sensor_data = get_latest_sensor_data()
    
    if not sensor_data:
        print("❌ No se encontraron datos del sensor en Supabase")
        print("💡 Asegúrate de que el ESP32 haya enviado datos recientemente")
        sys.exit(1)
    
    print("✅ Datos obtenidos:")
    print(f"   - UV Index: {sensor_data.get('uv_index', 'N/A')}")
    print(f"   - Temperatura 2: {sensor_data.get('temperature2', 'N/A')}°C")
    print(f"   - Humedad 2: {sensor_data.get('humidity2', 'N/A')}%")
    print(f"   - Humedad Suelo 1: {sensor_data.get('soil_moisture1', 'N/A')}%")
    print(f"   - Humedad Suelo 2: {sensor_data.get('soil_moisture2', 'N/A')}%")
    print(f"   - Timestamp: {sensor_data.get('timestamp', 'N/A')}")
    print()
    
    # Hacer la predicción
    print("🧠 Haciendo predicción con scikit-learn...")
    prediction_result = predict_irrigation(sensor_data)
    
    if prediction_result['status'] == 'error':
        print(f"❌ Error en la predicción: {prediction_result.get('error', 'Unknown')}")
        sys.exit(1)
    
    # Mostrar resultado
    print("=" * 60)
    print("📊 RESULTADO DE LA PREDICCIÓN")
    print("=" * 60)
    print(f"🌱 Decisión: {prediction_result['prediction']}")
    print(f"📈 Score: {prediction_result['score']:.4f}")
    print(f"🎯 Confianza: {prediction_result['confidence']:.2f}%")
    print(f"⚖️  Umbral: {prediction_result['threshold']}")
    print("=" * 60)
    print()
    
    # Guardar en Supabase
    print("💾 Guardando resultado en Supabase...")
    save_success = save_prediction_to_supabase(prediction_result, sensor_data)
    
    if save_success:
        print("✅ Predicción guardada exitosamente en Supabase")
        print()
        print("=" * 60)
        print("📤 FLUJO DE INFORMACIÓN")
        print("=" * 60)
        print("✅ Script Local → Supabase (guardado)")
        print("✅ Vercel → Supabase (lee cuando usuario presiona botón)")
        print("✅ Interfaz Web → Muestra resultado")
        print("=" * 60)
        print()
        print("🌐 El resultado está disponible en Vercel")
        print("💡 Presiona '¿Debo Regar?' en la interfaz web para verlo")
    else:
        print("⚠️ Predicción completada pero no se pudo guardar en Supabase")
        print("💡 Revisa que la tabla 'irrigation_predictions' exista")
        print("💡 Ejecuta CREAR_TABLA_PREDICCIONES.sql en Supabase")
    
    print()
    return prediction_result

if __name__ == '__main__':
    try:
        result = main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

