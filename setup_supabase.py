#!/usr/bin/env python3
"""
Script para configurar la base de datos de Supabase
"""
import os
from dotenv import load_dotenv
from supabase_config import get_supabase_client, create_sensor_table_sql

# Cargar variables de entorno
load_dotenv()
load_dotenv('supabase.env')

def setup_database():
    """Configurar la base de datos de Supabase"""
    try:
        print("Configurando base de datos de Supabase...")
        
        # Verificar variables de entorno
        print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NO_CONFIGURADO')}")
        print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY', 'NO_CONFIGURADO')[:20]}...")
        
        # Crear cliente de Supabase
        supabase = get_supabase_client()
        print("Cliente de Supabase creado exitosamente")
        
        # Ejecutar SQL para crear la tabla
        sql = create_sensor_table_sql()
        
        # Nota: En Supabase, las tablas se crean desde el dashboard
        # Este script es para verificar la conexión
        print("SQL para crear la tabla:")
        print(sql)
        print("\nInstrucciones:")
        print("1. Ve a tu dashboard de Supabase")
        print("2. Ve a SQL Editor")
        print("3. Ejecuta el SQL de arriba")
        print("4. Listo! Tu tabla estara creada")
        
        # Probar la conexión insertando un dato de prueba
        print("\nProbando conexion...")
        result = supabase.table('sensor_data').select('*').limit(1).execute()
        print("Conexion exitosa! La tabla ya existe o se creara automaticamente")
        
        return True
        
    except Exception as e:
        print(f"Error configurando Supabase: {e}")
        print("\nSolucion:")
        print("1. Verifica que las credenciales sean correctas")
        print("2. Asegurate de que el proyecto de Supabase este activo")
        print("3. Crea la tabla manualmente desde el dashboard")
        return False

if __name__ == "__main__":
    setup_database()
