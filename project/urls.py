from django.urls import path, include

urlpatterns = [
    path('users/', include('users.urls', namespace='users')),
    path('server_notices/', include('server_notices.urls', namespace='server_notices')),
    path('', include('dashboard.urls', namespace='dashboard'))
]
