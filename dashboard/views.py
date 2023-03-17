import datetime
import json
import synapse_graph as synapse_graph
from django.views.generic import TemplateView
from django.core.cache import cache
from django.conf import settings

from project.decorators import check_auth
from users.helpers import load_users
from .helpers import load_media_statistics
import requests


def update_map() -> dict:
    """
    Load synapse graph, use only in dashboard view.
    """

    try:
        graph = synapse_graph.SynapseGraph(
            name=settings.MATRIX_DOMAIN,
            headers={'Authorization': f'Bearer {settings.MATRIX_ADMIN_TOKEN}'},
            matrix_homeserver=settings.MATRIX_DOMAIN,
            hide_usernames=False,
            u2u_relation=True
        )

        server_map = json.loads(graph.json)

        # Clear all unnecessary information
        server_map = {
            'nodes': server_map['nodes'],
            'edges': server_map['edges']
        }

        return server_map

    except synapse_graph.SynapseGraphError as e:
        return {}


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    @check_auth
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check last users info updating
        last_users_info_update = cache.get('last_users_info_update', None)

        if last_users_info_update is None:
            load_users(
                server_name=settings.MATRIX_DOMAIN,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        # Check last media statistics info updating
        last_media_statistics_info_updating = cache.get('last_media_statistics_info_updating', None)

        if last_media_statistics_info_updating is None:
            load_media_statistics(
                server_name=settings.MATRIX_DOMAIN,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

        # Synapse graph
        server_map = cache.get('server_map', None)
        if server_map is None:
            server_map = update_map()
            cache.set('server_map', server_map, 60 * 60 * 60 * 24)  # 1 day

        context['server_map'] = json.dumps(server_map)

        # Sorts users by last creation_ts and slice last week
        users: dict = cache.get('users', {})
        last_week: datetime.datetime = datetime.datetime.now() - datetime.timedelta(weeks=1)
        new_users: list = [user for user in users.values() if user['created_at'] > last_week]
        context['new_users_for_last_week'] = new_users
        context['last_users_info_update'] = last_users_info_update

        context['size_of_all_media'] = cache.get('size_of_all_media', None)
        context['last_media_statistics_info_updating'] = cache.get('last_media_statistics_info_updating', None)

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

        return context
