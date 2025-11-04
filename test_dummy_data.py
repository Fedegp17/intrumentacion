"""
Script completo para enviar datos dummy y diagnosticar conexiones
- Envia datos dummy al servidor de Vercel
- Prueba conexion directa a Supabase
- Diagnostica problemas de conexion
"""

import requests
import json
import time
import random
import sys
from datetime import datetime

# Configuracion del servidor
SERVER_URL = "https://intrumentacion-7fkz.vercel.app"
ENDPOINT = "/data"
FULL_URL = f"{SERVER_URL}{ENDPOINT}"

# Credenciales de Supabase (para diagnostico)
SUPABASE_URL = "https://ohqufueaipkitngjqsbe.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ocXVmdWVhaXBraXRuZ2pxc2JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNTU5MTksImV4cCI6MjA3NjgzMTkxOX0.iG14a2j8dm2xrX_PDHERQRKP18u6NZPRpWVjmGpgtoY"

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

def test_supabase_direct():
    """Prueba conexion directa a Supabase"""
    print("\n" + "="*60)
    print("DIAGNOSTICO: Conexion directa a Supabase")
    print("="*60)
    
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/sensor_data"
    
    # Test 1: Verificar tabla
    print("\n1. Verificando tabla sensor_data...")
    try:
        response = requests.get(f"{url}?limit=1", headers=headers, timeout=5)
        if response.status_code == 200:
            print("   [OK] Tabla accesible")
        else:
            print(f"   [ERROR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False
    
    # Test 2: Intentar insertar
    print("\n2. Intentando insertar dato...")
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {
            "temperature1": 25.0,
            "humidity1": 65.0,
            "temperature2": 24.5,
            "humidity2": 63.0,
            "soil_moisture1": 50.0,
            "soil_moisture2": 52.0,
            "uv_index": 3.5,
            "timestamp": timestamp
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 201:
            print("   [OK] Dato insertado correctamente en Supabase")
            print(f"   Timestamp: {timestamp}")
            return True
        else:
            print(f"   [ERROR] Error {response.status_code}")
            print(f"   Respuesta: {response.text[:300]}")
            return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def run_diagnostics():
    """Ejecuta diagnostico completo"""
    print("\n" + "="*60)
    print("DIAGNOSTICO COMPLETO")
    print("="*60)
    
    # Test 1: Conexion a Vercel
    print("\n>>> Test 1: Conexion a Vercel")
    if not test_connection():
        print("\n[ERROR] No se puede conectar a Vercel")
        return False
    
    # Test 2: Conexion directa a Supabase
    print("\n>>> Test 2: Conexion directa a Supabase")
    supabase_ok = test_supabase_direct()
    
    # Test 3: Envio via Vercel
    print("\n>>> Test 3: Envio via Vercel")
    dummy_data = generate_dummy_data()
    vercel_ok = send_data(dummy_data)
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DEL DIAGNOSTICO")
    print("="*60)
    
    if supabase_ok:
        print("\n[OK] Supabase funciona correctamente")
    else:
        print("\n[ERROR] Problemas con Supabase:")
        print("   - Ejecuta CONFIGURAR_SUPABASE_TABLA.sql en Supabase")
        print("   - Verifica RLS policies")
    
    if vercel_ok:
        print("\n[OK] Vercel recibe datos correctamente")
    else:
        print("\n[ERROR] Problemas con Vercel")
    
    if supabase_ok and vercel_ok:
        print("\n[INFO] Si los datos no aparecen en Supabase:")
        print("   - Verifica variables de entorno en Vercel")
        print("   - Verifica logs de Vercel")
        print("   - Redeploy el proyecto en Vercel")
    
    return supabase_ok and vercel_ok

def main():
    """Funcion principal"""
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnostico":
        run_diagnostics()
        return
    
    print("\n" + "="*60)
    print("ESP32 DUMMY DATA TEST - Python Script")
    print("="*60)
    print("Este script envia datos dummy al servidor de Vercel")
    print("para probar la conexion: Python -> Vercel -> Supabase")
    print("\nUsa: python test_dummy_data.py --diagnostico")
    print("     para ejecutar diagnostico completo")
    print("="*60)
    
    # Prueba de conexion inicial
    if not test_connection():
        print("\nNo se puede continuar. Verifica la conexion al servidor.")
        print("\nEjecuta diagnostico: python test_dummy_data.py --diagnostico")
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

