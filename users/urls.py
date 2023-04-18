from django.urls import path

from .views import UsersView, UserView, DeactivateUserView, ActivateUserView, SetAdminView, RevokeAdminView

app_name = 'users'

urlpatterns = [
    path('<str:user_id>/', UserView.as_view(), name='detail'),
    path('deactivate/<str:user_id>/', DeactivateUserView.as_view(), name='deactivate'),
    path('activate/<str:user_id>/', ActivateUserView.as_view(), name='activate'),
    path('set_admin/<str:user_id>/', SetAdminView.as_view(), name='set_admin'),
    path('revoke_admin/<str:user_id>/', RevokeAdminView.as_view(), name='revoke_admin'),
    path('', UsersView.as_view(), name='list')
]
