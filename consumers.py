from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
import json
from .app import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # A unique room name is created based on the user IDs
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        
        if not message_text or not sender_id or not receiver_id:
            return

        # Save the message to the database
        sender = await self.get_user(sender_id)
        receiver = await self.get_user(receiver_id)
        
        # Check if abusive
        is_abusive = await self.is_message_abusive(message_text)

        await self.save_message(sender, receiver, message_text, is_abusive)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': sender_id,
                'is_abusive': is_abusive
            }
        )
    
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        is_abusive = event['is_abusive']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'is_abusive': is_abusive
        }))

    async def get_user(self, user_id):
        # Use sync_to_async to query the database
        from asgiref.sync import sync_to_async
        return await sync_to_async(get_object_or_404, thread_sensitive=True)(User, id=user_id)

    async def save_message(self, sender, receiver, text, is_abusive):
        # Use sync_to_async to save to the database
        from asgiref.sync import sync_to_async
        await sync_to_async(Message.objects.create, thread_sensitive=True)(
            sender=sender,
            receiver=receiver,
            text=text,
            is_abusive=is_abusive
        )

    async def is_message_abusive(self, text):
        # This is a placeholder for your AI model logic.
        # It should be a separate function that you call asynchronously.
        # For now, it will return False.
        return False
