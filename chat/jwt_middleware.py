from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])

        if b"authorization" in headers:
            try:
                access_token = self.get_access_token(headers)
                validated_token = await self.validate_token(access_token)
                user_id = validated_token["user_id"]
                scope["user"] = await self.get_user(user_id)
            except (InvalidToken, TokenError):
                scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @staticmethod
    def get_access_token(headers):
        auth_header = headers[b"authorization"].decode("utf-8")
        auth_token = auth_header.split(" ")[1]
        return auth_token

    @staticmethod
    @database_sync_to_async
    def validate_token(access_token):
        authentication = JWTAuthentication()
        return authentication.get_validated_token(access_token)

    @staticmethod
    @database_sync_to_async
    def get_user(user_id):
        User = get_user_model()
        try:
            print(user_id)
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
