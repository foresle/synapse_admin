from django.urls import path

from .views import UsersView, UpdateLastSeenView, UserView

app_name = 'users'

urlpatterns = [
    path('update_last_seen/', UpdateLastSeenView.as_view(url='/users/'), name='update_last_seen'),
    path('<str:user_id>/', UserView.as_view(), name='detail'),
    path('', UsersView.as_view(), name='list')
]
