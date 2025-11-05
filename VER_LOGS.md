# Como Ver los Logs del Servidor

## Endpoint de Logs

Para ver los logs del servidor y diagnosticar problemas con Supabase, puedes acceder a:

```
https://intrumentacion-7fkz.vercel.app/logs
```

Este endpoint retorna los ultimos 50 logs del servidor, incluyendo:
- Timestamp de cada evento
- Nivel (INFO, WARNING, ERROR)
- Mensaje descriptivo

## Tipos de Logs

### INFO
- Datos guardados exitosamente en Supabase
- Datos recibidos del ESP32
- Solicitudes de datos procesadas
- Datos cargados desde Supabase

### WARNING
- Datos recibidos pero fallo al guardar en Supabase
- Fallo al cargar datos desde Supabase

### ERROR
- Errores al guardar en Supabase (con detalles del error)
- Errores en las funciones del servidor

## Ejemplo de Uso

```bash
curl https://intrumentacion-7fkz.vercel.app/logs
```

O abre el URL en tu navegador para ver el JSON con los logs.

## Verificar Estado de Supabase

Si los logs muestran errores al guardar en Supabase, verifica:
1. Variables de entorno en Vercel (SUPABASE_URL, SUPABASE_KEY)
2. Permisos RLS en Supabase
3. Estructura de la tabla sensor_data

