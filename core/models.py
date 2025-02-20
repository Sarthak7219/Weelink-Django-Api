from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model
class UserProfile(AbstractUser):
    username = models.CharField(max_length=50, unique=True, primary_key=True)  #New primary key
    bio = models.TextField(null=True, blank=True, max_length=150)
    profile_image = models.ImageField(blank=True, null=True, upload_to="images/profile/")
    followers = models.ManyToManyField(
        "self",
        related_name="following",
        symmetrical=False,
        blank=True
    )
    
    def get_profile_pic_url(self):
        if self.image:
            return self.image.url
        else:
            return "/static/images/user/default_profile.jpeg"


    def __str__(self):
        return self.username


class Post(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='posts')
    body = models.CharField(null=True, blank=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(UserProfile, blank=True, related_name='likes')
    image = models.ImageField(blank=True, null=True, upload_to="images/post/")

    def __str__(self):
        body_preview = self.body[:30] + "..." if self.body else "" 
        return (
            f"{self.user} "
            f"{body_preview}"
        )


class Comment(models.Model):
    body = models.CharField(max_length=150)
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'{self.author.username} : {self.body[:30]}'



    