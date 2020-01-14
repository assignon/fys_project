from threading import Lock
from flask import Flask, redirect, url_for, render_template, request, jsonify, make_response
from flask_socketio import SocketIO, send, emit
import os
import time, math
import RPi.GPIO as GPIO
from pyfirmata import Arduino, util
import serial

GPIO.setmode(GPIO.BCM)

# board = Arduino('/dev/ttyUSB0')
# it = util.Iterator(board)
# it.start()
# board.analog[0].enable_reporting()
async_mode = None

pyser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
channel = 17
GPIO.setwarnings(True)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(channel, GPIO.IN)
# led = board.get_pin('d:3:p')
# ldr = board.get_pin('a:0:i')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'myKey'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)
thread = None
thread_lock = Lock()
# socketio = SocketIO(app, cors_allowed_origins="*")

ldr_val = []
player_A = []
player_B = []
game_board = {
    u'0': 0,
    u'1': 1,
    u'2': 2,
    u'3': 3,
    u'4': 4,
    u'5': 5,
    u'6': 6,
    u'7': 7,
    u'8': 8,
}
cube_faces = {
    u'6': 1,
    u'7': 2,
    u'8': 3,
    u'9': 4,
    u'10':5,
    u'11': 6,
}
players_turn = []
combinations = [
        [0,1,2],
        [3,4,5],
        [6,7,8],
        [0,3,6],
        [1,4,7],
        [2,5,8],
        [0,4,8],
        [2,4,6]
    ]

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

@app.route('/')
def hello_world():
    # state = GPIO.add_event_detect(23, GPIO.RISING, callback=btn_state, bouncetime=200)
    # state = btn_state()[0]
    # count = btn_state()[1]
    # arr = []
    # ldr_sensor()
    # print(SocketIO)
    # touch_sensor()
    # ldr_sensor()
    # return 'Hello World! state: {} - cout: {}'.format(state, count)
    # vibration_sensor()
    # while True:
    #     data = raw_input('user input')
    #     if data == 'sendit':
    #         print('ldr', 'sended')

    return render_template('home.html', async_mode=socketio.async_mode)

@socketio.on('my_event')
def handelMessage(msg):
    print('{} from client'.format(msg))
    # send(msg, broadcast=True)

@app.route('/data', methods=['POST'])
def getData():
    req = request.get_json()
    print(req)
    res = make_response(jsonify({'msg': 'received'}), 200)
    return res

# @app.route('/sensorData', methods=['POST'])
def callback(channel):
    # while True:
    res = ''
    # req = request.get_json()
    # print(req)
    if GPIO.input(channel) == 0:
        print('no mvt', GPIO.input(channel))
        socketio.emit('vibration', {'state': GPIO.input(channel), 'msg': 'mvt no detected'})
    else:
        # res = make_response(jsonify({'state': GPIO.input(channel), 'msg': 'mvt detected'}), 200)
        socketio.emit('vibration', {'state': GPIO.input(channel), 'msg': 'mvt detected'})

        # while True:
        #     data = pyser.readline().decode("ascii").rstrip()
        #     if data != '':
        #         face = cube_faces[data]
        #         print(face)
        #         break

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

def current_player(data):
    if len(players_turn) == 0:
        if check_uniq(data, player_A, player_B):
            players_turn.append('A')
            player_A.append(data)
        else:
            print('number already used')
    else:
        player = players_turn[-1]
        if player == "A":
            if check_uniq(data, player_B, player_A):
                players_turn.append('B')
                player_B.append(data)
            else:
                print('number already used')
        else:
            if check_uniq(data, player_A, player_B):
                players_turn.append('A')
                player_A.append(data)
            else:
                print('number already used')
    print(players_turn, len(players_turn), player_A,len(player_A), player_B)

def check_uniq(data, arr1, arr2):
    bool = False
    if len(arr1) != 0 or len(arr2) != 0:
        # for i in arr:
        if data in arr1 or data in arr2:
            bool = False
        else:
            bool = True
    else:
        bool = True
    return bool


def clear_arrays():
    pass

def play_again():
    print('new game starting ')

def check_combination():
    winner = ''
    status = False
    countA = 0
    countB = 0
    playerA_combination_arr = []
    playerB_combination_arr = []
    if len(player_A) >= 3:
        print(player_A)
        print(player_B)

        for (i, c) in enumerate(combinations):
            for pa in player_A:
                if pa in combinations[i] and len(playerA_combination_arr) <= 3:
                    # if len(playerA_combination_arr) <= 5:
                    playerA_combination_arr.append(1)
                    print('true')
                else:
                    playerA_combination_arr.append(0)
                    print('false')

            for pc in playerA_combination_arr:
                countA += pc
            if countA == 3:
                status = True
                winner = 'A'
                countA = 0
            else:
                playerA_combination_arr = []
                countA = 0

    if len(player_B) >= 3:
        for (i, c) in enumerate(combinations):
            for pb in player_B:
                if pb in combinations[i] and len(playerB_combination_arr) <= 3:
                    # if len(playerA_combination_arr) <= 5:
                    playerB_combination_arr.append(1)
                    print('true')
                else:
                    playerB_combination_arr.append(0)
                    print('false')

            for pc in playerB_combination_arr:
                countB += pc
            if countB == 3:
                status = True
                winner = 'B'
                countB = 0
            else:
                playerB_combination_arr = []
                countB = 0

    return [winner, status]

# @app.route('/sensorData', methods=['POST'])
def touch_sensor():
    while True:
        data = pyser.readline().decode("ascii").rstrip()
        if data != '' and data != u'9' and data != u'10' and data != u'11':
            current_player(game_board[data])
                # if data == u'{}'.format(i):
                #     print('{} is touched'.format(i))
            combination = check_combination()
            if combination[1]:
                print('winner is: {}'.format(check_combination()[0]))
                break
            # else:
            #     print('no winner')
            #     # break
            elif combination[1] ==  False and len(player_A) >= 4 and len(player_B) == 4:
                print('no winner')
                break
                # play_again()
            # break
            # touch_sensor()

    pyser.close()



# @socketio.on('message')
# def handelMessage(msg):
#     print(msg+'from server')
#     send(msg, broadcast=True)
#
# @socketio.on('connect')
# def ldr_data():
#     data = raw_input('user input')
#     emit('ldr', data)
#     # while True:
#     #     if data == 'sendit':
#     #         emit('ldr', 'sended')
#     #     else:
#     #         break
#
# def touch_sensor():
#     while True:
#         data = pyser.readline().decode('ascii')
#         print(pyser)
#         print(data)
#         if data == 11:
#             print('11 pin touched')
#
# def ldr_sensor():
#     loop = True
#     while loop:
#         # ldr_val = ldr.read()
#
#         if ldr.read() is not None:
#             ldrval_round = round(ldr.read(), 2)
#             # print(ldrval_round)
#             time.sleep(0.1)
#
#             if ldrval_round < 0.05:
#                 led.write(1)
#                 print('final', ldrval_round)
#                 ldr_val.append(ldrval_round)
#                 loop = False
#                 break
#             else:
#                 led.write(0)
#                 print(ldrval_round)
#     else:
#         print('else statment')
#         ldr_sensor()
#         ldr_data()
#         # @socketio.on('connect')
#         # def ldr_data():
#         #     emit('ldr', ldr_val)
#
# # ldr_sensor()
#
# def btn_state():
#     state = GPIO.input(23)
#     count = 0
#     if state == False:
#         state = 'btn pressed'
#         count += 1
#         time.sleep(0.3)
#     else:
#         state = 'btn not pressed'
#         count = count
#         time.sleep(0.3)
#     return [state, count]

if __name__ == '__main__':
    # app.run()
    socketio.run(app, debug=True)
