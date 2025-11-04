# Pasos Siguientes - Configuracion Completa

## ✅ Ya Completado:
1. ✅ Variables de entorno configuradas en Vercel:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

## 🔧 Siguiente Paso: Habilitar RLS en Supabase

### Instrucciones:

1. **Ve a Supabase Dashboard**
   - Abre: https://supabase.com/dashboard
   - Selecciona tu proyecto

2. **Abre SQL Editor**
   - En el menu lateral, click en "SQL Editor"
   - Click en "New query"

3. **Ejecuta el SQL**
   - Copia y pega el contenido de `SOLUCION_RLS_COMPLETA.sql`
   - Click en "Run" o presiona Ctrl+Enter

4. **Verifica que funciono**
   - Deberias ver un mensaje de exito
   - No deberia haber errores

## 🧪 Pruebas

### Test 1: Verificar que Supabase funciona
1. Espera a que el ESP32 envie datos (maximo 5 minutos)
2. Ve a Supabase → Table Editor → sensor_data
3. Deberias ver un nuevo registro con todos los valores

### Test 2: Verificar que la pagina muestra datos
1. Abre: https://intrumentacion.vercel.app
2. Presiona "Actualizar Datos Ahora"
3. Deberias ver los valores de los sensores actualizados

### Test 3: Verificar LED
1. Presiona "Probar LED - Parpadear" en la pagina
2. Espera maximo 10 segundos
3. El LED del ESP32 deberia parpadear
4. Revisa Serial Monitor para confirmar

## 📊 Verificacion de Tabla en Supabase

Ejecuta este SQL para verificar que la tabla tiene todas las columnas:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sensor_data'
ORDER BY ordinal_position;
```

Deberias ver:
- id
- temperature1
- humidity1
- temperature2
- humidity2
- soil_moisture1
- soil_moisture2
- uv_index
- timestamp

## ⚠️ Si Aun Hay Problemas

### Error: "Table is public, but RLS has not been enabled"
- **Solucion:** Ejecuta el SQL de `SOLUCION_RLS_COMPLETA.sql`

### Error: "column uv_index does not exist"
- **Solucion:** Ejecuta: `ALTER TABLE sensor_data ADD COLUMN IF NOT EXISTS uv_index REAL;`

### Error: "permission denied"
- **Solucion:** Verifica que las politicas RLS esten creadas correctamente

### Los datos no se guardan
1. Revisa logs de Vercel para ver errores
2. Verifica que las variables de entorno sean correctas
3. Verifica que la tabla tenga todas las columnas

## 🎯 Estado Actual

- ✅ Variables de entorno configuradas en Vercel
- ⏳ Pendiente: Ejecutar SQL para habilitar RLS
- ⏳ Pendiente: Verificar que todo funcione

## 📝 Notas

- Las variables de entorno estan configuradas para "All Environments"
- Esto significa que funcionan en Production, Preview y Development
- Despues de ejecutar el SQL, el sistema deberia funcionar completamente

