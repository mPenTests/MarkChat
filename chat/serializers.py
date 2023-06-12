from .models import User, UserProfile, Message, Group
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["username"], email=validated_data["email"], verification_code=validated_data["verification_code"])
        user.set_password(validated_data["password"])
        user.save()
        
        profile = UserProfile.objects.create(user=user)
        profile.save()
        
        return user