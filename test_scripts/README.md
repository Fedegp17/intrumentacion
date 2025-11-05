# Scripts de Prueba

Esta carpeta contiene scripts de prueba para diagnosticar y verificar el sistema.

## Scripts Disponibles

### test_dummy_data.py
Script principal para enviar datos dummy y diagnosticar conexiones.

**Uso:**
```bash
# Modo normal (envio continuo)
python test_dummy_data.py

# Modo diagnostico
python test_dummy_data.py --diagnostico
```

**Funcionalidades:**
- Envia datos dummy al servidor de Vercel
- Prueba conexion directa a Supabase
- Diagnostica problemas de conexion

### verificar_datos_supabase.py
Verifica si los datos se estan guardando en Supabase desde Vercel.

**Uso:**
```bash
python verificar_datos_supabase.py
```

**Funcionalidades:**
- Cuenta registros antes y despues de enviar
- Verifica si los datos se guardan correctamente

### test_verificar_ultimo_envio.py
Verifica si el ultimo envio se guardo en Supabase usando valores unicos.

**Uso:**
```bash
python test_verificar_ultimo_envio.py
```

**Funcionalidades:**
- Envia datos con valores unicos (para identificarlos)
- Verifica si aparecen en Supabase

## Notas

- Estos scripts son para pruebas y diagnostico
- No se usan en produccion
- Pueden modificarse segun necesidades

