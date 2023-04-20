from django.urls import path

from .views import RoomsView, RoomView

app_name = 'rooms'

urlpatterns = [
    path('<str:room_id>/', RoomView.as_view(), name='detail'),
    path('', RoomsView.as_view(), name='list')
]
