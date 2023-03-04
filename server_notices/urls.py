from django.urls import path

from .views import SendServerNoticeView

app_name = 'server_notices'

urlpatterns = [
    path('', SendServerNoticeView.as_view(), name='send')
]
