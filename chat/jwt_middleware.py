from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            headers = dict(scope["headers"])
            if b"authorization" in headers:
                token_name, token = headers[b"authorization"].decode().split()
                if token_name.lower() == "bearer":
                    validated_token = await self.validate_token(token)
                    if validated_token:
                        # Attach the user object to the scope
                        scope["user"] = validated_token.user
        except TokenError as e:
            # Handle invalid or expired tokens
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def validate_token(self, token):
        try:
            access_token = AccessToken(token)
            return access_token
        except (InvalidToken, TokenError) as e:
            return None
