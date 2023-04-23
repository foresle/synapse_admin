import datetime
import json
from django.views.generic import TemplateView
from django.core.cache import cache
from django.conf import settings
from project.decorators import check_auth
from users.helpers import load_users
from rooms.helpers import load_rooms
from .helpers import load_media_statistics, load_server_map, convert_size
import requests


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    @check_auth
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Checking last updating information about users
        cached_users_updated_at = cache.get(settings.CACHED_USERS_UPDATED_AT, None)

        if cached_users_updated_at is None:
            load_users(
                server_name=settings.MATRIX_DOMAIN,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        # Checking last updating information about rooms
        cached_rooms_updated_at = cache.get(settings.CACHED_ROOMS_UPDATED_AT, None)

        if cached_rooms_updated_at is None:
            load_rooms(
                server_name=settings.MATRIX_DOMAIN,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        # Checking last updating information of media statistics
        cached_media_statistics_updated_at = cache.get(settings.CACHED_MEDIA_STATISTICS_UPDATED_AT, None)

        if cached_media_statistics_updated_at is None:
            load_media_statistics(
                server_name=settings.MATRIX_DOMAIN,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        # Checking last updating server map
        cached_server_map_updated_at = cache.get(settings.CACHED_SERVER_MAP_UPDATED_AT, None)
        if cached_server_map_updated_at is None:
            load_server_map(
                server_name=settings.MATRIX_DOMAIN,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        users: dict = cache.get('users', {})

        # Sorts users by last creation_ts and slice last week
        last_week: datetime.datetime = datetime.datetime.now() - datetime.timedelta(weeks=1)
        new_users: list = [user for user in users.values() if user['created_at'] > last_week]

        # Sorts users by last_seen_at and filter for today
        today: datetime.date = datetime.datetime.now().date()
        active_users_today: list = sorted(
            [user for user in users.values() if
             user['last_seen_at'] != 'Unknown' and user['last_seen_at'].date() == today],
            key=lambda k: k['last_seen_at'], reverse=True
        )

        context['new_users_for_last_week'] = new_users
        context['active_users_today'] = active_users_today
        context['cached_users_updated_at'] = cached_users_updated_at

        context['amount_of_uploaded_media'] = convert_size(
            sum([user['media_length'] for user in cache.get(settings.CACHED_MEDIA_STATISTICS, [])])
        )
        context['cached_media_statistics_updated_at'] = cached_media_statistics_updated_at

        context['server_map'] = json.dumps(cache.get(settings.CACHED_SERVER_MAP, {}))
        context['cached_server_map_updated_at'] = cached_server_map_updated_at

        context['dashboard_page_active'] = True

        context['operations'] = list(reversed(cache.get(settings.CACHED_OPERATIONS_MESSAGES, [])))

        return context


class InitView(TemplateView):
    template_name = 'dashboard/init.html'

    @staticmethod
    def check_connection_to_server(server_name: str, server_access_token: str) -> bool:
        """
        Checks the connection to the server and verifies the access token.
        """

        # Check connection to server
        try:
            response = requests.get(url=f'https://{server_name}/_synapse/admin/v1/server_version', timeout=1)
        except requests.exceptions.ConnectionError:
            return False

        if response.status_code != 200:
            return False

        # Check access token
        response = requests.get(url=f'https://{server_name}/_synapse/admin/v1/rooms',
                                headers={
                                    'Authorization': f'Bearer {server_access_token}'
                                })

        if response.status_code != 200:
            return False

        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        init_result = self.check_connection_to_server(
            server_name=settings.MATRIX_DOMAIN,
            server_access_token=settings.MATRIX_ADMIN_TOKEN
        )
        cache.set(
            'init_successful',
            init_result,
            60 * 60 * 60 * 24  # 1 day
        )
        context['server_access_token'] = settings.MATRIX_ADMIN_TOKEN
        context['server_name'] = settings.MATRIX_DOMAIN
        context['init_successful'] = init_result
        context['init_page_active'] = True

        return context
