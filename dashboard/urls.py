from django.urls import path

from .views import DashboardView, InitView

app_name = 'dashboard'

urlpatterns = [
    path('init/', InitView.as_view(), name='init'),
    path('', DashboardView.as_view(), name='dashboard'),
]
