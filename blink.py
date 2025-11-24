from utime import sleep
from machine import UART, Pin

# --- CONFIGURACIÓN UART ---
# UART1 en pines GP8 (TX) y GP9 (RX)
uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

print("Inicializando comunicación serial en UART1...")

while True:
    if uart1.any():
        data = uart1.readline()
        if data:
            try:
                message_received = data.decode('utf-8').strip()
                print(f"Recibido de Arduino: {message_received}")
            except UnicodeError:
                print("Error al decodificar el mensaje.")

    message_to_send = "ACK de Pico W: Mensaje recibido o listo."
    uart1.write(message_to_send + '\n')

    sleep(1.5)
