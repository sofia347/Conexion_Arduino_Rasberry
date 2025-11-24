#include <DHT.h>

const int SENSOR_LUZ = A0;     // Sensor de Luz
const int SENSOR_TEMP = A1;  // Sensor de Temperatura analógica
const int SENSOR_GAS = A2;   // Sensor de Gas MQ-3

#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);


void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  int luz = analogRead(SENSOR_LUZ);
  int tempAnalog = analogRead(SENSOR_TEMP);
  int gas = analogRead(SENSOR_GAS);

  float tempD = dht.readTemperature();
  float humD = dht.readHumidity();
  
  if (isnan(tempD) || isnan(humD)) {
    tempD = -1;
    humD = -1;
  }

  Serial.print("Luz: ");
  Serial.println(luz);

  Serial.print("TempAnalog: ");
  Serial.println(tempAnalog);

  Serial.print("Gas: ");
  Serial.println(gas);

  Serial.print("TempDHT: ");
  Serial.println(tempD);

  Serial.print("HumDHT: ");
  Serial.println(humD);

  Serial.println("---");

  delay(1000);
}
