from django import forms
from django.conf import settings

from .helpers import deactivate_user, activate_user, set_admin, revoke_admin


class DeactivateUserForm(forms.Form):
    user_id = forms.CharField(label='User ID', initial='', required=True)

    def deactivate_user(self) -> bool:
        user_id = self.cleaned_data['user_id']

        return deactivate_user(
            access_token=settings.MATRIX_ADMIN_TOKEN,
            server_name=settings.MATRIX_DOMAIN,
            user_id=user_id
        )


class ActivateUserForm(forms.Form):
    user_id = forms.CharField(label='User ID', initial='', required=True)
    new_password = forms.CharField(label='New password', initial='', required=True, widget=forms.PasswordInput)

    def activate_user(self) -> bool:
        user_id = self.cleaned_data['user_id']
        new_password = self.cleaned_data['new_password']

        return activate_user(
            access_token=settings.MATRIX_ADMIN_TOKEN,
            server_name=settings.MATRIX_DOMAIN,
            user_id=user_id,
            new_password=new_password
        )


class SetAdminForm(forms.Form):
    user_id = forms.CharField(label='User ID', initial='', required=True)

    def set_admin(self) -> bool:
        user_id = self.cleaned_data['user_id']

        return set_admin(
            access_token=settings.MATRIX_ADMIN_TOKEN,
            server_name=settings.MATRIX_DOMAIN,
            user_id=user_id
        )


class RevokeAdminForm(forms.Form):
    user_id = forms.CharField(label='User ID', initial='', required=True)

    def revoke_admin(self) -> bool:
        user_id = self.cleaned_data['user_id']

        return revoke_admin(
            access_token=settings.MATRIX_ADMIN_TOKEN,
            server_name=settings.MATRIX_DOMAIN,
            user_id=user_id
        )
