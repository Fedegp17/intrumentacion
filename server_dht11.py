from flask import Flask, request, jsonify
from datetime import datetime
import json
import threading
import time
import os
import csv
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
load_dotenv('supabase.env')

# Importar Supabase
try:
    from supabase_config import get_supabase_client, insert_sensor_data, get_sensor_data, get_chart_data
    SUPABASE_AVAILABLE = True
    print("✅ Supabase disponible")
except ImportError:
    print("⚠️ Supabase no disponible, usando solo CSV")
    SUPABASE_AVAILABLE = False

app = Flask(__name__)

# File paths for data storage
DATA_FILE = 'esp32_data.json'
HISTORY_FILE = 'connection_history.json'
SENSOR_DATA_FILE = 'dht11_data.csv'

# Store ESP32 data
esp32_data = {
    'last_connection': None,
    'ip_address': None,
    'status': 'disconnected',
    'led_state': False,
    'led_status': 'OFF',  # LED state: ON, OFF, BLINKING
    'connection_count': 0,
    'device_info': {},
    'sensor_data': {
        'humidity': None,
        'temperature': None,
        'last_update': None
    },
    'last_heartbeat': None  # Track last heartbeat for timeout detection
}

# Store connection history
connection_history = []

def connection_monitor():
    """Background thread to monitor ESP32 connection status"""
    while True:
        try:
            check_connection_status()
            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Error in connection monitor: {e}")
            time.sleep(30)

def check_connection_status():
    """Check if ESP32 is still connected based on last heartbeat"""
    if esp32_data['last_heartbeat'] is None:
        esp32_data['status'] = 'disconnected'
        return
    
    # Calculate time since last heartbeat
    last_heartbeat = datetime.strptime(esp32_data['last_heartbeat'], '%Y-%m-%d %H:%M:%S')
    time_since_heartbeat = (datetime.now() - last_heartbeat).total_seconds()
    
    # If more than 2 minutes without heartbeat, mark as disconnected
    if time_since_heartbeat > 120:  # 2 minutes timeout
        if esp32_data['status'] == 'connected':
            print(f"⚠️ ESP32 timeout - marking as disconnected (last seen: {esp32_data['last_heartbeat']})")
        esp32_data['status'] = 'disconnected'
    else:
        esp32_data['status'] = 'connected'

def save_dht11_data(humidity, temperature):
    """Save DHT11 sensor data to CSV file and Supabase"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to CSV (backup)
    file_exists = os.path.exists(SENSOR_DATA_FILE)
    
    with open(SENSOR_DATA_FILE, 'a', newline='') as f:
        if not file_exists:
            f.write('timestamp,temperature,humidity\n')
        
        # Write data row
        f.write(f'{timestamp},{temperature},{humidity}\n')
    
    # Save to Supabase (primary storage) if available
    if SUPABASE_AVAILABLE:
        try:
            success = insert_sensor_data(temperature, humidity, timestamp)
            if success:
                print(f"✅ Datos guardados en Supabase: T={temperature}°C, H={humidity}%")
            else:
                print(f"❌ Error guardando en Supabase")
        except Exception as e:
            print(f"⚠️ Error con Supabase, usando CSV: {e}")
    
    print(f"DHT11 data saved: T={temperature}°C, H={humidity}%")

@app.route('/')
def home():
    """Home page with ESP32 status and DHT11 data visualization"""
    status_color = "green" if esp32_data['status'] == 'connected' else "red"
    led_color = "yellow" if esp32_data['led_state'] else "gray"
    
    # Get latest sensor data
    sensor_data = esp32_data['sensor_data']
    humidity = sensor_data.get('humidity', 'N/A')
    temperature = sensor_data.get('temperature', 'N/A')
    last_sensor_update = sensor_data.get('last_update', 'Never')
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <title>Sistema IoT - Monitoreo Inteligente</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                color: #333;
                line-height: 1.6;
            }}
            
            .header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 2rem 0;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 2rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            
            .logo {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            
            .logo i {{
                font-size: 2.5rem;
                color: #2a5298;
            }}
            
            .logo-text h1 {{
                font-size: 2rem;
                font-weight: 800;
                color: #1e3c72;
                margin: 0;
            }}
            
            .logo-text p {{
                font-size: 0.9rem;
                color: #666;
                margin: 0;
            }}
            
            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                background: {'rgba(40, 167, 69, 0.1)' if esp32_data['status'] == 'connected' else 'rgba(220, 53, 69, 0.1)'};
                border: 1px solid {'rgba(40, 167, 69, 0.3)' if esp32_data['status'] == 'connected' else 'rgba(220, 53, 69, 0.3)'};
            }}
            
            .status-dot {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: {'#28a745' if esp32_data['status'] == 'connected' else '#dc3545'};
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
            
            .container {{
                max-width: 1200px;
                margin: 2rem auto;
                padding: 0 2rem;
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            }}
            
            .card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            }}
            
            .card-header {{
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid #f8f9fa;
            }}
            
            .card-icon {{
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                color: white;
            }}
            
            .card-title {{
                font-size: 1.25rem;
                font-weight: 600;
                color: #1e3c72;
                margin: 0;
            }}
            
            .card-subtitle {{
                font-size: 0.875rem;
                color: #666;
                margin: 0;
            }}
            
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 1rem;
            }}
            
            .metric {{
                text-align: center;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 12px;
                transition: all 0.3s ease;
            }}
            
            .metric:hover {{
                background: #e9ecef;
                transform: scale(1.05);
            }}
            
            .metric-label {{
                font-size: 0.875rem;
                color: #666;
                margin-bottom: 0.5rem;
                font-weight: 500;
            }}
            
            .metric-value {{
                font-size: 1.75rem;
                font-weight: 700;
                color: #1e3c72;
            }}
            
            .metric-value.connected {{ color: #28a745; }}
            .metric-value.disconnected {{ color: #dc3545; }}
            .metric-value.on {{ color: #ffc107; }}
            .metric-value.off {{ color: #6c757d; }}
            .metric-value.blinking {{ color: #17a2b8; }}
            
            .control-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }}
            
            .btn {{
                padding: 0.875rem 1.5rem;
                border: none;
                border-radius: 12px;
                font-size: 0.875rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                text-decoration: none;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
            }}
            
            .btn-success {{
                background: linear-gradient(135deg, #28a745, #218838);
                color: white;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            }}
            
            .btn-danger {{
                background: linear-gradient(135deg, #dc3545, #c82333);
                color: white;
                box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
            }}
            
            .btn-warning {{
                background: linear-gradient(135deg, #ffc107, #e0a800);
                color: #212529;
                box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
            }}
            
            .btn-info {{
                background: linear-gradient(135deg, #17a2b8, #138496);
                color: white;
                box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
            }}
            
            .btn-purple {{
                background: linear-gradient(135deg, #6f42c1, #5a32a3);
                color: white;
                box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);
            }}
            
            .btn-orange {{
                background: linear-gradient(135deg, #fd7e14, #e65c00);
                color: white;
                box-shadow: 0 4px 15px rgba(253, 126, 20, 0.3);
            }}
            
            .chart-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin-bottom: 2rem;
            }}
            
            .chart-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1.5rem;
                flex-wrap: wrap;
                gap: 1rem;
            }}
            
            .chart-controls {{
                display: flex;
                gap: 0.5rem;
            }}
            
            .btn-clear-chart {{
                background: linear-gradient(135deg, #dc3545, #c82333);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 12px;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .btn-clear-chart:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
                background: linear-gradient(135deg, #c82333, #a71e2a);
            }}
            
            .btn-clear-chart:active {{
                transform: translateY(0);
            }}
            
            .chart-header {{
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid #f8f9fa;
            }}
            
            .chart-icon {{
                width: 48px;
                height: 48px;
                border-radius: 12px;
                background: linear-gradient(135deg, #17a2b8, #138496);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                color: white;
            }}
            
            .chart-content {{
                position: relative;
                height: 400px;
                width: 100%;
            }}
            
            #sensorChart {{
                max-height: 400px !important;
                max-width: 100% !important;
            }}
            
            .alert-container {{
                background: linear-gradient(135deg, #f56565, #e53e3e);
                border: 2px solid #fed7d7;
                padding: 1.5rem;
                border-radius: 16px;
                text-align: center;
                margin: 2rem 0;
                box-shadow: 0 8px 25px rgba(245, 101, 101, 0.3);
                animation: alertPulse 2s infinite;
                display: none;
                position: relative;
                overflow: hidden;
            }}
            
            .alert-container::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: rgba(255, 255, 255, 0.1);
                transform: rotate(45deg);
                animation: alertShine 3s infinite;
            }}
            
            @keyframes alertPulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.02); }}
                100% {{ transform: scale(1); }}
            }}
            
            @keyframes alertShine {{
                0% {{ opacity: 0; transform: scale(0) rotate(45deg); }}
                80% {{ opacity: 0.2; transform: scale(0) rotate(45deg); }}
                81% {{ opacity: 0.2; transform: scale(1) rotate(45deg); }}
                100% {{ opacity: 0; transform: scale(1) rotate(45deg); }}
            }}
            
            .alert-container h2 {{
                color: #fff;
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
                position: relative;
                z-index: 1;
            }}
            
            .alert-container p {{
                color: #fff;
                font-size: 1rem;
                position: relative;
                z-index: 1;
            }}
            
            .dismiss-btn {{
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 1rem;
                transition: background 0.3s ease;
                position: relative;
                z-index: 1;
            }}
            
            .dismiss-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            
            .footer {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 2rem 0;
                margin-top: 3rem;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .footer-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 2rem;
                text-align: center;
                color: #666;
            }}
            
            /* Responsive Design */
            @media (max-width: 768px) {{
                .header-content {{
                    flex-direction: column;
                    gap: 1rem;
                }}
                
                .container {{
                    padding: 0 1rem;
                }}
                
                .dashboard-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .metric-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
                .control-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .card {{
                    padding: 1.5rem;
                }}
            }}
            
            /* Historical Data Styles */
            .data-table {{
                overflow-x: auto;
                margin-top: 1rem;
            }}
            
            .data-table table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .data-table th {{
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                padding: 1rem;
                text-align: left;
                font-weight: 600;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .data-table td {{
                padding: 1rem;
                border-bottom: 1px solid #e9ecef;
                font-size: 0.9rem;
            }}
            
            .data-table tr:hover {{
                background-color: #f8f9fa;
            }}
            
            .data-table tr:last-child td {{
                border-bottom: none;
            }}
            
            .loading-spinner {{
                text-align: center;
                padding: 2rem;
            }}
            
            .spinner {{
                border: 3px solid #f3f3f3;
                border-top: 3px solid #28a745;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-microchip"></i>
                    <div class="logo-text">
                        <h1>Sistema IoT Inteligente</h1>
                        <p>Monitoreo y Control en Tiempo Real</p>
                    </div>
                </div>
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span id="connection-status">{'Conectado' if esp32_data['status'] == 'connected' else 'Desconectado'}</span>
                </div>
            </div>
        </header>
        
        <!-- Main Content -->
        <div class="container">
            <!-- Dashboard Grid -->
            <div class="dashboard-grid">
                <!-- System Status Card -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #218838);">
                            <i class="fas fa-server"></i>
                        </div>
                        <div>
                            <h3 class="card-title">Estado del Sistema</h3>
                            <p class="card-subtitle">Monitoreo de conexión</p>
                        </div>
                    </div>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">Estado ESP32</div>
                            <div class="metric-value" id="esp32-status" style="color: {status_color};">{esp32_data['status'].upper()}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Última Conexión</div>
                            <div class="metric-value" id="last-connection" style="font-size: 0.9rem;">{esp32_data['last_connection'] if esp32_data['last_connection'] else 'N/A'}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">IP del ESP32</div>
                            <div class="metric-value" id="esp32-ip" style="font-size: 0.9rem;">{esp32_data['ip_address'] if esp32_data['ip_address'] else 'N/A'}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Estado del LED</div>
                            <div class="metric-value" id="led-status-display" style="color: {led_color};">{esp32_data['led_status'].upper()}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Sensor Data Card -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-icon" style="background: linear-gradient(135deg, #17a2b8, #138496);">
                            <i class="fas fa-thermometer-half"></i>
                        </div>
                        <div>
                            <h3 class="card-title">Datos del Sensor</h3>
                            <p class="card-subtitle">DHT11 - Temperatura y Humedad</p>
                        </div>
                    </div>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">Temperatura</div>
                            <div class="metric-value" id="temperature-value" style="color: #dc3545;">{temperature}°C</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Humedad</div>
                            <div class="metric-value" id="humidity-value" style="color: #17a2b8;">{humidity}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Última Actualización</div>
                            <div class="metric-value" id="last-sensor-update" style="font-size: 0.9rem;">{last_sensor_update}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Temperature Alert -->
            <div id="temperature-alert" class="alert-container">
                <h2><i class="fas fa-exclamation-triangle"></i> ¡ALERTA DE TEMPERATURA ALTA!</h2>
                <p>La temperatura actual es de <span id="alert-temp-value"></span>°C, lo cual es superior a 35°C.</p>
                <button class="dismiss-btn" onclick="dismissAlert()">Entendido</button>
            </div>
            
            <!-- Historical Data from Supabase -->
            <div class="card" style="margin-bottom: 2rem;">
                <div class="card-header">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745, #20c997);">
                        <i class="fas fa-database"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Datos Históricos</h3>
                        <p class="card-subtitle">Últimas 10 lecturas desde Supabase</p>
                    </div>
                </div>
                <div id="historical-data-container">
                    <div class="loading-spinner" id="historical-loading">
                        <div class="spinner"></div>
                        <p>Cargando datos históricos...</p>
                    </div>
                    <div id="historical-data-content" style="display: none;">
                        <div class="data-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Fecha/Hora</th>
                                        <th>Temperatura</th>
                                        <th>Humedad</th>
                                    </tr>
                                </thead>
                                <tbody id="historical-data-table">
                                    <!-- Data will be populated by JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div id="historical-data-error" style="display: none; text-align: center; padding: 2rem; color: #dc3545;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                        <p>No se pudieron cargar los datos históricos</p>
                    </div>
                </div>
            </div>
            
            <!-- Control Cards -->
            <div class="dashboard-grid">
                <!-- LED Control Card -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-icon" style="background: linear-gradient(135deg, #ffc107, #e0a800);">
                            <i class="fas fa-lightbulb"></i>
                        </div>
                        <div>
                            <h3 class="card-title">Control del LED</h3>
                            <p class="card-subtitle">ESP32 LED Control</p>
                        </div>
                    </div>
                    <div class="control-grid">
                        <button class="btn btn-success" onclick="controlLED('on')">
                            <i class="fas fa-power-off"></i> Encender
                        </button>
                        <button class="btn btn-danger" onclick="controlLED('off')">
                            <i class="fas fa-times"></i> Apagar
                        </button>
                        <button class="btn btn-warning" onclick="controlLED('blink')">
                            <i class="fas fa-blink"></i> Parpadear
                        </button>
                        <button class="btn btn-info" onclick="controlLED('toggle')">
                            <i class="fas fa-toggle-on"></i> Alternar
                        </button>
                    </div>
                </div>
                
                <!-- Sensor Test Card -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-icon" style="background: linear-gradient(135deg, #6f42c1, #5a32a3);">
                            <i class="fas fa-flask"></i>
                        </div>
                        <div>
                            <h3 class="card-title">Pruebas del Sensor</h3>
                            <p class="card-subtitle">DHT11 Testing</p>
                        </div>
                    </div>
                    <div class="control-grid">
                        <button class="btn btn-purple" onclick="testSensor()">
                            <i class="fas fa-play"></i> Test Sensor
                        </button>
                        <button class="btn btn-orange" onclick="testAlert()">
                            <i class="fas fa-fire"></i> Test Alert
                        </button>
                    </div>
                    <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                        <div class="metric-label">Próxima Lectura Automática</div>
                        <div class="metric-value" id="next-reading" style="font-size: 1.25rem;">15 min</div>
                    </div>
                </div>
            </div>
            
            <!-- Chart Section -->
            <div class="chart-container">
                <div class="chart-header">
                    <div class="chart-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Datos Históricos</h3>
                        <p class="card-subtitle">Gráfica de Temperatura y Humedad</p>
                    </div>
                    <div class="chart-controls">
                        <button onclick="clearChartData()" class="btn-clear-chart">
                            <i class="fas fa-trash-alt"></i>
                            Limpiar Datos
                        </button>
                    </div>
                </div>
                <div class="chart-content">
                    <canvas id="sensorChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <footer class="footer">
            <div class="footer-content">
                <p>&copy; 2024 Sistema IoT Inteligente - Monitoreo y Control en Tiempo Real</p>
                <p>Desarrollado para Instrumentación y Medición</p>
            </div>
        </footer>

        <script>
            // Chart configuration
            const ctx = document.getElementById('sensorChart').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: '🌡️ Temperature (°C)',
                            data: [],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.15)',
                            borderWidth: 3,
                            tension: 0.4,
                            yAxisID: 'y',
                            pointBackgroundColor: '#dc3545',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 3,
                            pointRadius: 8,
                            pointHoverRadius: 10,
                            pointHoverBackgroundColor: '#dc3545',
                            pointHoverBorderColor: '#ffffff',
                            pointHoverBorderWidth: 3,
                            fill: true,
                            spanGaps: false
                        }},
                        {{
                            label: '💧 Humidity (%)',
                            data: [],
                            borderColor: '#17a2b8',
                            backgroundColor: 'rgba(23, 162, 184, 0.15)',
                            borderWidth: 3,
                            tension: 0.4,
                            yAxisID: 'y1',
                            pointBackgroundColor: '#17a2b8',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 3,
                            pointRadius: 8,
                            pointHoverRadius: 10,
                            pointHoverBackgroundColor: '#17a2b8',
                            pointHoverBorderColor: '#ffffff',
                            pointHoverBorderWidth: 3,
                            fill: true,
                            spanGaps: false
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    animations: {{
                        tension: {{
                            duration: 2000,
                            easing: 'easeInOutQuart',
                            from: 1,
                            to: 0,
                            loop: false
                        }},
                        x: {{
                            duration: 1000,
                            easing: 'easeInOutQuart'
                        }},
                        y: {{
                            duration: 1000,
                            easing: 'easeInOutQuart'
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            grid: {{
                                color: 'rgba(0,0,0,0.08)',
                                drawBorder: false,
                                lineWidth: 1
                            }},
                            ticks: {{
                                color: '#666',
                                font: {{
                                    size: 11,
                                    weight: '500',
                                    family: "'Inter', sans-serif"
                                }},
                                maxTicksLimit: 8,
                                padding: 8
                            }},
                            title: {{
                                display: true,
                                text: 'Tiempo',
                                color: '#333',
                                font: {{
                                    size: 12,
                                    weight: '600',
                                    family: "'Inter', sans-serif"
                                }},
                                padding: {{
                                    top: 10
                                }}
                            }}
                        }},
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            grid: {{
                                color: 'rgba(0,0,0,0.08)',
                                drawBorder: false,
                                lineWidth: 1
                            }},
                            ticks: {{
                                color: '#dc3545',
                                font: {{
                                    size: 11,
                                    weight: '500',
                                    family: "'Inter', sans-serif"
                                }},
                                padding: 8
                            }},
                            title: {{
                                display: true,
                                text: 'Temperatura (°C)',
                                color: '#dc3545',
                                font: {{
                                    size: 12,
                                    weight: '600',
                                    family: "'Inter', sans-serif"
                                }}
                            }},
                            min: 0,
                            max: 50
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {{
                                drawOnChartArea: false,
                                drawBorder: false
                            }},
                            ticks: {{
                                color: '#17a2b8',
                                font: {{
                                    size: 11,
                                    weight: '500',
                                    family: "'Inter', sans-serif"
                                }},
                                padding: 8
                            }},
                            title: {{
                                display: true,
                                text: 'Humedad (%)',
                                color: '#17a2b8',
                                font: {{
                                    size: 12,
                                    weight: '600',
                                    family: "'Inter', sans-serif"
                                }}
                            }},
                            min: 0,
                            max: 100
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: false
                        }},
                        legend: {{
                            display: true,
                            position: 'top',
                            align: 'start',
                            labels: {{
                                usePointStyle: true,
                                pointStyle: 'circle',
                                padding: 20,
                                font: {{
                                    size: 13,
                                    weight: '600',
                                    family: "'Inter', sans-serif"
                                }},
                                color: '#333',
                                boxWidth: 12,
                                boxHeight: 12
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.85)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            borderWidth: 1,
                            cornerRadius: 12,
                            displayColors: true,
                            titleFont: {{
                                size: 13,
                                weight: 'bold',
                                family: "'Inter', sans-serif"
                            }},
                            bodyFont: {{
                                size: 12,
                                family: "'Inter', sans-serif"
                            }},
                            padding: 12,
                            titleSpacing: 4,
                            bodySpacing: 4,
                            callbacks: {{
                                title: function(context) {{
                                    return '📊 ' + context[0].label;
                                }},
                                label: function(context) {{
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    return label + ': ' + value.toFixed(1);
                                }}
                            }}
                        }}
                    }}
                }}
            }});

            // Load chart data
            function loadChartData() {{
                fetch('/chart-data')
                    .then(response => response.json())
                    .then(data => {{
                        if (data.status === 'success') {{
                            // Format timestamps for display
                            const labels = data.labels.map(timestamp => {{
                                const date = new Date(timestamp);
                                return date.toLocaleTimeString();
                            }});
                            
                            chart.data.labels = labels;
                            chart.data.datasets[0].data = data.temperature;
                            chart.data.datasets[1].data = data.humidity;
                            
                            chart.update();
                        }} else {{
                            console.log('No chart data available yet');
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error loading chart data:', error);
                    }});
            }}

            // Clear chart data function
            function clearChartData() {{
                if (confirm('¿Estás seguro de que quieres limpiar todos los datos del gráfico? Esta acción no se puede deshacer.')) {{
                    // Clear chart data
                    chart.data.labels = [];
                    chart.data.datasets[0].data = [];
                    chart.data.datasets[1].data = [];
                    chart.update();
                    
                    // Show success message
                    const originalText = document.querySelector('.btn-clear-chart').innerHTML;
                    document.querySelector('.btn-clear-chart').innerHTML = '<i class="fas fa-check"></i> Datos Limpiados';
                    document.querySelector('.btn-clear-chart').style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                    
                    setTimeout(() => {{
                        document.querySelector('.btn-clear-chart').innerHTML = originalText;
                        document.querySelector('.btn-clear-chart').style.background = 'linear-gradient(135deg, #dc3545, #c82333)';
                    }}, 2000);
                }}
            }}

            // Check temperature alert
            function checkTemperatureAlert() {{
                const temperature = parseFloat(document.getElementById('temperature-value').textContent);
                const alertContainer = document.getElementById('temperature-alert');
                const alertTempValue = document.getElementById('alert-temp-value');
                
                if (!isNaN(temperature) && temperature > 35) {{
                    alertContainer.style.display = 'block';
                    alertTempValue.textContent = temperature;
                    
                    // Play alert sound if supported
                    playAlertSound();
                    
                    // Show browser notification
                    showBrowserNotification(temperature);
                    
                    console.log('🔥 ALERTA: Temperatura crítica detectada:', temperature + '°C');
                }} else {{
                    alertContainer.style.display = 'none';
                }}
            }}
            
            // Dismiss alert
            function dismissAlert() {{
                const alertContainer = document.getElementById('temperature-alert');
                alertContainer.style.display = 'none';
                console.log('✅ Alerta de temperatura descartada por el usuario');
            }}
            
            // Play alert sound
            function playAlertSound() {{
                try {{
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
                }} catch (error) {{
                    console.log('No se pudo reproducir el sonido de alerta');
                }}
            }}
            
            // Show browser notification
            function showBrowserNotification(temperature) {{
                if ('Notification' in window) {{
                    if (Notification.permission === 'granted') {{
                        new Notification('🔥 Alerta de Temperatura', {{
                            body: `Temperatura crítica: ${{temperature}}°C - ¡Supera los 35°C!`,
                            icon: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzIiIGN5PSIzMiIgcj0iMzIiIGZpbGw9IiNmZjY2NjYiLz4KPHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4PSIxNiIgeT0iMTYiPgo8cGF0aCBkPSJNMTIgMkMxMy4xIDIgMTQgMi45IDE0IDRWMTRMMTguNSA2LjVDMTguOSA1LjkgMTkuNSA1LjUgMjAgNUMyMC41IDQuNSAyMC4xIDMuNSAxOSAzLjVDMTguNSA0IDE3LjUgNC41IDE2IDVWMTRDMTYgMTUuMSAxNS4xIDE2IDE0IDE2SDEwQzguOSAxNiA4IDE1LjEgOCAxNFY0QzggMi45IDguOSAyIDEwIDJIMTJaTTEyIDIwQzEzLjEgMjAgMTQgMjAuOSAxNCAyMlMxMy4xIDI0IDEyIDI0IDEwIDIzLjEgMTAgMjIgMTAuOSAyMCAxMiAyMFoiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo8L3N2Zz4K',
                            tag: 'temperature-alert'
                        }});
                    }} else if (Notification.permission !== 'denied') {{
                        Notification.requestPermission().then(permission => {{
                            if (permission === 'granted') {{
                                showBrowserNotification(temperature);
                            }}
                        }});
                    }}
                }}
            }}
            
            // Test alert function
            function testAlert() {{
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = 'Sending...';

                fetch('/test-alert', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }}
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        alert('🔥 Alerta de prueba enviada! Temperatura: 38.5°C');
                        setTimeout(() => location.reload(), 1000);
                    }} else {{
                        alert('Error: ' + data.message);
                    }}
                }})
                .catch(error => {{
                    alert('Error: ' + error);
                }})
                .finally(() => {{
                    btn.disabled = false;
                    btn.textContent = 'Test Alert';
                }});
            }}

            // LED Control Functions
            function controlLED(action) {{
                const buttons = document.querySelectorAll('.btn');
                buttons.forEach(btn => btn.disabled = true);
                
                fetch('/led-control', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ action: action }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        updateLEDStatus(data.led_status, data.led_state);
                        console.log('LED Control:', data.message);
                    }} else {{
                        alert('Error: ' + data.message);
                    }}
                }})
                .catch(error => {{
                    alert('Error: ' + error);
                }})
                .finally(() => {{
                    buttons.forEach(btn => btn.disabled = false);
                }});
            }}
            
            // Sensor Test Function
            function testSensor() {{
                const button = event.target;
                button.disabled = true;
                button.textContent = 'Requesting...';
                
                fetch('/test-sensor', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{}})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        console.log('Sensor Test:', data.message);
                        alert('Sensor test request sent! Check the charts for new data.');
                    }} else {{
                        alert('Error: ' + data.message);
                    }}
                }})
                .catch(error => {{
                    alert('Error: ' + error);
                }})
                .finally(() => {{
                    button.disabled = false;
                    button.textContent = 'Test Sensor';
                }});
            }}

            function updateLEDStatus(status, state) {{
                const statusDisplay = document.getElementById('led-status-display');
                
                statusDisplay.textContent = status;
                
                // Update colors based on status
                if (status === 'ON') {{
                    statusDisplay.style.color = '#28a745';
                }} else if (status === 'BLINKING') {{
                    statusDisplay.style.color = '#ffc107';
                }} else {{
                    statusDisplay.style.color = '#6c757d';
                }}
            }}

            function loadLEDStatus() {{
                fetch('/led-status')
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        updateLEDStatus(data.led_status, data.led_state);
                    }}
                }})
                .catch(error => {{
                    console.log('Error loading LED status:', error);
                }});
            }}

            function checkConnectionStatus() {{
                fetch('/data')
                .then(response => response.json())
                .then(data => {{
                    updateConnectionStatus(data);
                }})
                .catch(error => {{
                    console.log('Error checking connection:', error);
                }});
            }}

            function updateConnectionStatus(data) {{
                const statusElement = document.getElementById('connection-status');
                const statusDot = document.querySelector('.status-dot');
                
                if (data.esp32_status === 'connected') {{
                    statusElement.textContent = 'Conectado';
                    statusDot.style.background = '#28a745';
                }} else {{
                    statusElement.textContent = 'Desconectado';
                    statusDot.style.background = '#dc3545';
                }}
            }}

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {{
                // Load chart data
                loadChartData();
                
                // Check temperature alert
                checkTemperatureAlert();
                
                // Load LED status
                loadLEDStatus();
                
                // Check connection status periodically
                setInterval(checkConnectionStatus, 5000); // Every 5 seconds
                
                // Auto-refresh every 30 seconds
                setInterval(() => {{
                    location.reload();
                }}, 30000);
                
                // Load historical data from Supabase
                loadHistoricalData();
            }});
            
            // Function to load historical data from Supabase
            async function loadHistoricalData() {{
                try {{
                    const response = await fetch('/historical-data');
                    const result = await response.json();
                    
                    const loadingEl = document.getElementById('historical-loading');
                    const contentEl = document.getElementById('historical-data-content');
                    const errorEl = document.getElementById('historical-data-error');
                    const tableEl = document.getElementById('historical-data-table');
                    
                    if (result.status === 'success' && result.data && result.data.length > 0) {{
                        // Hide loading and error, show content
                        loadingEl.style.display = 'none';
                        errorEl.style.display = 'none';
                        contentEl.style.display = 'block';
                        
                        // Populate table
                        tableEl.innerHTML = '';
                        result.data.forEach(row => {{
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td>${{formatDateTime(row.timestamp)}}</td>
                                <td style="color: #dc3545; font-weight: 600;">${{row.temperature}}°C</td>
                                <td style="color: #17a2b8; font-weight: 600;">${{row.humidity}}%</td>
                            `;
                            tableEl.appendChild(tr);
                        }});
                    }} else {{
                        // Show error
                        loadingEl.style.display = 'none';
                        contentEl.style.display = 'none';
                        errorEl.style.display = 'block';
                    }}
                }} catch (error) {{
                    console.error('Error loading historical data:', error);
                    const loadingEl = document.getElementById('historical-loading');
                    const errorEl = document.getElementById('historical-data-error');
                    loadingEl.style.display = 'none';
                    errorEl.style.display = 'block';
                }}
            }}
            
            // Function to format datetime
            function formatDateTime(timestamp) {{
                const date = new Date(timestamp);
                return date.toLocaleString('es-ES', {{
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }});
            }}
        </script>
    </body>
    </html>
    """

@app.route('/data', methods=['POST'])
def receive_sensor_data():
    """Receive DHT11 sensor data from ESP32"""
    try:
        data = request.get_json() or {}
        
        # Extract sensor values
        humidity = data.get('humidity')
        temperature = data.get('temperature')
        
        # Validate data
        if humidity is None or temperature is None:
            return jsonify({
                'status': 'error',
                'message': 'Missing sensor data. Required: humidity, temperature'
            }), 400
        
        # Save to CSV
        save_dht11_data(humidity, temperature)
        
        # Also update current sensor data
        esp32_data['sensor_data'] = {
            'humidity': humidity,
            'temperature': temperature,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Update connection status and heartbeat
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        esp32_data['last_connection'] = current_time
        esp32_data['last_heartbeat'] = current_time
        esp32_data['ip_address'] = request.remote_addr
        esp32_data['status'] = 'connected'
        esp32_data['connection_count'] += 1
        
        response = {
            'status': 'success',
            'message': 'DHT11 data received and saved',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': {
                'humidity': humidity,
                'temperature': temperature
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/data', methods=['GET'])
def get_esp32_data():
    """Get current ESP32 data and sensor readings"""
    try:
        # Check connection status before returning data
        check_connection_status()
        
        # Get latest sensor data
        sensor_data = esp32_data['sensor_data']
        
        return jsonify({
            'status': 'success',
            'esp32_status': esp32_data['status'],
            'last_connection': esp32_data['last_connection'],
            'ip_address': esp32_data['ip_address'],
            'connection_count': esp32_data['connection_count'],
            'temperature': sensor_data.get('temperature', 'N/A'),
            'humidity': sensor_data.get('humidity', 'N/A'),
            'timestamp': sensor_data.get('last_update', 'Never'),
            'led_state': esp32_data['led_state'],
            'led_status': esp32_data['led_status']
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/raw-data', methods=['GET'])
def view_data():
    """View raw sensor data"""
    try:
        if os.path.exists(SENSOR_DATA_FILE):
            with open(SENSOR_DATA_FILE, 'r') as f:
                content = f.read()
            return f"<pre>{content}</pre>"
        else:
            return "No data file found yet."
    except Exception as e:
        return f"Error reading data: {str(e)}"

@app.route('/historical-data')
def get_historical_data():
    """Get historical sensor data from Supabase for landing page"""
    try:
        if SUPABASE_AVAILABLE:
            try:
                # Get last 10 readings from Supabase
                historical_data = get_sensor_data(limit=10)
                return jsonify({
                    'status': 'success',
                    'data': historical_data,
                    'source': 'supabase'
                })
            except Exception as e:
                print(f"⚠️ Error obteniendo datos históricos de Supabase: {e}")
                return jsonify({
                    'status': 'error',
                    'message': 'Error obteniendo datos de Supabase',
                    'data': [],
                    'source': 'error'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Supabase no disponible',
                'data': [],
                'source': 'none'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'data': [],
            'source': 'error'
        })

@app.route('/chart-data')
def get_chart_data():
    """Get DHT11 data for charts from Supabase"""
    try:
        # Try to get data from Supabase first if available
        if SUPABASE_AVAILABLE:
            try:
                supabase_chart_data = get_chart_data(limit=20)
                if supabase_chart_data['status'] == 'success':
                    return jsonify(supabase_chart_data)
            except Exception as e:
                print(f"⚠️ Error con Supabase, usando CSV: {e}")
        
        # Fallback to CSV if Supabase fails
        if not os.path.exists(SENSOR_DATA_FILE):
            return jsonify({
                'status': 'error',
                'message': 'No sensor data available'
            })
        
        # Read CSV data using native CSV module
        chart_data = {
            'status': 'success',
            'labels': [],
            'temperature': [],
            'humidity': []
        }
        
        if os.path.exists(SENSOR_DATA_FILE):
            with open(SENSOR_DATA_FILE, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # Get last 20 records for chart
                recent_rows = rows[-20:] if len(rows) > 20 else rows
                
                for row in recent_rows:
                    chart_data['labels'].append(row['timestamp'])
                    chart_data['temperature'].append(float(row['temperature']))
                    chart_data['humidity'].append(float(row['humidity']))
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/generate-test-data', methods=['POST'])
def generate_test_data():
    """Generate test DHT11 data for demonstration"""
    try:
        import random
        from datetime import datetime, timedelta
        
        # Generate 10 test records
        for i in range(10):
            # Generate realistic DHT11 data with some high temperatures for alert testing
            if i == 7:  # Make one record have high temperature for alert testing
                temperature = round(random.uniform(36, 42), 1)  # Above 35°C to trigger alert
            else:
                temperature = round(random.uniform(20, 35), 1)
            humidity = round(random.uniform(40, 80), 1)
            
            # Create timestamp (spread over last hour)
            timestamp = datetime.now() - timedelta(minutes=i*6)
            
            # Save test data
            save_dht11_data(humidity, temperature)
        
        return jsonify({
            'status': 'success',
            'message': 'Generated 10 test DHT11 records'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/test-alert', methods=['POST'])
def test_alert():
    """Test the temperature alert with high temperature data"""
    try:
        # Send high temperature data to trigger alert
        humidity = 65.0
        temperature = 38.5  # Above 35°C threshold
        
        # Save to CSV
        save_dht11_data(humidity, temperature)
        
        # Update current sensor data
        esp32_data['sensor_data'] = {
            'humidity': humidity,
            'temperature': temperature,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = {
            'status': 'success',
            'message': 'Test alert data sent - Temperature: 38.5°C (Above 35°C threshold)',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': {
                'humidity': humidity,
                'temperature': temperature,
                'alert_triggered': True
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/led-control', methods=['POST'])
def led_control():
    """Control LED on ESP32"""
    try:
        data = request.get_json()
        action = data.get('action', 'toggle')  # on, off, blink, toggle
        
        # Store the command for ESP32 to pick up
        esp32_data['pending_led_command'] = action
        
        # Update LED status
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
        
        response = {
            'status': 'success',
            'message': f'LED command sent: {action}',
            'led_state': esp32_data['led_state'],
            'led_status': esp32_data['led_status'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"LED Control: {action} -> Status: {esp32_data['led_status']}")
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test-led', methods=['POST'])
def test_led():
    """Test LED command immediately"""
    try:
        data = request.get_json()
        action = data.get('action', 'on')
        
        # Store the command for ESP32 to pick up
        esp32_data['pending_led_command'] = action
        
        response = {
            'status': 'success',
            'message': f'Test LED command queued: {action}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"🧪 Test LED command queued: {action}")
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test-sensor', methods=['POST'])
def test_sensor():
    """Request immediate sensor reading from ESP32"""
    try:
        # Store the command for ESP32 to pick up
        esp32_data['pending_sensor_request'] = True
        
        response = {
            'status': 'success',
            'message': 'Sensor test request sent to ESP32',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"🌡️ Sensor test request sent to ESP32")
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/led-status', methods=['GET'])
def led_status():
    """Get current LED status and send commands to ESP32"""
    try:
        response = {
            'status': 'success',
            'led_state': esp32_data['led_state'],
            'led_status': esp32_data['led_status'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Check if there's a pending LED command for ESP32
        if 'pending_led_command' in esp32_data and esp32_data['pending_led_command']:
            response['led_command'] = esp32_data['pending_led_command']
            print(f"🔥 ESP32 LED Command sent: {esp32_data['pending_led_command']}")
            # Clear the command after sending
            del esp32_data['pending_led_command']
        
        # Check if there's a pending sensor request for ESP32
        if 'pending_sensor_request' in esp32_data and esp32_data['pending_sensor_request']:
            response['sensor_request'] = True
            print(f"🌡️ ESP32 Sensor Request sent")
            # Clear the request after sending
            del esp32_data['pending_sensor_request']
        
        # Update connection status and heartbeat when ESP32 checks in
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        esp32_data['status'] = 'connected'
        esp32_data['last_connection'] = current_time
        esp32_data['last_heartbeat'] = current_time
        esp32_data['ip_address'] = request.remote_addr
        print(f"ESP32 connected from: {request.remote_addr}")
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Vercel compatibility
app = app

if __name__ == '__main__':
    print("Starting ESP32 DHT11 Monitor...")
    print("Server will be available at: http://localhost:5000")
    print("ESP32 should connect to: http://YOUR_COMPUTER_IP:5000/data")
    print("Sensors: DHT11 (Temperature & Humidity)")
    
    # Start connection monitor thread
    monitor_thread = threading.Thread(target=connection_monitor, daemon=True)
    monitor_thread.start()
    print("🔍 Connection monitor started")
    
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
