-- ============================================
-- CONFIGURACION COMPLETA DE TABLA SUPABASE
-- ============================================
-- Ejecuta este SQL en Supabase SQL Editor
-- Paso a paso para configurar la tabla sensor_data

-- Paso 1: Crear tabla si no existe (o verificar que existe)
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGSERIAL PRIMARY KEY,
    temperature1 REAL,
    humidity1 REAL,
    temperature2 REAL,
    humidity2 REAL,
    soil_moisture1 REAL,
    soil_moisture2 REAL,
    uv_index REAL,
    timestamp TEXT
);

-- Paso 2: Agregar columnas si faltan (si la tabla ya existe)
ALTER TABLE sensor_data 
ADD COLUMN IF NOT EXISTS id BIGSERIAL PRIMARY KEY,
ADD COLUMN IF NOT EXISTS temperature1 REAL,
ADD COLUMN IF NOT EXISTS humidity1 REAL,
ADD COLUMN IF NOT EXISTS temperature2 REAL,
ADD COLUMN IF NOT EXISTS humidity2 REAL,
ADD COLUMN IF NOT EXISTS soil_moisture1 REAL,
ADD COLUMN IF NOT EXISTS soil_moisture2 REAL,
ADD COLUMN IF NOT EXISTS uv_index REAL,
ADD COLUMN IF NOT EXISTS timestamp TEXT;

-- Paso 3: Crear indice para busquedas rapidas
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp 
ON sensor_data(timestamp DESC);

-- Paso 4: Habilitar Row Level Security (RLS)
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Paso 5: Eliminar politicas existentes si hay
DROP POLICY IF EXISTS "Allow insert on sensor_data" ON sensor_data;
DROP POLICY IF EXISTS "Allow select on sensor_data" ON sensor_data;

-- Paso 6: Crear politica para INSERT
CREATE POLICY "Allow insert on sensor_data" 
ON sensor_data 
FOR INSERT 
TO anon, authenticated
WITH CHECK (true);

-- Paso 7: Crear politica para SELECT
CREATE POLICY "Allow select on sensor_data" 
ON sensor_data 
FOR SELECT 
TO anon, authenticated
USING (true);

-- Paso 8: Verificar estructura de la tabla
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sensor_data'
ORDER BY ordinal_position;

-- ============================================
-- VERIFICACION
-- ============================================
-- Despues de ejecutar, verifica que la tabla tenga:
-- - id (bigint)
-- - temperature1, humidity1 (real)
-- - temperature2, humidity2 (real)
-- - soil_moisture1, soil_moisture2 (real)
-- - uv_index (real)
-- - timestamp (text)

