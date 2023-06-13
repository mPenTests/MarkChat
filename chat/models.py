from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    verification_code = models.IntegerField(blank=True, null=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.CharField(max_length=500, default="MarkChat user.")
    friends = models.ManyToManyField('self', null=True, blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

class Message(models.Model):
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sender')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(UserProfile)
    messages = models.ManyToManyField(Message)