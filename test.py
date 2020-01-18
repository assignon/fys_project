import asyncio
import json
import logging
import websockets
import os
import time
import RPi.GPIO as GPIO
# from pyfirmata import Arduino, util
# from flask_socketio import SocketIO, send
import serial, requests, json

GPIO.setmode(GPIO.BCM)
logging.basicConfig()
# board = Arduino('/dev/ttyUSB0')
# it = util.Iterator(board)

# pyser = serial.Serial('/dev/ttyUSB1', baudrate=9600, timeout=1)

pyser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# pyser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)

# pyser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
# it.start()
# board.analog[0].enable_reporting()
channel = 17
GPIO.setwarnings(True)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(channel, GPIO.IN)

# led = board.get_pin('d:3:p')
# ldr = board.get_pin('a:0:i')


# def ldrdata():
#     ldr_arr = []
#     while True:
#         ldr_val = ldr.read()
#
#         if ldr_val is not None:
#             ldrval_round = round(ldr_val, 2)
#             # print(ldrval_round)
#             time.sleep(0.1)
#             ldr_arr.append(ldrval_round)
#
#             if ldrval_round < 0.03:
#                 led.write(1)
#             else:
#                 led.write(0)
#     return ldr_arr

USERS = set()
player_A = []
player_B = []
game_board = {
    # u'0': 0,
    u'1': 1,
    u'2': 2,
    u'3': 3,
    u'4': 4,
    u'5': 5,
    u'6': 6,
    u'7': 7,
    u'8': 8,
    u'9': 9,
}
cube_faces = {
    u'0': 3,
    u'4': 2,
    u'5': 6,
    u'11': 5,
    # u'10':5,
    # u'11': 6,
}
players_turn = []
combinations = [
        [1,2,3],
        [4,5,6],
        [7,8,9],
        [1,4,7],
        [2,5,8],
        [3,6,9],
        [1,5,9],
        [3,5,7]
    ]

def callback(channel):
    # while True:

    if GPIO.input(channel) == 0:
        print('no mvt', GPIO.input(channel))
        # while True:
        #     data = pyser.readline().decode("ascii").rstrip()
        #     if data != '':
        #         face = cube_faces[data]
        #         print(face)
        #         break

# GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
# GPIO.add_event_callback(channel, callback)

async def current_player(data, websocket):
    ws_data = {}
    if len(players_turn) == 0:
        if check_uniq(data, player_A, player_B):
            players_turn.append('A')
            player_A.append(data)
            # await websocket.send(json.dumps(ws_data))
        else:
            print('number already used')
            await websocket.send(json.dumps({'msg': 'Number already used'}))
    else:
        player = players_turn[-1]
        # ws_data = {'sensor': data, 'cur_player': players_turn[-1]}
        if player == "A":
            if check_uniq(data, player_B, player_A):
                players_turn.append('B')
                player_B.append(data)
                # await websocket.send(json.dumps(ws_data))
            else:
                print('number already used')
                await websocket.send(json.dumps({'msg': 'Number already used'}))
        else:
            if check_uniq(data, player_A, player_B):
                players_turn.append('A')
                player_A.append(data)
                # await websocket.send(json.dumps(ws_data))
            else:
                print('number already used')
                await websocket.send(json.dumps({'msg': 'Number already used'}))

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
                    # print('true')
                else:
                    playerA_combination_arr.append(0)
                    # print('false')

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
                    # print('true')
                else:
                    playerB_combination_arr.append(0)
                    # print('false')

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

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

async def touch_sensor(websocket, path):
    await register(websocket)
    try:
        # await websocket.send(state_event())
        while True:
            # await register(websocket)
            # try:
            data = pyser.readline().decode("ascii").rstrip()
            # await websocket.send(data)
            # print('hallo',data)
            if data != '' and data != u'0' and data != u'10' and data != u'11':
                if data in game_board:
                    await current_player(game_board[data], websocket)
                    if len(players_turn) != 0 and check_uniq(data, player_A, player_B):
                        ws_data = {'sensor': data, 'cur_player': players_turn[-1], 'msg': 'drth'}
                        if check_uniq(data, player_A, player_B):
                            await websocket.send(json.dumps(ws_data))
                        else:
                            print('already existttttttttt')
                            await websocket.send(json.dumps({'msg': 'Number already used'}))
                    else:
                        print('hallooooo')
                    #     ws_data = {'sensor': data, 'cur_player': 'A'}
                combination = check_combination()
                if combination[1]:
                    print('winner is: {}'.format(check_combination()[0]))
                    await websocket.send(json.dumps({'msg': check_combination()[0]}))
                    break
                elif combination[1] ==  False and len(player_A) > 4 and len(player_B) == 4:
                    print('no winner')
                    break
                    # play_again()

    finally:
        await unregister(websocket)

    pyser.close()

async def main(websocket, path):
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
    await touch_sensor(websocket, path)
    # async for message in websocket:
    #     data = json.loads(message)
    #     print(data)

    # vibration_sensor()

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

    # while True:
    #     time.sleep(1)

    # r = requests.post('http://127.0.0.1:5000/', params={'q': 'post request sended'})
    # print(r.text)
    # if r.status != 200:
    #     print(r.status_code)
    # else:
    #     print('request sended')

    # GPIO.cleanup()
start_server = websockets.serve(main, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
if __name__ == "__main__":
    main()
