/*
  Test Code for ESP32 DHT11 System
  Código de prueba para verificar funcionalidades del sistema IoT
  Simula datos del sensor DHT11 para pruebas sin hardware real
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "MEGACABLE-2.4G-F6A3";
const char* password = "mKyUQGz295";

// Server configuration
const char* serverURL = "http://192.168.100.25:5001";  // Test server port
const int LED_PIN = 13;  // LED interno del ESP32

// Test configuration
bool testMode = true;  // Enable test mode
unsigned long lastTestData = 0;
const unsigned long testInterval = 10000;  // Send test data every 10 seconds

// Simulated sensor data
float testTemperature = 25.0;
float testHumidity = 60.0;
int testCounter = 0;

// LED control variables
bool ledState = false;
bool ledBlinking = false;
unsigned long lastBlinkTime = 0;
const unsigned long blinkInterval = 500;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("🧪 ESP32 Test Code Starting...");
  Serial.println("📡 This code simulates DHT11 sensor for testing");
  
  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // LED off initially
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("🚀 ESP32 Test Code Ready!");
  Serial.println("📊 Will send test data every 10 seconds");
  Serial.println("💡 LED control enabled");
  Serial.println("────────────────────────────────");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi disconnected. Attempting reconnection...");
    connectToWiFi();
    return;
  }
  
  // Generate and send test data every 10 seconds
  if (currentTime - lastTestData > testInterval) {
    generateTestData();
    sendTestData();
    lastTestData = currentTime;
  }
  
  // Update LED state (for blinking)
  updateLED();
  
  // Check for server commands every 5 seconds
  static unsigned long lastCommandCheck = 0;
  if (currentTime - lastCommandCheck > 5000) {
    checkServerCommands();
    lastCommandCheck = currentTime;
  }
  
  delay(1000);
}

void connectToWiFi() {
  Serial.print("📶 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  int attempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
    
    // Blink LED during connection attempt
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected successfully!");
    Serial.print("🌐 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 Test Server URL: ");
    Serial.println(serverURL);
    
    // LED blinks 3 times for successful connection
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, LOW);
      delay(200);
      digitalWrite(LED_PIN, HIGH);
      delay(200);
    }
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
    digitalWrite(LED_PIN, HIGH);
  }
}

void generateTestData() {
  testCounter++;
  
  // Generate realistic test data with some variations
  if (testCounter % 5 == 0) {
    // Every 5th reading, generate high temperature for alert testing
    testTemperature = random(360, 420) / 10.0;  // 36.0 to 42.0°C
    testHumidity = random(60, 80);
    Serial.println("🔥 Generating HIGH temperature for alert test");
  } else {
    // Normal temperature range
    testTemperature = random(200, 350) / 10.0;  // 20.0 to 35.0°C
    testHumidity = random(40, 80);
  }
  
  Serial.println("🌡️ Generated test data:");
  Serial.printf("  Temperature: %.1f°C\n", testTemperature);
  Serial.printf("  Humidity: %.1f%%\n", testHumidity);
  Serial.printf("  Test counter: %d\n", testCounter);
}

void sendTestData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ No WiFi connection. Cannot send test data.");
    return;
  }
  
  Serial.println("⬆️ Sending test data to server...");
  
  HTTPClient http;
  String url = String(serverURL) + "/data";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);
  
  // Create JSON with test sensor data
  DynamicJsonDocument doc(256);
  doc["temperature"] = testTemperature;
  doc["humidity"] = testHumidity;
  doc["test_mode"] = true;
  doc["counter"] = testCounter;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("📤 Sending JSON: " + jsonString);
  
  int httpCode = http.POST(jsonString);
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✅ Test data sent successfully!");
    Serial.print("📥 Server response: ");
    Serial.println(response);
    
    // LED blinks twice for successful send
    for (int i = 0; i < 2; i++) {
      digitalWrite(LED_PIN, LOW);
      delay(150);
      digitalWrite(LED_PIN, HIGH);
      delay(150);
    }
    
  } else if (httpCode > 0) {
    Serial.printf("⚠️ HTTP error: %d\n", httpCode);
    String response = http.getString();
    Serial.println("Response: " + response);
    digitalWrite(LED_PIN, HIGH);
    
  } else {
    Serial.println("❌ Connection failed to test server");
    digitalWrite(LED_PIN, HIGH);
  }
  
  http.end();
  Serial.println("⏰ Next test data in 10 seconds");
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
      Serial.println("🌡️ Received sensor test request - generating test data now!");
      generateTestData();
      sendTestData();
    }
  }
  
  http.end();
}

// Test functions
void runSelfTest() {
  Serial.println("🧪 Running self-test...");
  
  // Test LED
  Serial.println("💡 Testing LED...");
  digitalWrite(LED_PIN, LOW);
  delay(500);
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  
  // Test WiFi
  Serial.println("📶 Testing WiFi...");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✅ WiFi test passed");
  } else {
    Serial.println("❌ WiFi test failed");
  }
  
  // Test data generation
  Serial.println("🌡️ Testing data generation...");
  generateTestData();
  Serial.println("✅ Data generation test passed");
  
  Serial.println("🎉 Self-test completed!");
}

void printSystemInfo() {
  Serial.println("📊 System Information:");
  Serial.printf("  ESP32 Chip ID: %d\n", ESP.getChipModel());
  Serial.printf("  Free Heap: %d bytes\n", ESP.getFreeHeap());
  Serial.printf("  Flash Size: %d bytes\n", ESP.getFlashChipSize());
  Serial.printf("  WiFi Status: %s\n", WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("  IP Address: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("  MAC Address: %s\n", WiFi.macAddress().c_str());
  }
  Serial.printf("  Test Counter: %d\n", testCounter);
  Serial.printf("  LED State: %s\n", ledState ? "ON" : "OFF");
  Serial.printf("  LED Blinking: %s\n", ledBlinking ? "YES" : "NO");
}
