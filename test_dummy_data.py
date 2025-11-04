"""
Script de prueba para enviar datos dummy al servidor de Vercel
Simula el comportamiento del ESP32 enviando datos de sensores
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuracion del servidor
SERVER_URL = "https://intrumentacion-7fkz.vercel.app"
ENDPOINT = "/data"
FULL_URL = f"{SERVER_URL}{ENDPOINT}"

# Intervalo de envio (en segundos)
SEND_INTERVAL = 30  # 30 segundos para pruebas rapidas

def generate_dummy_data():
    """Genera datos dummy de sensores"""
    data = {
        "temperature1": round(23.5 + random.uniform(0, 5), 1),  # 23.5-28.5
        "humidity1": round(60 + random.uniform(0, 30), 1),       # 60-90
        "temperature2": round(24.0 + random.uniform(0, 5), 1),   # 24.0-29.0
        "humidity2": round(58 + random.uniform(0, 35), 1),        # 58-93
        "soil_moisture1": round(40 + random.uniform(0, 40), 1),   # 40-80
        "soil_moisture2": round(45 + random.uniform(0, 35), 1),   # 45-80
        "uv_index": round(2.0 + random.uniform(0, 8), 1)          # 2.0-10.0
    }
    return data

def send_data(data):
    """Envia datos al servidor"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"\n{'='*60}")
        print(f"Enviando datos dummy al servidor...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*60}")
        print(f"DHT11 Sensor 1: T={data['temperature1']}°C, H={data['humidity1']}%")
        print(f"DHT11 Sensor 2: T={data['temperature2']}°C, H={data['humidity2']}%")
        print(f"Soil Moisture 1: {data['soil_moisture1']}%")
        print(f"Soil Moisture 2: {data['soil_moisture2']}%")
        print(f"UV Index: {data['uv_index']}")
        print(f"{'-'*60}")
        print(f"JSON payload:")
        print(json.dumps(data, indent=2))
        print(f"{'-'*60}")
        
        response = requests.post(
            FULL_URL,
            json=data,
            headers=headers,
            timeout=10
        )
        
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] SUCCESS! Datos enviados correctamente")
            print(f"Respuesta del servidor:")
            try:
                response_data = response.json()
                print(json.dumps(response_data, indent=2))
            except:
                print(response.text)
            print(f"{'='*60}\n")
            return True
        else:
            print(f"[ERROR] ERROR: HTTP {response.status_code}")
            print(f"Respuesta: {response.text}")
            print(f"{'='*60}\n")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] ERROR: No se pudo conectar al servidor")
        print(f"Verifica que:")
        print(f"  1. La URL sea correcta: {SERVER_URL}")
        print(f"  2. Vercel este desplegado y activo")
        print(f"  3. Tengas conexion a internet")
        print(f"{'='*60}\n")
        return False
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] ERROR: Timeout - El servidor no respondio a tiempo")
        print(f"{'='*60}\n")
        return False
        
    except Exception as e:
        print(f"[ERROR] ERROR: {str(e)}")
        print(f"{'='*60}\n")
        return False

def test_connection():
    """Prueba la conexion al servidor"""
    print(f"\n{'='*60}")
    print("PRUEBA DE CONEXION")
    print(f"{'='*60}")
    print(f"Servidor: {SERVER_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"{'-'*60}")
    
    try:
        # Intentar conectar al endpoint principal
        response = requests.get(SERVER_URL, timeout=5)
        print(f"[OK] Conexion al servidor: OK (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se pudo conectar al servidor")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

def main():
    """Funcion principal"""
    print("\n" + "="*60)
    print("ESP32 DUMMY DATA TEST - Python Script")
    print("="*60)
    print("Este script envia datos dummy al servidor de Vercel")
    print("para probar la conexion: Python -> Vercel -> Supabase")
    print("="*60)
    
    # Prueba de conexion inicial
    if not test_connection():
        print("\nNo se puede continuar. Verifica la conexion al servidor.")
        return
    
    print(f"\nEnviando datos cada {SEND_INTERVAL} segundos...")
    print("Presiona Ctrl+C para detener\n")
    
    send_count = 0
    
    try:
        while True:
            send_count += 1
            print(f"\n>>> Envio #{send_count}")
            
            # Generar y enviar datos dummy
            dummy_data = generate_dummy_data()
            success = send_data(dummy_data)
            
            if success:
                print(f"Esperando {SEND_INTERVAL} segundos hasta el proximo envio...")
            else:
                print(f"Reintentando en {SEND_INTERVAL} segundos...")
            
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print("Script detenido por el usuario")
        print(f"Total de envios: {send_count}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

