from datetime import datetime

from django.views.generic import TemplateView
from django.conf import settings
import requests

from .helpers import get_last_seen
from synapse_admin.helpers import assemble_mxc_url, get_download_url_for_media


class UsersView(TemplateView):
    template_name = 'users/users.html'

    def parse_users(self, sort_by: str) -> list:
        users: list = []

        request_url = f'https://{settings.MATRIX_DOMAIN}/_synapse/admin/v2/users?guests=false'

        response = requests.get(url=request_url, headers={
            'Authorization': f'Bearer {settings.MATRIX_ADMIN_TOKEN}'
        })

        if response.status_code != 200:
            raise Exception

        users = response.json()['users']

        for user in users:
            # Convert avatars
            if user['avatar_url'] is not None:
                mxc_url = assemble_mxc_url(user['avatar_url'])
                user['avatar_url'] = get_download_url_for_media(
                    server_name=mxc_url[0],
                    media_id=mxc_url[1],
                    access_token=settings.MATRIX_ADMIN_TOKEN
                )

            # Get last seen ts
            if sort_by in ('last_seen', '-last_seen'):
                last_seen_ts, device_name = get_last_seen(
                    access_token=settings.MATRIX_ADMIN_TOKEN,
                    server_name=settings.MATRIX_DOMAIN,
                    user_id=user['name']
                )

                if last_seen_ts is None:
                    last_seen_ts = 946684800
                else:
                    last_seen_ts = last_seen_ts / 1000

                last_seen_date = datetime.fromtimestamp(last_seen_ts)

                user['last_seen_date'] = last_seen_date
                user['device_name'] = device_name

        # Sort by name
        if sort_by == 'name':
            users = sorted(users, key=lambda k: k['name'])
        elif sort_by == '-name':
            users = sorted(users, key=lambda k: k['name'], reverse=True)

        # Sort by creation date
        if sort_by == 'creation_date':
            users = sorted(users, key=lambda k: k['creation_ts'])
        elif sort_by == '-creation_date':
            users = sorted(users, key=lambda k: k['creation_ts'], reverse=True)

        # Sort by last seen
        if sort_by == 'last_seen':
            users = sorted(users, key=lambda k: k['last_seen_date'])
        elif sort_by == '-last_seen':
            users = sorted(users, key=lambda k: k['last_seen_date'], reverse=True)

        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort_by = self.request.GET.get('sort_by', '-date_joined')
        context['users'] = self.parse_users(sort_by=sort_by)
        context['sort_by'] = sort_by
        return context
