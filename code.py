import os
import time
import wifi, ssl, socketpool
import board
import neopixel
import digitalio
import adafruit_minimqtt.adafruit_minimqtt as MQTT

num_pixels = 300
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

pixels = neopixel.NeoPixel(board.GP28, num_pixels)
pixels.brightness = 1.0

mqtt_topic = os.getenv("MQTT_TOPIC")

def blink_led(times, duration):
    '''Blink the LED a specified number of times with a given duration.'''
    for _ in range(times):
        led.value = True
        time.sleep(duration)
        led.value = False
        time.sleep(duration)

print("Connecting to Wi-Fi...")
blink_led(3, 0.5)  # Blink LED 3 times while connecting

# Attempt to connect to Wi-Fi, retrying every 5 seconds until successful
while True:
    try:
        wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
        print("Connected to Wi-Fi. IP address:", wifi.radio.ipv4_address)
        blink_led(5, 0.2)  # Blink LED 5 times to indicate successful connection
    except Exception as e:
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
    print("Connected to MQTT broker.")
    blink_led(5, 0.1)  # Blink LED 5 times quickly to indicate MQTT connection
    client.subscribe(mqtt_topic)
    print(f"Subscribed to topic: {mqtt_topic} with QoS 0")
    print("Waiting for messages...")

def disconnected(client, userdata, rc):
    '''Callback function when the client is disconnected from the MQTT broker.'''
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

print("Connecting to MQTT broker...")
blink_led(2, 0.5)  # Blink LED 2 times while connecting to MQTT
mqtt_client.connect()

while True:
    mqtt_client.loop(timeout=1)  # check for new messages and call handlers
    time.sleep(0.5)  # small delay to avoid busy loop