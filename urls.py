from django.urls import path
from app import register_user, login_user, users_list, messages_api
from consumers import ChatConsumer

urlpatterns = [
    # HTTP API Endpoints
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('users/', users_list, name='users_list'),
    path('messages/<int:user_id>/<int:partner_id>/', messages_api, name='messages_api'),
    
    # WebSocket URL for the chat consumer
    path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),
]
