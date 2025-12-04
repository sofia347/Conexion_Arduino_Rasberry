#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define TRIG_PIN 9
#define ECHO_PIN 10

#define LDR_PIN A0

void setup() {
  Serial.begin(115200);
  dht.begin();  

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.println("Iniciando sensores...");
}

void loop() {

  float humedad = dht.readHumidity();
  float temperatura = dht.readTemperature(); 

  long duracion;
  long distancia;

  // Leer ultrasonico
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duracion = pulseIn(ECHO_PIN, HIGH);
  distancia = duracion * 0.034 / 2;

  // Leer LDR
  int valorLDR = analogRead(LDR_PIN);

  // Leer datos vAlidos del DHT11
  if (!isnan(humedad) && !isnan(temperatura)) {
    
    // Enviar
    Serial.print(temperatura);
    Serial.print(",");
    Serial.print(humedad);
    Serial.print(",");
    Serial.print(distancia);
    Serial.print(",");
    Serial.println(valorLDR);
  }

  delay(1000);
}
