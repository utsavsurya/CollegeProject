#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <DHT.h>

DHT dht(D5, DHT11);
#define fan D6
#define LED D7

#define POWER_PIN  D8
#define SIGNAL_PIN A0

int water_value = 0;
int water=0;

String Database = "http://192.168.1.7:80/DataBoard";
String GetVoiceCommand = "http://192.168.1.7/voice";
WiFiClient client;

void setup() 
{
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
  pinMode(fan, OUTPUT);
  pinMode(POWER_PIN, OUTPUT);   // configure D7 pin as an OUTPUT
  digitalWrite(POWER_PIN, LOW); // turn the sensor OFF
  WiFi.begin("NETGEAR91", "roundwind200");
  while(WiFi.status() != WL_CONNECTED)
  {
    delay(200);
    Serial.print("..");
  }
  Serial.println();
  Serial.println("NodeMCU is connected!");
  Serial.println(WiFi.localIP());
  dht.begin();
}

void loop()
{
  // put your main code here, to run repeatedly:
  
  float h   = dht.readHumidity();
  float t   = dht.readTemperature();
  float w   = 90;
  float p   = 10;
  float ppl = 4;

  digitalWrite(POWER_PIN, HIGH);        // turn the sensor ON
  delay(10);                            // wait 10 milliseconds
  water_value = analogRead(SIGNAL_PIN); // read the analog value from sensor
  digitalWrite(POWER_PIN, LOW);         // turn the sensor OFF

  Serial.print("Sensor value: ");
  Serial.println(water_value);
  if(water_value<30)
  {
    water=0;
    Serial.println("0%");
  }
  if(water_value>30 && water_value<=230)
  {
    water=25;
    Serial.println("25%");
  }
  if(water_value>230 && water_value<=305)
  {
    water=50;
    Serial.println("50%");
  }
  if(water_value>305 && water_value<=380)
  {
    water=75;
    Serial.println("75%");
  }
  if(water_value>380)
  {
    water =100;
    Serial.println("100%");
  }
  
  if(t>=30 )
  {
    Serial.println("FAN ON");
    digitalWrite(fan,HIGH);
  }
  if(t<30)
  {
    Serial.println("FAN OFF");
    digitalWrite(fan,LOW);
  }
  Serial.println(t);
  Serial.println(h);
  Serial.println(w);
  Serial.println(p);
  Serial.println(ppl);
  
  if(WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;
    http.begin(Database);
    http.addHeader("Content-Type","application/json");
    DynamicJsonDocument doc(1024);
     doc["temp"]  = t;
     doc["hum"]   = h;
     doc["water"] = water;
     doc["pow"]   = p;
     doc["ppl"]   = ppl;

    String json;
    serializeJson(doc,json);     
    int httpResponseCode = http.POST(json);
    http.end();
    
    http.begin(GetVoiceCommand);
    http.GET();
    String httpGetResponse = http.getString();
    http.end();
    if(httpGetResponse == "on"){digitalWrite(D7,HIGH);}
    else{digitalWrite(D7,LOW);}
    
    if(httpResponseCode>0)
    {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    }
  
    else
    {
      Serial.print("An erroe has occured while POSTing: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }
  else
  {Serial.println("error connecting to wifi");}
 
   delay(5000);
}