from django.urls import re_path
from . import consumers

# Accept string usernames (or numeric ids) for chat rooms and add presence route
websocket_urlpatterns = [
	re_path(r'ws/chat/(?P<user_id>[^/]+)/(?P<partner_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
	re_path(r'ws/presence/(?P<username>[^/]+)/$', consumers.PresenceConsumer.as_asgi()),
]

