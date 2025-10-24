"""
Configuración de Supabase para el proyecto ESP32 DHT11
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', '')

def get_supabase_client() -> Client:
    """
    Crear cliente de Supabase
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_ANON_KEY deben estar configurados")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def create_sensor_table_sql():
    """
    SQL para crear la tabla de sensores
    """
    return """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        temperature DECIMAL(5,2),
        humidity DECIMAL(5,2),
        device_id VARCHAR(50) DEFAULT 'ESP32_DHT11',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Crear índice para consultas rápidas por timestamp
    CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
    
    -- Crear índice para consultas por device_id
    CREATE INDEX IF NOT EXISTS idx_sensor_data_device_id ON sensor_data(device_id);
    """

def insert_sensor_data(supabase: Client, temperature: float, humidity: float, device_id: str = 'ESP32_DHT11'):
    """
    Insertar datos del sensor en Supabase
    """
    try:
        data = {
            'temperature': temperature,
            'humidity': humidity,
            'device_id': device_id
        }
        
        result = supabase.table('sensor_data').insert(data).execute()
        print(f"✅ Datos guardados en Supabase: T={temperature}°C, H={humidity}%")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando en Supabase: {e}")
        return False

def get_sensor_data(supabase: Client, limit: int = 100):
    """
    Obtener datos del sensor desde Supabase
    """
    try:
        result = supabase.table('sensor_data')\
            .select('*')\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de Supabase: {e}")
        return []

def get_chart_data(supabase: Client, limit: int = 20):
    """
    Obtener datos para gráficos desde Supabase
    """
    try:
        result = supabase.table('sensor_data')\
            .select('timestamp, temperature, humidity')\
            .order('timestamp', desc=False)\
            .limit(limit)\
            .execute()
        
        if result.data:
            labels = [row['timestamp'] for row in result.data]
            temperatures = [row['temperature'] for row in result.data]
            humidities = [row['humidity'] for row in result.data]
            
            return {
                'status': 'success',
                'labels': labels,
                'temperature': temperatures,
                'humidity': humidities
            }
        else:
            return {
                'status': 'success',
                'labels': [],
                'temperature': [],
                'humidity': []
            }
            
    except Exception as e:
        print(f"❌ Error obteniendo datos de gráfico: {e}")
        return {
            'status': 'error',
            'labels': [],
            'temperature': [],
            'humidity': []
        }
