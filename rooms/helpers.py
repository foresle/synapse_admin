from datetime import datetime
import synapse_admin
from django.conf import settings
from django.core.cache import cache
from synapse_admin.base import SynapseException

from project.helpers import assemble_mxc_url, get_download_url_for_media


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

        # Loading room members
        members: list = []
        try:
            members = room_manager.list_members(room['room_id'])
        except SynapseException:
            pass

        rooms[room['room_id']]['local_members'] = [member for member in members if
                                                   member.endswith(settings.MATRIX_DOMAIN)]
        rooms[room['room_id']]['global_members'] = [member for member in members if
                                                    not member.endswith(settings.MATRIX_DOMAIN)]

        # Finding the room avatar
        states = []
        try:
            states = room_manager.get_state(room['room_id'])
        except SynapseException:
            pass

        states = [state for state in states if state['type'] == 'm.room.avatar']
        if len(states) == 1:
            avatar_server_name, avatar_media_id = assemble_mxc_url(states[0]['content']['url'])
            rooms[room['room_id']]['avatar_url'] = get_download_url_for_media(
                media_id=avatar_media_id,
                server_name=avatar_server_name,
                access_token=settings.MATRIX_ADMIN_TOKEN
            )
        else:
            rooms[room['room_id']]['avatar_url'] = None

    cache.set(settings.CACHED_ROOMS_UPDATED_AT, datetime.now(), 60 * 60 * 60 * 24)
    cache.set(settings.CACHED_ROOMS, rooms, 60 * 60 * 60 * 24)
