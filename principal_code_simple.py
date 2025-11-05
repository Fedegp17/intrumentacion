"""
Flask server para recibir datos del ESP32 y guardarlos en Supabase
"""

import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

# Intentar importar Supabase
SUPABASE_AVAILABLE = False
insert_sensor_data = None
get_latest_sensor_data = None

try:
    from supabase import create_client, Client
    import urllib3
    urllib3.disable_warnings()
    
    # Obtener credenciales de variables de entorno
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        SUPABASE_AVAILABLE = True
        
        def insert_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, uv_index, timestamp):
            """Inserta datos del sensor en Supabase"""
            try:
                data = {
                    'temperature1': temperature1,
                    'humidity1': humidity1,
                    'temperature2': temperature2,
                    'humidity2': humidity2,
                    'soil_moisture1': soil_moisture1,
                    'soil_moisture2': soil_moisture2,
                    'uv_index': uv_index,
                    'timestamp': timestamp
                }
                result = supabase.table('sensor_data').insert(data).execute()
                return True
            except Exception as e:
                return False
        
        def get_latest_sensor_data():
            """Obtiene los datos mas recientes del sensor desde Supabase"""
            try:
                result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(1).execute()
                if result.data and len(result.data) > 0:
                    return result.data[0]
                return None
            except Exception as e:
                return None
    else:
        pass
except Exception as e:
    pass

app = Flask(__name__)

# Global variables
esp32_data = {
    'sensor_data': {
        'temperature1': 0,
        'humidity1': 0,
        'temperature2': 0,
        'humidity2': 0,
        'soil_moisture1': 0,
        'soil_moisture2': 0,
        'uv_index': 0,
        'last_update': 'N/A'
    },
    'esp32_status': 'disconnected',
    'led_status': 'OFF',
    'led_state': 'off'
}

led_command_queue = None

def save_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, uv_index):
    """Save sensor data to Supabase"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if SUPABASE_AVAILABLE and insert_sensor_data:
        try:
            success = insert_sensor_data(
                float(temperature1), float(humidity1), 
                float(temperature2), float(humidity2),
                float(soil_moisture1), float(soil_moisture2),
                float(uv_index),
                timestamp
            )
            return success
        except Exception as e:
            return False
    return False

def load_latest_data_from_supabase():
    """Load latest sensor data from Supabase"""
    if SUPABASE_AVAILABLE and get_latest_sensor_data:
        try:
            latest = get_latest_sensor_data()
            if latest:
                esp32_data['sensor_data'] = {
                    'temperature1': float(latest.get('temperature1', 0) or 0),
                    'humidity1': float(latest.get('humidity1', 0) or 0),
                    'temperature2': float(latest.get('temperature2', 0) or 0),
                    'humidity2': float(latest.get('humidity2', 0) or 0),
                    'soil_moisture1': float(latest.get('soil_moisture1', 0) or 0),
                    'soil_moisture2': float(latest.get('soil_moisture2', 0) or 0),
                    'uv_index': float(latest.get('uv_index', 0) or 0),
                    'last_update': latest.get('timestamp', 'N/A')
                }
                esp32_data['esp32_status'] = 'connected'
                return True
        except Exception as e:
            pass
    return False

@app.route('/')
def home():
    """Main dashboard page"""
    try:
        load_latest_data_from_supabase()
    except Exception as e:
        pass
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema IoT - Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 25px;
        }
        .card-icon {
            width: 50px;
            height: 50px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 1.5rem;
            color: white;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { font-weight: 500; color: #666; }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; }
        .btn-warning { background: #ffc107; color: #333; }
        .btn-warning:hover { background: #e0a800; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sistema IoT - Dashboard</h1>
            <p>Monitoreo de Sensores en Tiempo Real</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                        <i class="fas fa-thermometer-half"></i>
                    </div>
                    <div>
                        <h3>DHT11 Sensor 1</h3>
                        <p>GPIO 2</p>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label">Temperatura</span>
                    <span class="metric-value" id="temperature1-value">{{ esp32_data.sensor_data.temperature1 }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="humidity1-value">{{ esp32_data.sensor_data.humidity1 }}</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                        <i class="fas fa-thermometer-half"></i>
                    </div>
                    <div>
                        <h3>DHT11 Sensor 2</h3>
                        <p>GPIO 4</p>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label">Temperatura</span>
                    <span class="metric-value" id="temperature2-value">{{ esp32_data.sensor_data.temperature2 }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="humidity2-value">{{ esp32_data.sensor_data.humidity2 }}</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #20c997);">
                        <i class="fas fa-seedling"></i>
                    </div>
                    <div>
                        <h3>Humedad de Suelo 1</h3>
                        <p>GPIO 35</p>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="soil1-value">{{ esp32_data.sensor_data.soil_moisture1 }}</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #20c997);">
                        <i class="fas fa-seedling"></i>
                    </div>
                    <div>
                        <h3>Humedad de Suelo 2</h3>
                        <p>GPIO 34</p>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="soil2-value">{{ esp32_data.sensor_data.soil_moisture2 }}</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #ffc107, #e0a800);">
                        <i class="fas fa-sun"></i>
                    </div>
                    <div>
                        <h3>Sensor UV</h3>
                        <p>GPIO 33</p>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label">UV Index</span>
                    <span class="metric-value" id="uv-value">{{ esp32_data.sensor_data.uv_index }}</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #6f42c1, #5a32a3);">
                        <i class="fas fa-sliders-h"></i>
                    </div>
                    <div>
                        <h3>Panel de Control</h3>
                        <p>Acciones disponibles</p>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="btn btn-success" onclick="fetchData()" style="width: 100%;">
                        <i class="fas fa-sync-alt"></i> Actualizar Datos Ahora
                    </button>
                    <button class="btn btn-warning" onclick="testLED('on')" style="width: 100%;">
                        <i class="fas fa-lightbulb"></i> Probar LED - Encender
                    </button>
                    <button class="btn btn-warning" onclick="testLED('off')" style="width: 100%;">
                        <i class="fas fa-lightbulb"></i> Probar LED - Apagar
                    </button>
                    <button class="btn btn-warning" onclick="testLED('blink')" style="width: 100%;">
                        <i class="fas fa-lightbulb"></i> Probar LED - Parpadear
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function fetchData() {
            fetch('/latest-data')
                .then(response => response.json())
                .then(data => {
                    if (data.sensor_data) {
                        updateSensorData(data.sensor_data);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function updateSensorData(sensorData) {
            document.getElementById('temperature1-value').textContent = sensorData.temperature1.toFixed(1);
            document.getElementById('humidity1-value').textContent = sensorData.humidity1.toFixed(1);
            document.getElementById('temperature2-value').textContent = sensorData.temperature2.toFixed(1);
            document.getElementById('humidity2-value').textContent = sensorData.humidity2.toFixed(1);
            document.getElementById('soil1-value').textContent = sensorData.soil_moisture1.toFixed(1);
            document.getElementById('soil2-value').textContent = sensorData.soil_moisture2.toFixed(1);
            document.getElementById('uv-value').textContent = sensorData.uv_index.toFixed(1);
        }
        
        function testLED(action) {
            fetch('/led-control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action })
            })
                .then(response => response.json())
                .then(data => console.log('LED:', data))
                .catch(error => console.error('Error:', error));
        }
        
        // Auto-refresh cada 5 minutos
        setInterval(fetchData, 300000);
        
        // Inicializar datos
        document.addEventListener('DOMContentLoaded', function() {
            updateSensorData({
                temperature1: {{ esp32_data.sensor_data.temperature1 }},
                humidity1: {{ esp32_data.sensor_data.humidity1 }},
                temperature2: {{ esp32_data.sensor_data.temperature2 }},
                humidity2: {{ esp32_data.sensor_data.humidity2 }},
                soil_moisture1: {{ esp32_data.sensor_data.soil_moisture1 }},
                soil_moisture2: {{ esp32_data.sensor_data.soil_moisture2 }},
                uv_index: {{ esp32_data.sensor_data.uv_index }}
            });
            fetchData();
        });
    </script>
</body>
</html>
    ''', esp32_data=esp32_data)

@app.route('/data', methods=['GET', 'POST'])
def receive_sensor_data():
    """Receive sensor data from ESP32"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            temperature1 = data.get('temperature1')
            humidity1 = data.get('humidity1')
            temperature2 = data.get('temperature2')
            humidity2 = data.get('humidity2')
            soil_moisture1 = data.get('soil_moisture1')
            soil_moisture2 = data.get('soil_moisture2')
            uv_index = data.get('uv_index')

            if temperature1 is None or humidity1 is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing sensor data. Required: temperature1, humidity1'
                }), 400

            if temperature2 is None: temperature2 = 0.0
            if humidity2 is None: humidity2 = 0.0
            if soil_moisture1 is None: soil_moisture1 = 0.0
            if soil_moisture2 is None: soil_moisture2 = 0.0
            if uv_index is None: uv_index = 0.0

            # Guardar en Supabase
            save_success = save_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, uv_index)

            esp32_data['sensor_data'] = {
                'temperature1': temperature1,
                'humidity1': humidity1,
                'temperature2': temperature2,
                'humidity2': humidity2,
                'soil_moisture1': soil_moisture1,
                'soil_moisture2': soil_moisture2,
                'uv_index': uv_index,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            esp32_data['esp32_status'] = 'connected'

            response = {
                'status': 'success',
                'message': 'Sensor data received and saved',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data': esp32_data['sensor_data']
            }
            return jsonify(response)
        else:
            return jsonify(esp32_data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/latest-data')
def latest_data():
    """Get latest sensor data from Supabase"""
    try:
        load_latest_data_from_supabase()
        return jsonify({
            'status': 'success',
            'sensor_data': esp32_data['sensor_data'],
            'esp32_status': esp32_data['esp32_status']
        })
    except Exception as e:
        return jsonify({
            'status': 'success',
            'sensor_data': esp32_data['sensor_data'],
            'esp32_status': esp32_data.get('esp32_status', 'disconnected')
        })

@app.route('/led-control', methods=['POST'])
def led_control():
    """Control LED on ESP32"""
    global led_command_queue
    try:
        data = request.get_json() or {}
        action = data.get('action', 'off')
        led_command_queue = action
        
        if action == 'on':
            esp32_data['led_status'] = 'ON'
            esp32_data['led_state'] = 'on'
        elif action == 'off':
            esp32_data['led_status'] = 'OFF'
            esp32_data['led_state'] = 'off'
        elif action == 'blink':
            esp32_data['led_status'] = 'BLINKING'
            esp32_data['led_state'] = 'blink'
        
        return jsonify({
            'status': 'success',
            'message': f'LED {action} command sent',
            'led_status': esp32_data['led_status'],
            'led_state': esp32_data['led_state']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/led-status')
def led_status():
    """Get LED status and return commands for ESP32"""
    global led_command_queue
    
    response = {
        'status': 'success',
        'led_status': esp32_data['led_status'],
        'led_state': esp32_data['led_state']
    }
    
    if led_command_queue is not None:
        response['led_command'] = led_command_queue
        led_command_queue = None
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

