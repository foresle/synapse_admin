from django.urls import path, include

urlpatterns = [
    path('users/', include('users.urls', namespace='users')),
    path('', include('dashboard.urls', namespace='dashboard'))
]
