# Configurar Variables de Entorno en Vercel

## Credenciales de Supabase

Usa estas credenciales para configurar Vercel:

### SUPABASE_URL
```
https://ohqufueaipkitngjqsbe.supabase.co
```

### SUPABASE_ANON_KEY
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ocXVmdWVhaXBraXRuZ2pxc2JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNTU5MTksImV4cCI6MjA3NjgzMTkxOX0.iG14a2j8dm2xrX_PDHERQRKP18u6NZPRpWVjmGpgtoY
```

## Pasos para Configurar en Vercel

### 1. Acceder a Vercel Dashboard
1. Ve a: https://vercel.com/dashboard
2. Selecciona tu proyecto: `intrumentacion-7fkz`

### 2. Ir a Environment Variables
1. Click en **Settings** (en el menu superior)
2. Click en **Environment Variables** (en el menu lateral)

### 3. Agregar SUPABASE_URL
1. Click en **"Add New"**
2. **Key:** `SUPABASE_URL`
3. **Value:** `https://ohqufueaipkitngjqsbe.supabase.co`
4. **Environment:** Selecciona "All Environments" (Production, Preview, Development)
5. Click en **"Save"**

### 4. Agregar SUPABASE_ANON_KEY
1. Click en **"Add New"**
2. **Key:** `SUPABASE_ANON_KEY`
3. **Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ocXVmdWVhaXBraXRuZ2pxc2JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNTU5MTksImV4cCI6MjA3NjgzMTkxOX0.iG14a2j8dm2xrX_PDHERQRKP18u6NZPRpWVjmGpgtoY`
4. **Environment:** Selecciona "All Environments"
5. Click en **"Save"**

### 5. IMPORTANTE: Redeploy el Proyecto
1. Ve a **Deployments** (en el menu superior)
2. Encuentra el ultimo deployment
3. Click en los **3 puntos** (...)
4. Click en **"Redeploy"**
5. Confirmar redeploy

**Nota:** Las variables de entorno solo se aplican en nuevos deployments. 
Por eso es necesario redeployar despues de agregar las variables.

## Verificacion

Despues de redeployar:

1. Espera a que el deployment termine (2-3 minutos)
2. Ejecuta: `python test_dummy_data.py`
3. Verifica en Supabase Table Editor que aparezcan datos

## Si No Funciona

1. Verifica que las variables esten correctamente escritas (sin espacios)
2. Verifica que hayas seleccionado "All Environments"
3. Verifica que hayas hecho redeploy
4. Revisa los logs de Vercel para errores

