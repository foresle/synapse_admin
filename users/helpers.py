from datetime import datetime
import requests
from django.core.cache import cache
import flag
import synapse_admin
from django.conf import settings


def get_country_by_ip(ip: str) -> str:
    country: str

    response = requests.get(f'https://api.country.is/{ip}')
    if response.status_code != 200:
        return 'Unknown'

    country = flag.flag(response.json()['country'])

    return country


def get_last_seen_info(access_token: str, server_name: str, user_id: str) -> dict:
    last_seen: dict = {
        'last_seen_ip': 'Unknown',
        'last_seen_at': 'Unknown',
        'last_seen_country': 'Unknown'
    }

    user_manager: synapse_admin.User = synapse_admin.User(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    active_sessions = user_manager.active_sessions(user_id)

    if len(active_sessions) > 0:
        last_seen = {
            'last_seen_ip': active_sessions[0]['ip'],
            'last_seen_at': datetime.fromtimestamp(active_sessions[0]['last_seen'] / 1000),
            'last_seen_country': get_country_by_ip(active_sessions[0]['ip'])
        }

    return last_seen


def load_users(access_token: str, server_name: str) -> None:
    """
    Load users and cache it to redis.
    """

    user_manager: synapse_admin.User = synapse_admin.User(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    users: dict = {}

    for user in user_manager.lists():
        users[user['name']] = {
            'name': user['name'],
            'name_without_server_name_ending': user['name'][:-(len(settings.MATRIX_DOMAIN)+1)],
            'display_name': user['displayname'],
            'is_admin': user['admin'],
            'is_deactivated': user['deactivated'],
            'created_at': datetime.fromtimestamp(user['creation_ts'] / 1000),
            'avatar_mxc_url': user['avatar_url']
        }

        # Get last seen info
        users[user['name']].update(
            get_last_seen_info(access_token=access_token, server_name=server_name, user_id=user['name'])
        )

    cache.set(settings.CACHED_USERS_UPDATED_AT, datetime.now(), 60 * 60 * 60 * 24)
    cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)
