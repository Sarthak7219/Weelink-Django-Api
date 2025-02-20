
from django.db import models
from core.models import UserProfile
from django.db.models import Q

class ThreadManager(models.Manager):
    def by_user(self, user):
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct().order_by("-updated_at")
        return qs
    
    def get_or_create_thread(self, user1, user2):
        thread = self.filter(
            Q(first_person=user1, second_person=user2) |
            Q(first_person=user2, second_person=user1)
        ).first()
        
        if thread:
            return thread, False
        else:
            thread = self.create(first_person=user1, second_person=user2)
            return thread, True

class Thread(models.Model):
    first_person = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='thread_first_person', null=True, blank=True)
    second_person = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='thread_second_person', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']

    def __str__(self):
        return f'[{self.first_person} , {self.second_person}]'
    
    def get_other_user(self, current_user):
        return self.first_person if self.second_person == current_user else self.second_person

class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
