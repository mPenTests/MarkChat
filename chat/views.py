from django.shortcuts import render
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests, random
from .serializers import (RegisterSerializer, VerifyVerificationCodeSerializer, 
                          LoginSerializer, GroupSerializer,
                          ChangePasswordSerializer, AddFriendSerializer,
                          GetProfileSerializer, UploadProfilePictureSerializer)
from MarkChat.settings import MARKMAIL_CAPTCHA
from .models import User, UserProfile, Group
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.core.exceptions import ValidationError



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
    


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.validated_data["verification_code"] = send_confirmation_code(serializer.validated_data["email"])
        serializer.save()  
        
        return Response({"message": "user_registered"}, status=HTTP_201_CREATED)
    
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_verification_code(request):
    serializer = VerifyVerificationCodeSerializer(data=request.data)
    
    if serializer.is_valid():
        user = User.objects.get(username=serializer.validated_data["username"])
        profile = UserProfile.objects.get(user=user)
        profile.is_verified = True
        profile.save()
            
        return Response({"message": "user_verified"}, status=HTTP_200_OK)
        
            
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        if UserProfile.objects.get(user=User.objects.get(username=serializer.validated_data["username"])).is_verified == False:
            return Response({"message": "user_not_verified"}, HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
        
        if user is None:
            return Response({"message": "auth_invalid"}, HTTP_400_BAD_REQUEST)
        
        tokens = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(tokens),
            "access": str(tokens.access_token)    
        }, HTTP_200_OK)
        
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_groups(request):
    profile = UserProfile.objects.get(user=request.user)
    groups = Group.objects.filter(users=profile)
    serializer = GroupSerializer(groups, many=True)
    
    return Response(serializer.data, HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    
    if serializer.is_valid():
        user = User.objects.get(username=request.user)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        
        return Response({"message": "password_changed"}, HTTP_200_OK)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request):
    serializer = AddFriendSerializer(data=request.data)
    
    if serializer.is_valid():
        profile = UserProfile.objects.get(user=request.user)
        friend = UserProfile.objects.get(user=User.objects.get(username=serializer.validated_data["username"]))
        
        if friend in profile.friends.all():
            return Response({"message": "friend_already_added"}, HTTP_400_BAD_REQUEST)
        
        profile.friends.add(friend)
        profile.save()
        
        return Response({"message": "friend_added"}, HTTP_200_OK)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    model = UserProfile.objects.get(user=request.user)
    serializer = GetProfileSerializer(model)
    
    return Response(serializer.data, HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload(request):
    serializer = UploadProfilePictureSerializer(data=request.data)
    user = UserProfile.objects.get(user=request.user)
    
    if serializer.is_valid():
        serializer.instance = user
        serializer.save()
        
        return Response({"message": "profile_picture_uploaded"}, HTTP_200_OK)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)