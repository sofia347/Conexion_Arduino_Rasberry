from machine import UART, Pin
from time import sleep, localtime
from micropyGPS import MicropyGPS
import network
from simple import MQTTClient
import json

AIO_USERNAME = "SofiGlez"
AIO_KEY = ""
FEED = "SofiGlez/feeds/recolecciondatos"

mqtt_client = MQTTClient(
    AIO_USERNAME,
    "io.adafruit.com",
    user=AIO_USERNAME,
    password=AIO_KEY
)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    #wlan.connect("Megacable_2.4G_C30A", "YnPknu6t")
    wlan.connect("Tenda_B92D60", "feellock")

    print("Conectando al WiFi...")
    while not wlan.isconnected():
        sleep(0.5)
    print("WiFi conectado:", wlan.ifconfig())

conectar_wifi()
mqtt_client.connect()


ARDUINO = UART(0, 115200, tx=Pin(0), rx=Pin(1))
GPS = UART(1, 115200, tx=Pin(4), rx=Pin(5))

gps_parser = MicropyGPS()

temperatura = humedad = distancia = luz = "N/A"
latitude = longitude = "N/A"

def calcular_heat_index(T, H):
    return 0.5 * (T + 61.0 + ((T - 68.0)*1.2) + (H * 0.094))

def es_dia():
    h = localtime()[3]
    return 6 <= h <= 18


while True:

    if GPS.any():
        data = GPS.read()
        if data:
            for b in data:
                gps_parser.update(chr(b))

    if ARDUINO.any():
        try:
            t, h, d, l = ARDUINO.readline().decode().strip().split(",")
            temperatura = float(t)
            humedad = float(h)
            distancia = float(d)
            luz = int(l)
        except:
            pass

    if gps_parser.latitude[0] != 0:
        latitude = f"{gps_parser.latitude[0]}° {round(gps_parser.latitude[1], 5)}' {gps_parser.latitude[2]}"
        longitude = f"{gps_parser.longitude[0]}° {round(gps_parser.longitude[1], 5)}' {gps_parser.longitude[2]}"
    else:
        latitude = f"Buscando Sats:{gps_parser.satellites_in_view}"
        longitude = "Buscando"

    estado_sensorial = None

    # Distancia 
    if distancia != "N/A":
        if distancia < 20:
            estado_sensorial = "RIESGO OBSTACULO MUY CERCANO"
        elif distancia < 50:
            estado_sensorial = "PELIGRO OBSTACULO PROXIMO"

    # Estres termico
    if temperatura != "N/A" and humedad != "N/A":
        HI = calcular_heat_index(temperatura, humedad)
        if HI >= 40 and estado_sensorial is None:
            estado_sensorial = "ESTRES TERMICO ALTO"

    # Niebla
    if humedad != "N/A" and luz != "N/A":
        if humedad > 85 and luz < 200 and estado_sensorial is None:
            estado_sensorial = "POSIBL NIEBLA BAJA VISIBILIDAD"

    # Oscuridad irregular
    if luz == 0 and es_dia() and estado_sensorial is None:
        estado_sensorial = "OSCURIDAD ANOMALA"

    # Si ninguna cumplio
    if estado_sensorial is None:
        estado_sensorial = "NORMAL"

    h, m, s = localtime()[3:6]
    hora_str = f"{h:02}:{m:02}:{s:02}"

    payload = {
        "hora": hora_str,
        "latitud": latitude,
        "longitud": longitude,
        "estado": estado_sensorial
    }

    try:
        mqtt_client.publish(FEED, json.dumps(payload))
        print("Enviado a AIO:", payload)
    except Exception as e:
        print("ERROR MQTT:", e)

    print("\n========== REPORTE DE SENSORES ==========")
    print(f"Temperatura:  {temperatura} °C")
    print(f"Humedad:      {humedad} %")
    print(f"Distancia:    {distancia} cm")
    print(f"Luz (LDR):    {luz} lux")
    print(f"GPS Latitude:  {latitude}")
    print(f"GPS Longitude: {longitude}")
    print(f"ESTADO GENERAL: {estado_sensorial}")

    sleep(5)
