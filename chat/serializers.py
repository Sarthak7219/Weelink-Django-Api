# chat/serializers.py
from rest_framework import serializers
from chat.models import Thread, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = ChatMessage
        fields = ['id', 'username', 'message', 'timestamp']

class ThreadSerializer(serializers.ModelSerializer):
    first_person = serializers.CharField(source="first_person.username", read_only=True)
    second_person = serializers.CharField(source="second_person.username", read_only=True)
    chat_messages_list = ChatMessageSerializer(source="chat_messages", many=True, read_only=True)
    
    class Meta:
        model = Thread
        fields = ['id', 'first_person', 'second_person', 'updated_at', 'timestamp', 'chat_messages_list']

class DisplayThreadsSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    other_user_img = serializers.SerializerMethodField()
    most_recent_message = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ["id", "other_user", "other_user_img", "most_recent_message", "formatted_date"]

    def get_other_user(self, obj):
        request_user = self.context["request"].user
        other_user = obj.get_other_user(request_user)
        return other_user.username  

    def get_other_user_img(self, obj):
        request_user = self.context["request"].user
        other_user = obj.get_other_user(request_user)
        return other_user.profile_image.url if hasattr(other_user, "profile_image") else None

    def get_most_recent_message(self, obj):
        last_message = obj.chat_messages.order_by("-timestamp").first()
        return last_message.message if last_message else None

    def get_formatted_date(self, obj):
        return obj.updated_at.strftime("%d %b %y")
