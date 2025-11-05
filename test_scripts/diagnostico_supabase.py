"""
Script de diagnostico para verificar conexion con Supabase
"""

import os
import sys
from datetime import datetime

# Credenciales de Supabase (las mismas que en Vercel)
SUPABASE_URL = "https://ohqufueaipkitngjqsbe.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ocXVmdWVhaXBraXRuZ2pxc2JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNTU5MTksImV4cCI6MjA3NjgzMTkxOX0.iG14a2j8dm2xrX_PDHERQRKP18u6NZPRpWVjmGpgtoY"

def test_supabase_connection():
    """Prueba la conexion con Supabase"""
    print("\n" + "="*60)
    print("DIAGNOSTICO DE CONEXION CON SUPABASE")
    print("="*60)
    
    try:
        from supabase import create_client, Client
        print("[OK] Libreria supabase importada correctamente")
    except ImportError as e:
        print(f"[ERROR] No se puede importar supabase: {e}")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("[OK] Cliente Supabase creado")
    except Exception as e:
        print(f"[ERROR] No se puede crear cliente Supabase: {e}")
        return False
    
    # Test 1: Verificar que la tabla existe
    print("\n[TEST 1] Verificando tabla sensor_data...")
    try:
        result = supabase.table('sensor_data').select('id').limit(1).execute()
        print(f"[OK] Tabla sensor_data existe. Registros encontrados: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"[ERROR] Error al acceder a tabla sensor_data: {e}")
        return False
    
    # Test 2: Intentar insertar un registro de prueba
    print("\n[TEST 2] Intentando insertar registro de prueba...")
    try:
        test_data = {
            'temperature1': 25.5,
            'humidity1': 60.0,
            'temperature2': 24.0,
            'humidity2': 65.0,
            'soil_moisture1': 50.0,
            'soil_moisture2': 55.0,
            'uv_index': 5.0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        result = supabase.table('sensor_data').insert(test_data).execute()
        
        if result.data and len(result.data) > 0:
            print(f"[OK] Registro insertado correctamente. ID: {result.data[0].get('id')}")
            
            # Eliminar el registro de prueba
            try:
                test_id = result.data[0].get('id')
                supabase.table('sensor_data').delete().eq('id', test_id).execute()
                print(f"[OK] Registro de prueba eliminado (ID: {test_id})")
            except Exception as e:
                print(f"[WARNING] No se pudo eliminar registro de prueba: {e}")
            
            return True
        else:
            print("[ERROR] Insert no devolvio datos")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Error al insertar: {error_msg}")
        
        # Diagnosticar el tipo de error
        if "RLS" in error_msg or "policy" in error_msg.lower():
            print("\n[DIAGNOSTICO] Problema con RLS (Row Level Security)")
            print("   - Verifica que las politicas de RLS esten configuradas correctamente")
            print("   - Las politicas deben permitir INSERT y SELECT para el rol 'anon'")
        elif "column" in error_msg.lower():
            print("\n[DIAGNOSTICO] Problema con columnas de la tabla")
            print("   - Verifica que todas las columnas existan en la tabla")
            print("   - Columnas requeridas: temperature1, humidity1, temperature2, humidity2,")
            print("     soil_moisture1, soil_moisture2, uv_index, timestamp")
        elif "permission" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print("\n[DIAGNOSTICO] Problema de permisos")
            print("   - Verifica que la anon key sea correcta")
            print("   - Verifica las politicas de RLS")
        else:
            print(f"\n[DIAGNOSTICO] Error desconocido: {error_msg}")
        
        return False
    
    # Test 3: Verificar estructura de la tabla
    print("\n[TEST 3] Verificando estructura de la tabla...")
    try:
        result = supabase.table('sensor_data').select('*').limit(1).execute()
        if result.data and len(result.data) > 0:
            columns = list(result.data[0].keys())
            print(f"[OK] Columnas encontradas: {', '.join(columns)}")
            
            required_columns = ['temperature1', 'humidity1', 'temperature2', 'humidity2', 
                              'soil_moisture1', 'soil_moisture2', 'uv_index', 'timestamp']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"[ERROR] Faltan columnas: {', '.join(missing_columns)}")
                return False
            else:
                print("[OK] Todas las columnas requeridas existen")
        else:
            print("[WARNING] No hay registros para verificar estructura")
    except Exception as e:
        print(f"[ERROR] Error al verificar estructura: {e}")
        return False
    
    print("\n" + "="*60)
    print("[OK] Todos los tests pasaron!")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)

