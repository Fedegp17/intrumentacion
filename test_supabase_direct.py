"""
Script para verificar conexion directa a Supabase
Prueba si podemos insertar datos directamente desde Python
"""

import os
import requests
import json
from datetime import datetime

# Supabase credentials - Actualizar con tus valores
# Obtener desde: Supabase Dashboard -> Settings -> API
SUPABASE_URL = os.getenv("SUPABASE_URL", "")  # Ej: https://xxxxx.supabase.co
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")  # Tu anon key

def test_supabase_connection():
    """Prueba conexion directa a Supabase"""
    print("\n" + "="*60)
    print("PRUEBA DIRECTA DE CONEXION A SUPABASE")
    print("="*60)
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("\n[ERROR] Variables de entorno no configuradas")
        print("\nPara configurar:")
        print("1. Obtener credenciales desde Supabase Dashboard:")
        print("   - Settings -> API")
        print("   - Project URL -> SUPABASE_URL")
        print("   - anon public key -> SUPABASE_ANON_KEY")
        print("\n2. Configurar en terminal:")
        print("   Windows PowerShell:")
        print("   $env:SUPABASE_URL='https://xxxxx.supabase.co'")
        print("   $env:SUPABASE_ANON_KEY='tu-anon-key'")
        print("\n   O agregar al inicio del script:")
        print("   SUPABASE_URL = 'https://xxxxx.supabase.co'")
        print("   SUPABASE_ANON_KEY = 'tu-anon-key'")
        return False
    
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Anon Key: {SUPABASE_ANON_KEY[:20]}...")
    print("-"*60)
    
    # Test 1: Verificar que la tabla existe
    print("\n1. Verificando tabla sensor_data...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sensor_data"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Intentar leer datos (solo verificar que la tabla existe)
        response = requests.get(
            f"{url}?limit=1",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print("   [OK] Tabla sensor_data existe y es accesible")
        elif response.status_code == 401:
            print("   [ERROR] No autorizado - Verifica SUPABASE_ANON_KEY")
            return False
        elif response.status_code == 404:
            print("   [ERROR] Tabla no encontrada - Verifica que la tabla exista")
            return False
        else:
            print(f"   [WARN] Status: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False
    
    # Test 2: Intentar insertar un dato dummy
    print("\n2. Intentando insertar dato dummy...")
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
        
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            print("   [OK] Dato insertado correctamente en Supabase")
            print(f"   Timestamp: {timestamp}")
            return True
        elif response.status_code == 400:
            print(f"   [ERROR] Error 400 - Datos invalidos")
            print(f"   Respuesta: {response.text}")
            return False
        elif response.status_code == 401:
            print(f"   [ERROR] Error 401 - No autorizado")
            print(f"   Verifica SUPABASE_ANON_KEY y RLS policies")
            return False
        elif response.status_code == 409:
            print(f"   [ERROR] Error 409 - Conflicto (posible problema de RLS)")
            print(f"   Verifica RLS policies en Supabase")
            return False
        else:
            print(f"   [ERROR] Error {response.status_code}")
            print(f"   Respuesta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def check_vercel_env():
    """Verifica que Vercel tenga las variables de entorno"""
    print("\n" + "="*60)
    print("VERIFICACION DE VARIABLES EN VERCEL")
    print("="*60)
    print("\nIMPORTANTE: Verifica manualmente en Vercel Dashboard:")
    print("\n1. Ve a Vercel Dashboard")
    print("2. Tu proyecto -> Settings -> Environment Variables")
    print("3. Debe tener:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY")
    print("\n4. Si no existen, agregalas:")
    print("   - Obtener desde Supabase Dashboard -> Settings -> API")
    print("   - Project URL -> SUPABASE_URL")
    print("   - anon public key -> SUPABASE_ANON_KEY")
    print("\n5. Despues de agregar, redeploya el proyecto en Vercel")

def check_rls():
    """Instrucciones para verificar RLS"""
    print("\n" + "="*60)
    print("VERIFICACION DE RLS (Row Level Security)")
    print("="*60)
    print("\nEjecuta este SQL en Supabase SQL Editor:")
    print("\n-- Verificar RLS")
    print("SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'sensor_data';")
    print("\n-- Si RLS esta habilitado, crear politicas:")
    print("ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;")
    print("\n-- Crear politica para INSERT")
    print("DROP POLICY IF EXISTS \"Allow insert on sensor_data\" ON sensor_data;")
    print("CREATE POLICY \"Allow insert on sensor_data\"")
    print("ON sensor_data FOR INSERT")
    print("TO anon, authenticated")
    print("WITH CHECK (true);")
    print("\n-- Crear politica para SELECT")
    print("DROP POLICY IF EXISTS \"Allow select on sensor_data\" ON sensor_data;")
    print("CREATE POLICY \"Allow select on sensor_data\"")
    print("ON sensor_data FOR SELECT")
    print("TO anon, authenticated")
    print("USING (true);")

def main():
    """Funcion principal"""
    print("\n" + "="*60)
    print("DIAGNOSTICO DE CONEXION SUPABASE")
    print("="*60)
    
    # Si no hay credenciales, mostrar instrucciones
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("\n[INFO] No hay credenciales configuradas para prueba directa")
        print("\nOpcion 1: Configurar variables de entorno")
        print("Opcion 2: Verificar en Vercel Dashboard")
        check_vercel_env()
        check_rls()
        return
    
    # Probar conexion directa
    success = test_supabase_connection()
    
    if success:
        print("\n" + "="*60)
        print("[OK] Supabase funciona correctamente")
        print("="*60)
        print("\nEl problema esta en Vercel:")
        print("1. Verifica variables de entorno en Vercel")
        print("2. Verifica logs de Vercel para errores")
        print("3. Asegurate de que el codigo del servidor este desplegado")
    else:
        print("\n" + "="*60)
        print("[ERROR] Problemas con Supabase")
        print("="*60)
        check_rls()
        check_vercel_env()

if __name__ == "__main__":
    main()

