"""
Módulo ligero para hacer predicciones de riego usando regresión lineal
Versión optimizada sin dependencias pesadas para Vercel
"""

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
    """Clase ligera para predecir si se debe regar o no (sin dependencias pesadas)"""
    
    def __init__(self):
        self.coefficients = [
            MODEL_COEFFICIENTS['uv_index'],
            MODEL_COEFFICIENTS['temperature2'],
            MODEL_COEFFICIENTS['humidity2'],
            MODEL_COEFFICIENTS['soil_moisture1'],
            MODEL_COEFFICIENTS['soil_moisture2']
        ]
        self.intercept = MODEL_COEFFICIENTS['intercept']
        self.threshold = THRESHOLD
    
    def predict(self, uv_index, temperature2, humidity2, soil_moisture1, soil_moisture2):
        """
        Hace una predicción basada en los datos del sensor usando solo Python puro
        
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
            # Convertir a float
            values = [
                float(uv_index),
                float(temperature2),
                float(humidity2),
                float(soil_moisture1),
                float(soil_moisture2)
            ]
            
            # Calcular el score usando la fórmula: y = intercept + coef1*x1 + coef2*x2 + ...
            # Esto es equivalente a: score = intercept + sum(coef[i] * values[i] for i in range(5))
            score = self.intercept
            for i in range(len(self.coefficients)):
                score += self.coefficients[i] * values[i]
            
            # Determinar si se debe regar
            prediction = "Regar" if score >= self.threshold else "No regar"
            
            # Calcular confianza (distancia al umbral)
            # Normalizar la distancia: cuanto más lejos del umbral, menos confianza
            distance_from_threshold = abs(score - self.threshold)
            # Convertir distancia a porcentaje de confianza (máximo 100%)
            confidence = min(100.0, max(0.0, (1.0 - distance_from_threshold) * 100.0))
            
            return {
                'prediction': prediction,
                'score': float(score),
                'confidence': round(confidence, 2),
                'threshold': self.threshold
            }
        except (ValueError, TypeError) as e:
            return {
                'prediction': 'Error',
                'score': 0.0,
                'confidence': 0.0,
                'error': f'Error de conversión: {str(e)}'
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
