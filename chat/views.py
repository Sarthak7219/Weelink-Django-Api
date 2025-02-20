# chat/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from chat.models import Thread
from chat.serializers import ThreadSerializer, DisplayThreadsSerializer
from core.models import UserProfile  # Import custom user model


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_thread_messages(request, thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        return Response({"error": "Thread not found."}, status=404)
    
    serializer = ThreadSerializer(thread)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_or_create_thread(request):
    try:
        profile_username = request.data['profile_username']
        try:
            other_user = UserProfile.objects.get(username=profile_username)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found."})
        except:
            return Response({"error": "Error finding user"})
        
        if request.user.username == other_user.username:
            return Response({"error": "Cannot create conversation with yourself."})
        
        thread, created = Thread.objects.get_or_create_thread(user1=request.user, user2=other_user)
        serializer = ThreadSerializer(thread)
        return Response(serializer.data)
    except Exception as e:
        print(e)
        return Response({"error": "Something went wrong"})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_display_threads(request):
    try:
        user = request.user
        threads = Thread.objects.by_user(user=user)
        serializer = DisplayThreadsSerializer(threads, many=True, context={'request': request})
        return Response(serializer.data)
    except:
        return Response({"error": "Error getting conversations"})
