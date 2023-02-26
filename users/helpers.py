import requests


def assemble_mxc_url(mxc_url: str) -> (str, str):
    """
    Return parsed mxc url:
    mxc://<server-name>/<media-id> -> (server_name, media_id)
    https://spec.matrix.org/v1.5/client-server-api/#matrix-content-mxc-uris
    """

    return tuple(mxc_url[6:].split('/'))


def get_download_url_for_media(server_name: str, media_id: str, access_token: str) -> str:
    return f'https://{server_name}/_matrix/media/v3/download/{server_name}/{media_id}?access_token={access_token}'


def get_last_seen(access_token: str, server_name: str, user_id: str) -> None | int:
    response = requests.get(url=f'https://{server_name}/_synapse/admin/v2/users/{user_id}/devices',
                            headers={
                                'Authorization': f'Bearer {access_token}'
                            })

    if response.status_code != 200:
        return None

    response = response.json()
    if response['total'] == 0:
        return None

    devices = response['devices']

    # Delete devices without last_seen_ts
    for device in devices:
        if device['last_seen_ts'] is None:
            return None

    devices = sorted(devices, key=lambda k: k['last_seen_ts'], reverse=True)

    return devices[0]['last_seen_ts']
