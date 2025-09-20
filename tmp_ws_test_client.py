import asyncio
import websockets
import json

async def main():
    uri = "ws://127.0.0.1:8000/ws/chat/0/1/"
    try:
        async with websockets.connect(uri) as ws:
            print('connected to', uri)
            await ws.send(json.dumps({"message":"You are a jerk","sender_id":0,"receiver_id":1}))
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                print('recv:', msg)
            except asyncio.TimeoutError:
                print('no message received within timeout')
    except Exception as e:
        print('connection error:', e)

if __name__ == '__main__':
    asyncio.run(main())
