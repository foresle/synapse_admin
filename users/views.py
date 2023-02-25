from django.views.generic import TemplateView
from django.conf import settings
import requests

from .helpers import assemble_mxc_url, get_download_url_for_media


class UsersView(TemplateView):
    template_name = 'users/users.html'

    def parse_users(self) -> list:
        users: list = []
        response = requests.get(f'https://{settings.MATRIX_DOMAIN}/_synapse/admin/v2/users?guests=false', headers={
            'Authorization': f'Bearer {settings.MATRIX_ADMIN_TOKEN}'
        })

        if response.status_code != 200:
            raise Exception

        users = response.json()['users']

        for user in users:
            if user['avatar_url'] is None:
                continue

            mxc_url = assemble_mxc_url(user['avatar_url'])
            user['avatar_url'] = get_download_url_for_media(
                server_name=mxc_url[0],
                media_id=mxc_url[1],
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.parse_users()
        return context
