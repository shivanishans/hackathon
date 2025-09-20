from django.db import models
from django.contrib.auth.models import AbstractUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth import get_user_model
from django.db.models import Q
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404

User = get_user_model()

# --- Django Database Models ---
class User(AbstractUser):
    class Meta:
        app_label = 'app'

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    is_abusive = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        app_label = 'app'

    def __str__(self):
        return f'{self.sender.username} to {self.receiver.username}: {self.text}'

# --- API Views ---
@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)
        
        user = User.objects.create_user(username=username, password=password)
        return JsonResponse({'status': 'success', 'username': user.username, 'id': user.id}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = User.objects.get(username=username)
        if user.check_password(password):
            return JsonResponse({'status': 'success', 'username': user.username, 'id': user.id})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def messages_api(request, user_id, partner_id):
    messages = Message.objects.filter(
        (Q(sender__id=user_id) & Q(receiver__id=partner_id)) | 
        (Q(sender__id=partner_id) & Q(receiver__id=user_id))
    ).order_by('timestamp')
    
    message_list = list(messages.values('id', 'sender__username', 'text', 'timestamp', 'is_abusive'))
    return JsonResponse(message_list, safe=False)

@require_http_methods(["GET"])
def users_list(request):
    users = list(User.objects.values('id', 'username'))
    return JsonResponse(users, safe=False)
