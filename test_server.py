#!/usr/bin/env python3
"""
Test Server for IoT System
Prueba las funcionalidades del sistema IoT sin hardware real
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import random
import time
import threading

app = Flask(__name__)

# Simulated ESP32 data
esp32_data = {
    'last_connection': None,
    'ip_address': None,
    'status': 'connected',
    'led_state': False,
    'led_status': 'OFF',
    'connection_count': 0,
    'sensor_data': {
        'humidity': 65.0,
        'temperature': 25.5,
        'last_update': None
    },
    'last_heartbeat': None
}

# Simulated sensor data storage
sensor_data_history = []

def generate_test_data():
    """Generate realistic test sensor data"""
    # Generate temperature between 20-40°C with occasional high values
    if random.random() < 0.1:  # 10% chance of high temperature
        temperature = round(random.uniform(35, 42), 1)
    else:
        temperature = round(random.uniform(20, 35), 1)
    
    # Generate humidity between 40-80%
    humidity = round(random.uniform(40, 80), 1)
    
    return temperature, humidity

def simulate_sensor_reading():
    """Simulate periodic sensor readings"""
    while True:
        temperature, humidity = generate_test_data()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update sensor data
        esp32_data['sensor_data'] = {
            'humidity': humidity,
            'temperature': temperature,
            'last_update': timestamp
        }
        
        # Store in history
        sensor_data_history.append({
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity
        })
        
        # Keep only last 50 readings
        if len(sensor_data_history) > 50:
            sensor_data_history.pop(0)
        
        print(f"🌡️ Simulated reading: T={temperature}°C, H={humidity}%")
        
        # Update connection status
        esp32_data['last_connection'] = timestamp
        esp32_data['last_heartbeat'] = timestamp
        esp32_data['status'] = 'connected'
        esp32_data['connection_count'] += 1
        
        time.sleep(30)  # Simulate reading every 30 seconds

@app.route('/')
def home():
    """Test home page"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <title>🧪 Test Server - Sistema IoT</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
                border-radius: 15px;
            }}
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .status-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                border-left: 5px solid #28a745;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .status-card h3 {{
                margin: 0 0 10px 0;
                color: #333;
            }}
            .status-value {{
                font-size: 1.5em;
                font-weight: bold;
                color: #28a745;
            }}
            .controls {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            .btn {{
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                color: white;
            }}
            .btn-primary {{ background: linear-gradient(135deg, #007bff, #0056b3); }}
            .btn-success {{ background: linear-gradient(135deg, #28a745, #20c997); }}
            .btn-danger {{ background: linear-gradient(135deg, #dc3545, #c82333); }}
            .btn-warning {{ background: linear-gradient(135deg, #ffc107, #e0a800); }}
            .btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
            .data-table {{
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .data-table table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .data-table th {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px;
                text-align: left;
            }}
            .data-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }}
            .data-table tr:hover {{
                background: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧪 Test Server - Sistema IoT</h1>
                <p>Servidor de pruebas para verificar funcionalidades del sistema</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>📡 Estado del Sistema</h3>
                    <div class="status-value">{esp32_data['status'].upper()}</div>
                </div>
                <div class="status-card">
                    <h3>🌡️ Temperatura</h3>
                    <div class="status-value">{esp32_data['sensor_data']['temperature']}°C</div>
                </div>
                <div class="status-card">
                    <h3>💧 Humedad</h3>
                    <div class="status-value">{esp32_data['sensor_data']['humidity']}%</div>
                </div>
                <div class="status-card">
                    <h3>💡 LED</h3>
                    <div class="status-value">{esp32_data['led_status']}</div>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn btn-primary" onclick="testSensor()">🌡️ Test Sensor</button>
                <button class="btn btn-success" onclick="testLED('on')">💡 LED ON</button>
                <button class="btn btn-danger" onclick="testLED('off')">🔴 LED OFF</button>
                <button class="btn btn-warning" onclick="testAlert()">🔥 Test Alert</button>
                <button class="btn btn-primary" onclick="generateData()">📊 Generate Data</button>
                <button class="btn btn-success" onclick="location.reload()">🔄 Refresh</button>
            </div>
            
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Temperatura</th>
                            <th>Humedad</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody id="dataTable">
                        <!-- Data will be populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            function testSensor() {{
                fetch('/test-sensor', {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    alert('✅ Test sensor: ' + data.message);
                    location.reload();
                }});
            }}
            
            function testLED(action) {{
                fetch('/test-led', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{action: action}})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert('💡 LED test: ' + data.message);
                    location.reload();
                }});
            }}
            
            function testAlert() {{
                fetch('/test-alert', {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    alert('🔥 Alert test: ' + data.message);
                    location.reload();
                }});
            }}
            
            function generateData() {{
                fetch('/generate-data', {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    alert('📊 Data generated: ' + data.message);
                    location.reload();
                }});
            }}
            
            function loadData() {{
                fetch('/get-data')
                .then(response => response.json())
                .then(data => {{
                    const table = document.getElementById('dataTable');
                    table.innerHTML = '';
                    data.forEach(item => {{
                        const row = table.insertRow();
                        row.innerHTML = `
                            <td>${{item.timestamp}}</td>
                            <td style="color: #dc3545; font-weight: bold;">${{item.temperature}}°C</td>
                            <td style="color: #17a2b8; font-weight: bold;">${{item.humidity}}%</td>
                            <td>${{item.temperature > 35 ? '🔥 ALERTA' : '✅ Normal'}}</td>
                        `;
                    }});
                }});
            }}
            
            // Load data on page load
            document.addEventListener('DOMContentLoaded', loadData);
            
            // Auto-refresh every 10 seconds
            setInterval(loadData, 10000);
        </script>
    </body>
    </html>
    """

@app.route('/data', methods=['POST'])
def receive_sensor_data():
    """Simulate receiving sensor data"""
    try:
        data = request.get_json() or {}
        temperature = data.get('temperature', 25.0)
        humidity = data.get('humidity', 60.0)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update sensor data
        esp32_data['sensor_data'] = {
            'humidity': humidity,
            'temperature': temperature,
            'last_update': timestamp
        }
        
        # Store in history
        sensor_data_history.append({
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity
        })
        
        # Update connection status
        esp32_data['last_connection'] = timestamp
        esp32_data['last_heartbeat'] = timestamp
        esp32_data['status'] = 'connected'
        esp32_data['connection_count'] += 1
        
        print(f"📥 Received test data: T={temperature}°C, H={humidity}%")
        
        return jsonify({
            'status': 'success',
            'message': 'Test sensor data received',
            'timestamp': timestamp,
            'data': {'temperature': temperature, 'humidity': humidity}
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/data', methods=['GET'])
def get_esp32_data():
    """Get current ESP32 data"""
    return jsonify({
        'status': 'success',
        'esp32_status': esp32_data['status'],
        'last_connection': esp32_data['last_connection'],
        'temperature': esp32_data['sensor_data']['temperature'],
        'humidity': esp32_data['sensor_data']['humidity'],
        'led_state': esp32_data['led_state'],
        'led_status': esp32_data['led_status']
    })

@app.route('/get-data')
def get_data():
    """Get sensor data history"""
    return jsonify(sensor_data_history[-20:])  # Last 20 readings

@app.route('/test-sensor', methods=['POST'])
def test_sensor():
    """Test sensor reading"""
    temperature, humidity = generate_test_data()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update sensor data
    esp32_data['sensor_data'] = {
        'humidity': humidity,
        'temperature': temperature,
        'last_update': timestamp
    }
    
    # Store in history
    sensor_data_history.append({
        'timestamp': timestamp,
        'temperature': temperature,
        'humidity': humidity
    })
    
    return jsonify({
        'status': 'success',
        'message': f'Test sensor reading: T={temperature}°C, H={humidity}%',
        'data': {'temperature': temperature, 'humidity': humidity}
    })

@app.route('/test-led', methods=['POST'])
def test_led():
    """Test LED control"""
    data = request.get_json()
    action = data.get('action', 'toggle')
    
    if action == 'on':
        esp32_data['led_state'] = True
        esp32_data['led_status'] = 'ON'
    elif action == 'off':
        esp32_data['led_state'] = False
        esp32_data['led_status'] = 'OFF'
    elif action == 'blink':
        esp32_data['led_state'] = True
        esp32_data['led_status'] = 'BLINKING'
    elif action == 'toggle':
        esp32_data['led_state'] = not esp32_data['led_state']
        esp32_data['led_status'] = 'ON' if esp32_data['led_state'] else 'OFF'
    
    return jsonify({
        'status': 'success',
        'message': f'LED test: {action} -> {esp32_data["led_status"]}',
        'led_state': esp32_data['led_state'],
        'led_status': esp32_data['led_status']
    })

@app.route('/test-alert', methods=['POST'])
def test_alert():
    """Test temperature alert"""
    # Generate high temperature
    temperature = round(random.uniform(36, 42), 1)
    humidity = round(random.uniform(60, 80), 1)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update sensor data
    esp32_data['sensor_data'] = {
        'humidity': humidity,
        'temperature': temperature,
        'last_update': timestamp
    }
    
    # Store in history
    sensor_data_history.append({
        'timestamp': timestamp,
        'temperature': temperature,
        'humidity': humidity
    })
    
    return jsonify({
        'status': 'success',
        'message': f'🔥 ALERTA: Temperatura crítica {temperature}°C (supera 35°C)',
        'data': {'temperature': temperature, 'humidity': humidity, 'alert': True}
    })

@app.route('/generate-data', methods=['POST'])
def generate_data():
    """Generate multiple test data points"""
    count = 0
    for i in range(10):
        temperature, humidity = generate_test_data()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sensor_data_history.append({
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity
        })
        count += 1
        time.sleep(0.1)  # Small delay between generations
    
    return jsonify({
        'status': 'success',
        'message': f'Generated {count} test data points',
        'count': count
    })

if __name__ == '__main__':
    print("🧪 Starting Test Server...")
    print("📡 Test server will be available at: http://localhost:5001")
    print("🔧 This server simulates ESP32 functionality for testing")
    print("🌡️ Simulating sensor readings every 30 seconds...")
    
    # Start sensor simulation thread
    sensor_thread = threading.Thread(target=simulate_sensor_reading, daemon=True)
    sensor_thread.start()
    
    # Run test server
    app.run(host='0.0.0.0', port=5001, debug=True)
