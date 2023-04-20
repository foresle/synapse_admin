from django.conf import settings


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
