import requests
from django.core.cache import cache

from synapse_admin.helpers import assemble_mxc_url, get_download_url_for_media


def get_last_seen(access_token: str, server_name: str, user_id: str) -> (None | int, None | str):
    response = requests.get(url=f'https://{server_name}/_synapse/admin/v2/users/{user_id}/devices',
                            headers={
                                'Authorization': f'Bearer {access_token}'
                            })

    if response.status_code != 200:
        return None, None

    response = response.json()
    if response['total'] == 0:
        return None, None

    devices = response['devices']

    # Delete devices without last_seen_ts
    for device in devices:
        if device['last_seen_ts'] is None:
            return None, None

    devices = sorted(devices, key=lambda k: k['last_seen_ts'], reverse=True)

    return devices[0]['last_seen_ts'], devices[0]['display_name']


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
            'creation_ts': user['creation_ts'],
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

    cache.set('users', users, 60 * 60 * 60 * 24)

    return True
