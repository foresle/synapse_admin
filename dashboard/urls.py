from django.urls import path

from .views import DashboardView, InitView

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', InitView.as_view(), name='init'),
]
