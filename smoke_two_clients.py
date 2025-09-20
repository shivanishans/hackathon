import asyncio
import websockets
import json
import time

# Two clients: A (id 100), B (id 101)
HOST = '127.0.0.1'
PORT = 8000
A_ID = 100
B_ID = 101


async def client_behaviour(name, my_id, other_id, messages_to_send, recv_queue, results):
    uri = f"ws://{HOST}:{PORT}/ws/chat/{my_id}/{other_id}/"
    try:
        async with websockets.connect(uri) as ws:
            now = time.time()
            print(f"{name} connected to {uri}")

            async def listener():
                try:
                    async for msg in ws:
                        print(f"{name} RECV: {msg}")
                        await recv_queue.put((name, msg))
                except Exception as e:
                    print(f"{name} listener ended: {e}")

            listener_task = asyncio.create_task(listener())

            # send typing start
            await ws.send(json.dumps({ 'typing': True, 'sender_id': my_id, 'receiver_id': other_id }))
            await asyncio.sleep(0.3)
            # send messages
            for m in messages_to_send:
                payload = {"message": m, "sender_id": my_id, "sender_name": name, "receiver_id": other_id}
                await ws.send(json.dumps(payload))
                print(f"{name} SENT: {m}")
                await asyncio.sleep(0.25)

            # typing stop
            await ws.send(json.dumps({ 'typing': False, 'sender_id': my_id, 'receiver_id': other_id }))

            # wait for inbound messages and delivered acks
            await asyncio.sleep(1.0)

            # send delivered ack for all persisted message ids we saw (from results)
            for mid in list(results.get('received_ids', [])):
                await ws.send(json.dumps({ 'delivered': mid, 'sender_id': my_id }))
                print(f"{name} sent delivered ack for {mid}")
                await asyncio.sleep(0.05)

            # send read receipt for messages where appropriate
            for mid in list(results.get('received_ids', [])):
                await ws.send(json.dumps({ 'read': mid, 'sender_id': my_id }))
                print(f"{name} sent read receipt for {mid}")
                await asyncio.sleep(0.05)

            await asyncio.sleep(0.2)
            listener_task.cancel()
    except Exception as e:
        print(f"{name} connection error: {e}")


async def run_smoke():
    q = asyncio.Queue()
    a_msgs = ["Hi, this is A", "How are you, B?", "Let's test moderation: You are an idiot"]
    b_msgs = ["Hey A, I am B", "I'm fine thanks", "No need to be rude"]

    # shared results collector (thread-safe-ish for test)
    results = { 'received_by_A': [], 'received_by_B': [], 'received_ids': set(), 'flagged': [] }

    async def collector():
        # read queue and populate results
        while True:
            try:
                who, raw = await asyncio.wait_for(q.get(), timeout=2.0)
            except asyncio.TimeoutError:
                break
            try:
                j = json.loads(raw)
            except Exception:
                continue
            if j.get('type') == 'flagged':
                results['flagged'].append((who, j))
            if j.get('message'):
                mid = j['message'].get('id')
                text = j['message'].get('text')
                if who == 'ClientA':
                    results['received_by_A'].append((mid, text))
                else:
                    results['received_by_B'].append((mid, text))
                if mid:
                    results['received_ids'].add(mid)

    # start clients
    task_a = asyncio.create_task(client_behaviour('ClientA', A_ID, B_ID, a_msgs, q, results))
    await asyncio.sleep(0.05)
    task_b = asyncio.create_task(client_behaviour('ClientB', B_ID, A_ID, b_msgs, q, results))
    # collector
    coll = asyncio.create_task(collector())

    await asyncio.gather(task_a, task_b)
    # allow collector to finish
    await asyncio.sleep(0.5)
    coll.cancel()

    # Evaluate results
    print('\n--- Test report ---')
    ok = True
    # check that A received messages from B and vice versa (by text)
    texts_A = [t for (_,t) in results['received_by_A'] if t]
    texts_B = [t for (_,t) in results['received_by_B'] if t]
    print('ClientA received texts:', texts_A)
    print('ClientB received texts:', texts_B)

    # ensure each sent message appears in other's inbox (approx)
    for m in b_msgs:
        if not any(m in t for t in texts_A):
            print('FAIL: ClientA did NOT receive:', m)
            ok = False
    for m in a_msgs:
        # flagged message will not be persisted for other side; handle that
        if "You are an idiot" in m:
            # should be flagged and appear in results['flagged'] for sender
            if not any('You are an idiot' in f[1]['original'] for f in results['flagged']):
                print('FAIL: flagged message not observed')
                ok = False
        else:
            if not any(m in t for t in texts_B):
                print('FAIL: ClientB did NOT receive:', m)
                ok = False

    # check delivered/read ids
    if results['received_ids']:
        print('Observed message ids persisted:', sorted(results['received_ids']))
    else:
        print('WARN: No persisted message ids observed; DB or consumer may not be saving')

    print('\nTest result:', 'PASS' if ok else 'FAIL')


if __name__ == '__main__':
    asyncio.run(run_smoke())
