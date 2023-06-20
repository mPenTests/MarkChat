"""
ASGI config for MarkChat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routing import websocket_urlpatterns
from chat.jwt_middleware import JWTAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MarkChat.settings')


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})