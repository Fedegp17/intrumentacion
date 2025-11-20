# 🔧 Configuración Completa de Supabase

## 📋 ¿Qué necesitas configurar en Supabase?

Para que el sistema funcione completamente, necesitas **2 tablas** en Supabase:

1. ✅ **`sensor_data`** - Para datos de sensores (probablemente ya existe)
2. ⭐ **`irrigation_predictions`** - Para predicciones de riego (NUEVA - necesitas crearla)

---

## 🚀 Pasos para Configurar Supabase

### **Paso 1: Verificar/Crear Tabla `sensor_data`**

Esta tabla probablemente ya existe, pero verifica que tenga todas las columnas:

1. Ve a **Supabase Dashboard** → **SQL Editor**
2. Ejecuta este SQL para verificar/crear la tabla:

```sql
-- Verificar si la tabla existe y tiene todas las columnas
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

-- Crear índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp 
ON sensor_data(timestamp DESC);

-- Habilitar Row Level Security (RLS)
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Política para INSERT (desde Vercel/ESP32)
DROP POLICY IF EXISTS "Allow insert on sensor_data" ON sensor_data;
CREATE POLICY "Allow insert on sensor_data" 
ON sensor_data 
FOR INSERT 
TO anon, authenticated
WITH CHECK (true);

-- Política para SELECT (desde Vercel y script local)
DROP POLICY IF EXISTS "Allow select on sensor_data" ON sensor_data;
CREATE POLICY "Allow select on sensor_data" 
ON sensor_data 
FOR SELECT 
TO anon, authenticated
USING (true);
```

### **Paso 2: Crear Tabla `irrigation_predictions`** ⭐ **NUEVA**

Esta es la tabla nueva que necesitas crear para las predicciones:

1. Ve a **Supabase Dashboard** → **SQL Editor**
2. Ejecuta este SQL completo:

```sql
-- Crear tabla para almacenar predicciones de riego
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
DROP POLICY IF EXISTS "Allow insert for authenticated users" ON irrigation_predictions;
CREATE POLICY "Allow insert for authenticated users"
ON irrigation_predictions
FOR INSERT
TO authenticated
WITH CHECK (true);

-- Política alternativa para INSERT desde anon (si el script usa anon key)
DROP POLICY IF EXISTS "Allow insert for anon users" ON irrigation_predictions;
CREATE POLICY "Allow insert for anon users"
ON irrigation_predictions
FOR INSERT
TO anon
WITH CHECK (true);

-- Política para permitir SELECT (desde Vercel)
DROP POLICY IF EXISTS "Allow select for all users" ON irrigation_predictions;
CREATE POLICY "Allow select for all users"
ON irrigation_predictions
FOR SELECT
TO anon
USING (true);

-- Política para permitir SELECT a usuarios autenticados
DROP POLICY IF EXISTS "Allow select for authenticated users" ON irrigation_predictions;
CREATE POLICY "Allow select for authenticated users"
ON irrigation_predictions
FOR SELECT
TO authenticated
USING (true);
```

### **Paso 3: Verificar Configuración**

Ejecuta estos queries para verificar que todo esté bien:

```sql
-- Verificar tabla sensor_data
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sensor_data'
ORDER BY ordinal_position;

-- Verificar tabla irrigation_predictions
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'irrigation_predictions'
ORDER BY ordinal_position;

-- Verificar políticas RLS de sensor_data
SELECT * FROM pg_policies WHERE tablename = 'sensor_data';

-- Verificar políticas RLS de irrigation_predictions
SELECT * FROM pg_policies WHERE tablename = 'irrigation_predictions';
```

---

## 📊 Estructura de las Tablas

### **Tabla `sensor_data`** (Datos de Sensores)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | BIGSERIAL | ID único (auto-incremental) |
| `temperature1` | REAL | Temperatura sensor DHT11 #1 |
| `humidity1` | REAL | Humedad sensor DHT11 #1 |
| `temperature2` | REAL | Temperatura sensor DHT11 #2 |
| `humidity2` | REAL | Humedad sensor DHT11 #2 |
| `soil_moisture1` | REAL | Humedad suelo sensor #1 (0-100%) |
| `soil_moisture2` | REAL | Humedad suelo sensor #2 (0-100%) |
| `uv_index` | REAL | Índice UV (0-15) |
| `timestamp` | TEXT | Fecha/hora formato: YYYY-MM-DD HH:MM:SS |

### **Tabla `irrigation_predictions`** (Predicciones de Riego) ⭐

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | BIGSERIAL | ID único (auto-incremental) |
| `timestamp` | TEXT | Fecha/hora de la predicción |
| `prediction` | TEXT | "Regar" o "No regar" |
| `score` | REAL | Score continuo del modelo |
| `confidence` | REAL | Confianza (0-100%) |
| `uv_index` | REAL | Valor UV usado en predicción |
| `temperature2` | REAL | Temperatura usada |
| `humidity2` | REAL | Humedad usada |
| `soil_moisture1` | REAL | Humedad suelo 1 usada |
| `soil_moisture2` | REAL | Humedad suelo 2 usada |
| `created_at` | TIMESTAMP | Fecha de creación (auto) |

---

## 🔐 Políticas de Seguridad (RLS)

### **Para `sensor_data`:**
- ✅ **INSERT**: Permitido para `anon` y `authenticated` (Vercel y ESP32 pueden insertar)
- ✅ **SELECT**: Permitido para `anon` y `authenticated` (Todos pueden leer)

### **Para `irrigation_predictions`:**
- ✅ **INSERT**: Permitido para `anon` y `authenticated` (Script local puede insertar)
- ✅ **SELECT**: Permitido para `anon` y `authenticated` (Vercel puede leer)

---

## ✅ Checklist de Configuración

Marca cada paso cuando lo completes:

- [ ] Tabla `sensor_data` existe y tiene todas las columnas
- [ ] Tabla `sensor_data` tiene políticas RLS configuradas
- [ ] Tabla `irrigation_predictions` creada
- [ ] Tabla `irrigation_predictions` tiene todas las columnas
- [ ] Tabla `irrigation_predictions` tiene políticas RLS configuradas
- [ ] Índices creados en ambas tablas
- [ ] Verificación SQL ejecutada sin errores

---

## 🧪 Probar que Funciona

### **1. Probar Tabla `sensor_data`:**

```sql
-- Insertar un dato de prueba
INSERT INTO sensor_data (temperature1, humidity1, temperature2, humidity2, soil_moisture1, soil_moisture2, uv_index, timestamp)
VALUES (25.5, 60.0, 26.0, 58.0, 45.0, 50.0, 5.2, '2025-11-11 12:00:00');

-- Verificar que se insertó
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1;
```

### **2. Probar Tabla `irrigation_predictions`:**

```sql
-- Insertar una predicción de prueba
INSERT INTO irrigation_predictions (timestamp, prediction, score, confidence, uv_index, temperature2, humidity2, soil_moisture1, soil_moisture2)
VALUES ('2025-11-11 12:00:00', 'No regar', -0.0606, 43.94, 5.2, 25.5, 60.0, 45.0, 50.0);

-- Verificar que se insertó
SELECT * FROM irrigation_predictions ORDER BY timestamp DESC LIMIT 1;
```

---

## 🐛 Solución de Problemas

### **Error: "relation does not exist"**
- **Solución**: Ejecuta el SQL de creación de tabla primero

### **Error: "permission denied"**
- **Solución**: Verifica que las políticas RLS estén creadas correctamente

### **Error: "policy already exists"**
- **Solución**: Usa `DROP POLICY IF EXISTS` antes de crear la política

### **No se pueden insertar datos**
- **Solución**: Verifica que RLS esté habilitado y las políticas permitan INSERT

### **No se pueden leer datos**
- **Solución**: Verifica que las políticas permitan SELECT para `anon`

---

## 📝 Resumen Rápido

**Para que todo funcione, necesitas:**

1. ✅ Tabla `sensor_data` con políticas RLS (probablemente ya existe)
2. ⭐ Tabla `irrigation_predictions` con políticas RLS (NUEVA - créala)
3. ✅ Índices en ambas tablas para búsquedas rápidas
4. ✅ Políticas que permitan INSERT y SELECT

**Archivos SQL disponibles:**
- `CONFIGURAR_SUPABASE_TABLA.sql` - Para `sensor_data`
- `CREAR_TABLA_PREDICCIONES.sql` - Para `irrigation_predictions`

---

**¡Una vez configurado, el sistema funcionará completamente!** 🚀

