import RPi.GPIO as GPIO
import time
import adafruit_dht
import board

dht_device = adafruit_dht.DHT22(board.D17)
Buzzer_pin = 23
Green_LED = 18  # green LED connected to GPIO 18
Red_LED = 12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Buzzer_pin, GPIO.OUT)
GPIO.setup(Green_LED, GPIO.OUT)
GPIO.setup(Red_LED, GPIO.OUT)


def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.2)


# turn on green led
def green_led():
    GPIO.output(Green_LED, GPIO.HIGH)
    print("Green LED is turned on")


# turn the green led off
def green_led_off():
    GPIO.output(Green_LED, GPIO.LOW)
    print("Green LED is turned off")


# turn on red led
def red_led():
    GPIO.output(Red_LED, GPIO.HIGH)
    print("Red LED is turned on")


# turn off red led
def red_led_off():
    GPIO.output(Red_LED, GPIO.LOW)
    print("Green LED is turned off")


while True:
    try:
        temperature_c = dht_device.temperature
        temperature_f = temperature_c * (9 / 5) + 32

        humidity = dht_device.humidity

        print(
            "Temp:{:.1f} C / {:.1f} F Humidity: {}%".format(
                temperature_c, temperature_f, humidity
            )
        )
    except RuntimeError as err:
        print(err.args[0])

    if humidity > 40 or humidity < 70:
        print("Normal humidity range.")
        green_led()  # turn on green led
        red_led_off()
    elif humidity < 40 or humidity > 70:
        print("Activate buzzer, humidity is outside normal range")
        beep(3)
        red_led()  # turn on red led
        green_led_off()

    time.sleep(2.0)

GPIO.cleanup()

if __name__ == "__main__":
    main()
