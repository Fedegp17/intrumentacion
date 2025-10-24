"""
API Flask para el Modelo de Machine Learning
Sistema IoT - Predicción de Riego

Este archivo contiene la API REST para el modelo de ML
desplegado en Render.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import io
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for the model
model = None
model_loaded = False

def load_model():
    """Load the trained ML model"""
    global model, model_loaded
    try:
        # Try to load the model from file
        if os.path.exists('irrigation_model.pkl'):
            model = joblib.load('irrigation_model.pkl')
            model_loaded = True
            print("✅ Model loaded successfully")
            return True
        else:
            print("⚠️ Model file not found, will train a new one")
            return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def train_new_model():
    """Train a new model with sample data"""
    global model, model_loaded
    try:
        print("🌱 Training new model...")
        
        # Generate sample data for training
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic sensor data
        data = {
            'temperature': np.random.normal(25, 5, n_samples),
            'humidity': np.random.normal(60, 15, n_samples),
            'soil_moisture': np.random.normal(50, 20, n_samples),
            'uv_index': np.random.normal(5, 2, n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Ensure realistic ranges
        df['temperature'] = np.clip(df['temperature'], 10, 40)
        df['humidity'] = np.clip(df['humidity'], 20, 100)
        df['soil_moisture'] = np.clip(df['soil_moisture'], 0, 100)
        df['uv_index'] = np.clip(df['uv_index'], 0, 11)
        
        # Create labels (needs irrigation if soil moisture < 30%)
        df['needs_irrigation'] = (df['soil_moisture'] < 30).astype(int)
        
        # Prepare features
        feature_columns = ['temperature', 'humidity', 'soil_moisture', 'uv_index', 'hour', 'day_of_week']
        X = df[feature_columns]
        y = df['needs_irrigation']
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        model.fit(X, y)
        
        # Save model
        joblib.dump(model, 'irrigation_model.pkl')
        model_loaded = True
        
        print("✅ New model trained and saved successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error training model: {e}")
        return False

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': '🌱 IoT Irrigation Prediction API',
        'version': '1.0.0',
        'status': 'active',
        'model_loaded': model_loaded,
        'endpoints': {
            '/predict': 'POST - Make irrigation prediction',
            '/train': 'POST - Train new model',
            '/model-info': 'GET - Get model information',
            '/health': 'GET - Health check'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model_loaded
    })

@app.route('/model-info')
def model_info():
    """Get model information"""
    if not model_loaded:
        return jsonify({
        'status': 'error',
        'message': 'Model not loaded'
    }), 400
    
    try:
        # Get feature importance
        feature_names = ['temperature', 'humidity', 'soil_moisture', 'uv_index', 'hour', 'day_of_week']
        importance = model.feature_importances_
        
        importance_dict = dict(zip(feature_names, importance.tolist()))
        
        return jsonify({
            'status': 'success',
            'model_type': 'RandomForestClassifier',
            'n_estimators': model.n_estimators,
            'max_depth': model.max_depth,
            'feature_importance': importance_dict,
            'model_loaded': model_loaded
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/predict', methods=['POST'])
def predict_irrigation():
    """Make irrigation prediction"""
    if not model_loaded:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded. Please train a model first.'
        }), 400
    
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['temperature', 'humidity', 'soil_moisture', 'uv_index']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Prepare features
        current_time = datetime.now()
        features = {
            'temperature': float(data['temperature']),
            'humidity': float(data['humidity']),
            'soil_moisture': float(data['soil_moisture']),
            'uv_index': float(data['uv_index']),
            'hour': current_time.hour,
            'day_of_week': current_time.weekday()
        }
        
        # Create DataFrame for prediction
        prediction_data = pd.DataFrame([features])
        
        # Make prediction
        prediction = model.predict(prediction_data)[0]
        probability = model.predict_proba(prediction_data)[0]
        
        # Prepare response
        response = {
            'status': 'success',
            'prediction': {
                'needs_irrigation': bool(prediction),
                'confidence': float(max(probability)),
                'probability_irrigation': float(probability[1])
            },
            'input_data': features,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/train', methods=['POST'])
def train_model():
    """Train a new model"""
    try:
        # Get training data from request (optional)
        data = request.get_json()
        
        if data and 'training_data' in data:
            # Use provided training data
            print("📊 Using provided training data")
            # TODO: Implement custom training data processing
            pass
        else:
            # Use sample data
            print("📊 Using sample training data")
        
        # Train new model
        success = train_new_model()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Model trained successfully',
                'model_loaded': model_loaded,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to train model'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """Make batch predictions"""
    if not model_loaded:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded'
        }), 400
    
    try:
        data = request.get_json()
        
        if not data or 'sensor_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No sensor data provided'
            }), 400
        
        sensor_data = data['sensor_data']
        
        if not isinstance(sensor_data, list):
            return jsonify({
                'status': 'error',
                'message': 'Sensor data must be a list'
            }), 400
        
        # Process each sensor reading
        predictions = []
        current_time = datetime.now()
        
        for reading in sensor_data:
            try:
                # Prepare features
                features = {
                    'temperature': float(reading.get('temperature', 0)),
                    'humidity': float(reading.get('humidity', 0)),
                    'soil_moisture': float(reading.get('soil_moisture', 0)),
                    'uv_index': float(reading.get('uv_index', 0)),
                    'hour': current_time.hour,
                    'day_of_week': current_time.weekday()
                }
                
                # Create DataFrame for prediction
                prediction_data = pd.DataFrame([features])
                
                # Make prediction
                prediction = model.predict(prediction_data)[0]
                probability = model.predict_proba(prediction_data)[0]
                
                predictions.append({
                    'input': reading,
                    'prediction': {
                        'needs_irrigation': bool(prediction),
                        'confidence': float(max(probability)),
                        'probability_irrigation': float(probability[1])
                    }
                })
                
            except Exception as e:
                predictions.append({
                    'input': reading,
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'count': len(predictions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Initialize model on startup
if __name__ == '__main__':
    print("🤖 Starting ML API Server...")
    
    # Try to load existing model
    if not load_model():
        # Train new model if none exists
        print("🌱 Training new model...")
        train_new_model()
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Server starting on port {port}")
    print(f"📊 Model loaded: {model_loaded}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
