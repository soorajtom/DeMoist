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
#define STASSID "ACT102659353172"
#define STAPSK  "89993286"
#endif
DHT20 DHT(&Wire);

const char* ssid = STASSID;
const char* password = STAPSK;

const int led = LED_BUILTIN;

// Create an instance of the server
// specify the port to listen on as an argument
ESP8266WebServer server(80);

void setup()
{
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
}

void handleRoot() {
  digitalWrite(led, 0);
  server.send(200, "text/plain", "hello from esp8266!");
  digitalWrite(led, 255);
}

void handleRead() {
  digitalWrite(led, 0);
  DHT.read();
  char buff[50];
  sprintf(buff, "{\"temp\":%f,\"humidity\":%f}", DHT.getTemperature(), DHT.getHumidity());
//  String s = "{\"temp\":" + DHT.getTemperature() + ",\"humidity\":" + DHT.getHumidity()+ "}";
  server.send(200, "application/json", buff);
  digitalWrite(led, 255);
}


// -- END OF FILE --
