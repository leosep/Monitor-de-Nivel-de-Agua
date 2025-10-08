# Proyecto de Monitor de Nivel de Agua para Raspberry Pi 4
# Este script controla un sistema de llenado automático de agua usando sensor ultrasónico,
# display OLED, relé para bomba, notificaciones Pushbullet y interfaz web.

import RPi.GPIO as GPIO  # Librería para controlar los pines GPIO
import time  # Para delays y timestamps
from Adafruit_SSD1306 import SSD1306_128_64  # Control del display OLED SSD1306
from PIL import Image, ImageDraw, ImageFont  # Para dibujar en el OLED
from pushbullet import Pushbullet  # Para enviar notificaciones
from flask import Flask, render_template_string, request  # Servidor web Flask
from threading import Thread  # Para ejecutar el servidor web en un hilo separado

# Constantes de configuración
TRIG = 23  # Pin GPIO para el trigger del sensor ultrasónico
ECHO = 24  # Pin GPIO para el echo del sensor ultrasónico
RELAY = 17  # Pin GPIO para controlar el relé de la bomba
OLED_ADDRESS = 0x3C  # Dirección I2C del display OLED
RECIPIENT_HEIGHT = 20.0  # Altura del recipiente en cm (ajusta según tu setup)
PUSHBULLET_API_KEY = "YOUR_API_KEY_HERE"  # Reemplaza con tu clave API de Pushbullet

# Inicialización del hardware
GPIO.setmode(GPIO.BCM)  # Usar numeración BCM para pines GPIO
GPIO.setup(TRIG, GPIO.OUT)  # Configurar pin TRIG como salida
GPIO.setup(ECHO, GPIO.IN)  # Configurar pin ECHO como entrada
GPIO.setup(RELAY, GPIO.OUT)  # Configurar pin RELAY como salida
GPIO.output(RELAY, GPIO.LOW)  # Apagar la bomba inicialmente

# Inicializar el display OLED
oled = SSD1306_128_64(rst=None, i2c_address=OLED_ADDRESS)
oled.begin()  # Iniciar comunicación con OLED
oled.clear()  # Limpiar pantalla
oled.display()  # Mostrar cambios

# Inicializar cliente Pushbullet para notificaciones
pb = Pushbullet(PUSHBULLET_API_KEY)

# Inicializar aplicación Flask para la interfaz web
app = Flask(__name__)
pump_state = False  # Estado actual de la bomba (False = apagada)

# Función para medir la distancia con el sensor ultrasónico
def measure_distance():
    """
    Mide la distancia usando el sensor ultrasónico HC-SR04.
    Retorna la distancia en centímetros.
    """
    # Enviar pulso de trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # Pulso de 10 microsegundos
    GPIO.output(TRIG, False)

    # Esperar el pulso de echo
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calcular duración del pulso
    pulse_duration = pulse_end - pulse_start

    # Calcular distancia (velocidad del sonido = 34300 cm/s, ida y vuelta = 2)
    distance = pulse_duration * 17150

    # Limitar distancia máxima para evitar lecturas erróneas
    if distance > 400:
        distance = 400

    return distance

# Función para calcular el porcentaje de llenado
def calculate_percentage(distance):
    """
    Convierte la distancia medida en porcentaje de llenado.
    Asume que el sensor está en la parte superior apuntando hacia abajo.
    """
    # Si la distancia es mayor que la altura del recipiente, está vacío
    if distance >= RECIPIENT_HEIGHT:
        return 0.0
    # Si la distancia es cero o negativa, está lleno
    elif distance <= 0:
        return 100.0
    else:
        # Calcular porcentaje: 100% cuando distancia = 0, 0% cuando distancia = altura
        return 100.0 - (distance / RECIPIENT_HEIGHT * 100.0)

# Función para mostrar el porcentaje en el display OLED
def display_percentage(percentage):
    """
    Muestra el porcentaje de llenado en el display OLED.
    """
    # Crear imagen en blanco y negro
    image = Image.new('1', (128, 64))
    draw = ImageDraw.Draw(image)

    # Usar fuente por defecto
    font = ImageFont.load_default()

    # Dibujar texto con el porcentaje
    draw.text((0, 0), f"Nivel: {percentage:.1f}%", font=font, fill=255)

    # Mostrar en OLED
    oled.image(image)
    oled.display()

# Función para controlar la bomba de agua
def control_pump(state):
    """
    Enciende o apaga la bomba de agua mediante el relé.
    state: True para encender, False para apagar.
    """
    global pump_state
    pump_state = state
    GPIO.output(RELAY, GPIO.HIGH if state else GPIO.LOW)

# Función para enviar notificaciones Pushbullet
def send_notification(message):
    """
    Envía una notificación a través de Pushbullet.
    """
    try:
        pb.push_note("Monitor de Nivel de Agua", message)
    except Exception as e:
        print(f"Error enviando notificación: {e}")

# Rutas de la aplicación web Flask

@app.route('/')
def index():
    """
    Página principal con el interruptor virtual para la bomba.
    """
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Control de Bomba de Agua</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            button { padding: 10px 20px; font-size: 18px; margin: 10px; }
            #status { font-size: 20px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Control de Bomba de Agua</h1>
        <button onclick="togglePump()">Encender/Apagar Bomba</button>
        <p id="status">Estado: Apagado</p>

        <script>
            function togglePump() {
                fetch('/toggle', { method: 'POST' })
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('status').innerText = data;
                    })
                    .catch(error => console.error('Error:', error));
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/toggle', methods=['POST'])
def toggle():
    """
    Endpoint para alternar el estado de la bomba.
    """
    global pump_state
    pump_state = not pump_state
    control_pump(pump_state)
    status = "Estado: Encendido" if pump_state else "Estado: Apagado"
    return status

# Función principal
if __name__ == '__main__':
    # Ejecutar el servidor web en un hilo separado
    web_thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False})
    web_thread.daemon = True
    web_thread.start()

    print("Sistema de monitor de nivel de agua iniciado.")
    print("Accede a la interfaz web en: http://<IP_DEL_RASPBERRY>:5000")

    try:
        # Bucle principal de monitoreo
        while True:
            # Medir distancia
            distance = measure_distance()
            print(f"Distancia medida: {distance:.2f} cm")

            # Calcular porcentaje
            percentage = calculate_percentage(distance)
            print(f"Porcentaje de llenado: {percentage:.1f}%")

            # Mostrar en OLED
            display_percentage(percentage)

            # Control automático: apagar bomba si está lleno (>95%)
            if percentage > 95.0 and pump_state:
                control_pump(False)
                send_notification("¡El recipiente está lleno! La bomba se ha apagado automáticamente.")
                print("Bomba apagada automáticamente - recipiente lleno.")

            # Esperar 2 segundos antes de la siguiente medición
            time.sleep(2)

    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario.")
    except Exception as e:
        print(f"Error en el programa: {e}")
    finally:
        # Limpiar GPIO y OLED al salir
        GPIO.cleanup()
        oled.clear()
        oled.display()
        print("Recursos liberados. Programa terminado.")