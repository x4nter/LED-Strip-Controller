# Wireless-LED-Strip-Controller

A Raspberry Pi Pico based wireless controller built using CircuitPython

## Part List
- ***WS2815 LED Strip:*** 5m, 12V, 300 LEDs @ 60 LEDs/m, dual data signal ([Amazon Canada](https://www.amazon.ca/dp/B0F6CVHWVL?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)).
- ***12V 5A Power Supply:*** 60W is more than enough to drive 300 LEDs and the Pico.
- ***Logic Level Shifter:*** Required to convert 3.3V GPIO signal to 5V that WS2815 uses. I used 74AHCT125.
- ***5V Step-Down Voltage Regulator:*** Required to step-down 12V coming from the power supply to 5V to power the Pico. I used CN3903.

## (a not so professional) Circuit Diagram
<img width="720" height="420" alt="circuit" src="https://github.com/user-attachments/assets/61074e27-3ebf-49bc-8dc4-067d40dd6bd8" />

## Usage
- The controller listens to commands via MQTT packets. To serve as an MQTT broker, I have `mosquitto` running on my local Home Assistant server. The broker can be configured in the `settings.toml` file.
- When powered up, the controller connects to Wifi and the broker, and then starts listening to the specified topic. Wifi is also configured in the `settings.toml` file, along with the topic that the controller will subscribe to.
- Once the controller starts listening to the topic, packets can be published on that topic with the following payload format: *`R,G,B,brightness`* where *R,G,B* is the comma separated RGB value of the color (0-255 per component) and *brightness* is the brightness level between 0 and 100 (inclusive).
- The LEDs start in off configuration on power up. Any payload sent with a non-zero brightness will turn the LEDs on. To turn off the LEDs, a payload with any RGB value paired with a 0 brightness level can be sent.
