from django.urls import path

from .views import DashboardView, InitView

app_name = 'dashboard'

urlpatterns = [
    path('', InitView.as_view(), name='init'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
