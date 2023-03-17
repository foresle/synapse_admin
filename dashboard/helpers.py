import datetime

from django.core.cache import cache
import synapse_admin
import math


def convert_size(size_bytes: int):
    if size_bytes == 0:
        return '0B'

    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


def load_media_statistics(access_token: str, server_name: str) -> None:
    size_of_all_media: str

    media_manager: synapse_admin.Media = synapse_admin.Media(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    size_of_all_media = convert_size(sum([user['media_length'] for user in media_manager.statistics()]))

    cache.set('size_of_all_media', size_of_all_media, 60 * 60 * 60 * 6)  # 6 hours
    cache.set('last_media_statistics_info_updating', datetime.datetime.now(), 60 * 60 * 60 * 6)  # 6 hours
