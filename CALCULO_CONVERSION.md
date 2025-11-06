# Calculo de Conversion: Voltaje a ADC y Humedad

## Datos proporcionados
- **Voltaje medido**: 0.169V
- **Voltaje de referencia ESP32**: 3.3V
- **Resolucion ADC**: 12 bits (0-4095)

## Calculo 1: Voltaje a Valor ADC

```
ADC_value = (Voltaje_medido / Voltaje_referencia) * Resolucion_maxima
ADC_value = (0.169V / 3.3V) * 4095
ADC_value = 0.0512 * 4095
ADC_value ≈ 209.7
ADC_value ≈ 210 (redondeado)
```

**Resultado: ADC ≈ 210**

## Calculo 2: Valor ADC a Porcentaje de Humedad

Con la configuracion actual (mapeo invertido):
- **ADC_MIN** = 1000 (suelo completamente humedo - LOW ADC = HIGH HUMIDITY)
- **ADC_MAX** = 3200 (suelo completamente seco - HIGH ADC = LOW HUMIDITY)

### Caso 1: Si el valor ADC esta dentro del rango

```
ADC_value = 210 (por debajo de ADC_MIN = 1000)
```

El valor 210 esta **por debajo del rango minimo** (1000), por lo que:
- `constrain(210, 1000, 3200) = 1000`
- `map(1000, 1000, 3200, 100, 0) = 100%`

**Resultado: Humedad = 100%** (suelo muy humedo)

### Caso 2: Si ajustamos el rango para incluir este valor

Si el sensor esta dando 0.169V (ADC ≈ 210) cuando el suelo esta humedo, necesitamos ajustar `ADC_MIN`:

**Opcion A: Ajustar ADC_MIN a un valor mas bajo**
```
ADC_MIN = 200   // Incluir valores ADC bajos (suelo muy humedo)
ADC_MAX = 3200  // Mantener para suelo seco
```

Entonces:
```
map(210, 200, 3200, 100, 0) = 100 - ((210-200) / (3200-200)) * 100
map(210, 200, 3200, 100, 0) = 100 - (10/3000) * 100
map(210, 200, 3200, 100, 0) = 100 - 0.33
map(210, 200, 3200, 100, 0) ≈ 99.67%
```

**Resultado: Humedad ≈ 99.7%**

## Recomendaciones

1. **Si 0.169V es cuando el suelo esta muy humedo (recien regado):**
   - Ajusta `ADC_MIN = 200` o menos para capturar este valor
   - Esto permitira que valores ADC bajos (como 210) mapeen a humedad alta (>90%)

2. **Si 0.169V es cuando el suelo esta seco:**
   - El codigo actual deberia funcionar correctamente
   - Pero necesitaras ajustar `ADC_MAX` basado en el valor cuando este seco

3. **Para calibrar correctamente:**
   - Mide el voltaje/ADC cuando el suelo este completamente seco
   - Mide el voltaje/ADC cuando el suelo este completamente humedo (recien regado)
   - Usa esos valores para ajustar `ADC_MIN` y `ADC_MAX`

## Formula General

```
Voltaje → ADC:
ADC = (Voltaje / 3.3V) * 4095

ADC → Humedad (con mapeo invertido):
Si ADC < ADC_MIN: Humedad = 100%
Si ADC > ADC_MAX: Humedad = 0%
Si ADC_MIN ≤ ADC ≤ ADC_MAX:
  Humedad = 100 - ((ADC - ADC_MIN) / (ADC_MAX - ADC_MIN)) * 100
```

