from datetime import datetime
import requests
from django.core.cache import cache
import flag

from synapse_admin.helpers import assemble_mxc_url, get_download_url_for_media


def get_country_by_ip(ip: str) -> str:
    country: str

    response = requests.get(f'https://api.country.is/{ip}')
    if response.status_code != 200:
        return 'Unknown'

    country = flag.flag(response.json()['country'])

    return country


def load_user_devices(access_token: str, server_name: str, username: str) -> list:
    """
    Load devices for user, includes:
     - Device name
     - Last seen
     - Device IP
    """
    devices = []

    response = requests.get(url=f'https://{server_name}/_synapse/admin/v2/users/{username}/devices',
                            headers={
                                'Authorization': f'Bearer {access_token}'
                            })

    if response.status_code != 200:
        return devices

    response = response.json()
    if response['total'] == 0:
        return devices

    for device in response['devices']:
        # If ts is None set default
        if device['last_seen_ts'] is None:
            device['last_seen_ts'] = 946684800
        else:
            device['last_seen_ts'] = device['last_seen_ts'] / 1000

        devices.append({
            'id': device['device_id'],
            'name': device['display_name'],
            'user_agent': device['last_seen_user_agent'],
            'last_seen_ts': datetime.fromtimestamp(device['last_seen_ts']),
            'last_seen_ip': device['last_seen_ip'],
            'country_by_ip': get_country_by_ip(device['last_seen_ip'])
        })

    return devices


def load_users(access_token: str, server_name: str) -> bool:
    """
    Load users to redis, with additional data like a:
     - Last seen time
     - Devices list
     - Joined rooms
     - Uploaded media
    """

    users = {}

    # Load all users list for first
    request_url = f'https://{server_name}/_synapse/admin/v2/users?guests=false'

    response = requests.get(url=request_url, headers={
        'Authorization': f'Bearer {access_token}'
    })

    if response.status_code != 200:
        # raise Exception
        return False

    for user in response.json()['users']:
        users[f'{user["name"]}'] = {
            'name': user['name'],
            'display_name': user['displayname'],
            'admin': user['admin'],
            'deactivated': user['deactivated'],
            'creation_ts': datetime.fromtimestamp(user['creation_ts'] / 1000),
            'avatar_url': user['avatar_url']
        }

    # Convert avatar url
    for user in users.values():
        if user['avatar_url'] is None:
            continue

        mxc_url = assemble_mxc_url(user['avatar_url'])
        user['avatar_url'] = get_download_url_for_media(
            server_name=mxc_url[0],
            media_id=mxc_url[1],
            access_token=access_token
        )

    # Load users devices
    for user in users.values():
        user['devices'] = load_user_devices(
            access_token=access_token,
            server_name=server_name,
            username=user['name']
        )

        # Find last seen device
        devices = sorted(user['devices'], key=lambda k: k['last_seen_ts'], reverse=True)
        if len(devices) > 0:
            user['last_seen_device'] = devices[0]
        else:
            user['last_seen_device'] = {
                'id': 'Unknown',
                'name': 'Unknown',
                'user_agent': 'Unknown',
                'last_seen_ts': datetime.fromtimestamp(946684800),
                'last_seen_ip': 'Unknown',
                'country_by_ip': 'Unknown'
            }

    cache.set('users', users, 60 * 60 * 60 * 24)

    return True
