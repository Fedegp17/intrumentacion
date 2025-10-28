from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import os
import json
import csv
from supabase_config import get_supabase_client, insert_sensor_data, get_sensor_data, get_chart_data

app = Flask(__name__)

# Global variables to store ESP32 data
esp32_data = {
    'sensor_data': {
        'humidity': 0,
        'temperature': 0,
        'uv_index': 0,
        'last_update': 'N/A'
    },
    'esp32_status': 'disconnected',
    'led_status': 'OFF',
    'led_state': 'off'
}

# Configuration
SENSOR_DATA_FILE = 'dht11_data.csv'
SUPABASE_AVAILABLE = True

try:
    supabase = get_supabase_client()
    print("Supabase configurado correctamente")
except Exception as e:
    print(f"Error configurando Supabase: {e}")
    SUPABASE_AVAILABLE = False

def save_sensor_data(humidity, temperature, uv_index):
    """Save sensor data to CSV file and Supabase"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if we're in Vercel (read-only filesystem)
    is_vercel = os.environ.get('VERCEL') == '1'

    # Save to CSV (backup) - only if not in Vercel
    if not is_vercel:
        try:
            file_exists = os.path.exists(SENSOR_DATA_FILE)

            with open(SENSOR_DATA_FILE, 'a', newline='') as f:
                if not file_exists:
                    f.write('timestamp,temperature,humidity,uv_index\n')

                # Write data row
                f.write(f'{timestamp},{temperature},{humidity},{uv_index}\n')
            print(f"CSV backup saved: T={temperature}C, H={humidity}%, UV={uv_index}")
        except Exception as e:
            print(f"Error saving CSV: {e}")
    else:
        print("Running on Vercel - skipping CSV save")

    # Save to Supabase (primary storage) if available
    if SUPABASE_AVAILABLE:
        try:
            success = insert_sensor_data(temperature, humidity, timestamp, uv_index)
            if success:
                print(f"Datos guardados en Supabase: T={temperature}C, H={humidity}%, UV={uv_index}")
            else:
                print(f"Error guardando en Supabase")
        except Exception as e:
            print(f"Error con Supabase: {e}")

    print(f"Sensor data saved: T={temperature}C, H={humidity}%, UV={uv_index}")

@app.route('/')
def home():
    """Main dashboard page"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema IoT Inteligente - Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

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

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }

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

        .card-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #333;
            margin: 0;
        }

        .card-subtitle {
            font-size: 0.9rem;
            color: #666;
            margin: 5px 0 0 0;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #007bff;
        }

        .metric-label {
            font-weight: 500;
            color: #555;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
        }

        .temperature { border-left-color: #dc3545; }
        .humidity { border-left-color: #17a2b8; }
        .uv { border-left-color: #ffc107; }

        .temperature .metric-value { color: #dc3545; }
        .humidity .metric-value { color: #17a2b8; }
        .uv .metric-value { color: #ffc107; }

        .btn {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95rem;
            margin: 5px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.3);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .btn-danger {
            background: linear-gradient(135deg, #dc3545, #c82333);
        }

        .btn-success {
            background: linear-gradient(135deg, #28a745, #20c997);
        }

        .btn-warning {
            background: linear-gradient(135deg, #ffc107, #e0a800);
        }

        .status-indicator {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }

        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
            background: #dc3545;
        }

        .status-text {
            font-weight: 500;
            color: #333;
        }

        .alert {
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: none;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        .alert-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .alert-text {
            font-weight: 600;
            font-size: 1.1rem;
        }

        .alert-dismiss {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }

        .footer-content p {
            margin: 5px 0;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1>Sistema IoT Inteligente</h1>
            <p>Monitoreo y Control en Tiempo Real</p>
        </header>

        <!-- Temperature Alert -->
        <div id="temperature-alert" class="alert">
            <div class="alert-content">
                <div class="alert-text">
                    <i class="fas fa-exclamation-triangle"></i>
                    Alerta de Temperatura: <span id="alert-temp-value">0</span>C - Supera los 35C!
                </div>
                <button class="alert-dismiss" onclick="dismissAlert()">
                    <i class="fas fa-times"></i> Descartar
                </button>
            </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="dashboard-grid">
            <!-- Sensor Data Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #20c997);">
                        <i class="fas fa-thermometer-half"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Datos del Sensor</h3>
                        <p class="card-subtitle">Temperatura, Humedad y UV Index</p>
                    </div>
                </div>
                
                <div class="metric temperature">
                    <span class="metric-label">Temperatura</span>
                    <span class="metric-value" id="temperature-value">{{ esp32_data.sensor_data.temperature }}</span>
                </div>
                
                <div class="metric humidity">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="humidity-value">{{ esp32_data.sensor_data.humidity }}</span>
                </div>
                
                <div class="metric uv">
                    <span class="metric-label">UV Index</span>
                    <span class="metric-value" id="uv-value">{{ esp32_data.sensor_data.uv_index }}</span>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <button class="btn btn-success" onclick="testSensor()">
                        <i class="fas fa-play"></i> Test Sensor
                    </button>
                </div>
            </div>

            <!-- Connection Status Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #17a2b8, #138496);">
                        <i class="fas fa-wifi"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Estado de Conexion</h3>
                        <p class="card-subtitle">Estado del ESP32</p>
                    </div>
                </div>
                
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span class="status-text" id="connection-status">Desconectado</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Ultima Actualizacion</span>
                    <div class="metric-value" id="last-update" style="font-size: 1rem;">{{ esp32_data.sensor_data.last_update }}</div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Proxima Lectura</span>
                    <div class="metric-value" id="next-reading" style="font-size: 1.25rem;">1 hora</div>
                </div>
            </div>
            
        </div>
        
        <!-- Footer -->
        <footer class="footer">
            <div class="footer-content">
                <p>&copy; 2024 Sistema IoT Inteligente - Monitoreo y Control en Tiempo Real</p>
                <p>Desarrollado para Instrumentacion y Medicion</p>
            </div>
        </footer>

        <script>
            // Check temperature alert
            function checkTemperatureAlert() {
                const temperature = parseFloat(document.getElementById('temperature-value').textContent);
                const alertContainer = document.getElementById('temperature-alert');
                const alertTempValue = document.getElementById('alert-temp-value');
                
                if (!isNaN(temperature) && temperature > 35) {
                    alertContainer.style.display = 'block';
                    alertTempValue.textContent = temperature;
                    
                    // Play alert sound if supported
                    playAlertSound();
                    
                    // Show browser notification
                    showBrowserNotification(temperature);
                    
                    console.log('ALERTA: Temperatura critica detectada:', temperature + 'C');
                } else {
                    alertContainer.style.display = 'none';
                }
            }
            
            // Dismiss alert
            function dismissAlert() {
                const alertContainer = document.getElementById('temperature-alert');
                alertContainer.style.display = 'none';
                console.log('Alerta de temperatura descartada por el usuario');
            }
            
            // Play alert sound
            function playAlertSound() {
                try {
                    // Create a simple beep sound using Web Audio API
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2);
                    
                    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
                    
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.5);
                } catch (error) {
                    console.log('No se pudo reproducir el sonido de alerta');
                }
            }
            
            // Show browser notification
            function showBrowserNotification(temperature) {
                if ('Notification' in window) {
                    if (Notification.permission === 'granted') {
                        new Notification('Alerta de Temperatura', {
                            body: `Temperatura critica: ${temperature}C - Supera los 35C!`,
                            icon: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzIiIGN5PSIzMiIgcj0iMzIiIGZpbGw9IiNmZjY2NjYiLz4KPHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4PSIxNiIgeT0iMTYiPgo8cGF0aCBkPSJNMTIgMkMxMy4xIDIgMTQgMi45IDE0IDRWMTRMMTguNSA2LjVDMTguOSA1LjkgMTkuNSA1LjUgMjAgNUMyMC41IDQuNSAyMC4xIDMuNSAxOSAzLjVDMTguNSA0IDE3LjUgNC41IDE2IDVWMTRDMTYgMTUuMSAxNS4xIDE2IDE0IDE2SDEwQzguOSAxNiA4IDE1LjEgOCAxNFY0QzggMi45IDguOSAyIDEwIDJIMTJaTTEyIDIwQzEzLjEgMjAgMTQgMjAuOSAxNCAyMlMxMy4xIDI0IDEyIDI0IDEwIDIzLjEgMTAgMjIgMTAuOSAyMCAxMiAyMFoiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo8L3N2Zz4K',
                            tag: 'temperature-alert'
                        });
                    } else if (Notification.permission !== 'denied') {
                        Notification.requestPermission().then(permission => {
                            if (permission === 'granted') {
                                showBrowserNotification(temperature);
                            }
                        });
                    }
                }
            }
            
            // Test alert function
            function testAlert() {
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = 'Sending...';

                fetch('/test-alert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Alerta de prueba enviada! Temperatura: 38.5C');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error: ' + error);
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.textContent = 'Test Alert';
                });
            }

            // LED Control Functions
            function controlLED(action) {
                const buttons = document.querySelectorAll('.btn');
                buttons.forEach(btn => btn.disabled = true);
                
                fetch('/led-control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ action: action })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        updateLEDStatus(data.led_status, data.led_state);
                        console.log('LED Control:', data.message);
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error: ' + error);
                })
                .finally(() => {
                    buttons.forEach(btn => btn.disabled = false);
                });
            }
            
            // Sensor Test Function
            function testSensor() {
                const button = event.target;
                button.disabled = true;
                button.textContent = 'Requesting...';
                
                fetch('/test-sensor', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('Sensor Test:', data.message);
                        alert('Sensor test request sent! Check the indicators for new data.');
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error: ' + error);
                })
                .finally(() => {
                    button.disabled = false;
                    button.textContent = 'Test Sensor';
                });
            }

            function updateLEDStatus(status, state) {
                const statusDisplay = document.getElementById('led-status-display');
                
                statusDisplay.textContent = status;
                
                // Update colors based on status
                if (status === 'ON') {
                    statusDisplay.style.color = '#28a745';
                } else if (status === 'BLINKING') {
                    statusDisplay.style.color = '#ffc107';
                } else {
                    statusDisplay.style.color = '#6c757d';
                }
            }

            function loadLEDStatus() {
                fetch('/led-status')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        updateLEDStatus(data.led_status, data.led_state);
                    }
                })
                .catch(error => {
                    console.log('Error loading LED status:', error);
                });
            }

            function checkConnectionStatus() {
                fetch('/data')
                .then(response => response.json())
                .then(data => {
                    updateConnectionStatus(data);
                })
                .catch(error => {
                    console.log('Error checking connection:', error);
                });
            }

            function updateConnectionStatus(data) {
                const statusElement = document.getElementById('connection-status');
                const statusDot = document.querySelector('.status-dot');
                
                if (data.esp32_status === 'connected') {
                    statusElement.textContent = 'Conectado';
                    statusDot.style.background = '#28a745';
                } else {
                    statusElement.textContent = 'Desconectado';
                    statusDot.style.background = '#dc3545';
                }
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                // Check temperature alert
                checkTemperatureAlert();
                
                // Load LED status
                loadLEDStatus();
                
                // Check connection status periodically
                setInterval(checkConnectionStatus, 5000); // Every 5 seconds
                
                // Auto-refresh every hour
                setInterval(() => {
                    location.reload();
                }, 3600000);
            });
        </script>
    </body>
</html>
    ''')

@app.route('/data', methods=['GET', 'POST'])
def receive_sensor_data():
    """Receive sensor data from ESP32"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            humidity = data.get('humidity')
            temperature = data.get('temperature')
            uv_index = data.get('uv_index', 0)

            if humidity is None or temperature is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing sensor data. Required: humidity, temperature'
                }), 400

            save_sensor_data(humidity, temperature, uv_index)

            esp32_data['sensor_data'] = {
                'humidity': humidity,
                'temperature': temperature,
                'uv_index': uv_index,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            esp32_data['esp32_status'] = 'connected'

            response = {
                'status': 'success',
                'message': 'Sensor data received and saved',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data': {
                    'humidity': humidity,
                    'temperature': temperature,
                    'uv_index': uv_index
                }
            }
            return jsonify(response)
        else:
            # GET request - return current data
            return jsonify(esp32_data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test-sensor', methods=['POST'])
def test_sensor():
    """Test sensor endpoint"""
    try:
        data = request.get_json() or {}
        
        # Simulate sensor test
        test_data = {
            'humidity': 45.2,
            'temperature': 23.8,
            'uv_index': 3.5
        }
        
        save_sensor_data(test_data['humidity'], test_data['temperature'], test_data['uv_index'])
        
        esp32_data['sensor_data'] = {
            'humidity': test_data['humidity'],
            'temperature': test_data['temperature'],
            'uv_index': test_data['uv_index'],
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        esp32_data['esp32_status'] = 'connected'
        
        return jsonify({
            'status': 'success',
            'message': 'Sensor test completed successfully',
            'data': test_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test-alert', methods=['POST'])
def test_alert():
    """Test alert endpoint"""
    try:
        # Simulate high temperature alert
        test_data = {
            'humidity': 30.0,
            'temperature': 38.5,
            'uv_index': 8.2
        }
        
        save_sensor_data(test_data['humidity'], test_data['temperature'], test_data['uv_index'])
        
        esp32_data['sensor_data'] = {
            'humidity': test_data['humidity'],
            'temperature': test_data['temperature'],
            'uv_index': test_data['uv_index'],
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        esp32_data['esp32_status'] = 'connected'
        
        return jsonify({
            'status': 'success',
            'message': 'Alert test completed - High temperature simulated',
            'data': test_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/led-control', methods=['POST'])
def led_control():
    """Control LED on ESP32"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'off')
        
        # Simulate LED control
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
    """Get LED status"""
    return jsonify({
        'status': 'success',
        'led_status': esp32_data['led_status'],
        'led_state': esp32_data['led_state']
    })

@app.route('/chart-data')
def chart_data():
    """Get chart data from Supabase"""
    try:
        if SUPABASE_AVAILABLE:
            chart_data = get_chart_data(limit=50)
            return jsonify(chart_data)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Supabase not available'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/historical-data')
def historical_data():
    """Get historical data from Supabase"""
    try:
        if SUPABASE_AVAILABLE:
            result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(20).execute()
            data = result.data
            
            return jsonify({
                'status': 'success',
                'data': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Supabase not available'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)