import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the global queue room
        self.room_group_name = 'live_queue'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def queue_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'queue_update',
            'message': event.get('message'),
            'token_number': event.get('token_number'),
            'status': event.get('status'),
            'service': event.get('service'),
            'counter_number': event.get('counter_number', 'Counter 1'),
            'branch_id': event.get('branch_id'),
            'branch_code': event.get('branch_code'),
            'action': event.get('action')
        }))
