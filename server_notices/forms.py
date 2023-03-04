from django import forms
from django.conf import settings
from django.core.cache import cache

from .helpers import send_server_notice


class SendServiceNoticeForm(forms.Form):
    payload = forms.CharField(widget=forms.Textarea())

    def send_server_notice(self) -> dict:
        users = cache.get('users', {}).values()

        result = {}

        for user in users:
            status_code = send_server_notice(
                access_token=settings.MATRIX_ADMIN_TOKEN,
                server_name=settings.MATRIX_DOMAIN,
                payload=self.cleaned_data['payload'],
                user_id=user['name']
            )

            result[user['name']] = status_code

        return result
