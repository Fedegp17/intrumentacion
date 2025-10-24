#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "MEGACABLE-2.4G-F6A3";
const char* password = "mKyUQGz295";

// Server configuration
const char* serverURL = "http://192.168.100.25:5000";  // IP de tu PC (actualizada)
const int LED_PIN = 13;  // LED interno del ESP32 (cambiamos para evitar conflicto con DHT11)

// DHT11 sensor configuration
#define DHT_PIN 2        // GPIO 2 (Pin 2) - Connect DHT11 data pin here (ESP32 DevKit v1)
#define DHT_TYPE DHT11   // DHT sensor type
DHT dht(DHT_PIN, DHT_TYPE);

// Timing configuration
unsigned long lastConnectionAttempt = 0;
unsigned long lastSensorReading = 0;
unsigned long lastDataSend = 0;
const unsigned long connectionInterval = 30000;  // 30 segundos
const unsigned long sensorInterval = 60000;      // 1 minuto
const unsigned long dataSendInterval = 900000;   // 15 minutos

// Connection status
bool serverConnected = false;
int connectionAttempts = 0;

// Sensor data variables
float humidity = 0.0;
float temperature = 0.0;

// LED control variables
bool ledState = false;
bool ledBlinking = false;
unsigned long lastBlinkTime = 0;
const unsigned long blinkInterval = 500;  // 500ms blink interval

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("🌱 ESP32 DHT11 Monitor Starting...");
  
  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // LED off initially
  
  // Initialize DHT11 sensor
  dht.begin();
  Serial.println("✅ DHT11 sensor initialized on GPIO 2");
  
  // Test DHT11 sensor on startup
  Serial.println("🧪 Testing DHT11 sensor...");
  delay(2000);  // Wait for sensor to stabilize
  readDHT11Sensor();
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("🚀 ESP32 DHT11 Monitor Ready!");
  Serial.println("📡 Will send data every 15 minutes");
  Serial.println("💡 LED control enabled - checking commands every 10 seconds");
  Serial.println("────────────────────────────────");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    if (currentTime - lastConnectionAttempt > connectionInterval) {
      Serial.println("❌ WiFi disconnected. Attempting reconnection...");
      connectToWiFi();
      lastConnectionAttempt = currentTime;
    }
    return;
  }
  
  // Read sensors every minute
  if (currentTime - lastSensorReading > sensorInterval) {
    readDHT11Sensor();
    lastSensorReading = currentTime;
  }
  
  // Send data to server every 30 minutes
  if (currentTime - lastDataSend > dataSendInterval) {
    sendSensorData();
    lastDataSend = currentTime;
  }
  
  // Update LED state (for blinking)
  updateLED();
  
  // Check for server commands every 10 seconds
  static unsigned long lastCommandCheck = 0;
  if (currentTime - lastCommandCheck > 10000) {  // Every 10 seconds
    checkServerCommands();
    lastCommandCheck = currentTime;
  }
  
  delay(1000);  // Small delay to prevent overwhelming the system
}

void connectToWiFi() {
  Serial.print("📶 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  connectionAttempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && connectionAttempts < 20) {
    delay(500);
    Serial.print(".");
    connectionAttempts++;
    
    // Blink LED during connection attempt
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected successfully!");
    Serial.print("🌐 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 Server URL: ");
    Serial.println(serverURL);
    
    // LED blinks 3 times for successful connection
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, LOW);
      delay(200);
      digitalWrite(LED_PIN, HIGH);
      delay(200);
    }
    
    serverConnected = true;
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
    digitalWrite(LED_PIN, HIGH);  // LED off on failure
    serverConnected = false;
  }
}

void readDHT11Sensor() {
  Serial.println("🌡️ Starting DHT11 sensor reading...");
  Serial.println("📍 Pin: GPIO 2 (D2)");
  
  // Read temperature and humidity
  float newTemperature = dht.readTemperature();
  float newHumidity = dht.readHumidity();
  
  Serial.printf("🔍 Raw readings - T: %.2f°C, H: %.2f%%\n", newTemperature, newHumidity);
  
  // Check if readings are valid
  if (isnan(newTemperature) || isnan(newHumidity)) {
    Serial.println("❌ FAILED to read from DHT11 sensor!");
    Serial.println("🔧 Troubleshooting steps:");
    Serial.println("   1. Check DHT11 connections:");
    Serial.println("      - VCC → 3.3V or 5V");
    Serial.println("      - GND → GND");
    Serial.println("      - Data → GPIO 2 (D2)");
    Serial.println("   2. Verify DHT11 is working");
    Serial.println("   3. Check power supply stability");
    Serial.println("   4. Try different DHT11 sensor");
    Serial.println("────────────────────────────────");
    return;
  }
  
  // Update global variables
  temperature = newTemperature;
  humidity = newHumidity;
  
  Serial.println("✅ DHT11 Reading SUCCESS:");
  Serial.printf("  🌡️ Temperature: %.1f°C\n", temperature);
  Serial.printf("  💧 Humidity: %.1f%%\n", humidity);
  Serial.println("📤 Data ready for transmission");
  Serial.println("────────────────────────────────");
  
  // LED blinks once for successful reading
  digitalWrite(LED_PIN, LOW);
  delay(100);
  digitalWrite(LED_PIN, HIGH);
}

void sendSensorData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ No WiFi connection. Cannot send data.");
    return;
  }
  
  Serial.println("⬆️ Sending DHT11 data to server...");
  Serial.printf("  Temperature: %.1f°C\n", temperature);
  Serial.printf("  Humidity: %.1f%%\n", humidity);
  
  HTTPClient http;
  String url = String(serverURL) + "/data";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);
  
  // Create JSON with sensor data
  DynamicJsonDocument doc(256);
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("📤 Sending JSON: " + jsonString);
  
  int httpCode = http.POST(jsonString);
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✅ DHT11 data sent successfully!");
    Serial.print("📥 Server response: ");
    Serial.println(response);
    
    // LED blinks twice for successful send
    for (int i = 0; i < 2; i++) {
      digitalWrite(LED_PIN, LOW);
      delay(150);
      digitalWrite(LED_PIN, HIGH);
      delay(150);
    }
    
    serverConnected = true;
    
  } else if (httpCode > 0) {
    Serial.printf("⚠️ HTTP error: %d\n", httpCode);
    String response = http.getString();
    Serial.println("Response: " + response);
    digitalWrite(LED_PIN, HIGH);  // LED off on error
    serverConnected = false;
    
  } else {
    Serial.println("❌ Connection failed to server");
    digitalWrite(LED_PIN, HIGH);  // LED off on error
    serverConnected = false;
  }
  
  http.end();
  
  // Print connection status
  if (serverConnected) {
    Serial.println("🟢 Server connection: OK");
  } else {
    Serial.println("🔴 Server connection: FAILED");
  }
  
  Serial.println("⏰ Next data send in 30 minutes");
  Serial.println("────────────────────────────────");
}

// LED Control Functions
void controlLED(String action) {
  Serial.println("💡 LED Control: " + action);
  
  if (action == "on") {
    ledState = true;
    ledBlinking = false;
    digitalWrite(LED_PIN, LOW);  // LED on
    Serial.println("✅ LED turned ON");
    
  } else if (action == "off") {
    ledState = false;
    ledBlinking = false;
    digitalWrite(LED_PIN, HIGH);  // LED off
    Serial.println("🔴 LED turned OFF");
    
  } else if (action == "blink") {
    ledState = true;
    ledBlinking = true;
    Serial.println("⚡ LED set to BLINKING mode");
    
  } else if (action == "toggle") {
    ledState = !ledState;
    ledBlinking = false;
    digitalWrite(LED_PIN, ledState ? LOW : HIGH);
    Serial.println(ledState ? "✅ LED toggled ON" : "🔴 LED toggled OFF");
  }
}

void updateLED() {
  if (ledBlinking) {
    unsigned long currentTime = millis();
    if (currentTime - lastBlinkTime >= blinkInterval) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      lastBlinkTime = currentTime;
    }
  }
}

void checkServerCommands() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/led-status";
  http.begin(url);
  http.setTimeout(5000);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("📥 Checking server commands...");
    
    // Parse JSON response to check for LED commands
    DynamicJsonDocument doc(256);
    deserializeJson(doc, response);
    
    if (doc.containsKey("led_command")) {
      String command = doc["led_command"];
      Serial.println("🎯 Received LED command: " + command);
      controlLED(command);
    }
    
    if (doc.containsKey("sensor_request")) {
      Serial.println("🌡️ Received sensor test request - reading sensors now!");
      readDHT11Sensor();
      sendSensorData();
    }
  }
  
  http.end();
}