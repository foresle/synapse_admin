from django.urls import path

from .views import UsersView, UserView

app_name = 'users'

urlpatterns = [
    path('<str:user_id>/', UserView.as_view(), name='detail'),
    path('', UsersView.as_view(), name='list')
]
