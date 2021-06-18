#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <DHT.h>

DHT dht(D5, DHT11);
#define fan D6
#define day D7
#define night D1
#define party D2
#define movie D3

#define POWER_PIN  D8
#define SIGNAL_PIN A0

int water_value = 0;

String Database = "http://192.168.1.7:80/DataBoard";
String GetVoiceCommand = "http://192.168.1.7/voice";
WiFiClient client;

void setup() 
{
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(day, OUTPUT);
  pinMode(fan, OUTPUT);
  pinMode(night, OUTPUT);
  pinMode(party, OUTPUT);
  pinMode(movie, OUTPUT);
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
  digitalWrite(POWER_PIN, HIGH);        // turn the sensor ON
  delay(10);                            // wait 10 milliseconds
  water_value = analogRead(SIGNAL_PIN); // read the analog value from sensor
  digitalWrite(POWER_PIN, LOW);         // turn the sensor OFF

  float h   = dht.readHumidity();
  float t   = dht.readTemperature();
  float w   = water_value;
  float p   = 10;
  float ppl = 4;

  

  Serial.print("Water level value: ");
  Serial.println(water_value); 
  
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
    doc["water"] = w;
    doc["pow"]   = p;
    doc["ppl"]   = ppl;

    String json;
    serializeJson(doc,json);     
    int httpResponseCode = http.POST(json);
    http.end();
    
    http.begin(GetVoiceCommand);
    http.GET();
    StaticJsonDocument<128> docback;
    String httpGetResponse = http.getString();
    http.end();
  
    DeserializationError error = deserializeJson(docback,httpGetResponse);  
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }
  
    int day_mode = docback["day_mode"]; 
    int movie_mode = docback["movie_mode"]; 
    int night_mode = docback["night_mode"]; 
    int party_mode = docback["party_mode"]; 

    Serial.println("----------------------");
    if(day_mode){digitalWrite(day,HIGH);}
    else{digitalWrite(day,LOW);}
    if(night_mode){digitalWrite(night,HIGH);}
    else{digitalWrite(night,LOW);}
    if(party_mode){digitalWrite(party,HIGH);}
    else{digitalWrite(party,LOW);}
    if(movie_mode){digitalWrite(movie,HIGH);}
    else{digitalWrite(movie,LOW);}

    Serial.println(day_mode);
    Serial.println(movie_mode);
    Serial.println(night_mode);
    Serial.println(party_mode);
    
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