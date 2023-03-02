from django.urls import path

from .views import DashboardView, AuthView

app_name = 'dashboard'

urlpatterns = [
    path('auth/', AuthView.as_view(), name='auth'),
    path('', DashboardView.as_view(), name='dashboard'),
]
