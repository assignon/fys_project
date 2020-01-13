import os
import time
import RPi.GPIO as GPIO
from pyfirmata import Arduino, util
from flask_socketio import SocketIO, send
import serial, requests, json

GPIO.setmode(GPIO.BCM)
# board = Arduino('/dev/ttyUSB0')
# it = util.Iterator(board)
pyser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
# pyser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
# it.start()
# board.analog[0].enable_reporting()
channel = 17
GPIO.setwarnings(True)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(channel, GPIO.IN)

# led = board.get_pin('d:3:p')
# ldr = board.get_pin('a:0:i')

arr = []


# def callback(channel):
#     if GPIO.input(channel):
#         print('movement detected')
#     else:
#         print('mvt detected')


def ldrdata():
    ldr_arr = []
    while True:
        ldr_val = ldr.read()

        if ldr_val is not None:
            ldrval_round = round(ldr_val, 2)
            # print(ldrval_round)
            time.sleep(0.1)
            ldr_arr.append(ldrval_round)

            if ldrval_round < 0.03:
                led.write(1)
            else:
                led.write(0)
    return ldr_arr


# def vibration_sensor():
#     while True:
#         data = pyser.readline()
#         print(pyser)
#         print(data)
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

# def win_combinations():
#     combinations = [
#         [0,1,2],
#         [3,4,5],
#         [6,7,8],
#         [0,3,6],
#         [1,4,7],
#         [2,5,8],
#         [0,4,8],
#         [2,4,6]
#     ]
#     return combinations

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
    if len(player_A) == 3 or len(player_B) == 3:
        # for c in combinations:
        print(player_A)
        print(player_B)
        for c in combinations:
            for pa in player_A:
                if pa in c:
                    winner = 'A'
                    status = True
                else:
                    status = False
                    winner = 'no winner'

            for pb in player_B:
                if player_B in combinations:
                    winner = 'B'
                    status = True
                else:
                    status = False
                    winner = 'no winner'
    return [winner, status]

def touch_sensor():
    while True:
        data = pyser.readline().decode("ascii").rstrip()
        print(data)
        # if data != '':
        #     print('DATA are')
        # else:
        #     print('no data yet')
        if data != '':
            # for i in range(0, 9):
            current_player(game_board[data])
                # if data == u'{}'.format(i):
                #     print('{} is touched'.format(i))
            combination = check_combination()
            if combination[1]:
                print('winner is: {}'.format(check_combination()[0]))
            else:
                print('no winner')
                # play_again()
            # break
            # touch_sensor()

    pyser.close()




def main():
    # GPIO.add_event_detect(23, GPIO.RISING, callback=my_func, bouncetime=200)
    # while True:
    #     state = GPIO.input(23)
    #     if state == False:
    #         print(state)
    #         GPIO.output(24, True)
    #         print('pressedd')
    #         time.sleep(0.3)
    #     else:
    #         GPIO.output(24, False)
    #         print('not pressed')
    #         time.sleep(0.3)
    touch_sensor()

    # ldr_val = ldr.read()
    # if ldr.read() is None:
    #     ldr_val = ldr.read()
    #     print(ldr_val)
    #     main()

    # ldr_val = 0
    # while True:
    #     # ldr_val = ldr.read()
    #
    #     if ldr.read() is not None:
    #         ldr_val += ldr.read()
    #         ldrval_round = round(ldr.read(), 2)
    #         # print(ldrval_round)
    #         time.sleep(0.1)
    #
    #         if ldrval_round < 0.05:
    #             led.write(1)
    #             print('final', ldrval_round)
    #             ldr_val = ldrval_round
    #             break
    #         else:
    #             led.write(0)
    #             print(ldrval_round)
    # print('ldr_val:',ldr_val)

    # vibration_sensor()

    # GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
    # GPIO.add_event_callback(channel, callback)
    # print(requests)
    # payload = json.dumps({"field1": "xyz", "field2": "abc"})
    # url = "http://127.0.0.1:5000"
    #
    # headers = {
    #     'content-type': "application/json",
    #     'x-apikey': "560bd47058e7ab1b2648f4e7",
    #     'cache-control': "no-cache",
    #     'cors_allowed_origins': "*",
    #     'Referer': "http://127.0.0.1:5000/"
    # }
    #
    # response = requests.request("POST", url, data=payload, headers=headers)

    # print(response.text)

    while True:
        time.sleep(1)

    # r = requests.post('http://127.0.0.1:5000/', params={'q': 'post request sended'})
    # print(r.text)
    # if r.status != 200:
    #     print(r.status_code)
    # else:
    #     print('request sended')

    # GPIO.cleanup()

if __name__ == "__main__":
    main()