#!/usr/bin/env python3
"""
Test script for receiver warning functionality.
Tests that receivers get a warning prompt when receiving force-sent abusive messages.
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)

async def test_receiver_warning():
    """Test that receiver gets warning for force-sent abusive messages"""
    
    # User A will send abusive message with force
    # User B should receive a warning prompt
    
    print("🧪 Testing Receiver Warning for Abusive Force-Sent Messages")
    print("=" * 60)
    
    try:
        # Connect User A (sender)
        uri_a = "ws://localhost:8000/ws/chat/UserA/UserB/"
        ws_a = await websockets.connect(uri_a)
        print("✅ UserA connected")
        
        # Connect User B (receiver) 
        uri_b = "ws://localhost:8000/ws/chat/UserB/UserA/"
        ws_b = await websockets.connect(uri_b)
        print("✅ UserB connected")
        
        # User A sends a normal message first
        normal_msg = {
            "message": "Hello UserB!",
            "sender": "UserA",
            "sender_name": "UserA",
            "receiver": "UserB"
        }
        await ws_a.send(json.dumps(normal_msg))
        print("📤 UserA sent normal message")
        
        # User B should receive the normal message
        response_b = await ws_b.recv()
        data_b = json.loads(response_b)
        print(f"📥 UserB received: {data_b}")
        
        # Now User A sends an abusive message with force=True
        print("\n🚨 Testing abusive force-sent message...")
        abusive_msg = {
            "message": "You are an idiot and stupid!",
            "sender": "UserA", 
            "sender_name": "UserA",
            "receiver": "UserB",
            "force": True
        }
        await ws_a.send(json.dumps(abusive_msg))
        print("📤 UserA force-sent abusive message")
        
        # User B should receive the message with is_abusive flag
        response_b2 = await ws_b.recv()
        data_b2 = json.loads(response_b2)
        print(f"📥 UserB received: {data_b2}")
        
        # Check if the message was flagged as abusive
        if data_b2.get('is_abusive'):
            print("✅ SUCCESS: Message was properly flagged as abusive!")
            print("🔍 Frontend should now show receiver warning modal")
        else:
            print("❌ FAIL: Message was not flagged as abusive")
            
        print(f"📊 Message details: is_abusive={data_b2.get('is_abusive')}, text='{data_b2.get('message', {}).get('text')}'")
        
        await ws_a.close()
        await ws_b.close()
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_receiver_warning())