"""
Script de prueba para la API de ML
Prueba todos los endpoints de la API desplegada en Render
"""

import requests
import json
import time
from datetime import datetime

def test_api(base_url):
    """Probar todos los endpoints de la API"""
    print(f"🧪 Probando API en: {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🔍 Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ Model loaded: {data['model_loaded']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Model Info
    print("\n2. 📊 Model Info")
    try:
        response = requests.get(f"{base_url}/model-info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model type: {data['model_type']}")
            print(f"✅ Estimators: {data['n_estimators']}")
            print("✅ Feature importance:")
            for feature, importance in data['feature_importance'].items():
                print(f"   - {feature}: {importance:.3f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Single Prediction
    print("\n3. 🔮 Single Prediction")
    test_data = {
        "temperature": 28.5,
        "humidity": 45.0,
        "soil_moisture": 25.0,
        "uv_index": 7.2
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            prediction = data['prediction']
            print(f"✅ Needs irrigation: {prediction['needs_irrigation']}")
            print(f"✅ Confidence: {prediction['confidence']:.3f}")
            print(f"✅ Probability: {prediction['probability_irrigation']:.3f}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Batch Prediction
    print("\n4. 📦 Batch Prediction")
    batch_data = {
        "sensor_data": [
            {
                "temperature": 30.0,
                "humidity": 40.0,
                "soil_moisture": 20.0,
                "uv_index": 8.5
            },
            {
                "temperature": 25.0,
                "humidity": 60.0,
                "soil_moisture": 45.0,
                "uv_index": 5.0
            },
            {
                "temperature": 35.0,
                "humidity": 30.0,
                "soil_moisture": 15.0,
                "uv_index": 9.0
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/batch-predict",
            json=batch_data,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Predictions count: {data['count']}")
            for i, pred in enumerate(data['predictions']):
                if 'prediction' in pred:
                    p = pred['prediction']
                    print(f"   {i+1}. Needs irrigation: {p['needs_irrigation']} (conf: {p['confidence']:.3f})")
                else:
                    print(f"   {i+1}. Error: {pred.get('error', 'Unknown error')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Performance Test
    print("\n5. ⚡ Performance Test")
    start_time = time.time()
    successful_requests = 0
    total_requests = 10
    
    for i in range(total_requests):
        try:
            response = requests.post(
                f"{base_url}/predict",
                json=test_data,
                timeout=5
            )
            if response.status_code == 200:
                successful_requests += 1
        except:
            pass
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / total_requests
    
    print(f"✅ Successful requests: {successful_requests}/{total_requests}")
    print(f"✅ Total time: {total_time:.2f}s")
    print(f"✅ Average time per request: {avg_time:.2f}s")
    print(f"✅ Requests per second: {total_requests/total_time:.2f}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")

def test_local_api():
    """Probar API local"""
    print("🏠 Testing local API...")
    test_api("http://localhost:5000")

def test_render_api(render_url):
    """Probar API en Render"""
    print("🌐 Testing Render API...")
    test_api(render_url)

if __name__ == "__main__":
    print("🤖 ML API Test Suite")
    print("=" * 50)
    
    # Opción 1: Probar API local
    print("\n¿Quieres probar la API local? (y/n)")
    choice = input().lower()
    if choice == 'y':
        test_local_api()
    
    # Opción 2: Probar API en Render
    print("\n¿Quieres probar la API en Render? (y/n)")
    choice = input().lower()
    if choice == 'y':
        render_url = input("Ingresa la URL de tu API en Render: ").strip()
        if render_url:
            test_render_api(render_url)
        else:
            print("❌ URL no proporcionada")
    
    print("\n✅ Testing completed!")
