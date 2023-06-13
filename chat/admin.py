from django.contrib import admin
from .models import User, UserProfile, Message, Group
from django.utils.html import format_html



# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_pic', 'is_verified', 'bio', 'created_at']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image.url))
    
    image_tag.allow_tags = True    

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register([User, Message, Group])