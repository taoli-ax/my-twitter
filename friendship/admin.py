from django.contrib import admin
from friendship.models import Friendship
# Register your models here.
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id' ,'from_user','to_user')
    date_hierarchy = 'created_at'