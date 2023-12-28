from django.contrib import admin

from .models import User,Posts,Likes,Followers,Followings
# Register your models here.
admin.site.register(User)
admin.site.register(Posts)
admin.site.register(Likes)
admin.site.register(Followers)
admin.site.register(Followings)