import datetime
from django.conf import settings
from django.core.cache import cache


def assemble_mxc_url(mxc_url: str) -> (str, str):
    """
    Return parsed mxc url:
    mxc://<server-name>/<media-id> -> (server_name, media_id)
    https://spec.matrix.org/v1.5/client-server-api/#matrix-content-mxc-uris
    """

    return tuple(mxc_url[6:].split('/'))


def get_download_url_for_media(media_id: str, server_name: str | None = None, access_token: str | None = None) -> str:
    """
    Return link to original media file.
    """

    if server_name is None:
        server_name = settings.MATRIX_DOMAIN

    if access_token is None:
        access_token = settings.MATRIX_ADMIN_TOKEN

    return f'https://{settings.MATRIX_DOMAIN}/_matrix/media/v3/download/{server_name}/{media_id}?access_token={access_token}'


def make_operation_message(func_name: str, spent_time: datetime.timedelta) -> None:
    """
    Make operation object and then save to cache.
    """

    operation_message: dict = {
        'name': func_name,
        'spent_time': spent_time.seconds,
        'made_at': datetime.datetime.now()
    }

    operations_messages: list = cache.get(settings.CACHED_OPERATIONS_MESSAGES, [])
    operations_messages.append(operation_message)

    cache.set(settings.CACHED_OPERATIONS_MESSAGES, operations_messages, 60*60*60*24*7)


def spent_time_counter(func):
    """
    Record spent time and save to cached operations.
    """

    def wrapper(*args, **kwargs):
        start_time: datetime.datetime = datetime.datetime.now()
        result = func(*args, **kwargs)
        make_operation_message(func_name=func.__name__, spent_time=datetime.datetime.now() - start_time)
        return result

    return wrapper
