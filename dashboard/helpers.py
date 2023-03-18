import datetime
import json

import synapse_graph as synapse_graph
from django.core.cache import cache
import synapse_admin
import math
from django.conf import settings


def convert_size(size_bytes: int):
    if size_bytes == 0:
        return '0B'

    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


def load_media_statistics(access_token: str, server_name: str) -> None:
    media_manager: synapse_admin.Media = synapse_admin.Media(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    media_statistics: list = media_manager.statistics()
    cache.set(settings.CACHED_MEDIA_STATISTICS_UPDATED_AT, datetime.datetime.now(), 60 * 60 * 60 * 6)  # 6 hours
    cache.set(settings.CACHED_MEDIA_STATISTICS, media_statistics, 60 * 60 * 60 * 6)  # 6 hours

    # Update media info in cached users
    users = cache.get(settings.CACHED_USERS, {})

    for user_statistics in media_statistics:
        try:
            users[user_statistics['user_id']]['upload_media_count'] = user_statistics['media_count']
            users[user_statistics['user_id']]['size_of_upload_media'] = convert_size(user_statistics['media_length'])
        except KeyError:
            continue

    cache.set(settings.CACHED_USERS, users, 60 * 60 * 60 * 24)  # 1 day


def load_server_map(access_token: str, server_name: str) -> None:
    try:
        graph = synapse_graph.SynapseGraph(
            name=server_name,
            headers={'Authorization': f'Bearer {access_token}'},
            matrix_homeserver=server_name,
            hide_usernames=False,
            u2u_relation=True
        )

        server_map = json.loads(graph.json)

        # Clear all unnecessary information
        server_map = {
            'nodes': server_map['nodes'],
            'edges': server_map['edges']
        }

    except synapse_graph.SynapseGraphError as e:
        server_map = None

    cache.set(settings.CACHED_SERVER_MAP_UPDATED_AT, datetime.datetime.now(), 60 * 60 * 60 * 24)  # 1 day
    cache.set(settings.CACHED_SERVER_MAP, server_map, 60 * 60 * 60 * 24)  # 1 day
