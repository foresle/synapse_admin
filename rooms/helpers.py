from datetime import datetime

import synapse_admin
from django.conf import settings
from django.core.cache import cache
from synapse_admin.base import SynapseException


def load_rooms(access_token: str, server_name: str) -> None:
    """
    Load rooms and cache it to redis.
    """

    room_manager: synapse_admin.Room = synapse_admin.Room(
        server_addr=server_name,
        server_port=443,
        access_token=access_token,
        server_protocol='https://'
    )

    rooms: dict = {}

    for room in room_manager.lists(limit=1000000):
        rooms[room['room_id']] = {
            'room_id': room['room_id'],
            'name': room['name'],
            'joined_members': room['joined_members'],
            'joined_local_members': room['joined_local_members'],
            'version': room['version'],
            'creator': room['creator'],
            'encryption': room['encryption'],
            'federatable': room['federatable'],
            'public': room['public']
        }

        members: list = []
        try:
            members = room_manager.list_members(room['room_id'])
        except SynapseException:
            pass

        rooms[room['room_id']]['local_members'] = [member for member in members if member.endswith(settings.MATRIX_DOMAIN)]
        rooms[room['room_id']]['global_members'] = [member for member in members if not member.endswith(settings.MATRIX_DOMAIN)]

    cache.set(settings.CACHED_ROOMS_UPDATED_AT, datetime.now(), 60 * 60 * 60 * 24)
    cache.set(settings.CACHED_ROOMS, rooms, 60 * 60 * 60 * 24)
