# 🌱 Sistema de Predicción de Riego Local

## 📋 Descripción

Este sistema permite ejecutar la predicción de riego en tu computadora local usando **scikit-learn completo**, mientras que Vercel solo muestra el resultado. Esto permite usar modelos más robustos sin las limitaciones de tamaño de Vercel.

## 🔄 Flujo de Información

```
ESP32 → Vercel → Supabase → Computadora Local → Supabase → Vercel → Interfaz Web
         (envía)  (guarda)   (lee, predice)      (guarda)   (lee)    (muestra)
```

### Paso a Paso:

1. **ESP32** envía datos de sensores → **Vercel** (cada 5 minutos)
2. **Vercel** guarda datos en **Supabase** (tabla `sensor_data`)
3. **Computadora Local** ejecuta `local_irrigation_predictor.py`:
   - Lee últimos datos de Supabase
   - Usa scikit-learn para hacer predicción
   - Guarda resultado en Supabase (tabla `irrigation_predictions`)
4. **Usuario** presiona botón "¿Debo Regar?" en Vercel
5. **Vercel** lee última predicción de Supabase
6. **Interfaz Web** muestra el resultado

## 🚀 Configuración Inicial

### 1. Crear Tabla en Supabase

Ejecuta el SQL en Supabase SQL Editor:

```bash
# Abre CREAR_TABLA_PREDICCIONES.sql y copia el contenido
# Pégalo en Supabase SQL Editor y ejecuta
```

O ejecuta directamente:

```sql
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

-- Habilitar RLS
ALTER TABLE irrigation_predictions ENABLE ROW LEVEL SECURITY;

-- Políticas
CREATE POLICY "Allow insert for authenticated users"
ON irrigation_predictions FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow select for all users"
ON irrigation_predictions FOR SELECT TO anon USING (true);
```

### 2. Instalar Dependencias en Computadora Local

```bash
pip install -r requirements-ml.txt
pip install supabase python-dotenv
```

### 3. Configurar Variables de Entorno

Asegúrate de tener `supabase.env` con:

```
SUPABASE_URL=tu_url_de_supabase
SUPABASE_ANON_KEY=tu_anon_key
```

## 📝 Uso

### Ejecución Manual

Ejecuta el script cuando quieras hacer una predicción:

```bash
python local_irrigation_predictor.py
```

**Salida esperada:**
```
============================================================
🌱 Sistema de Predicción de Riego Local
============================================================

📡 Obteniendo últimos datos de Supabase...
✅ Datos obtenidos:
   - UV Index: 5.2
   - Temperatura 2: 25.5°C
   - Humedad 2: 60.0%
   - Humedad Suelo 1: 45.0%
   - Humedad Suelo 2: 50.0%
   - Timestamp: 2025-11-11 12:30:45

🧠 Haciendo predicción con scikit-learn...
============================================================
📊 RESULTADO DE LA PREDICCIÓN
============================================================
🌱 Decisión: No regar
📈 Score: -0.0606
🎯 Confianza: 43.94%
⚖️  Umbral: 0.5
============================================================

💾 Guardando resultado en Supabase...
✅ Predicción guardada en Supabase: No regar
✅ Proceso completado exitosamente
🌐 El resultado está disponible en Vercel
```

### Ejecución Automática (Opcional)

Puedes configurar una tarea programada para ejecutar el script periódicamente:

#### Windows (Task Scheduler):

1. Abre "Programador de tareas"
2. Crea tarea básica
3. Configura para ejecutar cada hora:
   ```
   Programa: python
   Argumentos: C:\ruta\a\local_irrigation_predictor.py
   ```

#### Linux/Mac (Cron):

```bash
# Editar crontab
crontab -e

# Ejecutar cada hora
0 * * * * cd /ruta/al/proyecto && python local_irrigation_predictor.py >> /tmp/irrigation.log 2>&1
```

## 🔧 Funcionamiento Técnico

### Script Local (`local_irrigation_predictor.py`)

1. **Conecta a Supabase** usando credenciales de `supabase.env`
2. **Obtiene últimos datos** de la tabla `sensor_data`
3. **Crea modelo de regresión lineal** con scikit-learn:
   - Usa los coeficientes entrenados del modelo
   - Pipeline con StandardScaler y LinearRegression
4. **Hace predicción** con los datos del sensor
5. **Guarda resultado** en tabla `irrigation_predictions`

### Vercel (`principal_code_simple.py`)

1. **Endpoint `/predict-irrigation`** (POST):
   - Lee última predicción de Supabase
   - Retorna resultado en JSON
   - No hace procesamiento pesado

### Interfaz Web

1. **Botón "¿Debo Regar?"**:
   - Envía POST a `/predict-irrigation`
   - Muestra resultado en alerta
   - Incluye score, confianza y datos utilizados

## 📊 Estructura de Datos

### Tabla `irrigation_predictions`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único (auto-incremental) |
| timestamp | TEXT | Timestamp de la predicción |
| prediction | TEXT | "Regar" o "No regar" |
| score | REAL | Score continuo del modelo |
| confidence | REAL | Confianza (0-100%) |
| uv_index | REAL | Valor UV usado |
| temperature2 | REAL | Temperatura usada |
| humidity2 | REAL | Humedad usada |
| soil_moisture1 | REAL | Humedad suelo 1 usada |
| soil_moisture2 | REAL | Humedad suelo 2 usada |
| created_at | TIMESTAMP | Fecha de creación |

## 🎯 Ventajas de este Sistema

✅ **Modelos más robustos**: Puedes usar scikit-learn completo  
✅ **Sin limitaciones de tamaño**: No hay restricción de 250MB  
✅ **Procesamiento local**: Control total sobre el modelo  
✅ **Historial completo**: Todas las predicciones guardadas  
✅ **Flexibilidad**: Puedes cambiar el modelo fácilmente  
✅ **Escalabilidad**: Vercel solo muestra resultados (muy rápido)  

## 🔍 Verificación

### Verificar que funciona:

1. **Ejecuta el script local**:
   ```bash
   python local_irrigation_predictor.py
   ```

2. **Verifica en Supabase**:
   - Ve a la tabla `irrigation_predictions`
   - Debe haber un nuevo registro

3. **Prueba en Vercel**:
   - Abre la interfaz web
   - Presiona "¿Debo Regar?"
   - Debe mostrar el resultado

## 🐛 Solución de Problemas

### Error: "No se encontraron datos del sensor"
- **Solución**: Asegúrate de que el ESP32 haya enviado datos recientemente

### Error: "No se pudo guardar la predicción"
- **Solución**: Verifica que la tabla `irrigation_predictions` exista en Supabase

### Error: "Supabase no disponible"
- **Solución**: Verifica que `supabase.env` tenga las credenciales correctas

### Error: "No hay predicciones disponibles"
- **Solución**: Ejecuta `local_irrigation_predictor.py` primero

## 📈 Próximos Pasos

- [ ] Configurar ejecución automática cada hora
- [ ] Agregar notificaciones cuando se recomienda regar
- [ ] Mejorar el modelo con más datos
- [ ] Agregar gráficas de historial de predicciones

---

**Última actualización**: 2025-11-11

