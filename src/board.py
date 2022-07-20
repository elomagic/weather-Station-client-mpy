import time
from machine import Pin, ADC

# Pin D7 - ESP8266 WeMos D1 Mini
LED_BOARD = Pin(2, Pin.OUT)
LED_BOARD.on()

# Pin D1 / GPIO5 / SCL
SCL_PIN = Pin(5)
# Pin D2 / GPIO4 / SDA
SDA_PIN = Pin(4)

# Pin D6 - GPIO12 - ESP8266 WeMos D1 Mini
MEASURE_MODE_PIN = Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)

# Pin D7 - GPIO13 - ESP8266 WeMos D1 Mini
WIFI_CLIENT_MODE_PIN = Pin(13, mode=Pin.IN, pull=Pin.PULL_UP)

# PIN A0 - ADC0
BATTERY_MONITOR_PIN = ADC(0)


def flash_led(count=1, speed=1):
    for i in range(abs(count)):
        LED_BOARD.off()
        time.sleep(0.5 * speed)
        LED_BOARD.on()
        time.sleep(0.5)

    time.sleep(0.25 * speed)
