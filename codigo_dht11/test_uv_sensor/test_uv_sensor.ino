const int UV_PIN = 34; // ADC1 pin

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // 0..4095
  analogSetPinAttenuation(UV_PIN, ADC_11db); // hasta ~3.3V rango
  delay(100);
}

void loop() {
  int raw = analogRead(UV_PIN);
  float voltage = raw * (3.3 / 4095.0);
  // aproximación de UVI (regla práctica en muchos módulos): UVI ≈ voltage / 0.1
  float uvi_approx = voltage / 0.1;
  Serial.print("RAW: "); Serial.print(raw);
  Serial.print("  V: "); Serial.print(voltage, 3);
  Serial.print("  UVI aprox: "); Serial.println(uvi_approx, 2);
  delay(500);
}