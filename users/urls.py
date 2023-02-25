from django.urls import path

from .views import UsersView

app_name = 'users'

urlpatterns = [
    path('', UsersView.as_view(), name='list')
]
