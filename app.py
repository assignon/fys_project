from flask import Flask, redirect, url_for, render_template
from flask_socketio import SocketIO, send, emit
import os
import time, math
import RPi.GPIO as GPIO
from pyfirmata import Arduino, util
import serial
import requests

GPIO.setmode(GPIO.BCM)

# board = Arduino('/dev/ttyUSB0')
# it = util.Iterator(board)
# it.start()
# board.analog[0].enable_reporting()

pyser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

GPIO.setwarnings(True)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT)
# led = board.get_pin('d:3:p')
# ldr = board.get_pin('a:0:i')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'myKey'
socketio = SocketIO(app, cors_allowed_origins="*")

ldr_val = []

@app.route('/')
def hello_world():
    # state = GPIO.add_event_detect(23, GPIO.RISING, callback=btn_state, bouncetime=200)
    state = btn_state()[0]
    count = btn_state()[1]
    arr = []
    # ldr_sensor()
    print(SocketIO)
    touch_sensor()
    # ldr_sensor()
    # return 'Hello World! state: {} - cout: {}'.format(state, count)
    # vibration_sensor()
    # while True:
    #     data = raw_input('user input')
    #     if data == 'sendit':
    #         print('ldr', 'sended')

    return render_template('home.html')


@socketio.on('message')
def handelMessage(msg):
    print(msg+'from server')
    send(msg, broadcast=True)

# @socketio.on('connect')
# def ldr_data():
#     data = raw_input('user input')
#     while True:
#         if data == 'sendit':
#             emit('ldr', 'sended')
#         else:
#             break

def touch_sensor():
    while True:
        data = pyser.readline().decode('ascii')
        print(pyser)
        print(data)
        if data == 11:
            print('11 pin touched')

def ldr_sensor():
    loop = True
    while loop:
        # ldr_val = ldr.read()

        if ldr.read() is not None:
            ldrval_round = round(ldr.read(), 2)
            # print(ldrval_round)
            time.sleep(0.1)

            if ldrval_round < 0.05:
                led.write(1)
                print('final', ldrval_round)
                ldr_val.append(ldrval_round)
                loop = False
                break
            else:
                led.write(0)
                print(ldrval_round)
    else:
        print('else statment')
        ldr_sensor()
        ldr_data()
        # @socketio.on('connect')
        # def ldr_data():
        #     emit('ldr', ldr_val)

# ldr_sensor()

def btn_state():
    state = GPIO.input(23)
    count = 0
    if state == False:
        state = 'btn pressed'
        count += 1
        time.sleep(0.3)
    else:
        state = 'btn not pressed'
        count = count
        time.sleep(0.3)
    return [state, count]

if __name__ == '__main__':
    # app.run()
    socketio.run(app)