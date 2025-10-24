# Configuración de Supabase para Vercel

## 📋 Pasos para configurar Supabase

### 1. Crear cuenta en Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Crea una cuenta gratuita
3. Crea un nuevo proyecto

### 2. Configurar la base de datos
1. En el dashboard de Supabase, ve a **SQL Editor**
2. Ejecuta este SQL para crear la tabla:

```sql
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    device_id VARCHAR(50) DEFAULT 'ESP32_DHT11',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_device_id ON sensor_data(device_id);
```

### 3. Obtener credenciales
1. Ve a **Settings** > **API**
2. Copia:
   - **Project URL** (SUPABASE_URL)
   - **anon public** key (SUPABASE_ANON_KEY)

### 4. Configurar variables en Vercel
1. Ve a tu proyecto en Vercel
2. Ve a **Settings** > **Environment Variables**
3. Agrega estas variables:
   - `SUPABASE_URL` = tu_project_url
   - `SUPABASE_ANON_KEY` = tu_anon_key

### 5. Configurar variables locales (opcional)
Crea un archivo `.env` en tu proyecto local:
```
SUPABASE_URL=tu_project_url
SUPABASE_ANON_KEY=tu_anon_key
```

## 🚀 Beneficios de Supabase

- **Base de datos en la nube** - No dependes de archivos locales
- **Escalabilidad** - Maneja millones de registros
- **Tiempo real** - Actualizaciones instantáneas
- **Backup automático** - Tus datos están seguros
- **API REST** - Fácil integración
- **Dashboard** - Visualiza tus datos fácilmente

## 📊 Estructura de la tabla

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | SERIAL | ID único auto-incremental |
| timestamp | TIMESTAMP | Fecha y hora de la lectura |
| temperature | DECIMAL(5,2) | Temperatura en °C |
| humidity | DECIMAL(5,2) | Humedad en % |
| device_id | VARCHAR(50) | ID del dispositivo (ESP32_DHT11) |
| created_at | TIMESTAMP | Fecha de creación del registro |

## 🔧 Funcionalidades implementadas

- ✅ **Guardado automático** en Supabase
- ✅ **Fallback a CSV** si Supabase falla
- ✅ **Gráficos desde Supabase** con fallback a CSV
- ✅ **Configuración flexible** con variables de entorno
- ✅ **Compatible con Vercel** y desarrollo local
