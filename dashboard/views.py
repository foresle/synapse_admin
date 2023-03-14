import datetime
import json
import synapse_graph as synapse_graph
from django.views.generic import TemplateView
from django.core.cache import cache
from django.conf import settings

from synapse_admin.decorators import check_auth
from users.helpers import load_users
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

        _map = json.loads(graph.json)

        # Clear all unnecessary information
        _map = {
            'nodes': _map['nodes'],
            'edges': _map['edges']
        }

        return _map

    except synapse_graph.SynapseGraphError as e:
        return {}


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    @check_auth
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Scan users
        last_scan = cache.get('last_scan', None)

        if last_scan is None:
            scan_result = load_users(
                access_token=settings.MATRIX_ADMIN_TOKEN,
                server_name=settings.MATRIX_DOMAIN
            )

            if scan_result:
                last_scan = datetime.datetime.now()

            cache.set('last_scan', last_scan, (60 * 60 * 60 * 23))

        # Map
        _map = cache.get('map')
        if _map is None:
            _map = update_map()
            cache.set('map', _map, 60 * 60 * 60 * 24)

        context['map'] = json.dumps(_map)
        context['last_scan'] = last_scan

        # Sorts users by last creation_ts and slice for 5
        context['users'] = sorted(cache.get('users', {}).values(), key=lambda k: k.created_at, reverse=True)[:5]

        return context


class InitView(TemplateView):
    template_name = 'dashboard/init.html'

    def init_synapse_admin(self) -> (int, str | None):
        """
        Returns (status_code, error msg), if last exists.
        """

        try:
            response = requests.get(url=f'https://{settings.MATRIX_DOMAIN}/_synapse/admin/v1/server_version', timeout=1)
        except requests.exceptions.ConnectionError:
            return 0, 'Connection Timeout'

        if response.status_code != 200:
            return response.status_code, response.text

        response = requests.get(url=f'https://{settings.MATRIX_DOMAIN}/_synapse/admin/v1/rooms',
                                headers={
                                    'Authorization': f'Bearer {settings.MATRIX_ADMIN_TOKEN}'
                                })

        if response.status_code != 200:
            return response.status_code, response.json().get('error', 'Unknown Error')

        return 200, None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        init_results = self.init_synapse_admin()
        cache.set(
            'init_completed',
            1 if init_results[0] == 200 else 0,
            60 * 60 * 60 * 24
        )

        context['access_token'] = settings.MATRIX_ADMIN_TOKEN
        context['server_name'] = settings.MATRIX_DOMAIN
        context['connection_status_code'] = init_results[0]
        context['error_message'] = init_results[1]

        return context
