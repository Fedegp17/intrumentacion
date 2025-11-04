# Como Encontrar tu Supabase Project URL y Anon Key

## Paso 1: Acceder a Supabase Dashboard

1. Ve a: https://supabase.com/dashboard
2. Inicia sesion con tu cuenta
3. Selecciona tu proyecto (o crea uno nuevo si no tienes)

## Paso 2: Encontrar Project URL

### Opcion A: Desde Settings -> API

1. En el menu lateral izquierdo, click en **"Settings"** (Configuracion)
2. Click en **"API"** en el submenu
3. En la seccion **"Project URL"**, encontraras:
   - URL: `https://xxxxx.supabase.co`
   - Este es tu `SUPABASE_URL`

### Opcion B: Desde Project Settings

1. Click en el icono de engranaje (Settings) en el menu lateral
2. Click en **"API"**
3. Busca **"Project URL"** o **"Project URL"**
4. Copia la URL completa

### Opcion C: Desde la URL del navegador

1. Cuando estas en Supabase Dashboard
2. Mira la URL del navegador
3. Deberia ser algo como: `https://supabase.com/dashboard/project/xxxxx`
4. El `xxxxx` es tu project reference
5. Tu Project URL seria: `https://xxxxx.supabase.co`

## Paso 3: Encontrar Anon Key

En la misma pagina de Settings -> API:

1. Busca **"anon public"** key
2. O busca **"Project API keys"**
3. Copia la clave que dice **"anon public"** o **"anon"**
4. Esta es tu `SUPABASE_ANON_KEY`

## Ejemplo de Ubicacion

```
Supabase Dashboard
├── Settings
    ├── API
        ├── Project URL: https://abcdefghijklmnop.supabase.co
        ├── Project API keys
            ├── anon public: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Paso 4: Configurar en Vercel

Una vez que tengas ambos valores:

1. Ve a Vercel Dashboard
2. Tu proyecto -> Settings -> Environment Variables
3. Agrega:
   - **Key:** `SUPABASE_URL`
   - **Value:** `https://xxxxx.supabase.co` (tu Project URL)
4. Agrega:
   - **Key:** `SUPABASE_ANON_KEY`
   - **Value:** `eyJhbGci...` (tu anon key)
5. **Importante:** Selecciona "All Environments" para ambos
6. Click en "Save"
7. **Redeploy** el proyecto

## Si No Puedes Acceder a Supabase

### Opcion 1: Verificar Email de Invitacion
- Busca en tu email una invitacion a Supabase
- Puede tener el link al proyecto

### Opcion 2: Crear Nuevo Proyecto
1. Ve a https://supabase.com
2. Click en "Start your project"
3. Crea un nuevo proyecto
4. Sigue los pasos para obtener URL y Key

### Opcion 3: Contactar al Administrador
- Si alguien mas creo el proyecto
- Pide las credenciales al administrador

## Troubleshooting

### "No veo Settings en el menu"
- Asegurate de estar logueado
- Verifica que tienes permisos en el proyecto

### "No veo Project URL"
- Puede estar en otra seccion
- Busca "API" o "Configuration"

### "La URL no funciona"
- Verifica que sea HTTPS
- Verifica que termine en `.supabase.co`
- No uses la URL del dashboard

