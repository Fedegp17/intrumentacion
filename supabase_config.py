import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
load_dotenv('supabase.env')

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
    
    def insert_sensor_data(temperature, humidity, timestamp):
        """Inserta datos del sensor en Supabase"""
        try:
            data = {
                'temperature': temperature,
                'humidity': humidity,
                'timestamp': timestamp
            }
            result = supabase.table('sensor_data').insert(data).execute()
            print(f"Datos insertados en Supabase: {data}")
            return True
        except Exception as e:
            print(f"Error insertando en Supabase: {e}")
            return False
    
    def get_sensor_data(limit=50):
        """Obtiene los últimos datos del sensor desde Supabase"""
        try:
            result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"Error obteniendo datos de Supabase: {e}")
            return []
    
    def get_chart_data(limit=50):
        """Obtiene datos para el gráfico desde Supabase"""
        try:
            result = supabase.table('sensor_data').select('*').order('timestamp', desc=True).limit(limit).execute()
            data = result.data
            
            if not data:
                return {
                    'status': 'success',
                    'labels': [],
                    'temperature': [],
                    'humidity': []
                }
            
            # Procesar datos para el gráfico
            labels = []
            temperature = []
            humidity = []
            
            for item in reversed(data):  # Invertir para orden cronológico
                labels.append(item['timestamp'])
                temperature.append(item['temperature'])
                humidity.append(item['humidity'])
            
            return {
                'status': 'success',
                'labels': labels,
                'temperature': temperature,
                'humidity': humidity
            }
        except Exception as e:
            print(f"Error obteniendo datos del gráfico de Supabase: {e}")
            return {
                'status': 'error',
                'labels': [],
                'temperature': [],
                'humidity': []
            }
    
    print("✅ Supabase configurado correctamente")
    
except ImportError:
    print("⚠️ Supabase no disponible, usando solo CSV")
    supabase = None
    
    def get_supabase_client():
        return None
    
    def insert_sensor_data(temperature, humidity, timestamp):
        return False
    
    def get_sensor_data(limit=50):
        return []
    
    def get_chart_data(limit=50):
        return {
            'status': 'error',
            'labels': [],
            'temperature': [],
            'humidity': []
        }
