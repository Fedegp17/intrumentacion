"""
Script para verificar si los datos se estan guardando en Supabase
desde Vercel
"""

import requests
import json
from datetime import datetime

# Credenciales de Supabase
SUPABASE_URL = "https://ohqufueaipkitngjqsbe.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ocXVmdWVhaXBraXRuZ2pxc2JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNTU5MTksImV4cCI6MjA3NjgzMTkxOX0.iG14a2j8dm2xrX_PDHERQRKP18u6NZPRpWVjmGpgtoY"

def contar_registros_supabase():
    """Cuenta cuantos registros hay en Supabase"""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/sensor_data"
    
    try:
        # Obtener todos los registros (o al menos los últimos)
        response = requests.get(
            f"{url}?select=id,timestamp&order=timestamp.desc&limit=10",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return len(data), data
        else:
            print(f"Error obteniendo datos: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return 0, []
    except Exception as e:
        print(f"Error: {e}")
        return 0, []

def obtener_ultimo_registro():
    """Obtiene el ultimo registro de Supabase"""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/sensor_data"
    
    try:
        response = requests.get(
            f"{url}?order=timestamp.desc&limit=1",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def enviar_dato_y_verificar():
    """Envia un dato a Vercel y verifica si se guarda en Supabase"""
    print("\n" + "="*60)
    print("PRUEBA: Enviar dato y verificar en Supabase")
    print("="*60)
    
    # Contar registros antes
    count_before, _ = contar_registros_supabase()
    print(f"\nRegistros en Supabase ANTES: {count_before}")
    
    # Enviar dato a Vercel
    print("\nEnviando dato a Vercel...")
    data = {
        "temperature1": 30.0,
        "humidity1": 70.0,
        "temperature2": 29.5,
        "humidity2": 68.0,
        "soil_moisture1": 55.0,
        "soil_moisture2": 57.0,
        "uv_index": 5.0
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
            
            # Esperar un momento para que se procese
            import time
            print("Esperando 3 segundos para que se procese...")
            time.sleep(3)
            
            # Contar registros despues
            count_after, _ = contar_registros_supabase()
            print(f"\nRegistros en Supabase DESPUES: {count_after}")
            
            if count_after > count_before:
                print(f"[OK] Se guardo el dato! (Nuevos registros: {count_after - count_before})")
                
                # Obtener ultimo registro
                ultimo = obtener_ultimo_registro()
                if ultimo:
                    print("\nUltimo registro guardado:")
                    print(json.dumps(ultimo, indent=2))
                return True
            else:
                print(f"[ERROR] No se guardo el dato (registros iguales: {count_before})")
                print("\nPosibles causas:")
                print("1. Variables de entorno no configuradas correctamente en Vercel")
                print("2. Error en el codigo del servidor que no se muestra")
                print("3. Problema con RLS que bloquea inserts")
                print("4. El servidor no tiene codigo para guardar en Supabase")
                return False
        else:
            print(f"[ERROR] Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("VERIFICACION DE DATOS EN SUPABASE")
    print("="*60)
    
    # Mostrar estado actual
    print("\n1. Estado actual de Supabase:")
    count, registros = contar_registros_supabase()
    print(f"   Total de registros: {count}")
    
    if count > 0:
        print("\n   Ultimos registros:")
        for i, reg in enumerate(registros[:5], 1):
            timestamp = reg.get('timestamp', 'N/A')
            print(f"   {i}. ID: {reg.get('id')}, Timestamp: {timestamp}")
    
    # Probar envio y verificacion
    print("\n2. Prueba de envio y verificacion:")
    enviar_dato_y_verificar()
    
    # Estado final
    print("\n" + "="*60)
    print("RECOMENDACIONES")
    print("="*60)
    print("\nSi los datos NO se guardan:")
    print("1. Verifica logs de Vercel para errores silenciosos")
    print("2. Verifica que el codigo del servidor tenga la funcion de insert")
    print("3. Verifica que las variables de entorno esten correctas")
    print("4. Verifica RLS policies en Supabase")
    print("\nSi solo se guarda UNA vez:")
    print("- Puede haber un error en el codigo que solo permite un insert")
    print("- O un problema con el manejo de errores en el servidor")

if __name__ == "__main__":
    main()

