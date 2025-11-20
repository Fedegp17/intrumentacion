# 🔄 Flujo de Predicción de Riego

## 📋 ¿Qué hace el script `local_irrigation_predictor.py`?

### ✅ **SÍ hace:**
1. ✅ **Lee datos de Supabase** (últimos datos del sensor)
2. ✅ **Hace predicción** usando scikit-learn completo
3. ✅ **Guarda resultado en Supabase** (tabla `irrigation_predictions`)

### ❌ **NO hace directamente:**
- ❌ NO envía directamente a Vercel
- ❌ NO se comunica con Vercel

## 🔄 Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO ACTUAL                              │
└─────────────────────────────────────────────────────────────┘

1. ESP32 → Vercel → Supabase (sensor_data)
   └─ Datos de sensores guardados cada 5 minutos

2. Tú ejecutas: python local_irrigation_predictor.py
   ├─ Lee últimos datos de Supabase
   ├─ Hace predicción con scikit-learn
   └─ Guarda resultado en Supabase (irrigation_predictions)

3. Usuario presiona "¿Debo Regar?" en Vercel
   └─ Vercel lee última predicción de Supabase
   └─ Muestra resultado en interfaz web
```

## 📊 Detalles del Flujo

### **Paso 1: Script Local**
```python
# local_irrigation_predictor.py hace:
1. get_latest_sensor_data() → Lee de Supabase (sensor_data)
2. predict_irrigation() → Hace predicción con scikit-learn
3. save_prediction_to_supabase() → Guarda en Supabase (irrigation_predictions)
```

### **Paso 2: Vercel**
```python
# principal_code_simple.py hace:
1. Usuario presiona botón "¿Debo Regar?"
2. POST /predict-irrigation
3. get_latest_irrigation_prediction() → Lee de Supabase (irrigation_predictions)
4. Retorna resultado al usuario
```

## 🎯 Respuesta a tu Pregunta

**¿El script manda la predicción a Vercel y la guarda en Supabase?**

**Respuesta:**
- ✅ **SÍ guarda en Supabase** (tabla `irrigation_predictions`)
- ❌ **NO envía directamente a Vercel**
- ✅ **Vercel lee de Supabase** cuando el usuario presiona el botón

## 💡 ¿Por qué este diseño?

### **Ventajas:**
1. **Desacoplamiento**: Script local y Vercel son independientes
2. **Historial**: Todas las predicciones quedan guardadas en Supabase
3. **Flexibilidad**: Puedes ejecutar el script cuando quieras
4. **Simplicidad**: No necesitas mantener conexión con Vercel

### **Flujo Alternativo (si quisieras enviar directamente a Vercel):**

Si quisieras que el script también envíe directamente a Vercel, necesitarías:
1. Un endpoint en Vercel para recibir predicciones (ej: POST /receive-prediction)
2. Modificar el script para hacer HTTP POST a ese endpoint
3. Vercel almacenaría la predicción en memoria o en Supabase

**Pero esto NO es necesario** porque:
- Vercel ya lee de Supabase (más confiable)
- Supabase actúa como base de datos centralizada
- Es más simple y robusto

## 📝 Resumen

```
Script Local:
  ✅ Lee de Supabase
  ✅ Predice con scikit-learn
  ✅ Guarda en Supabase
  
Vercel:
  ✅ Lee de Supabase (cuando usuario presiona botón)
  ✅ Muestra resultado
  
Supabase:
  ✅ Almacena datos de sensores (sensor_data)
  ✅ Almacena predicciones (irrigation_predictions)
```

## 🚀 Para Usar

1. **Ejecuta el script local**:
   ```bash
   python local_irrigation_predictor.py
   ```

2. **Verifica en Supabase**:
   - Ve a tabla `irrigation_predictions`
   - Debe haber un nuevo registro

3. **Prueba en Vercel**:
   - Abre la interfaz web
   - Presiona "¿Debo Regar?"
   - Verás el resultado guardado en Supabase

---

**Conclusión**: El script guarda en Supabase, y Vercel lee de Supabase. No hay comunicación directa entre el script y Vercel, pero ambos usan Supabase como intermediario.

