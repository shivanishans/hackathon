import importlib
r = importlib.import_module('chat.routing')
print('websocket_urlpatterns from chat.routing:')
for p in getattr(r, 'websocket_urlpatterns', []):
    try:
        print(' -', p.pattern)
    except Exception:
        print(' -', repr(p))
