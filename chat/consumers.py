# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.models import UserProfile  # Import your custom user model from the core app
from chat.models import Thread, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, event):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        await self.accept()
        # Add to the chat room group based on thread_id
        await self.channel_layer.group_add(
            f'chat_{self.thread_id}',
            self.channel_name
        )
        await self.send(text_data=json.dumps({
            'type': 'websocket.accept'
        }))

    async def websocket_receive(self, event):
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        # Now sent_by and send_to are expected to be usernames (strings)
        sent_by_username = received_data.get('sent_by')
        send_to_username = received_data.get('send_to')

        if not msg:
            return

        sent_by_user = await self.get_user_object(sent_by_username)
        send_to_user = await self.get_user_object(send_to_username)
        thread_obj = await self.get_thread(self.thread_id)

        if not sent_by_user or not send_to_user or not thread_obj:
            return

        await self.create_chat_message(thread_obj, sent_by_user, msg)

        response = {
            'username': sent_by_username,
            'message': msg,
            'thread_id': self.thread_id
        }

        # Send the message to the chat room group
        await self.channel_layer.group_send(
            f'chat_{self.thread_id}',
            {
                'type': 'chat_message',
                'text': json.dumps(response)  # Serialize response to JSON
            }
        )

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            f'chat_{self.thread_id}',
            self.channel_name
        )

    async def chat_message(self, event):
        text_data = event['text']
        await self.send(text_data=text_data)

    @database_sync_to_async
    def get_user_object(self, username):
        # Look up by username since that's the primary key
        return UserProfile.objects.filter(username=username).first()

    @database_sync_to_async
    def get_thread(self, thread_id):
        return Thread.objects.filter(id=thread_id).first()

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        ChatMessage.objects.create(thread=thread, user=user, message=msg)
