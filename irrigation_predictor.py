"""
Módulo para hacer predicciones de riego usando regresión lineal
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import joblib
import os

# Coeficientes del modelo entrenado (extraídos del último entrenamiento)
MODEL_COEFFICIENTS = {
    'intercept': 0.0267,
    'uv_index': -0.0333,
    'temperature2': 0.0041,
    'humidity2': 0.0299,
    'soil_moisture1': 0.0944,
    'soil_moisture2': -0.0309
}

DEFAULT_FEATURES = ['uv_index', 'temperature2', 'humidity2', 'soil_moisture1', 'soil_moisture2']
THRESHOLD = 0.5

class IrrigationPredictor:
    """Clase para predecir si se debe regar o no"""
    
    def __init__(self):
        self.model = None
        self.features = DEFAULT_FEATURES
        self.threshold = THRESHOLD
        self._build_model()
    
    def _build_model(self):
        """Construye el modelo de regresión lineal con los coeficientes entrenados"""
        # Crear un modelo simple sin scaler para usar los coeficientes directamente
        # Los coeficientes ya fueron entrenados con datos normalizados, así que usaremos
        # una aproximación directa
        self.model = LinearRegression()
        
        # Establecer los coeficientes conocidos directamente
        self.model.coef_ = np.array([
            MODEL_COEFFICIENTS['uv_index'],
            MODEL_COEFFICIENTS['temperature2'],
            MODEL_COEFFICIENTS['humidity2'],
            MODEL_COEFFICIENTS['soil_moisture1'],
            MODEL_COEFFICIENTS['soil_moisture2']
        ])
        self.model.intercept_ = MODEL_COEFFICIENTS['intercept']
    
    def predict(self, uv_index, temperature2, humidity2, soil_moisture1, soil_moisture2):
        """
        Hace una predicción basada en los datos del sensor
        
        Args:
            uv_index: Índice UV
            temperature2: Temperatura del sensor 2
            humidity2: Humedad del sensor 2
            soil_moisture1: Humedad del suelo 1
            soil_moisture2: Humedad del suelo 2
        
        Returns:
            dict: {
                'prediction': 'Regar' o 'No regar',
                'score': float (score continuo),
                'confidence': float (confianza basada en la distancia al umbral)
            }
        """
        try:
            # Preparar los datos en el orden correcto
            data = np.array([[
                float(uv_index),
                float(temperature2),
                float(humidity2),
                float(soil_moisture1),
                float(soil_moisture2)
            ]])
            
            # Hacer la predicción usando la fórmula: y = intercept + coef1*x1 + coef2*x2 + ...
            score = self.model.intercept_ + np.dot(data[0], self.model.coef_)
            
            # Determinar si se debe regar
            prediction = "Regar" if score >= self.threshold else "No regar"
            
            # Calcular confianza (distancia al umbral)
            distance_from_threshold = abs(score - self.threshold)
            confidence = min(100, max(0, (1 - distance_from_threshold) * 100))
            
            return {
                'prediction': prediction,
                'score': float(score),
                'confidence': round(confidence, 2),
                'threshold': self.threshold
            }
        except Exception as e:
            return {
                'prediction': 'Error',
                'score': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def predict_from_dict(self, sensor_data):
        """
        Hace una predicción desde un diccionario con los datos del sensor
        
        Args:
            sensor_data: dict con las claves: uv_index, temperature2, humidity2, 
                        soil_moisture1, soil_moisture2
        
        Returns:
            dict: Resultado de la predicción
        """
        return self.predict(
            sensor_data.get('uv_index', 0),
            sensor_data.get('temperature2', 0),
            sensor_data.get('humidity2', 0),
            sensor_data.get('soil_moisture1', 0),
            sensor_data.get('soil_moisture2', 0)
        )

# Instancia global del predictor
_predictor_instance = None

def get_predictor():
    """Obtiene la instancia global del predictor"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = IrrigationPredictor()
    return _predictor_instance

