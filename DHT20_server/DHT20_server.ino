//
//    FILE: DHT20_plotter.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: Demo for DHT20 I2C humidity & temperature sensor
//

//  Always check datasheet - front view
//
//          +--------------+
//  VDD ----| 1            |
//  SDA ----| 2    DHT20   |
//  GND ----| 3            |
//  SCL ----| 4            |
//          +--------------+

#include "DHT20.h"
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#ifndef STASSID
#define STASSID "Totoro"
#define STAPSK  "chicken1"
#endif

DHT20 DHT(&Wire);

const char* ssid = STASSID;
const char* password = STAPSK;

const int led = LED_BUILTIN;

const int low_cutoff = 65;
const int high_cutoff = 75;

bool cooler_state = false;

const int cooler_pin = GPIO14; // D5

float humidity, temperature;

// Create an instance of the server
// specify the port to listen on as an argument
ESP8266WebServer server(80);

void setup()
{
  pinMode(cooler_pin, OUTPUT);
  digitalWrite(cooler_pin, HIGH);
  DHT.begin();  //  ESP32 default pins 21 22
  Serial.begin(115200);
// Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  IPAddress  ip = WiFi.localIP();
  Serial.println(ip);
  Serial.println("");
  Serial.println("WiFi connected");

  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }
  
//  Serial.println("Humidity, Temperature");
  server.on("/", handleRoot);
  server.on("/read", handleRead);
  server.begin();
}


void loop()
{
  server.handleClient();
  MDNS.update();

  update_cooler_FSM();
  delay(50);
}

void handleRoot() {
  digitalWrite(led, 0);
  server.send(200, "text/plain", "hello from esp8266!");
  digitalWrite(led, 255);
}

void handleRead() {
  digitalWrite(led, 0);
  char buff[100];
  sprintf(buff, "{\"temp\":%f,\"humidity\":%f,\"cooler_state\":%d}", temperature, humidity, cooler_state);
  server.send(200, "application/json", buff);
  digitalWrite(led, 255);
}

void update_cooler_FSM() {
  DHT.read();
  humidity = DHT.getHumidity();
  temperature = DHT.getTemperature();
  if (humidity < low_cutoff) {
    cooler_state = false;
  } else if (humidity > high_cutoff) {
    cooler_state = true;
  };
  digitalWrite(cooler_pin, cooler_state ? LOW : HIGH);
}


// -- END OF FILE --
