import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
try:
    load_dotenv('supabase.env')
except Exception:
    pass  # Ignore if supabase.env doesn't exist

try:
    from supabase import create_client, Client
    
    # Obtener credenciales de Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_ANON_KEY deben estar configurados")
    
    # Crear cliente de Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    def get_supabase_client():
        """Retorna el cliente de Supabase"""
        return supabase
    
    def insert_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, timestamp):
        """Inserta datos del sensor en Supabase"""
        try:
            data = {
                'temperature1': temperature1,
                'humidity1': humidity1,
                'temperature2': temperature2,
                'humidity2': humidity2,
                'soil_moisture1': soil_moisture1,
                'soil_moisture2': soil_moisture2,
                'timestamp': timestamp
            }
            result = supabase.table('sensor_data').insert(data).execute()
            return True
        except Exception as e:
            return False
    
    def get_sensor_data(limit=50):
        """Obtiene los ultimos datos del sensor desde Supabase"""
        try:
            result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            return []
    
    def get_latest_sensor_data():
        """Obtiene los datos mas recientes del sensor desde Supabase"""
        try:
            result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(1).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            return None
    
    # Supabase configurado correctamente
    
except (ImportError, ValueError, Exception) as e:
    # Supabase no disponible
    supabase = None
    
    def get_supabase_client():
        return None
    
    def insert_sensor_data(temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, timestamp):
        return False
    
    def get_latest_sensor_data():
        return None
    
    def get_sensor_data(limit=50):
        return []
    
    def get_chart_data(limit=50):
        return {
            'status': 'error',
            'labels': [],
            'temperature': [],
            'humidity': []
        }
