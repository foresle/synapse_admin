from datetime import datetime
import requests
from django.core.cache import cache
import flag
import synapse_admin
from django.conf import settings

from project.helpers import get_download_url_for_media, assemble_mxc_url, spent_time_counter
from dashboard.helpers import load_media_statistics


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
        'last_seen_country': 'Unknown',
        'last_seen_user_agent': 'Unknown'
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
            'last_seen_country': get_country_by_ip(active_sessions[0]['ip']),
            'last_seen_user_agent': active_sessions[0]['user_agent']
        }

    return last_seen


@spent_time_counter
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

    for user in user_manager.lists(limit=1000000):
        users[user['name']] = {
            'name': user['name'],
            'name_without_server_name_ending': user['name'][:-(len(settings.MATRIX_DOMAIN) + 1)],
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

        # Convert avatar url address
        if user['avatar_url'] is not None:
            avatar_server_name, avatar_media_id = assemble_mxc_url(user['avatar_url'])
            users[user['name']]['avatar_url'] = get_download_url_for_media(
                media_id=avatar_media_id,
                server_name=avatar_server_name,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )

    cache.set(settings.CACHED_USERS_UPDATED_AT, datetime.now(), 60 * 60 * 60 * 24)
    cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)

    # Also update media statistics
    load_media_statistics(access_token=access_token, server_name=server_name)


@spent_time_counter
def deactivate_user(access_token: str, server_name: str, user_id: str) -> bool:
    """
    Deactivate user in the server.
    """

    user_manager: synapse_admin.User = synapse_admin.User(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    result: bool = user_manager.deactivate(userid=user_id)

    # Change cached data if deactivation will be successful
    if result:
        users: dict = cache.get(settings.CACHED_USERS)

        users[user_id]['is_deactivated'] = True

        cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)

    return result


@spent_time_counter
def activate_user(access_token: str, server_name: str, user_id: str, new_password: str) -> bool:
    """
    Activate user in the server.
    """

    user_manager: synapse_admin.User = synapse_admin.User(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    result: bool = user_manager.reactivate(userid=user_id, password=new_password)

    # Change cached data if reactivation will be successful
    if result:
        users: dict = cache.get(settings.CACHED_USERS)

        users[user_id]['is_deactivated'] = False

        cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)

    return result


@spent_time_counter
def set_admin(access_token: str, server_name: str, user_id: str) -> bool:
    """
    Set admin of the server.
    """

    user_manager: synapse_admin.User = synapse_admin.User(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    result: bool = user_manager.set_admin(userid=user_id, activate=True)[0]

    # Change cached data if admin access has been granted
    if result:
        users: dict = cache.get(settings.CACHED_USERS)

        users[user_id]['is_admin'] = True

        cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)

    return result


@spent_time_counter
def revoke_admin(access_token: str, server_name: str, user_id: str) -> bool:
    """
    Revoke admin of the server.
    """

    user_manager: synapse_admin.User = synapse_admin.User(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    result: bool = user_manager.set_admin(userid=user_id, activate=False)[0]

    # Change cached data if admin access has been revoked
    if result:
        users: dict = cache.get(settings.CACHED_USERS)

        users[user_id]['is_admin'] = False

        cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)

    return result
