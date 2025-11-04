#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials - Usar credenciales guardadas
// IMPORTANTE: Actualizar con tus credenciales desde CREDENCIALES.txt
const char* ssid = "MEGACABLE-2.4G-F6A3";
const char* password = "mKyUQGz295";

// Server configuration
const char* serverURL = "https://intrumentacion-7fkz.vercel.app";

// Timing configuration
unsigned long lastDataSend = 0;
const unsigned long dataSendInterval = 30000;  // 30 segundos para pruebas rapidas

// Connection status
bool serverConnected = false;
int connectionAttempts = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("==========================================");
  Serial.println("ESP32 Dummy Data Test - Starting...");
  Serial.println("==========================================");
  Serial.println("This code sends dummy sensor data to test");
  Serial.println("the connection between ESP32 -> Vercel -> Supabase");
  Serial.println("--------------------------------");
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("ESP32 Dummy Data Test Ready!");
  Serial.println("Will send dummy data every 30 seconds");
  Serial.println("==========================================");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    if (currentTime - lastDataSend > 30000) {  // Try to reconnect every 30 seconds
      Serial.println("WiFi disconnected. Attempting reconnection...");
      connectToWiFi();
      lastDataSend = currentTime;
    }
    delay(1000);
    return;
  }
  
  // Send dummy data every 30 seconds
  if (currentTime - lastDataSend > dataSendInterval) {
    sendDummyData();
    lastDataSend = currentTime;
  }
  
  delay(1000);
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  connectionAttempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && connectionAttempts < 20) {
    delay(500);
    Serial.print(".");
    connectionAttempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi connected successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Server URL: ");
    Serial.println(serverURL);
    Serial.println("--------------------------------");
    serverConnected = true;
  } else {
    Serial.println();
    Serial.println("WiFi connection failed!");
    Serial.println("Check your credentials in CREDENCIALES.txt");
    serverConnected = false;
  }
}

void sendDummyData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("No WiFi connection. Cannot send data.");
    return;
  }
  
  // Generate dummy sensor data
  // Using fixed values for consistent testing, with slight variations
  float temperature1 = 23.5 + (random(0, 50) / 10.0);  // 23.5 to 28.5
  float humidity1 = 60.0 + (random(0, 30) / 1.0);      // 60 to 90
  float temperature2 = 24.0 + (random(0, 50) / 10.0);   // 24.0 to 29.0
  float humidity2 = 58.0 + (random(0, 35) / 1.0);       // 58 to 93
  float soilMoisture1 = 40.0 + (random(0, 40) / 1.0);   // 40 to 80
  float soilMoisture2 = 45.0 + (random(0, 35) / 1.0);   // 45 to 80
  float uvIndex = 2.0 + (random(0, 80) / 10.0);         // 2.0 to 10.0
  
  Serial.println("\n==========================================");
  Serial.println("Sending DUMMY data to server...");
  Serial.println("--------------------------------");
  Serial.printf("DHT11 Sensor 1: T=%.1fC, H=%.1f%%\n", temperature1, humidity1);
  Serial.printf("DHT11 Sensor 2: T=%.1fC, H=%.1f%%\n", temperature2, humidity2);
  Serial.printf("Soil Moisture 1: %.1f%%\n", soilMoisture1);
  Serial.printf("Soil Moisture 2: %.1f%%\n", soilMoisture2);
  Serial.printf("UV Index: %.1f\n", uvIndex);
  Serial.println("--------------------------------");
  
  HTTPClient http;
  String url = String(serverURL) + "/data";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);
  
  // Create JSON with dummy sensor data
  DynamicJsonDocument doc(512);
  doc["temperature1"] = temperature1;
  doc["humidity1"] = humidity1;
  doc["temperature2"] = temperature2;
  doc["humidity2"] = humidity2;
  doc["soil_moisture1"] = soilMoisture1;
  doc["soil_moisture2"] = soilMoisture2;
  doc["uv_index"] = uvIndex;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("JSON payload:");
  Serial.println(jsonString);
  Serial.println("--------------------------------");
  
  int httpCode = http.POST(jsonString);
  
  Serial.print("HTTP Response Code: ");
  Serial.println(httpCode);
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("SUCCESS! Data sent to server");
    Serial.print("Server response: ");
    Serial.println(response);
    Serial.println("==========================================");
    
    serverConnected = true;
    
  } else if (httpCode > 0) {
    Serial.print("HTTP ERROR: ");
    Serial.println(httpCode);
    String response = http.getString();
    Serial.print("Response: ");
    Serial.println(response);
    Serial.println("==========================================");
    serverConnected = false;
    
  } else {
    Serial.println("CONNECTION FAILED - Could not reach server");
    Serial.println("Check:");
    Serial.println("  1. Server URL is correct");
    Serial.println("  2. Vercel deployment is active");
    Serial.println("  3. Internet connection");
    Serial.println("==========================================");
    serverConnected = false;
  }
  
  http.end();
  
  Serial.print("Next data send in 30 seconds...");
  Serial.println("\n");
}

