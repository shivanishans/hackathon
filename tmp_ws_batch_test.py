import asyncio
import websockets
import json

TEST_MESSAGES = [
    "You are an idiot",
    "You are stupid",
    "I hate you",
    "Go kill yourself",
    "You're an asshole",
    "Fuck you",
    "You piece of shit",
    "Idiot",
    "moron",
    "I don't like you"
]

async def run_tests():
    uri = "ws://127.0.0.1:8000/ws/chat/0/1/"
    try:
        async with websockets.connect(uri) as ws:
            print('connected to', uri)
            for msg in TEST_MESSAGES:
                payload = {"message": msg, "sender_id": 0, "receiver_id": 1}
                await ws.send(json.dumps(payload))
                print('\nSENT:', msg)
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=4)
                    print('RECV:', resp)
                    try:
                        j = json.loads(resp)
                        if isinstance(j, dict) and j.get('type') == 'flagged':
                            print('-> FLAGGED by server:', j.get('suggestions'))
                        elif isinstance(j, dict) and j.get('message'):
                            print('-> Persisted/broadcast. is_abusive=', j.get('is_abusive'))
                        else:
                            print('-> Unknown payload')
                    except Exception as e:
                        print('-> Non-JSON response')
                except asyncio.TimeoutError:
                    print('-> No response within timeout')
                await asyncio.sleep(0.2)
    except Exception as e:
        print('connection error:', e)

if __name__ == '__main__':
    asyncio.run(run_tests())
