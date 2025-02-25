from flask_mongoengine import MongoEngine
from mongoengine import Document, StringField, FloatField
import base64
import datetime

from app import db


# weather class is for the weather table
class Weather(db.Document):
    meta = {"collection": "Weather"}
    temperature = db.FloatField()
    humidity = db.FloatField()
    humidity_type = db.StringField()  # low, normal, high
    created_at = db.DateTimeField(default=datetime.datetime.now)


# add new weather data record to the table in mongoDB
def add_new_weather_data(temperature, humidity):
    if temperature is not False:
        humidity_type = get_humidity_type(humidity)
        Weather(
            temperature=temperature, humidity=humidity, humidity_type=humidity_type
        ).save()

        print(str(temperature) + " | " + str(humidity) + " | " + str(humidity_type))

    else:
        print("No temperature data.")


# set a humidity type based on the humidity range
def get_humidity_type(humidity):
    if humidity >= 41 and humidity <= 69:
        return "Normal"
    elif humidity <= 40:
        return "Low"
    else:
        return "High"


def get_weather_record():
    weather_record = {"weather": []}
    for weather in Weather.objects:
        weather_record["weather"].append(
            {
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "humidity_type": weather.humidity_type,
            }
        )
    return weather_record


# get the most recent record from weather table
def get_current_weather_record():
    current_weather_status = Weather.objects.order_by(
        "-created_at"
    ).first()  # descending order

    return {
        "current_weather": [
            {
                "temperature": current_weather_status.temperature,
                "humidity": current_weather_status.humidity,
                "humidity_type": current_weather_status.humidity_type,
            }
        ]
    }
