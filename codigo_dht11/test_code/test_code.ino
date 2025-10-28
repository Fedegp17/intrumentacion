/*
  ESP32 + DHT11 - Lecturas simples por Serial
  Conecta el DHT11 a: VCC (3.3V/5V), GND, DATA → GPIO 2
*/

#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("🌡️ Test DHT11 (Serial)");
  Serial.println("📍 Pin: GPIO 2");
  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("❌ Error leyendo DHT11. Revisa conexiones.");
  } else {
    Serial.printf("Temp: %.1f°C  |  Hum: %.1f%%\n", temperature, humidity);
  }

  delay(2000);
}
