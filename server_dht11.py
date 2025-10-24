from flask import Flask, request, jsonify
from datetime import datetime
import json
import threading
import time
import os
import csv

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
    }
}

# Store connection history
connection_history = []

def save_dht11_data(humidity, temperature):
    """Save DHT11 sensor data to CSV"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if CSV file exists, if not create with headers
    file_exists = os.path.exists(SENSOR_DATA_FILE)
    
    with open(SENSOR_DATA_FILE, 'a', newline='') as f:
        if not file_exists:
            f.write('timestamp,temperature,humidity\n')
        
        # Write data row
        f.write(f'{timestamp},{temperature},{humidity}\n')
    
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
    <html>
    <head>
        <title>ESP32 DHT11 Monitor</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                min-height: 100vh;
                padding: 20px;
                animation: gradientShift 10s ease infinite;
                background-size: 400% 400%;
            }}
            
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 40px;
                border-radius: 25px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            h1 {{
                text-align: center;
                margin-bottom: 40px;
                font-size: 3.5em;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 4px 8px rgba(0,0,0,0.1);
                animation: titleGlow 3s ease-in-out infinite alternate;
            }}
            
            @keyframes titleGlow {{
                from {{ filter: brightness(1); }}
                to {{ filter: brightness(1.2); }}
            }}
            
            .status-card {{
                background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
                backdrop-filter: blur(10px);
                padding: 30px;
                border-radius: 20px;
                margin-bottom: 30px;
                border: 2px solid {status_color};
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .status-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
                animation: shimmer 3s infinite;
            }}
            
            @keyframes shimmer {{
                0% {{ left: -100%; }}
                100% {{ left: 100%; }}
            }}
            
            .sensor-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }}
            
            .sensor-card {{
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 50%, #ff9ff3 100%);
                color: white;
                padding: 40px;
                border-radius: 25px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3);
                transform: translateY(0);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                position: relative;
                overflow: hidden;
            }}
            
            .sensor-card:hover {{
                transform: translateY(-10px) scale(1.02);
                box-shadow: 0 30px 60px rgba(255, 107, 107, 0.4);
            }}
            
            .sensor-card::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
                animation: rotate 4s linear infinite;
            }}
            
            @keyframes rotate {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .sensor-card:nth-child(2) {{
                background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 50%, #093637 100%);
                box-shadow: 0 20px 40px rgba(78, 205, 196, 0.3);
            }}
            
            .sensor-card:nth-child(2):hover {{
                box-shadow: 0 30px 60px rgba(78, 205, 196, 0.4);
            }}
            
            .sensor-value {{
                font-size: 4em;
                font-weight: 700;
                margin: 20px 0;
                text-shadow: 0 4px 8px rgba(0,0,0,0.2);
                animation: pulse 2s ease-in-out infinite;
                position: relative;
                z-index: 1;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            
            .sensor-label {{
                font-size: 1.5em;
                font-weight: 600;
                opacity: 0.95;
                position: relative;
                z-index: 1;
            }}
            
            .sensor-unit {{
                font-size: 0.7em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            
            .info-item {{
                background: linear-gradient(135deg, rgba(255,255,255,0.8), rgba(255,255,255,0.6));
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.3);
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}
            
            .info-item:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }}
            
            .info-label {{
                font-weight: 600;
                color: #4a5568;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            
            .info-value {{
                color: #2d3748;
                font-size: 1.3em;
                font-weight: 500;
            }}
            
            .chart-container {{
                margin: 40px 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
                backdrop-filter: blur(15px);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.3);
            }}
            
            .chart-container h3 {{
                font-size: 2em;
                font-weight: 600;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-align: center;
            }}
            
            .refresh-btn {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 50px;
                cursor: pointer;
                margin: 15px 10px;
                font-weight: 600;
                font-size: 1em;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }}
            
            .refresh-btn:hover {{
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
            }}
            
            .led-btn {{
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
                font-size: 0.9em;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
                min-width: 80px;
            }}
            
            .led-btn:hover {{
                transform: translateY(-2px) scale(1.05);
                box-shadow: 0 12px 25px rgba(40, 167, 69, 0.4);
            }}
            
            .led-btn:active {{
                transform: translateY(0) scale(0.95);
            }}
            
            .status-indicator {{
                display: inline-block;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                background: {status_color};
                margin-right: 10px;
                animation: blink 2s infinite;
                box-shadow: 0 0 10px {status_color};
            }}
            
            @keyframes blink {{
                0%, 50% {{ opacity: 1; }}
                51%, 100% {{ opacity: 0.5; }}
            }}
            
            .realtime-btn {{
                background: linear-gradient(135deg, #56ab2f, #a8e6cf);
                color: white;
                border: none;
                padding: 18px 35px;
                border-radius: 50px;
                cursor: pointer;
                font-size: 1.1em;
                font-weight: 600;
                margin: 15px;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                box-shadow: 0 15px 30px rgba(86, 171, 47, 0.3);
                position: relative;
                overflow: hidden;
            }}
            
            .realtime-btn::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                transition: left 0.5s;
            }}
            
            .realtime-btn:hover::before {{
                left: 100%;
            }}
            
            .realtime-btn:hover {{
                transform: translateY(-5px) scale(1.08);
                box-shadow: 0 25px 50px rgba(86, 171, 47, 0.4);
            }}
            
            .section-title {{
                font-size: 2.5em;
                font-weight: 600;
                margin: 40px 0 20px 0;
                text-align: center;
                background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .section-description {{
                text-align: center;
                font-size: 1.2em;
                color: #4a5568;
                margin-bottom: 30px;
                font-weight: 400;
            }}
            
            .alert-container {{
                margin: 30px 0;
                padding: 25px;
                border-radius: 20px;
                text-align: center;
                animation: alertPulse 2s ease-in-out infinite;
                box-shadow: 0 20px 40px rgba(255, 0, 0, 0.3);
                border: 3px solid #ff4444;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24, #ff4757);
                color: white;
                position: relative;
                overflow: hidden;
                display: none;
            }}
            
            .alert-container::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255,255,255,0.2), transparent);
                animation: alertShine 3s linear infinite;
            }}
            
            @keyframes alertPulse {{
                0%, 100% {{ 
                    transform: scale(1);
                    box-shadow: 0 20px 40px rgba(255, 0, 0, 0.3);
                }}
                50% {{ 
                    transform: scale(1.02);
                    box-shadow: 0 25px 50px rgba(255, 0, 0, 0.5);
                }}
            }}
            
            @keyframes alertShine {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .alert-title {{
                font-size: 2em;
                font-weight: 700;
                margin-bottom: 15px;
                text-shadow: 0 4px 8px rgba(0,0,0,0.3);
                position: relative;
                z-index: 1;
            }}
            
            .alert-message {{
                font-size: 1.3em;
                font-weight: 500;
                opacity: 0.95;
                position: relative;
                z-index: 1;
            }}
            
            .alert-temperature {{
                font-size: 3em;
                font-weight: 800;
                margin: 15px 0;
                text-shadow: 0 4px 8px rgba(0,0,0,0.3);
                position: relative;
                z-index: 1;
            }}
            
            .alert-actions {{
                margin-top: 20px;
                position: relative;
                z-index: 1;
            }}
            
            .alert-btn {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.5);
                padding: 12px 25px;
                border-radius: 50px;
                cursor: pointer;
                font-weight: 600;
                margin: 0 10px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }}
            
            .alert-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.8);
                transform: translateY(-2px);
            }}
            
            .floating-elements {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -1;
            }}
            
            .floating-circle {{
                position: absolute;
                border-radius: 50%;
                background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                animation: float 6s ease-in-out infinite;
            }}
            
            .floating-circle:nth-child(1) {{
                width: 80px;
                height: 80px;
                top: 20%;
                left: 10%;
                animation-delay: 0s;
            }}
            
            .floating-circle:nth-child(2) {{
                width: 120px;
                height: 120px;
                top: 60%;
                right: 15%;
                animation-delay: 2s;
            }}
            
            .floating-circle:nth-child(3) {{
                width: 60px;
                height: 60px;
                bottom: 20%;
                left: 20%;
                animation-delay: 4s;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                50% {{ transform: translateY(-20px) rotate(180deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="floating-elements">
            <div class="floating-circle"></div>
            <div class="floating-circle"></div>
            <div class="floating-circle"></div>
        </div>
        
        <div class="container">
            <h1>🌡️ ESP32 DHT11 Temperature & Humidity Monitor</h1>
            
            <div class="status-card">
                <h2><span class="status-indicator"></span>Connection Status</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Status</div>
                        <div class="info-value">{esp32_data['status'].upper()}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Last Connection</div>
                        <div class="info-value">{esp32_data['last_connection'] or 'Never'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">ESP32 IP</div>
                        <div class="info-value">{esp32_data['ip_address'] or 'Unknown'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Last Sensor Update</div>
                        <div class="info-value">{last_sensor_update}</div>
                    </div>
                </div>
            </div>

            <div class="sensor-grid">
                <div class="sensor-card">
                    <div class="sensor-label">🌡️ Temperature</div>
                    <div class="sensor-value">{temperature}<span class="sensor-unit">°C</span></div>
                </div>
                <div class="sensor-card">
                    <div class="sensor-label">💧 Humidity</div>
                    <div class="sensor-value">{humidity}<span class="sensor-unit">%</span></div>
                </div>
            </div>

            <div id="temperature-alert" class="alert-container">
                <div class="alert-title">🔥 ALERTA DE TEMPERATURA ALTA</div>
                <div class="alert-message">La temperatura ha superado los 35°C</div>
                <div class="alert-temperature" id="alert-temp-value">--°C</div>
                <div class="alert-message">⚠️ Condición crítica detectada</div>
                <div class="alert-actions">
                    <button class="alert-btn" onclick="dismissAlert()">✅ Entendido</button>
                    <button class="alert-btn" onclick="location.reload()">🔄 Actualizar</button>
                </div>
            </div>

            <div class="chart-container">
                <h3>📊 DHT11 Data History</h3>
                <div style="position: relative; height: 400px; width: 100%;">
                    <canvas id="dht11Chart"></canvas>
                </div>
            </div>

            <div style="text-align: center; margin: 50px 0;">
                <h2 class="section-title">📡 Data Collection & Control</h2>
                <p class="section-description">ESP32 sends DHT11 data every 30 minutes • Real-time monitoring • Interactive controls</p>
                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; margin-top: 40px;">
                    <button class="realtime-btn" onclick="location.reload()">
                        🔄 Refresh Data
                    </button>
                    <button class="refresh-btn" onclick="window.open('/data', '_blank')">
                        📊 View Raw Data
                    </button>
                    <button class="refresh-btn" onclick="generateTestData()" style="background: linear-gradient(135deg, #17a2b8, #138496);">
                        🧪 Generate Test Data
                    </button>
                    <button class="refresh-btn" onclick="testAlert()" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                        🔥 Test Alert (38.5°C)
                    </button>
                </div>
                
                <!-- LED Control Section -->
                <div style="margin-top: 40px; padding: 30px; background: rgba(255, 255, 255, 0.1); border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2);">
                    <h3 style="color: #fff; margin-bottom: 20px; text-align: center;">💡 LED Control & Status</h3>
                    <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <!-- LED Status Display -->
                        <div id="led-status-display" style="padding: 15px 25px; background: rgba(0, 0, 0, 0.3); border-radius: 15px; border: 2px solid #666; min-width: 150px; text-align: center;">
                            <div style="color: #fff; font-weight: bold; margin-bottom: 5px;">LED Status</div>
                            <div id="led-status-text" style="color: #ff6b6b; font-size: 18px; font-weight: bold;">OFF</div>
                        </div>
                        
                        <!-- LED Control Buttons -->
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <button class="led-btn" onclick="controlLED('on')" style="background: linear-gradient(135deg, #28a745, #20c997);">
                                💡 ON
                            </button>
                            <button class="led-btn" onclick="controlLED('off')" style="background: linear-gradient(135deg, #6c757d, #5a6268);">
                                🔴 OFF
                            </button>
                            <button class="led-btn" onclick="controlLED('blink')" style="background: linear-gradient(135deg, #ffc107, #e0a800);">
                                ⚡ BLINK
                            </button>
                            <button class="led-btn" onclick="controlLED('toggle')" style="background: linear-gradient(135deg, #17a2b8, #138496);">
                                🔄 TOGGLE
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Sensor Test Section -->
                <div style="margin-top: 30px; padding: 30px; background: rgba(255, 255, 255, 0.1); border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2);">
                    <h3 style="color: #fff; margin-bottom: 20px; text-align: center;">🌡️ DHT11 Sensor Test</h3>
                    <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <button class="led-btn" onclick="testSensor()" style="background: linear-gradient(135deg, #6f42c1, #5a32a3); min-width: 200px;">
                            🌡️ Test Sensor Reading
                        </button>
                        <div style="padding: 15px 25px; background: rgba(0, 0, 0, 0.3); border-radius: 15px; border: 2px solid #666; min-width: 200px; text-align: center;">
                            <div style="color: #fff; font-size: 14px; margin-bottom: 5px;">Next Reading:</div>
                            <div id="next-reading" style="color: #20c997; font-size: 16px; font-weight: bold;">15 min</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Chart configuration
            const ctx = document.getElementById('dht11Chart').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: '🌡️ Temperature (°C)',
                            data: [],
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.2)',
                            borderWidth: 3,
                            tension: 0.4,
                            yAxisID: 'y',
                            pointBackgroundColor: '#ff6b6b',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            fill: true
                        }},
                        {{
                            label: '💧 Humidity (%)',
                            data: [],
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.2)',
                            borderWidth: 3,
                            tension: 0.4,
                            yAxisID: 'y1',
                            pointBackgroundColor: '#4ecdc4',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            fill: true
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
                            duration: 1000,
                            easing: 'linear',
                            from: 1,
                            to: 0,
                            loop: true
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            grid: {{
                                color: 'rgba(255,255,255,0.2)',
                                borderColor: 'rgba(255,255,255,0.3)'
                            }},
                            ticks: {{
                                color: '#4a5568',
                                font: {{
                                    size: 12,
                                    weight: '500'
                                }}
                            }},
                            title: {{
                                display: true,
                                text: '⏰ Time',
                                color: '#4a5568',
                                font: {{
                                    size: 14,
                                    weight: '600'
                                }}
                            }}
                        }},
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            grid: {{
                                color: 'rgba(255,255,255,0.2)',
                                borderColor: 'rgba(255,255,255,0.3)'
                            }},
                            ticks: {{
                                color: '#4a5568',
                                font: {{
                                    size: 12,
                                    weight: '500'
                                }}
                            }},
                            title: {{
                                display: true,
                                text: '🌡️ Temperature (°C)',
                                color: '#4a5568',
                                font: {{
                                    size: 14,
                                    weight: '600'
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
                                color: 'rgba(255,255,255,0.2)'
                            }},
                            ticks: {{
                                color: '#4a5568',
                                font: {{
                                    size: 12,
                                    weight: '500'
                                }}
                            }},
                            title: {{
                                display: true,
                                text: '💧 Humidity (%)',
                                color: '#4a5568',
                                font: {{
                                    size: 14,
                                    weight: '600'
                                }}
                            }},
                            min: 0,
                            max: 100
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '📊 DHT11 Real-time Sensor Data',
                            color: '#4a5568',
                            font: {{
                                size: 18,
                                weight: '700'
                            }},
                            padding: {{
                                top: 20,
                                bottom: 30
                            }}
                        }},
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                usePointStyle: true,
                                padding: 20,
                                font: {{
                                    size: 14,
                                    weight: '600'
                                }},
                                color: '#4a5568'
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            titleColor: '#4a5568',
                            bodyColor: '#4a5568',
                            borderColor: 'rgba(0,0,0,0.1)',
                            borderWidth: 1,
                            cornerRadius: 10,
                            displayColors: true,
                            titleFont: {{
                                size: 14,
                                weight: '600'
                            }},
                            bodyFont: {{
                                size: 13,
                                weight: '500'
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

            // Generate test data function
            function generateTestData() {{
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = 'Generating...';

                fetch('/generate-test-data', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }}
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        alert('Test data generated successfully! Refresh to see the charts.');
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
                    btn.textContent = '🧪 Generate Test Data';
                }});
            }}

            // Check temperature alert
            function checkTemperatureAlert() {{
                const temperature = parseFloat(document.querySelector('.sensor-value').textContent);
                const alertContainer = document.getElementById('temperature-alert');
                const alertTempValue = document.getElementById('alert-temp-value');
                
                if (!isNaN(temperature) && temperature > 35) {{
                    alertContainer.style.display = 'block';
                    alertTempValue.textContent = temperature + '°C';
                    
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
            
            // Load chart data on page load
            loadChartData();
            
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
                    btn.textContent = '🔥 Test Alert (38.5°C)';
                }});
            }}

            // LED Control Functions
            function controlLED(action) {{
                const buttons = document.querySelectorAll('.led-btn');
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
                button.textContent = '🌡️ Requesting...';
                
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
                    button.textContent = '🌡️ Test Sensor Reading';
                }});
            }}

            function updateLEDStatus(status, state) {{
                const statusText = document.getElementById('led-status-text');
                const statusDisplay = document.getElementById('led-status-display');
                
                statusText.textContent = status;
                
                // Update colors based on status
                if (status === 'ON') {{
                    statusText.style.color = '#28a745';
                    statusDisplay.style.borderColor = '#28a745';
                    statusDisplay.style.boxShadow = '0 0 20px rgba(40, 167, 69, 0.5)';
                }} else if (status === 'BLINKING') {{
                    statusText.style.color = '#ffc107';
                    statusDisplay.style.borderColor = '#ffc107';
                    statusDisplay.style.boxShadow = '0 0 20px rgba(255, 193, 7, 0.5)';
                }} else {{
                    statusText.style.color = '#ff6b6b';
                    statusDisplay.style.borderColor = '#666';
                    statusDisplay.style.boxShadow = 'none';
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
                const statusElement = document.querySelector('.status-indicator');
                const statusText = document.querySelector('.status-text');
                
                if (data.status === 'connected') {{
                    statusElement.style.background = '#28a745';
                    statusElement.style.boxShadow = '0 0 10px #28a745';
                    statusText.textContent = 'Connected';
                    statusText.style.color = '#28a745';
                }} else {{
                    statusElement.style.background = '#dc3545';
                    statusElement.style.boxShadow = '0 0 10px #dc3545';
                    statusText.textContent = 'Disconnected';
                    statusText.style.color = '#dc3545';
                }}
            }}

            // Check temperature alert on page load
            checkTemperatureAlert();
            
            // Load LED status on page load
            loadLEDStatus();
            
            // Check connection status periodically
            setInterval(checkConnectionStatus, 5000); // Every 5 seconds

            // Auto-refresh every 30 seconds
            setInterval(() => {{
                location.reload();
            }}, 30000);
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
        
        # Update connection status
        esp32_data['last_connection'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

@app.route('/chart-data')
def get_chart_data():
    """Get DHT11 data for charts"""
    try:
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
        
        # Update connection status when ESP32 checks in
        esp32_data['status'] = 'connected'
        esp32_data['last_connection'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
    
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
