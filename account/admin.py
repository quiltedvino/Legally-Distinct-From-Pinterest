from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.


class CustomUserAdmin(UserAdmin):
    # Specify the fields to be displayed in the User change list page
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'Followers', 'Following')

    def Following(self, obj):
        following_count = obj.following.count()
        following_usernames = ', '.join(
            [following.username for following in obj.following.all()])
        return f"Following {following_count} users ({following_usernames})"

    def Followers(self, obj):
        follower_count = obj.followers.count()
        follower_usernames = ', '.join(
            [follower.username for follower in obj.followers.all()])
        return f"{follower_count} followers ({follower_usernames})"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']
    raw_id_fields = ['user']


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
