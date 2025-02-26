from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile, Post, Comment
from django.conf import settings
from .serializers import UserProfileSerializer, UserRegisterSerializer, PostSerializer, UserSerializer, FollowersFollowingSerializer, CommentSerializer
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.core.files.base import ContentFile
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

#Google Auth
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

        try: 
            username = request.data.get('username')
            password = request.data.get('password')
            try:
                user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                return Response({'error':'User does not exist'})
            
            if not user.check_password(password):
                return Response({'error': 'Invalid credentials'})
            
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']
            

            res = Response()
            res.data = {"success": True, 
                        "user": {
                            "username": username,
                            "bio": user.bio,
                            "email": user.email, 
                            "profile_image": user.profile_image.url if user.profile_image else None,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                        }}

            res.set_cookie(
                key='access_token',
                value = access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            res.set_cookie(
                key='refresh_token',
                value = refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            return res
        except Exception as e:
            return Response({"error": str(e)})


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            data = request.data.copy()
            data['refresh'] = refresh_token
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data

            access_token = tokens['access']

            res = Response()
            res.data = {"success": True}

            res.set_cookie(
                key='access_token',
                value = access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            return res
        except Exception as e:
            return Response({"success": False})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def authenticated(request):
    print("Authenticated user:",request.user.username)
    return Response({"success": True})


def save_profile_picture(user, image_url):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        file_name = f"{user.username}_profile_pic.jpg" 
        user.profile_image.save(file_name, ContentFile(response.content), save=True)


@api_view(['POST'])
def google_auth(request):
    try:
        token = request.data.get("access_token")
        
        # Verify token with Google
        google_data = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        email = google_data.get("email")
        first_name = google_data.get("given_name", "")
        last_name = google_data.get("family_name", "")
        profile_image = google_data.get("picture", None)

        if not email:
            return Response({"error": "Email not provided by Google"}, status=400)

        user, created = UserProfile.objects.get_or_create(email=email, defaults={
            "first_name": first_name,
            "last_name": last_name,
        })
        if profile_image and created:
            save_profile_picture(user, profile_image)

        if created or not user.username:
            return Response({"success": False, "message": "Username required", "set_username": True, "email": email})
        
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        res = Response({
            "success": True,
            "user": {
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_image": user.profile_image.url
            }
        })
        res.set_cookie("access_token", str(access_token), httponly=True, secure=True, samesite="None", path="/")
        res.set_cookie("refresh_token", str(refresh), httponly=True, secure=True, samesite="None", path="/")

        return res

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=400)


@api_view(['POST'])
def set_username(request):
    email = request.data.get("email")
    username = request.data.get("username")

    if not email or not username:
        return Response({"error": "Email and username are required"}, status=400)

    if UserProfile.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)

    user = UserProfile.objects.get(email=email)
    user.username = username
    user.save()

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    res = Response({
        "success": True,
        "user": {
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image": user.profile_image.url if user.profile_image else None,
        }
    })
    res.set_cookie("access_token", str(access_token), httponly=True, secure=True, samesite="None", path="/")
    res.set_cookie("refresh_token", str(refresh), httponly=True, secure=True, samesite="None", path="/")

    return res


@api_view(['POST'])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    print(serializer.errors)
    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_data(request, pk):
    try:
        try:
            user = UserProfile.objects.get(username = pk)
        except UserProfile.DoesNotExist: 
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfileSerializer(user, many=False)
        following = False
        if request.user in user.followers.all():
            following=True

        return Response({**serializer.data, 'is_our_profile': request.user.username == user.username, 'following': following})
    except:
        return Response({"error": "Error fetching user data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow(request):
    try:
        try:
            my_user = UserProfile.objects.get(username = request.user.username)
            user_to_follow = UserProfile.objects.get(username = request.data['username'])
        except UserProfile.DoesNotExist: 
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if my_user in user_to_follow.followers.all():
            user_to_follow.followers.remove(my_user)
            return Response({"now_following": False})
        else:
            user_to_follow.followers.add(my_user)
            return Response({"now_following": True})
    except:
        return Response({"error": "error following user"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request, pk):
    try:
        try:
            my_user = UserProfile.objects.get(username = request.user.username)
            user = UserProfile.objects.get(username = pk)
        except UserProfile.DoesNotExist: 
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        posts = user.posts.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)

        data = []

        for post in serializer.data:
            new_post = {}
            if my_user.id in post['likes']:
                new_post = {**post, 'liked':True}
            else:
                new_post = {**post, 'liked': False}
            data.append(new_post)
    
        return paginator.get_paginated_response(data)
    except Exception as e:
        print(e)
        return Response({"error": "Error fetching user posts"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request):
    try:
        try:
            post = Post.objects.get(id = request.data['id'])
        except : 
            return Response({"error": "Post not found!"})

        try:
            my_user = UserProfile.objects.get(username = request.user.username)
        except : 
            return Response({"error": "User does not exist"})
        
        if my_user in post.likes.all():
            post.likes.remove(my_user)
            return Response({"now_liked": False})
        else:
            post.likes.add(my_user)
            return Response({"now_liked": True})
    except:
        return Response({"error": "Error liking post"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_post(request):
    try:
        try:
            my_user = UserProfile.objects.get(username = request.user.username)
        except UserProfile.DoesNotExist: 
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "Error finding user"})

        body = request.data.get('body')
        post = Post.objects.create(
            user = my_user,
            body = body,
        )
        if "image" in request.FILES:
            post.image = request.FILES["image"]
            post.save()

        serialier = PostSerializer(post, many=False)
        return Response(serialier.data)
    except:
        return Response({"error": "Error creating post!"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request):  ## for homepage
    try:
        try:
            my_user = UserProfile.objects.get(username = request.user.username)
        except UserProfile.DoesNotExist: 
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "Error finding user"})
        
        posts = Post.objects.all().order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)

        data = []

        for post in serializer.data:
            new_post = {}
            if my_user.id in post['likes']:
                new_post = {**post, 'liked':True}
            else:
                new_post = {**post, 'liked': False}
            data.append(new_post)

        return paginator.get_paginated_response(data)
    except:
      
        return Response({"error": "Error fetching posts!"})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.query_params.get('query', '')
    users = UserProfile.objects.filter(username__icontains = query)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_details(request):
    data = request.data
    try:
        my_user = UserProfile.objects.get(username = request.user.username)
    except UserProfile.DoesNotExist: 
        return Response({"error": "User does not exist"})

    serializer = UserSerializer(my_user, data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({**serializer.data, "success":True})
    
    return Response({**serializer.errors, "success": False})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        res = Response()
        res.data = {"success": True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    except:
        return Response({"success": False})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_post(request):
    try:
        post = Post.objects.get(id = request.data['id'])
        if request.user != post.user :
            return Response({"error": "User not allowed to delete this post"})
        post.delete()
        return Response({"success": True})
    except Post.DoesNotExist: 
        return Response({"error": "Post not found!"})
    except:
        return Response({"error": "Error deleting post"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends(request, pk):
    try:
        try:
            user = UserProfile.objects.get(username = pk)
        except UserProfile.DoesNotExist: 
            return Response({"error": "User does not exist"})
        
        serializer = FollowersFollowingSerializer(user)
        return Response(serializer.data)
    except:
        return Response({"error": "Error getting friends"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_comment(request):
    try:
        try:
            post = Post.objects.get(id = request.data['id'])
        except : 
            return Response({"error": "Post not found!"})
        
        try:
            my_user = UserProfile.objects.get(username = request.user.username)
        except : 
            return Response({"error": "User does not exist"})
        
        comment = request.data['comment']
        obj = Comment.objects.create(
            body = comment,
            post = post,
            author = my_user
        )

        serializer = CommentSerializer(obj, many=False)
        return Response(serializer.data)
    except:
        return Response({"error": "Error posting comment"})

    
@api_view(["POST"]) 
def check_username(request):
    try:
        username = request.data.get("username")  

        if not username:
            return Response({"error": "Username is required"}, status=400)

        if UserProfile.objects.filter(username=username).exists():
            return Response({"available": False, "message": "Username already taken"}, status=200)
        
        return Response({"available": True, "message": "Username is available"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_user_photos(request):  
    try:
        username = request.data['username']
        try:
            user = UserProfile.objects.get(username = username)
        except : 
            return Response({"error": "User does not exist"})
        images = user.posts.exclude(image="").order_by('-created_at').values_list('image', flat=True)
        image_urls = [request.build_absolute_uri(f"/media/{img}") for img in images]
        return Response({"success": True, "images": image_urls}, status=200)
    except:
        return Response({"error": "Error fetching photos"})