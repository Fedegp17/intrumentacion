# Solucion: Datos no aparecen en Supabase

## Problema
- Los POST se ven en Vercel ✓
- Los datos NO aparecen en Supabase ✗

## Posibles Causas y Soluciones

### 1. Variables de Entorno no Configuradas en Vercel

**Sintoma:** Los logs de Vercel muestran errores de conexion a Supabase

**Solucion:**
1. Ve a Vercel Dashboard
2. Tu proyecto -> Settings -> Environment Variables
3. Agrega estas variables (si no existen):
   - **SUPABASE_URL**: Tu URL de Supabase (ej: `https://xxxxx.supabase.co`)
   - **SUPABASE_ANON_KEY**: Tu anon key de Supabase

4. **Importante:** Despues de agregar, redeploya el proyecto:
   - Ve a Deployments
   - Click en los 3 puntos del ultimo deployment
   - "Redeploy"

### 2. RLS (Row Level Security) no Configurado

**Sintoma:** Error 401 o 403 en logs de Vercel

**Solucion:**
Ejecuta este SQL en Supabase SQL Editor:

```sql
-- Habilitar RLS
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Eliminar politicas existentes si hay
DROP POLICY IF EXISTS "Allow insert on sensor_data" ON sensor_data;
DROP POLICY IF EXISTS "Allow select on sensor_data" ON sensor_data;

-- Crear politica para INSERT
CREATE POLICY "Allow insert on sensor_data" 
ON sensor_data 
FOR INSERT 
TO anon, authenticated
WITH CHECK (true);

-- Crear politica para SELECT
CREATE POLICY "Allow select on sensor_data" 
ON sensor_data 
FOR SELECT 
TO anon, authenticated
USING (true);
```

### 3. Tabla no Tiene Todas las Columnas

**Sintoma:** Error 400 en logs de Vercel

**Solucion:**
Verifica que la tabla tenga todas las columnas:

```sql
-- Ver columnas
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sensor_data'
ORDER BY ordinal_position;
```

Si falta alguna columna, agregala:

```sql
ALTER TABLE sensor_data 
ADD COLUMN IF NOT EXISTS temperature1 REAL,
ADD COLUMN IF NOT EXISTS humidity1 REAL,
ADD COLUMN IF NOT EXISTS temperature2 REAL,
ADD COLUMN IF NOT EXISTS humidity2 REAL,
ADD COLUMN IF NOT EXISTS soil_moisture1 REAL,
ADD COLUMN IF NOT EXISTS soil_moisture2 REAL,
ADD COLUMN IF NOT EXISTS uv_index REAL,
ADD COLUMN IF NOT EXISTS timestamp TEXT;
```

### 4. Codigo del Servidor no Guarda en Supabase

**Sintoma:** El servidor responde 200 pero no guarda

**Solucion:**
- Verifica que el servidor tenga el codigo para guardar en Supabase
- Si eliminaste el codigo del servidor, necesitas recrearlo

## Pasos de Diagnostico

### Paso 1: Verificar Logs de Vercel
1. Ve a Vercel Dashboard
2. Tu proyecto -> Logs
3. Busca errores relacionados con:
   - "Supabase"
   - "insert"
   - "401", "403", "500"

### Paso 2: Probar Conexion Directa a Supabase
Ejecuta:
```bash
python test_supabase_direct.py
```

Este script intentara insertar datos directamente en Supabase.

### Paso 3: Verificar Variables de Entorno
1. Ve a Vercel Dashboard
2. Settings -> Environment Variables
3. Verifica que existan:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

### Paso 4: Verificar RLS
1. Ve a Supabase Dashboard
2. SQL Editor
3. Ejecuta:
```sql
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5;
```

Si no puedes leer, RLS esta bloqueando.

## Checklist de Verificacion

- [ ] Variables de entorno configuradas en Vercel
- [ ] Proyecto redeployado en Vercel despues de agregar variables
- [ ] RLS habilitado en Supabase
- [ ] Politicas RLS creadas (INSERT y SELECT)
- [ ] Tabla tiene todas las columnas necesarias
- [ ] Logs de Vercel no muestran errores de Supabase
- [ ] Prueba directa a Supabase funciona

## Test Rapido

1. **Verificar variables en Vercel:**
   - Dashboard -> Settings -> Environment Variables
   - Debe tener SUPABASE_URL y SUPABASE_ANON_KEY

2. **Verificar RLS:**
   - Supabase SQL Editor
   - Ejecutar politicas de RLS

3. **Redeployar en Vercel:**
   - Deployments -> Redeploy

4. **Probar de nuevo:**
   ```bash
   python test_dummy_data.py
   ```

5. **Verificar en Supabase:**
   - Table Editor -> sensor_data
   - Debe aparecer nuevos registros

## Si Nada Funciona

Si despues de todos estos pasos no funciona:

1. Verifica que el servidor en Vercel tenga el codigo para guardar en Supabase
2. Si el servidor fue eliminado, necesitas recrearlo
3. El servidor debe tener:
   - Import de supabase
   - Funcion para insertar datos
   - Llamada a esa funcion cuando recibe POST /data

