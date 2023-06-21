from django.urls import re_path
from . import consumers


uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>{})/$".format(uuid_pattern), consumers.ChatConsumer.as_asgi()),
]