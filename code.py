import os
import time
import wifi, ssl, socketpool
import board
import neopixel
import digitalio
import adafruit_minimqtt.adafruit_minimqtt as MQTT

num_pixels = 478
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

relay = digitalio.DigitalInOut(board.GP26)
relay.direction = digitalio.Direction.OUTPUT
relay.value = False  # Ensure relay is off at startup

pixels = neopixel.NeoPixel(board.GP28, num_pixels)
pixels.brightness = 1.0

debug = False

if not debug:
    led.value = True  # Turn on LED to indicate startup

mqtt_topic = os.getenv("MQTT_TOPIC")

def blink_led(times, duration):
    '''Blink the LED a specified number of times with a given duration.'''
    for _ in range(times):
        led.value = True
        time.sleep(duration)
        led.value = False
        time.sleep(duration)

if debug:
    print("Connecting to Wi-Fi...")
    blink_led(3, 0.5)  # Blink LED 3 times while connecting

# Attempt to connect to Wi-Fi, retrying every 5 seconds until successful
while True:
    try:
        wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
        if debug:
            print("Connected to Wi-Fi. IP address:", wifi.radio.ipv4_address)
            blink_led(5, 0.2)  # Blink LED 5 times to indicate successful connection
    except Exception as e:
        debug = True  # Enable debug mode if connection fails
        blink_led(10, 0.1)  # Blink LED 10 times quickly to indicate connection failure
        print("Failed to connect to Wi-Fi:", e, "Retrying in 5 seconds...")
        time.sleep(5)
    else:
        break

mqtt_client = MQTT.MQTT(
    broker=os.getenv("MQTT_BROKER"),
    port=os.getenv("MQTT_PORT"),
    username=os.getenv("MQTT_USERNAME"),
    password=os.getenv("MQTT_PASSWORD"),
    socket_pool=socketpool.SocketPool(wifi.radio),
    ssl_context=ssl.create_default_context(),
)

def connected(client, userdata, flags, rc):
    '''Callback function when the client is connected to the MQTT broker.'''
    if debug:
        print("Connected to MQTT broker with result code {0}".format(rc))
        blink_led(5, 0.1)  # Blink LED 5 times quickly to indicate MQTT connection
    client.subscribe(mqtt_topic)
    if debug:
        print(f"Subscribed to topic: {mqtt_topic} with QoS 0")
        print("Waiting for messages...")
    else:
        led.value = False  # Turn off LED to indicate successful MQTT connection

def disconnected(client, userdata, rc):
    '''Callback function when the client is disconnected from the MQTT broker.'''
    debug = True  # Enable debug mode on disconnection
    print("Disconnected from MQTT broker. Reconnecting in 5 seconds...")
    blink_led(10, 0.1)  # Blink LED 10 times quickly to indicate disconnection
    time.sleep(5)
    mqtt_client.connect()

def message(client, topic, message):
    '''Callback function when a message is received on the subscribed topic.'''
    print("New message on topic {0}: {1}".format(topic, message))
    val = None
    try: 
        val = str(message).split(",")
        if len(val) == 4:
            r, g, b, brightness = map(int, val)
            if brightness <= 0:
                pixels.fill((0, 0, 0))  # Turn off all pixels
                relay.value = False  # Turn off relay if brightness is 0 or negative
                print("Brightness is 0 or negative. Relay turned off and LEDs turned off.")
                return
            else:
                relay.value = True  # Turn on relay if brightness is greater than 0
                pixels.fill((r, g, b))
                pixels.brightness = brightness / 100.0
                print(f"Set LED color to ({r}, {g}, {b}) with brightness {brightness}")
        else:
            print("Invalid message format. Expected 'R,G,B,BRIGHTNESS' where R,G,B are 0-255 and BRIGHTNESS is 0-100.")
    except Exception as e:
        print("Error occurred while processing message:", e)
    
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

if debug:
    print("Connecting to MQTT broker...")
    blink_led(2, 0.5)  # Blink LED 2 times while connecting to MQTT
mqtt_client.connect()

while True:
    mqtt_client.loop(timeout=1)  # check for new messages and call handlers
    time.sleep(0.5)  # small delay to avoid busy loop
