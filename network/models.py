from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Posts(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="like")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes_count": [user.username for user in self.likes.all()],
        }
    

    def __str__(self):
        return f"{self.user} said, {self.content} on {self.timestamp.strftime('%d %b %Y %H:%M:%S')}"

class Likes(models.Model):
    liked_post = models.ForeignKey("Posts", on_delete=models.CASCADE, related_name="liked_post")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="liker")

    def __str__(self):
        return f"{self.user.username} liked {self.liked_post.content}"
    
class Followers(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="who_is_followed")
    followers = models.ManyToManyField(User, related_name="followers", blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s followers"
    
class Followings(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="who_is_following")
    followings = models.ManyToManyField(User, related_name="followings", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s followings"
    