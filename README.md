# Monitor de Nivel de Agua para Raspberry Pi

Este proyecto implementa un sistema automático de monitoreo y control de nivel de agua usando un Raspberry Pi 4.

## Características

- Medición de nivel de agua con sensor ultrasónico
- Display OLED que muestra el porcentaje de llenado
- Control automático de bomba de agua mediante relé
- Notificaciones Pushbullet cuando el recipiente está lleno
- Interfaz web simple para control manual de la bomba

## Hardware Requerido

- Raspberry Pi 4
- Sensor ultrasónico HC-SR04
- Display OLED SSD1306 0.96" 128x64 (I2C)
- Módulo relé
- Bomba de agua conectada al relé
- Cables de conexión

## Conexiones GPIO

- **Sensor Ultrasónico**:
  - TRIG: GPIO 23
  - ECHO: GPIO 24
- **Relé**: GPIO 17
- **OLED** (modo I2C):
  - SDA: GPIO 2
  - SCL: GPIO 3

## Instalación

1. Actualiza tu Raspberry Pi:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. Instala Python y pip si no están instalados:
   ```bash
   sudo apt install python3 python3-pip
   ```

3. Instala las librerías requeridas:
   ```bash
   sudo pip3 install RPi.GPIO
   sudo pip3 install Adafruit-SSD1306
   sudo pip3 install pillow
   sudo pip3 install pushbullet.py
   sudo pip3 install flask
   ```

4. Habilita I2C en tu Raspberry Pi (para el OLED):
   ```bash
   sudo raspi-config
   ```
   Ve a Interfacing Options > I2C > Enable

5. Configura Pushbullet:
   - Crea una cuenta en [Pushbullet](https://www.pushbullet.com/)
   - Obtén tu API key desde la configuración de tu cuenta
   - Reemplaza `YOUR_API_KEY_HERE` en el código con tu clave real

## Configuración

1. Ajusta la altura del recipiente en la constante `RECIPIENT_HEIGHT` (en cm)
2. Si usas pines GPIO diferentes, modifica las constantes al inicio del archivo

## Ejecución

1. Conecta todo el hardware según las conexiones GPIO especificadas
2. Ejecuta el script:
   ```bash
   python3 water_level_monitor.py
   ```

3. Accede a la interfaz web desde cualquier dispositivo en la red:
   - URL: `http://<IP_DE_TU_RASPBERRY_PI>:5000`
   - La página mostrará un botón para encender/apagar la bomba manualmente

## Funcionamiento

- El sistema mide continuamente la distancia al agua cada 2 segundos
- Calcula el porcentaje de llenado basado en la altura del recipiente
- Muestra el porcentaje en el display OLED
- Apaga automáticamente la bomba cuando el recipiente está >95% lleno
- Envía una notificación Pushbullet cuando se apaga automáticamente
- Permite control manual a través de la interfaz web

## Detención

Presiona `Ctrl+C` para detener el programa. Los pines GPIO se limpiarán automáticamente.

## Solución de Problemas

- **Error de permisos GPIO**: Ejecuta con `sudo python3 water_level_monitor.py`
- **OLED no funciona**: Verifica la dirección I2C con `sudo i2cdetect -y 1`
- **Sensor ultrasónico**: Asegúrate de que esté conectado correctamente y no haya obstáculos
- **Pushbullet no envía**: Verifica tu API key y conexión a internet

## Personalización

- Modifica `RECIPIENT_HEIGHT` para ajustar a tu recipiente
- Cambia los pines GPIO en las constantes si es necesario
- Ajusta el umbral de apagado automático (actualmente 95%) en el bucle principal
- Personaliza el HTML de la interfaz web según tus necesidades

¡Disfruta tu proyecto de monitoreo de agua!