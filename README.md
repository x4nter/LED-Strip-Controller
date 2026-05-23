# Wireless-LED-Strip-Controller

A Raspberry Pi Pico based wireless controller built using CircuitPython

## Part List
- ***WS2815 LED Strip:*** 5m, 12V, 300 LEDs @ 60 LEDs/m, dual data signal ([Amazon Canada](https://www.amazon.ca/dp/B0F6CVHWVL?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)). Soldered 2 strips and cut to size to get 478 LEDs.
- ***12V 10A Power Supply:*** Total measured power consumption is around 60W so this is more than enough.
- ***Logic Level Shifter:*** Required to convert 3.3V GPIO signal to 5V that WS2815 uses. I used 74AHCT125.
- ***5V Step-Down Voltage Regulator:*** Required to step-down 12V coming from the power supply to 5V to power the Pico. I used CN3903.
- ***5V DC Relay Module:*** Required to turn off power when LEDs are off.

## Circuit Diagram
<img width="840" height="440" alt="circuit" src="https://github.com/user-attachments/assets/7a5ef1ae-4d8a-4957-a834-6dc4e6ce3930" />


## Usage
- The controller listens to commands via MQTT packets. To serve as an MQTT broker, I have `mosquitto` running on my local Home Assistant server. The broker can be configured in the `settings.toml` file.
- When powered up, the controller connects to Wifi and the broker, and then starts listening to the specified topic. Wifi is also configured in the `settings.toml` file, along with the topic that the controller will subscribe to.
- Once the controller starts listening to the topic, packets can be published on that topic with the following payload format: *`R,G,B,brightness`* where *R,G,B* is the comma separated RGB value of the color (0-255 per component) and *brightness* is the brightness level between 0 and 100 (inclusive).
- The LEDs start in off configuration on power up. Any payload sent with a non-zero brightness will turn the LEDs on. To turn off the LEDs, a payload with any RGB value paired with a 0 brightness level can be sent.
