from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import os

# Import Supabase functions
try:
    from supabase_config import insert_sensor_data, get_latest_sensor_data, get_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase no disponible")

app = Flask(__name__)

# Global variables to store ESP32 data
esp32_data = {
    'sensor_data': {
        'temperature1': 0,
        'humidity1': 0,
        'temperature2': 0,
        'humidity2': 0,
        'soil_moisture1': 0,
        'soil_moisture2': 0,
        'last_update': 'N/A'
    },
    'esp32_status': 'disconnected',
    'led_status': 'OFF',
    'led_state': 'off'
}

def save_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2):
    """Save sensor data to Supabase"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if SUPABASE_AVAILABLE:
        try:
            success = insert_sensor_data(
                temperature1, humidity1, 
                temperature2, humidity2,
                soil_moisture1, soil_moisture2,
                timestamp
            )
            if success:
                print(f"Datos guardados en Supabase: T1={temperature1}C, H1={humidity1}%, T2={temperature2}C, H2={humidity2}%, SM1={soil_moisture1}%, SM2={soil_moisture2}%")
            else:
                print(f"Error guardando en Supabase")
        except Exception as e:
            print(f"Error con Supabase: {e}")
    
    print(f"Sensor data saved: T1={temperature1}C, H1={humidity1}%, T2={temperature2}C, H2={humidity2}%, SM1={soil_moisture1}%, SM2={soil_moisture2}%")

def load_latest_data_from_supabase():
    """Load latest sensor data from Supabase"""
    if SUPABASE_AVAILABLE:
        try:
            latest = get_latest_sensor_data()
            if latest:
                esp32_data['sensor_data'] = {
                    'temperature1': latest.get('temperature1', 0),
                    'humidity1': latest.get('humidity1', 0),
                    'temperature2': latest.get('temperature2', 0),
                    'humidity2': latest.get('humidity2', 0),
                    'soil_moisture1': latest.get('soil_moisture1', 0),
                    'soil_moisture2': latest.get('soil_moisture2', 0),
                    'last_update': latest.get('timestamp', 'N/A')
                }
                esp32_data['esp32_status'] = 'connected'
                return True
        except Exception as e:
            print(f"Error cargando datos de Supabase: {e}")
    return False

# Load initial data from Supabase
load_latest_data_from_supabase()

@app.route('/')
def home():
    """Main dashboard page"""
    # Refresh data from Supabase on page load
    load_latest_data_from_supabase()
    
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
            max-width: 1400px;
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
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #007bff;
        }

        .metric-label {
            font-weight: 500;
            color: #555;
            font-size: 0.95rem;
        }

        .metric-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #333;
        }

        .temperature { border-left-color: #dc3545; }
        .humidity { border-left-color: #17a2b8; }
        .soil { border-left-color: #28a745; }

        .temperature .metric-value { color: #dc3545; }
        .humidity .metric-value { color: #17a2b8; }
        .soil .metric-value { color: #28a745; }

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

        .refresh-indicator {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9rem;
            opacity: 0.8;
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
            <p style="font-size: 0.9rem; margin-top: 10px;">Actualizacion automatica cada 5 minutos</p>
        </header>

        <!-- Dashboard Grid -->
        <div class="dashboard-grid">
            <!-- DHT11 Sensor 1 Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                        <i class="fas fa-thermometer-half"></i>
                    </div>
                    <div>
                        <h3 class="card-title">DHT11 Sensor 1</h3>
                        <p class="card-subtitle">GPIO 2 (D2)</p>
                    </div>
                </div>
                
                <div class="metric temperature">
                    <span class="metric-label">Temperatura</span>
                    <span class="metric-value" id="temperature1-value">{{ esp32_data.sensor_data.temperature1 }}</span><span style="font-size: 1rem;">°C</span>
                </div>
                
                <div class="metric humidity">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="humidity1-value">{{ esp32_data.sensor_data.humidity1 }}</span><span style="font-size: 1rem;">%</span>
                </div>
            </div>

            <!-- DHT11 Sensor 2 Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                        <i class="fas fa-thermometer-half"></i>
                    </div>
                    <div>
                        <h3 class="card-title">DHT11 Sensor 2</h3>
                        <p class="card-subtitle">GPIO 4 (D4)</p>
                    </div>
                </div>
                
                <div class="metric temperature">
                    <span class="metric-label">Temperatura</span>
                    <span class="metric-value" id="temperature2-value">{{ esp32_data.sensor_data.temperature2 }}</span><span style="font-size: 1rem;">°C</span>
                </div>
                
                <div class="metric humidity">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="humidity2-value">{{ esp32_data.sensor_data.humidity2 }}</span><span style="font-size: 1rem;">%</span>
                </div>
            </div>

            <!-- Soil Moisture Sensor 1 Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #20c997);">
                        <i class="fas fa-seedling"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Humedad de Suelo 1</h3>
                        <p class="card-subtitle">GPIO 35 (ADC)</p>
                    </div>
                </div>
                
                <div class="metric soil">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="soil1-value">{{ esp32_data.sensor_data.soil_moisture1 }}</span><span style="font-size: 1rem;">%</span>
                </div>
            </div>

            <!-- Soil Moisture Sensor 2 Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #20c997);">
                        <i class="fas fa-seedling"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Humedad de Suelo 2</h3>
                        <p class="card-subtitle">GPIO 36 (ADC)</p>
                    </div>
                </div>
                
                <div class="metric soil">
                    <span class="metric-label">Humedad</span>
                    <span class="metric-value" id="soil2-value">{{ esp32_data.sensor_data.soil_moisture2 }}</span><span style="font-size: 1rem;">%</span>
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
            </div>
        </div>
        
        <!-- Refresh Indicator -->
        <div class="refresh-indicator">
            <p>Proxima actualizacion automatica en: <span id="countdown">5:00</span></p>
        </div>
        
        <!-- Footer -->
        <footer class="footer" style="text-align: center; color: white; margin-top: 40px; opacity: 0.8;">
            <div class="footer-content">
                <p>&copy; 2024 Sistema IoT Inteligente - Monitoreo y Control en Tiempo Real</p>
                <p>Desarrollado para Instrumentacion y Medicion</p>
            </div>
        </footer>

        <script>
            let countdownSeconds = 300; // 5 minutes in seconds
            
            function updateCountdown() {
                const minutes = Math.floor(countdownSeconds / 60);
                const seconds = countdownSeconds % 60;
                document.getElementById('countdown').textContent = 
                    `${minutes}:${seconds.toString().padStart(2, '0')}`;
                
                if (countdownSeconds > 0) {
                    countdownSeconds--;
                } else {
                    countdownSeconds = 300; // Reset to 5 minutes
                    refreshData();
                }
            }
            
            function refreshData() {
                console.log('Refrescando datos desde Supabase...');
                fetch('/latest-data')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            updateSensorData(data.sensor_data);
                            updateConnectionStatus(data);
                        }
                    })
                    .catch(error => {
                        console.log('Error refrescando datos:', error);
                    });
            }
            
            function updateSensorData(sensorData) {
                document.getElementById('temperature1-value').textContent = sensorData.temperature1.toFixed(1);
                document.getElementById('humidity1-value').textContent = sensorData.humidity1.toFixed(1);
                document.getElementById('temperature2-value').textContent = sensorData.temperature2.toFixed(1);
                document.getElementById('humidity2-value').textContent = sensorData.humidity2.toFixed(1);
                document.getElementById('soil1-value').textContent = sensorData.soil_moisture1.toFixed(1);
                document.getElementById('soil2-value').textContent = sensorData.soil_moisture2.toFixed(1);
                document.getElementById('last-update').textContent = sensorData.last_update;
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
                // Start countdown timer
                setInterval(updateCountdown, 1000);
                
                // Initial data refresh
                refreshData();
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

            if temperature1 is None or humidity1 is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing sensor data. Required: temperature1, humidity1'
                }), 400

            # Use defaults if sensor 2 or soil sensors are not provided
            if temperature2 is None:
                temperature2 = 0.0
            if humidity2 is None:
                humidity2 = 0.0
            if soil_moisture1 is None:
                soil_moisture1 = 0.0
            if soil_moisture2 is None:
                soil_moisture2 = 0.0

            save_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2)

            esp32_data['sensor_data'] = {
                'temperature1': temperature1,
                'humidity1': humidity1,
                'temperature2': temperature2,
                'humidity2': humidity2,
                'soil_moisture1': soil_moisture1,
                'soil_moisture2': soil_moisture2,
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
            # GET request - return current data
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
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/led-status')
def led_status():
    """Get LED status"""
    return jsonify({
        'status': 'success',
        'led_status': esp32_data['led_status'],
        'led_state': esp32_data['led_state']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
