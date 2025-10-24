"""
Modelo de Machine Learning para Predicción de Riego
Sistema IoT - ESP32 DHT11

Este archivo contiene el código para entrenar y usar un modelo de ML
para predecir cuándo regar las plantas basado en datos de sensores.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime

class IrrigationPredictor:
    """
    Clase para manejar el modelo de machine learning
    para predicción de riego basado en datos de sensores
    """
    
    def __init__(self, model_path='irrigation_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.features = ['temperature', 'humidity', 'soil_moisture', 'uv_index']
        self.target = 'needs_irrigation'
        
    def load_data(self, csv_file='sensor_data.csv'):
        """
        Cargar datos de sensores desde CSV
        """
        try:
            if not os.path.exists(csv_file):
                print(f"❌ Archivo {csv_file} no encontrado")
                return None
                
            df = pd.read_csv(csv_file)
            print(f"✅ Datos cargados: {len(df)} registros")
            return df
            
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return None
    
    def prepare_features(self, df):
        """
        Preparar características para el modelo
        """
        try:
            # Crear características adicionales
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            
            # Características del modelo
            feature_columns = self.features + ['hour', 'day_of_week']
            
            # Verificar que todas las columnas existan
            missing_cols = [col for col in feature_columns if col not in df.columns]
            if missing_cols:
                print(f"⚠️ Columnas faltantes: {missing_cols}")
                # Usar solo las columnas disponibles
                feature_columns = [col for col in feature_columns if col in df.columns]
            
            X = df[feature_columns].fillna(0)
            return X, feature_columns
            
        except Exception as e:
            print(f"❌ Error preparando características: {e}")
            return None, None
    
    def create_labels(self, df):
        """
        Crear etiquetas para entrenamiento
        Regla simple: necesita riego si humedad del suelo < 30%
        """
        try:
            if 'soil_moisture' in df.columns:
                # Regla basada en humedad del suelo
                labels = (df['soil_moisture'] < 30).astype(int)
            else:
                # Regla basada en humedad del aire si no hay sensor de suelo
                labels = (df['humidity'] < 40).astype(int)
            
            print(f"✅ Etiquetas creadas: {labels.sum()} casos de riego necesario")
            return labels
            
        except Exception as e:
            print(f"❌ Error creando etiquetas: {e}")
            return None
    
    def train_model(self, X, y):
        """
        Entrenar el modelo de Random Forest
        """
        try:
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Crear y entrenar modelo
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Modelo entrenado - Precisión: {accuracy:.3f}")
            print("\n📊 Reporte de clasificación:")
            print(classification_report(y_test, y_pred))
            
            return True
            
        except Exception as e:
            print(f"❌ Error entrenando modelo: {e}")
            return False
    
    def save_model(self):
        """
        Guardar modelo entrenado
        """
        try:
            if self.model is not None:
                joblib.dump(self.model, self.model_path)
                print(f"✅ Modelo guardado en {self.model_path}")
                return True
            else:
                print("❌ No hay modelo para guardar")
                return False
                
        except Exception as e:
            print(f"❌ Error guardando modelo: {e}")
            return False
    
    def load_model(self):
        """
        Cargar modelo previamente entrenado
        """
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"✅ Modelo cargado desde {self.model_path}")
                return True
            else:
                print(f"❌ Modelo no encontrado en {self.model_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False
    
    def predict(self, sensor_data):
        """
        Hacer predicción con datos de sensores
        """
        try:
            if self.model is None:
                print("❌ Modelo no cargado")
                return None
            
            # Preparar datos para predicción
            prediction_data = pd.DataFrame([sensor_data])
            
            # Agregar características adicionales
            current_time = datetime.now()
            prediction_data['hour'] = current_time.hour
            prediction_data['day_of_week'] = current_time.weekday()
            
            # Hacer predicción
            prediction = self.model.predict(prediction_data)[0]
            probability = self.model.predict_proba(prediction_data)[0]
            
            return {
                'needs_irrigation': bool(prediction),
                'confidence': float(max(probability)),
                'probability_irrigation': float(probability[1])
            }
            
        except Exception as e:
            print(f"❌ Error en predicción: {e}")
            return None
    
    def get_feature_importance(self):
        """
        Obtener importancia de características
        """
        try:
            if self.model is None:
                print("❌ Modelo no cargado")
                return None
            
            feature_names = self.features + ['hour', 'day_of_week']
            importance = self.model.feature_importances_
            
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            print("\n📊 Importancia de características:")
            print(importance_df)
            
            return importance_df
            
        except Exception as e:
            print(f"❌ Error obteniendo importancia: {e}")
            return None

def train_irrigation_model(csv_file='sensor_data.csv'):
    """
    Función principal para entrenar el modelo
    """
    print("🌱 Entrenando modelo de predicción de riego...")
    print("=" * 50)
    
    # Crear predictor
    predictor = IrrigationPredictor()
    
    # Cargar datos
    df = predictor.load_data(csv_file)
    if df is None:
        return False
    
    # Preparar características
    X, feature_columns = predictor.prepare_features(df)
    if X is None:
        return False
    
    # Crear etiquetas
    y = predictor.create_labels(df)
    if y is None:
        return False
    
    # Entrenar modelo
    if not predictor.train_model(X, y):
        return False
    
    # Guardar modelo
    if not predictor.save_model():
        return False
    
    # Mostrar importancia de características
    predictor.get_feature_importance()
    
    print("\n✅ Modelo entrenado exitosamente!")
    return True

def predict_irrigation_needs(sensor_data):
    """
    Función para hacer predicción con datos de sensores
    """
    predictor = IrrigationPredictor()
    
    # Cargar modelo
    if not predictor.load_model():
        return None
    
    # Hacer predicción
    return predictor.predict(sensor_data)

def generate_sample_data(num_samples=1000):
    """
    Generar datos de muestra para entrenamiento
    """
    print("📊 Generando datos de muestra...")
    
    np.random.seed(42)
    
    # Generar datos sintéticos
    data = {
        'timestamp': pd.date_range('2024-01-01', periods=num_samples, freq='H'),
        'temperature': np.random.normal(25, 5, num_samples),
        'humidity': np.random.normal(60, 15, num_samples),
        'soil_moisture': np.random.normal(50, 20, num_samples),
        'uv_index': np.random.normal(5, 2, num_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Asegurar que los valores estén en rangos realistas
    df['temperature'] = np.clip(df['temperature'], 10, 40)
    df['humidity'] = np.clip(df['humidity'], 20, 100)
    df['soil_moisture'] = np.clip(df['soil_moisture'], 0, 100)
    df['uv_index'] = np.clip(df['uv_index'], 0, 11)
    
    # Guardar datos
    df.to_csv('sample_sensor_data.csv', index=False)
    print(f"✅ Datos de muestra guardados: {len(df)} registros")
    
    return df

if __name__ == "__main__":
    """
    Ejemplo de uso del modelo de ML
    """
    print("🤖 Sistema de Predicción de Riego con ML")
    print("=" * 50)
    
    # Opción 1: Generar datos de muestra
    print("\n1. Generando datos de muestra...")
    generate_sample_data(500)
    
    # Opción 2: Entrenar modelo
    print("\n2. Entrenando modelo...")
    if train_irrigation_model('sample_sensor_data.csv'):
        print("✅ Modelo entrenado exitosamente!")
        
        # Opción 3: Hacer predicción
        print("\n3. Probando predicción...")
        sample_sensor_data = {
            'temperature': 28.5,
            'humidity': 45.0,
            'soil_moisture': 25.0,
            'uv_index': 7.2
        }
        
        prediction = predict_irrigation_needs(sample_sensor_data)
        if prediction:
            print(f"🌱 Predicción: {prediction}")
        else:
            print("❌ Error en predicción")
    else:
        print("❌ Error entrenando modelo")
