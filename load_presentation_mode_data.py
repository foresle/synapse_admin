import datetime
import os
import random
from django.core.cache import cache
from django.conf import settings

from dashboard.helpers import convert_size

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

now_datetime: datetime.datetime = datetime.datetime.now()

# Set init successful
cache.set(
    'init_successful',
    True,
    60 * 60  # 1 hour
)

# Set random users
users = {}
for i in range(0, 20):
    user_name: str = f'@user_{i}:matrix.test.server'

    user = {
        'name': user_name,
        'name_without_server_name_ending': user_name[:-(len('matrix.test.server') + 1)],
        'display_name': f'@user_{i}',
        'is_admin': random.getrandbits(1),
        'is_deactivated': random.getrandbits(1),
        'created_at': now_datetime - datetime.timedelta(
            days=random.randint(2, 20), hours=random.randint(1, 6), minutes=random.randint(1, 60)
        ),
        'avatar_mxc_url': None,
        'last_seen_ip': '127.0.0.1',
        'last_seen_at': now_datetime - datetime.timedelta(
            days=random.randint(0, 2), hours=random.randint(1, 4), minutes=random.randint(1, 60)
        ),
        'last_seen_country': random.choice(('🇺🇸', '🇺🇦', '🏳️‍🌈'))
    }

    users[user_name] = user

cache.set(
    settings.CACHED_USERS,
    users,
    60 * 60  # 1 hour
)
cache.set(
    settings.CACHED_USERS_UPDATED_AT,
    now_datetime,
    60 * 60  # 1 hour
)

# Set media statistics
media_statistics = []

for user in users.values():
    media_count: int = random.randint(0, 100)

    media_statistics.append(
        {
            'user_id': user['name'],
            'displayname': user['name_without_server_name_ending'],
            'media_count': media_count,
            'media_length': media_count * random.randint(100000, 900000)
        }
    )

cache.set(
    settings.CACHED_MEDIA_STATISTICS,
    media_statistics,
    60 * 60  # 1 hour
)
cache.set(
    settings.CACHED_MEDIA_STATISTICS_UPDATED_AT,
    now_datetime,
    60 * 60  # 1 hour
)

for user_statistics in media_statistics:
    try:
        users[user_statistics['user_id']]['upload_media_count'] = user_statistics['media_count']
        users[user_statistics['user_id']]['size_of_upload_media'] = convert_size(user_statistics['media_length'])
    except KeyError:
        continue

cache.set(
    settings.CACHED_USERS,
    users,
    60 * 60  # 1 hour
)

# Set server map
server_map: dict = {
    'nodes': [
        {
            'color': '#99a9af',
            'size': random.randint(10, 30),
            'id': '!420C1B7875A242ADB6:matrix.org',
            'label': '#public_room_1:matrix.test.server',
            'shape': 'dot'
        },
        {
            'color': '#99a9af',
            'size': random.randint(10, 30),
            'id': '!420C1B7875A242ADB7:matrix.org',
            'label': '#public_room_2:matrix.test.server',
            'shape': 'dot'
        }
    ],
    'edges': []
}

for user in users.values():
    server_map['nodes'].append(
        {
            'color': '#326051',
            'size': 5,
            'id': user['name'],
            'label': user['name_without_server_name_ending'],
            'shape': 'dot'
        }
    )

    if random.getrandbits(1):
        server_map['edges'].append(
            {
                'from': user['name'],
                'to': server_map['nodes'][random.getrandbits(1)]['id']
            }
        )

for user in users.values():
    if random.getrandbits(1):
        first_user = random.choice(tuple(users.values()))
        second_user = random.choice(tuple(users.values()))

        if first_user != second_user:
            server_map['edges'].append(
                {
                    'from': first_user['name'],
                    'to': second_user['name']
                }
            )

cache.set(
    settings.CACHED_SERVER_MAP,
    server_map,
    60 * 60  # 1 hour
)
cache.set(
    settings.CACHED_SERVER_MAP_UPDATED_AT,
    now_datetime,
    60 * 60  # 1 hour
)
