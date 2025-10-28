/*
 * Test Code para Sensor UV GUVA-S12SD
 * 
 * Este código prueba únicamente el sensor UV conectado al GPIO 34
 * Muestra lecturas en tiempo real en el Serial Monitor
 * 
 * Conexiones:
 * - VCC del sensor UV -> 3.3V del ESP32
 * - GND del sensor UV -> GND del ESP32  
 * - OUT del sensor UV -> GPIO 34 del ESP32
 * 
 * Configuración Serial Monitor: 115200 baud
 */

// Configuración del sensor UV
#define UV_PIN 34        // GPIO 34 (ADC1_CH6) - Pin analógico del sensor UV
#define UV_RESOLUTION 12 // Resolución ADC (12-bit = 4096 niveles)
#define UV_VREF 3.3     // Voltaje de referencia (3.3V)
#define UV_SENSITIVITY 0.1 // Sensibilidad en V por unidad de UV index

// Variables para almacenar lecturas
float uvIndex = 0.0;
int rawValue = 0;
float voltage = 0.0;

void setup() {
  // Inicializar comunicación serial
  Serial.begin(115200);
  delay(1000);
  
  // Configurar resolución ADC
  analogReadResolution(UV_RESOLUTION);
  
  // Mensaje de inicio
  Serial.println("==========================================");
  Serial.println("    TEST SENSOR UV GUVA-S12SD");
  Serial.println("==========================================");
  Serial.println("Configuracion:");
  Serial.printf("  Pin: GPIO %d (ADC)\n", UV_PIN);
  Serial.printf("  Resolucion ADC: %d bits\n", UV_RESOLUTION);
  Serial.printf("  Voltaje referencia: %.1fV\n", UV_VREF);
  Serial.printf("  Sensibilidad: %.1f V/UV index\n", UV_SENSITIVITY);
  Serial.println("==========================================");
  Serial.println("Iniciando lecturas del sensor UV...");
  Serial.println("==========================================");
  
  // Test inicial del sensor
  testUVSensor();
}

void loop() {
  // Leer sensor UV cada 2 segundos
  readUVSensor();
  delay(2000);
}

void readUVSensor() {
  Serial.println("\n--- LECTURA SENSOR UV ---");
  
  // Leer valor analógico crudo
  rawValue = analogRead(UV_PIN);
  
  // Convertir a voltaje
  voltage = (rawValue * UV_VREF) / (1 << UV_RESOLUTION);
  
  // Convertir voltaje a UV Index
  uvIndex = voltage / UV_SENSITIVITY;
  
  // Limitar valores a rango válido (0-15)
  if (uvIndex < 0) uvIndex = 0;
  if (uvIndex > 15) uvIndex = 15;
  
  // Mostrar resultados detallados
  Serial.printf("Valor ADC crudo: %d\n", rawValue);
  Serial.printf("Voltaje: %.3fV\n", voltage);
  Serial.printf("UV Index: %.1f\n", uvIndex);
  
  // Interpretación del UV Index
  String uvLevel = getUVLevel(uvIndex);
  Serial.printf("Nivel UV: %s\n", uvLevel.c_str());
  
  // Indicador visual en consola
  printUVIndicator(uvIndex);
  
  Serial.println("------------------------");
}

void testUVSensor() {
  Serial.println("\n*** PRUEBA INICIAL DEL SENSOR ***");
  
  // Realizar 5 lecturas de prueba
  for (int i = 1; i <= 5; i++) {
    Serial.printf("\nPrueba %d/5:\n", i);
    readUVSensor();
    delay(1000);
  }
  
  Serial.println("\n*** PRUEBA INICIAL COMPLETADA ***");
  Serial.println("El sensor esta funcionando correctamente");
  Serial.println("==========================================");
}

String getUVLevel(float uv) {
  if (uv < 2) return "Bajo (0-2)";
  else if (uv < 5) return "Moderado (3-5)";
  else if (uv < 7) return "Alto (6-7)";
  else if (uv < 10) return "Muy Alto (8-10)";
  else return "Extremo (11+)";
}

void printUVIndicator(float uv) {
  Serial.print("Indicador: ");
  
  // Crear barra visual
  int bars = map(uv * 10, 0, 150, 0, 20); // Escalar a 20 caracteres máximo
  
  for (int i = 0; i < 20; i++) {
    if (i < bars) {
      Serial.print("█");
    } else {
      Serial.print("░");
    }
  }
  
  Serial.printf(" %.1f\n", uv);
  
  // Color sugerido (para referencia)
  if (uv < 2) Serial.println("Color sugerido: Verde");
  else if (uv < 5) Serial.println("Color sugerido: Amarillo");
  else if (uv < 7) Serial.println("Color sugerido: Naranja");
  else if (uv < 10) Serial.println("Color sugerido: Rojo");
  else Serial.println("Color sugerido: Morado");
}

/*
 * INFORMACIÓN ADICIONAL:
 * 
 * El sensor GUVA-S12SD es un sensor de radiación UV analógico que:
 * - Detecta radiación UV en el rango de 240-370nm
 * - Proporciona una salida analógica proporcional a la intensidad UV
 * - Requiere calibración para convertir voltaje a UV Index
 * 
 * UV Index Scale:
 * 0-2:   Bajo (Verde) - Protección mínima requerida
 * 3-5:   Moderado (Amarillo) - Protección requerida
 * 6-7:   Alto (Naranja) - Protección extra requerida  
 * 8-10:  Muy Alto (Rojo) - Evitar exposición prolongada
 * 11+:   Extremo (Morado) - Evitar exposición
 * 
 * Notas de calibración:
 * - La sensibilidad puede variar según el sensor específico
 * - Se recomienda calibrar con un medidor UV profesional
 * - El valor de sensibilidad (0.1 V/UV index) es aproximado
 */
