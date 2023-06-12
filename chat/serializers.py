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
    
    
class VerifyVerificationCodeSerializer(serializers.Serializer):
    verification_code = serializers.IntegerField()
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            
        except User.DoesNotExist:
            raise serializers.ValidationError("user_does_not_exist")
        
        return value
    
    def validate_verification_code(self, value):
        try:
            user = User.objects.get(username=self.initial_data["username"])
            
        except User.DoesNotExist:
            raise serializers.ValidationError("user_does_not_exist")
        
        if user.verification_code != value:
            raise serializers.ValidationError("verification_code_is_wrong")
        
        return value