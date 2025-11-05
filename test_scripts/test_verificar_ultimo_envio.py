"""
Script para verificar si el ultimo envio se guardo en Supabase
"""

import requests
import json
import time

SUPABASE_URL = "https://ohqufueaipkitngjqsbe.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ocXVmdWVhaXBraXRuZ2pxc2JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNTU5MTksImV4cCI6MjA3NjgzMTkxOX0.iG14a2j8dm2xrX_PDHERQRKP18u6NZPRpWVjmGpgtoY"

def obtener_ultimos_registros():
    """Obtiene los ultimos 5 registros de Supabase"""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/sensor_data"
    
    try:
        response = requests.get(
            f"{url}?select=id,temperature1,humidity1,timestamp&order=timestamp.desc&limit=5",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def enviar_y_verificar():
    """Envia un dato y verifica si se guarda"""
    print("\n" + "="*60)
    print("PRUEBA: Envio y Verificacion")
    print("="*60)
    
    # Estado antes
    print("\nEstado ANTES del envio:")
    registros_antes = obtener_ultimos_registros()
    print(f"Total de registros visibles: {len(registros_antes)}")
    if registros_antes:
        print(f"Ultimo registro ID: {registros_antes[0].get('id')}")
        print(f"Ultimo timestamp: {registros_antes[0].get('timestamp')}")
    
    # Enviar dato
    print("\nEnviando dato a Vercel...")
    data = {
        "temperature1": 99.9,  # Valor unico para identificarlo
        "humidity1": 88.8,      # Valor unico
        "temperature2": 24.5,
        "humidity2": 63.0,
        "soil_moisture1": 50.0,
        "soil_moisture2": 52.0,
        "uv_index": 3.5
    }
    
    try:
        response = requests.post(
            "https://intrumentacion-7fkz.vercel.app/data",
            json=data,
            timeout=10
        )
        
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] Vercel recibio el dato")
            
            # Esperar 5 segundos
            print("Esperando 5 segundos...")
            time.sleep(5)
            
            # Verificar estado despues
            print("\nEstado DESPUES del envio:")
            registros_despues = obtener_ultimos_registros()
            print(f"Total de registros visibles: {len(registros_despues)}")
            
            if registros_despues:
                print(f"\nUltimos 5 registros:")
                for i, reg in enumerate(registros_despues, 1):
                    print(f"{i}. ID: {reg.get('id')}, T1: {reg.get('temperature1')}, H1: {reg.get('humidity1')}, Time: {reg.get('timestamp')}")
                
                # Buscar nuestro dato unico
                encontrado = False
                for reg in registros_despues:
                    if reg.get('temperature1') == 99.9 and reg.get('humidity1') == 88.8:
                        print(f"\n[OK] DATO ENCONTRADO EN SUPABASE!")
                        print(f"ID: {reg.get('id')}")
                        print(f"Timestamp: {reg.get('timestamp')}")
                        encontrado = True
                        break
                
                if not encontrado:
                    print(f"\n[ERROR] El dato NO se guardo en Supabase")
                    print("El servidor de Vercel no esta guardando los datos")
                    print("\nVerifica:")
                    print("1. Que el deploy en Vercel este completo")
                    print("2. Que las variables de entorno esten configuradas")
                    print("3. Logs de Vercel para errores")
            else:
                print("[ERROR] No se pudieron obtener registros")
        else:
            print(f"[ERROR] Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    enviar_y_verificar()

