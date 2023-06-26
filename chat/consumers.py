import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .serializers import MessageSerializer
from .models import UserProfile, Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from channels.exceptions import StopConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        
        if user.is_anonymous:
            await self.close(403)
            raise StopConsumer()
           
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        try:
            group = database_sync_to_async(Group.objects.get)(uuid=self.room_name)
        except (ObjectDoesNotExist, ValidationError):
            await self.close(404)
            raise StopConsumer()
            
            
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )


        @database_sync_to_async
        def get_messages():
            messages = Group.objects.get(uuid=self.room_name).messages.all()
            serializer = MessageSerializer(messages, many=True)

            return serializer.data
            

        await self.accept()
        data = await get_messages()
        await self.send(text_data=json.dumps(data))
            

    async def disconnect(self, close_code):
        if close_code == 403:
            await self.close(close_code)
            
        else:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
        

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))