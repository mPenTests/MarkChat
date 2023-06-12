from django.shortcuts import render
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests, random
from .serializers import RegisterSerializer
from MarkChat.settings import MARKMAIL_CAPTCHA

# Create your views here.

MARKMAIL_URL = "https://markmail-production.up.railway.app"


def login_markmail():
    data = {
        "email": "admin@markmail.com",
        "password": "unejammarko",
        "recaptcha_token": MARKMAIL_CAPTCHA    
    }
    
    request = requests.post(MARKMAIL_URL + "/api/login", json=data)
    response = request.json()
    
    return response["access"]


def send_confirmation_code(email):
    access_token = login_markmail()
    random_code = random.randint(1000, 9999)
    data = {
        "content": f"Here's your verification code: {random_code}",
        "receiver": email,
        "subject": "Verify your MarkChat account"
    }

    request = requests.post(MARKMAIL_URL + "/api/compose", json=data, headers={"Authorization": "Bearer " + access_token})
    
    return random_code
    


@api_view(['GET'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(verification_code=send_confirmation_code(serializer.validated_data["email"]))
        
        return Response({"message": "user_registered"}, status=HTTP_201_CREATED)
    
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    