-- Crear tabla para almacenar predicciones de riego
-- Ejecutar este SQL en Supabase SQL Editor

CREATE TABLE IF NOT EXISTS irrigation_predictions (
    id BIGSERIAL PRIMARY KEY,
    timestamp TEXT NOT NULL,
    prediction TEXT NOT NULL CHECK (prediction IN ('Regar', 'No regar')),
    score REAL NOT NULL,
    confidence REAL NOT NULL,
    uv_index REAL,
    temperature2 REAL,
    humidity2 REAL,
    soil_moisture1 REAL,
    soil_moisture2 REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índice para búsquedas rápidas por timestamp
CREATE INDEX IF NOT EXISTS idx_irrigation_predictions_timestamp 
ON irrigation_predictions(timestamp DESC);

-- Habilitar Row Level Security (RLS)
ALTER TABLE irrigation_predictions ENABLE ROW LEVEL SECURITY;

-- Política para permitir INSERT (desde el script local)
CREATE POLICY "Allow insert for authenticated users"
ON irrigation_predictions
FOR INSERT
TO authenticated
WITH CHECK (true);

-- Política para permitir SELECT (desde Vercel)
CREATE POLICY "Allow select for all users"
ON irrigation_predictions
FOR SELECT
TO anon
USING (true);

-- Política para permitir SELECT a usuarios autenticados
CREATE POLICY "Allow select for authenticated users"
ON irrigation_predictions
FOR SELECT
TO authenticated
USING (true);

-- Comentarios en la tabla
COMMENT ON TABLE irrigation_predictions IS 'Almacena predicciones de riego generadas por el script local';
COMMENT ON COLUMN irrigation_predictions.prediction IS 'Resultado: Regar o No regar';
COMMENT ON COLUMN irrigation_predictions.score IS 'Score continuo del modelo de regresión';
COMMENT ON COLUMN irrigation_predictions.confidence IS 'Confianza de la predicción (0-100%)';

