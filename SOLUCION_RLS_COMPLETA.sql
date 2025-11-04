-- ============================================
-- SOLUCION COMPLETA PARA ERROR DE RLS
-- ============================================
-- Ejecuta este SQL en Supabase SQL Editor

-- Paso 1: Agregar columna uv_index si no existe
ALTER TABLE sensor_data 
ADD COLUMN IF NOT EXISTS uv_index REAL;

-- Paso 2: Habilitar Row Level Security (RLS)
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Paso 3: Eliminar politicas existentes si hay conflictos
DROP POLICY IF EXISTS "Allow insert on sensor_data" ON sensor_data;
DROP POLICY IF EXISTS "Allow select on sensor_data" ON sensor_data;

-- Paso 4: Crear politica para INSERT (permitir guardar datos)
CREATE POLICY "Allow insert on sensor_data" 
ON sensor_data 
FOR INSERT 
TO anon, authenticated
WITH CHECK (true);

-- Paso 5: Crear politica para SELECT (permitir leer datos)
CREATE POLICY "Allow select on sensor_data" 
ON sensor_data 
FOR SELECT 
TO anon, authenticated
USING (true);

-- ============================================
-- VERIFICACION
-- ============================================
-- Despues de ejecutar, verifica que funcione:
-- SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1;

