from rest_framework import serializers
from .models import UserProfile, Post, Comment


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = UserProfile(
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):

    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    

    class Meta:
        model = UserProfile
        fields = ['username', 'bio', 'profile_image', 'follower_count', 'following_count', 'first_name', 'last_name', 'email']

    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    

class CommentSerializer(serializers.ModelSerializer):

    formatted_comment_date = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['body', 'author', 'formatted_comment_date']

    def get_formatted_comment_date(self, obj):
        return obj.created_on.strftime("%d %b %y")

class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'username', 'body', 'formatted_date', 'likes', 'likes_count', 'user_image', 'image', 'comments']

    def get_username(self, obj):
        return obj.user.username
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_formatted_date(self, obj):
        return obj.created_at.strftime("%d %b %y")
    
    def get_user_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url
        return None
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'bio', 'email', 'profile_image', 'first_name', 'last_name']


class FollowersFollowingSerializer(serializers.ModelSerializer):
    followers_list = UserSerializer(source='followers', many=True, read_only=True)
    following_list = UserSerializer(source='following', many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'followers_list', 'following_list']