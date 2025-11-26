import time
from machine import UART, Pin
import network
from simple import MQTTClient


WIFI_SSID = "Megacable_2.4G_FA6C" #"Megacable_2.4G_C30A"
WIFI_PASSWORD = "rpjWChSJ" #"YnPknu6t"

# Credenciales de Adafruit IO
AIO_USERNAME = "SofiGlez"
AIO_KEY = #TOKEN 
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_FEED_ID = "SofiGlez/feeds/recolecciondatos" 
CLIENT_ID = "picp-w-client" 

# --- CONFIGURACIÓN UART ---
# UART1 en pines GP8 (TX) y GP9 (RX)
uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

wlan = None
mqtt_client = None

# Conexion a internet
def do_connect():
    """Conecta la Pico W a la red WiFi y reporta el estado."""
    global wlan
    print("Conectando a WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1) 
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    max_wait = 15
    while max_wait > 0:
        status = wlan.status()
        print(f'Esperando conexión...')
        if status < 0 or status >= 3:
            break
        max_wait -= 1
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Fallo la conexión de red')
    else:
        print('Conexión exitosa. Configuración de red:', wlan.ifconfig())

    
# Conexion a MQTT Broker de Adfruit
def mqtt_connect():
    global mqtt_client
    print(f"Conectando a Adafruit IO como {AIO_USERNAME}...")
    
    mqtt_client = MQTTClient(
        client_id=CLIENT_ID,
        server=AIO_SERVER,
        port=AIO_PORT,
        user=AIO_USERNAME,
        password=AIO_KEY,
        ssl=False #
    )
    
    try:
        mqtt_client.connect()
        print("Conexión MQTT exitosa a Adafruit IO!")
        return mqtt_client
    except Exception as e:
        print(f"Error al conectar MQTT: {e}")
        return None


# Publicacion de los datos recibidos
def publish_data(topic, data):
    global mqtt_client
    try:
        mqtt_client.publish(topic, str(data).encode('utf-8'))
        print(f"Publicado en '{topic}': {data}")
    except Exception as e:
        print(f"Error al publicar el dato: {e}")
        reconnect_mqtt()

def reconnect_mqtt():
    global mqtt_client
    try:
        mqtt_client.disconnect()
    except:
        pass
    time.sleep(1)
    mqtt_connect()


def main():
    global mqtt_client
    
    # Realiza la conexion con con WiFi y MQTT
    try:
        do_connect()
        mqtt_client = mqtt_connect()
    except Exception as e:
        print(f"Inicialización fallida: {e}")
        return

    print("Inicializando comunicación serial en UART1...")

    while True:
        if uart1.any():
            data = uart1.readline()
            if data:
                try:
                    # Recibe el mensaje del Arudino y lo decodifica
                    message_received = data.decode('utf-8').strip()
                    print(f"Recibido de Arduino: {message_received}")

                    # Publica lo recibido a Adafruit
                    if mqtt_client:
                        publish_data(AIO_FEED_ID, message_received)

                except UnicodeError:
                    print("Error al decodificar el mensaje.")

        if mqtt_client:
            try:
                mqtt_client.check_msg()
            except Exception as e:
                print(f"Error al chequear mensaje MQTT: {e}")
                reconnect_mqtt()

        time.sleep(1.5)

if __name__ == "__main__":
    main()