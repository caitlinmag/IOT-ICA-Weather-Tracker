import RPi.GPIO as GPIO
import time
import adafruit_dht
import board
import os

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv

dht_device = adafruit_dht.DHT22(board.D17)
Buzzer_pin = 23  # buzzer is connected to GPIO 23
Green_LED = 18  # green LED connected to GPIO 18
Red_LED = 12  # red LED connected to GPIO 12
PIR_pin = 5  # pir is connected to GPIO 5

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Buzzer_pin, GPIO.OUT)
GPIO.setup(Green_LED, GPIO.OUT)
GPIO.setup(Red_LED, GPIO.OUT)
GPIO.setup(PIR_pin, GPIO.IN)

load_dotenv()
data = {}


class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f"Status: \n{status.category.name}")


config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.secret_key = os.getenv("PUBNUB_SECRET_KEY")
config.uuid = os.getenv("PUBNUB_USER_ID")
pubnub = PubNub(config)
pubnub.add_listener(Listener())
app_channel = "Weather-Lookout-Channel"
subscription = pubnub.channel(app_channel).subscription()
subscription.subscribe()
publish_result = (
    pubnub.publish().channel(app_channel).message("Hello from Weather Lookout").sync()
)


def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.2)


# normal humidity range between 41 - 69
def normal_humidity():
    GPIO.output(Green_LED, GPIO.HIGH)
    GPIO.output(Red_LED, GPIO.LOW)
    print("Green LED on, Red LED off")
    pubnub.publish().channel(app_channel).message("Green LED on").sync()


# bad humidity range less than 40 or greater than 70
def bad_humidity():
    GPIO.output(Green_LED, GPIO.LOW)
    GPIO.output(Red_LED, GPIO.HIGH)
    print("Green LED off, Red LED on")
    pubnub.publish().channel(app_channel).message("Red LED on").sync()


def main():
    try:
        while True:
            if GPIO.input(PIR_pin):
                print("Motion detected")
                pubnub.publish().channel(app_channel).message("Motion detected").sync()
            else:
                print("No Motion detected")
                pubnub.publish().channel(app_channel).message(
                    "No Motion detected"
                ).sync()
            time.sleep(1)

            try:
                temperature_c = dht_device.temperature
                temperature_f = temperature_c * (9 / 5) + 32

                humidity = dht_device.humidity

                print(
                    "Temp:{:.1f} C / {:.1f} F Humidity: {}%".format(
                        temperature_c, temperature_f, humidity
                    )
                )
                pubnub.publish().channel(app_channel).message(
                    {"type": "temperature", "value": temperature_c}
                ).sync()

                pubnub.publish().channel(app_channel).message(temperature_f).sync()

                pubnub.publish().channel(app_channel).message(
                    {"type": "humidity", "value": humidity}
                ).sync()
                if humidity >= 41 and humidity <= 69:
                    print("Normal humidity range.")
                    normal_humidity()
                    pubnub.publish().channel(app_channel).message(
                        "Normal humidity range"
                    ).sync()
                else:
                    # out of normal humidity range
                    print("Activate buzzer, humidity outside of normal range")
                    bad_humidity()
                    beep(3)
                    pubnub.publish().channel(app_channel).message(
                        "Buzzer activated"
                    ).sync()
                    pubnub.publish().channel(app_channel).message(
                        "Bad humidity range"
                    ).sync()
            except RuntimeError as err:
                print(err.args[0])
    except KeyboardInterrupt:
        print("Exit")
    finally:
        time.sleep(2.0)
        GPIO.cleanup()


if __name__ == "__main__":
    main()
