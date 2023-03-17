import sys
from datetime import datetime
import requests
from django.core.cache import cache
import flag
import synapse_admin

from project.helpers import assemble_mxc_url, get_download_url_for_media


# def get_country_by_ip(ip: str) -> str:
#     country: str
#
#     response = requests.get(f'https://api.country.is/{ip}')
#     if response.status_code != 200:
#         return 'Unknown'
#
#     country = flag.flag(response.json()['country'])
#
#     return country


# def load_user_devices(access_token: str, server_name: str, username: str) -> list:
#     """
#     Load devices for user, includes:
#      - Device name
#      - Last seen
#      - Device IP
#     """
#
#     devices = []
#
#     response = requests.get(url=f'https://{server_name}/_synapse/admin/v2/users/{username}/devices',
#                             headers={
#                                 'Authorization': f'Bearer {access_token}'
#                             })
#
#     if response.status_code != 200:
#         return devices
#
#     response = response.json()
#     if response['total'] == 0:
#         return devices
#
#     for device in response['devices']:
#         # If ts is None set default
#         if device['last_seen_ts'] is None:
#             device['last_seen_ts'] = 946684800
#         else:
#             device['last_seen_ts'] = device['last_seen_ts'] / 1000
#
#         devices.append({
#             'id': device['device_id'],
#             'name': device['display_name'],
#             'user_agent': device['last_seen_user_agent'],
#             'last_seen_ts': datetime.fromtimestamp(device['last_seen_ts']),
#             'last_seen_ip': device['last_seen_ip'],
#             'country_by_ip': get_country_by_ip(device['last_seen_ip'])
#         })
#
#     return devices


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
            'display_name': user['displayname'],
            'is_admin': user['admin'],
            'is_deactivated': user['deactivated'],
            'created_at': datetime.fromtimestamp(user['creation_ts'] / 1000),
            'avatar_mxc_url': user['avatar_url']
        }

    cache.set('users', users, 60 * 60 * 60 * 24)
    cache.set('last_users_info_update', datetime.now(), 60 * 60 * 60 * 24)
