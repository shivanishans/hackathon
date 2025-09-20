import websocket
try:
    ws = websocket.create_connection('ws://127.0.0.1:8000/ws/chat/0/1/')
    ws.send('{"message":"test from python client","sender_id":0,"receiver_id":1}')
    print('sent')
    print('recv:', ws.recv())
    ws.close()
except Exception as e:
    print('error', repr(e))
