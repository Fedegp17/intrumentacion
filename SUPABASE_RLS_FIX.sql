-- Habilitar Row Level Security (RLS) en la tabla sensor_data
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Crear politica para permitir INSERT (insercion) de datos
-- Esta politica permite que cualquier usuario (incluso anonimo) pueda insertar datos
CREATE POLICY "Allow insert on sensor_data" 
ON sensor_data 
FOR INSERT 
TO anon, authenticated
WITH CHECK (true);

-- Crear politica para permitir SELECT (lectura) de datos
-- Esta politica permite que cualquier usuario pueda leer datos
CREATE POLICY "Allow select on sensor_data" 
ON sensor_data 
FOR SELECT 
TO anon, authenticated
USING (true);

-- Si quieres permitir UPDATE (actualizacion) tambien:
-- CREATE POLICY "Allow update on sensor_data" 
-- ON sensor_data 
-- FOR UPDATE 
-- TO anon, authenticated
-- USING (true);

-- Si quieres permitir DELETE (eliminacion) tambien:
-- CREATE POLICY "Allow delete on sensor_data" 
-- ON sensor_data 
-- FOR DELETE 
-- TO anon, authenticated
-- USING (true);

