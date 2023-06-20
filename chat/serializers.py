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
    
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            
        except User.DoesNotExist:
            raise serializers.ValidationError("user_does_not_exist")
        
        return value
    
    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
        

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
    def validate_old_password(self, value):
        user = self.context["request"].user
        
        if not user.check_password(value):
            raise serializers.ValidationError("old_password_is_wrong")
        
        return value
    
    
class AddFriendSerializer(serializers.Serializer):
    username = serializers.CharField()
    
    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            
        except User.DoesNotExist:
            raise serializers.ValidationError("user_does_not_exist")
        
        return value
    
    
class GetProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    
    class Meta:
        model = UserProfile
        fields = ["bio", "user"]
        
    def get_user(self, obj):
        return obj.user.username
    
    
class UploadProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["profile_pic"]
        
        
class SendResetPasswordCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            
        except User.DoesNotExist:
            raise serializers.ValidationError("no_account_found")
        
        return value
    
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.IntegerField()
    new_password = serializers.CharField()
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            
        except User.DoesNotExist:
            raise serializers.ValidationError("no_account_found")
        
        return value
    
    def validate_verification_code(self, value):
        user = User.objects.get(email=self.initial_data["email"])
        
        if user.verification_code != value:
            raise serializers.ValidationError("verification_code_is_wrong")
        
        return value
    
    
class GetFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "profile_pic"]
        
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["from_user", "to_user", "message", "created_at"]