import random
import requests
from tkinter import *
import math
import time
import pyowm
import sys
from Adafruit_IO import MQTTClient
import serial

AIO_USERNAME = "YOUR USER NAME"
AIO_KEY = "YOUR AIO KEY"

LED_INDEX = 1
RGB_INDEX = 1

APIKEY = "YOUR API KEY"
city_id = 1566083
state = 1
next_state = 2
count = 0
feed = ""
value = ""

ard_feed = ""
ard_value = ""

sensor = ""
sensor_value = 0
waiting_period = 3
sent_again = 0
timer_sent = 0

sent2ard = 0
sent_ard_counter = 0
sent_ard_period = 3

line = ""
data = ""
message_sent = 0
ard_period = 3
ard_counter = 0

read_state = 1
read_ard = 1


def get_data(feed_id):
    global line
    return line.find(feed_id)

def get_data_ard(feed_id):
    global data
    return data.find(feed_id)


def sent_to_ard(arduino, feed_id, value):
    if feed_id == "light":
        if value == 1:
            arduino.write(b"light1\n")
        else:
            arduino.write(b"light0\n")
    elif feed_id == "door":
        if value == 1:
            arduino.write(b"door1\n")
        else:
            arduino.write(b"door0\n")

def convert(code):
    return code - 273

def get_temp(API_KEY, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city}&appid={API_KEY}"

    response = requests.get(url).json()
    currentTemp = response['main']['temp']
    formattedTemp = '{:.0f}'.format(convert(currentTemp))
    return formattedTemp

def get_hum(API_KEY, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city}&appid={API_KEY}"

    response = requests.get(url).json()
    currentHum = response['main']['humidity']
    formattedHum = '{:.0f}'.format(convert(currentHum))
    return formattedHum

def get_sky(API_KEY, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city}&appid={API_KEY}"

    response = requests.get(url).json()
    currentSky = ""
    currentSky = response['weather'][0]['main']
    formattedSky = '{}'.format(currentSky)
    return formattedSky


def connected(client):
    print("Ket noi thanh cong...")
    client.subscribe("Light")
    client.subscribe("door")
    client.subscribe("gateway-error")

def  subscribe(client, userdata, mid, granted_qos):
    print("Subscribe thanh cong...")

def  disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)

def  message(client, feed_id, payload):
    global sent2ard
    global sensor
    global sensor_value
    global sent_again
    global waiting_period
    global timer_sent
    global ard_period
    global message_sent
    global ard_counter
    print("Nhan du lieu: " + feed_id + payload)
    if str(feed_id) == "Light":
        sent2ard = 1
        sensor = "light"
        sensor_value = int(payload)

    if str(feed_id) == "door":
        sent2ard = 1
        sensor = "door"
        sensor_value = int(payload)
    if str(feed_id) == "gateway-error":
        if payload == "1":
            print("Send data to", feed, "Successfully")
            timer_sent = 0
            sent_again = 0
            waiting_period = 3
        elif payload == "0":
            print("Send data to", ard_feed, "Successfully")
            ard_period = 3
            message_sent = 0
            ard_counter = 0


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()
ard1 = serial.Serial('COM3', 9600, timeout=1)
ard1.flush()
ard2 = serial.Serial('COM4', 9600, timeout=1)
ard2.flush()



def sent_message(feed, message):
    print("Sending", feed, message)
    client.publish(feed, message)



while True:
    if state == 1:  # read temperat
        value = get_temp(APIKEY, city_id)
        feed = "Temperature"
        sent_again = 1
        state = -1
    elif state == 2:
        value = get_hum(APIKEY, city_id)
        feed = "Humidity"
        sent_again = 1
        state = -1
    elif state == 3:
        value = get_sky(APIKEY, city_id)
        feed = "co2"
        sent_again = 1
        state = -1
    elif state == 0:
        if count < 5:
            count += 1
        else:
            count = 0
            if next_state > 3:
                state = 1
                next_state = 2
            else:
                state = next_state
                next_state += 1
    elif state == -1:
        if sent_again == 1:
            if timer_sent < 3:
                timer_sent += 1
            else:
                timer_sent = 0
                sent_message(feed, value)
                waiting_period -= 1
            if waiting_period == 0:
                waiting_period = 3
                sent_again = 0
                timer_sent = 0
                print("Failed! Feed: ", feed)
        else:
            state = 0

    if sent2ard == 1:
        if sent_ard_counter < 3:
            sent_ard_counter += 1
        else:
            sent_ard_counter = 0
            sent_to_ard(ard1, sensor, sensor_value)
            sent_ard_period -= 1
            if sent_ard_period == 0:
                sent_ard_period = 3
                sent_ard_counter = 0
                sent2ard = 0
                print("Failed!")

    if read_state == 1:
        if ard1.in_waiting > 0:
            line = ard1.readline().decode('utf-8').rstrip()
            read_state = 2
    elif read_state == 2:
        read_state = 1
        index = get_data("light")
        if index != -1:
            sent_ard_period = 3
            sent_ard_counter = 0
            sent2ard = 0
            if sensor_value == 0:
                client.publish("error-control", "light0")
                print("Light OFF")
            elif sensor_value == 1:
                client.publish("error-control", "light1")
                print("Light ON")
        index = get_data("door")
        if index != -1:
            sent_ard_period = 3
            sent_ard_counter = 0
            sent2ard = 0
            if sensor_value == 0:
                client.publish("error-control", "door0")
                print("Door CLOSE")
            elif sensor_value == 1:
                client.publish("error-control", "door1")
                print("Door OPEN")

    if read_ard == 1:
        if ard2.in_waiting > 0:
            data = ard2.readline().decode('utf-8').rstrip()
            read_ard = 2
    elif read_ard == 2:
        read_ard = -1
        ard_index = get_data_ard("camera")
        if ard_index != - 1:
            message_sent = 1
            ard_feed = "camera"
            ard_index = get_data_ard("99")
            if ard_index != -1:
                ard_value = "-1"
            ard_index = get_data_ard("0")
            if ard_index != -1:
                ard_value = "0"
            ard_index = get_data_ard("1")
            if ard_index != -1:
                ard_value = "1"
        ard_index = get_data_ard("lamp")
        if ard_index != - 1:
            message_sent = 1
            ard_feed = "lamp"
            ard_index = get_data_ard("0")
            if ard_index != -1:
                ard_value = "0"
            ard_index = get_data_ard("1")
            if ard_index != -1:
                ard_value = "1"

    elif read_ard == -1:
        if message_sent == 1:
            if ard_counter < 3:
                ard_counter += 1
            else:
                ard_counter = 0
                sent_message(ard_feed, ard_value)
                ard_period -= 1
            if ard_period == 0:
                ard_period = 3
                message_sent = 0
                ard_counter = 0
                print("Failed! Feed: ", ard_feed)
        else:
            read_ard = 1


    time.sleep(1)

