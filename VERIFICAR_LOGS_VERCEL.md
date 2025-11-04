# Como Verificar Logs de Vercel para Diagnosticar Supabase

## Acceder a Logs de Vercel

### Paso 1: Ir a Vercel Dashboard
1. Ve a: https://vercel.com/dashboard
2. Selecciona tu proyecto: `intrumentacion-7fkz`

### Paso 2: Abrir Logs
1. Click en **"Logs"** en el menu superior
2. O ve a **"Deployments"** y click en el ultimo deployment
3. Luego click en **"Logs"** o **"View Logs"**

### Paso 3: Buscar Errores
Busca en los logs mensajes relacionados con:
- `Supabase`
- `insert`
- `401`, `403`, `500`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `error`
- `failed`

## Errores Comunes y Soluciones

### Error: "SUPABASE_URL is not defined"
**Causa:** Variable de entorno no configurada
**Solucion:**
1. Settings -> Environment Variables
2. Agrega `SUPABASE_URL`
3. Redeploy

### Error: "SUPABASE_ANON_KEY is not defined"
**Causa:** Variable de entorno no configurada
**Solucion:**
1. Settings -> Environment Variables
2. Agrega `SUPABASE_ANON_KEY`
3. Redeploy

### Error: "401 Unauthorized"
**Causa:** RLS bloqueando o key incorrecta
**Solucion:**
1. Verifica que `SUPABASE_ANON_KEY` sea correcta
2. Verifica RLS policies en Supabase
3. Ejecuta CONFIGURAR_SUPABASE_TABLA.sql

### Error: "404 Not Found"
**Causa:** Tabla no existe o URL incorrecta
**Solucion:**
1. Verifica que `SUPABASE_URL` sea correcta
2. Verifica que la tabla `sensor_data` exista
3. Ejecuta CONFIGURAR_SUPABASE_TABLA.sql

### Error: "400 Bad Request"
**Causa:** Columnas faltantes en la tabla
**Solucion:**
1. Ejecuta CONFIGURAR_SUPABASE_TABLA.sql
2. Verifica que todas las columnas existan

### Sin Errores pero No Guarda
**Causa:** El servidor no tiene codigo para guardar
**Solucion:**
1. Verifica que el servidor tenga el codigo de Supabase
2. Si eliminaste el servidor, necesitas recrearlo

## Como Filtrar Logs

En la interfaz de logs de Vercel:
1. Usa el campo de busqueda
2. Busca: `Supabase`, `error`, `insert`
3. Filtra por tiempo (ultimas horas)

## Verificar Variables de Entorno

1. Ve a Settings -> Environment Variables
2. Verifica que existan:
   - `SUPABASE_URL` = `https://ohqufueaipkitngjqsbe.supabase.co`
   - `SUPABASE_ANON_KEY` = `eyJhbGci...`
3. Verifica que esten en "All Environments"

## Verificar Deployment

1. Ve a Deployments
2. Verifica que el ultimo deployment sea exitoso
3. Si hay errores, click en el deployment para ver detalles
4. Si cambiaste variables, asegurate de hacer redeploy

## Script de Verificacion

Ejecuta:
```bash
python test_vercel_supabase_connection.py
```

Este script:
1. Prueba conexion directa a Supabase (como lo haria Vercel)
2. Prueba enviando datos via Vercel
3. Muestra donde esta el problema

