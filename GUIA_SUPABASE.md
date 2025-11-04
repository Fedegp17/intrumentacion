# Guia de Configuracion Supabase

## 📋 Tabla `sensor_data` - Estructura Requerida

Necesitas crear o actualizar la tabla `sensor_data` en Supabase con las siguientes columnas:

### Columnas de la Tabla:

| Nombre de Columna | Tipo | Descripcion |
|------------------|------|-------------|
| `id` | `bigint` (Primary Key, Auto-increment) | ID unico del registro |
| `temperature1` | `real` o `float` | Temperatura del DHT11 Sensor 1 (GPIO 2) |
| `humidity1` | `real` o `float` | Humedad del DHT11 Sensor 1 (GPIO 2) |
| `temperature2` | `real` o `float` | Temperatura del DHT11 Sensor 2 (GPIO 4) |
| `humidity2` | `real` o `float` | Humedad del DHT11 Sensor 2 (GPIO 4) |
| `soil_moisture1` | `real` o `float` | Humedad de suelo Sensor 1 (GPIO 35) |
| `soil_moisture2` | `real` o `float` | Humedad de suelo Sensor 2 (GPIO 36) |
| `timestamp` | `text` o `timestamp` | Fecha y hora del registro (formato: 'YYYY-MM-DD HH:MM:SS') |

## 🔧 Instrucciones para Crear/Actualizar la Tabla

### Opcion 1: SQL Editor en Supabase

1. Ve a tu proyecto en Supabase Dashboard
2. Navega a **SQL Editor**
3. Ejecuta este SQL:

```sql
-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGSERIAL PRIMARY KEY,
    temperature1 REAL,
    humidity1 REAL,
    temperature2 REAL,
    humidity2 REAL,
    soil_moisture1 REAL,
    soil_moisture2 REAL,
    timestamp TEXT
);

-- Crear indice para busquedas rapidas por timestamp
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp 
ON sensor_data(timestamp DESC);

-- Habilitar Row Level Security (RLS) - Opcional pero recomendado
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Crear politica para permitir inserciones (si usas RLS)
CREATE POLICY "Allow insert on sensor_data" 
ON sensor_data FOR INSERT 
TO anon 
WITH CHECK (true);

-- Crear politica para permitir lecturas (si usas RLS)
CREATE POLICY "Allow select on sensor_data" 
ON sensor_data FOR SELECT 
TO anon 
USING (true);
```

### Opcion 2: Table Editor en Supabase

1. Ve a **Table Editor** en el Dashboard
2. Si la tabla existe, verifica que tenga todas las columnas
3. Si falta alguna columna, agrega:
   - Click en "Add Column"
   - Nombre: `temperature1`, Tipo: `real`
   - Repite para todas las columnas faltantes

### Opcion 3: Migracion desde Tabla Existente

Si ya tienes una tabla `sensor_data` con columnas antiguas:

```sql
-- Agregar nuevas columnas si no existen
ALTER TABLE sensor_data 
ADD COLUMN IF NOT EXISTS temperature2 REAL,
ADD COLUMN IF NOT EXISTS humidity2 REAL,
ADD COLUMN IF NOT EXISTS soil_moisture1 REAL,
ADD COLUMN IF NOT EXISTS soil_moisture2 REAL;

-- Renombrar columnas antiguas si es necesario
-- (Si antes eran 'temperature' y 'humidity')
ALTER TABLE sensor_data 
RENAME COLUMN temperature TO temperature1;

ALTER TABLE sensor_data 
RENAME COLUMN humidity TO humidity1;
```

## 🔐 Variables de Entorno en Vercel

Para que Supabase funcione, necesitas configurar estas variables en Vercel:

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Agrega:

- **Variable:** `SUPABASE_URL`
  - **Value:** Tu URL de Supabase (ej: `https://xxxxx.supabase.co`)

- **Variable:** `SUPABASE_ANON_KEY`
  - **Value:** Tu Anon/Public Key de Supabase

### Como obtener las credenciales:

1. Ve a tu proyecto en Supabase Dashboard
2. Settings → API
3. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`

## ✅ Verificacion

Para verificar que todo funciona:

1. Ejecuta el ESP32 y espera que envie datos
2. Ve a Supabase → Table Editor → sensor_data
3. Deberias ver nuevos registros cada 5 minutos
4. Cada registro debe tener todos los valores de los sensores

## 📊 Ejemplo de Datos Esperados

```json
{
  "id": 1,
  "temperature1": 23.5,
  "humidity1": 65.2,
  "temperature2": 24.1,
  "humidity2": 63.8,
  "soil_moisture1": 45.5,
  "soil_moisture2": 48.2,
  "timestamp": "2025-11-04 19:50:00"
}
```

