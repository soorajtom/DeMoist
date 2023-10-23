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

int low_cutoff = 65;
int high_cutoff = 75;

bool cooler_state = false;
bool cooler_fsm = true;

const int cooler_pin = 14; // D5

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
  server.on("/params", handle_params);
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
  if (!cooler_fsm) {
    return;
  }
  if (humidity < low_cutoff) {
    cooler_state = false;
  } else if (humidity > high_cutoff) {
    cooler_state = true;
  };
  digitalWrite(cooler_pin, cooler_state ? LOW : HIGH);
}

void handle_params() {
  if (server.arg("low") != ""){
    low_cutoff = server.arg("low").toInt();
  }
  if (server.arg("high") != ""){
    high_cutoff = server.arg("high").toInt();
  }
  if (server.arg("cooler") != ""){
    String state = server.arg("cooler");
    if (state == "true") {
      cooler_state = true;
    } else if (state == "false") {
      cooler_state = false;
    }
  }
  if (server.arg("cooler_fsm") != ""){
    String state = server.arg("cooler_fsm");
    if (state == "true") {
      cooler_fsm = true;
    } else if (state == "false") {
      cooler_fsm = false;
    }
  }
  String params = get_params_string();
  server.send(200, "application/json", params);
}

String get_params_string() {
  char buff[100];
  sprintf(buff, "{\"low\":%d,\"high\":%d,\"cooler_state\":%d,\"cooler_fsm\":%d}", low_cutoff, high_cutoff, cooler_state, cooler_fsm);
  return String(buff);
}

// -- END OF FILE --
