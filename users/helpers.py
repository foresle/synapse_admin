def assemble_mxc_url(mxc_url: str) -> (str, str):
    """
    Return parsed mxc url:
    mxc://<server-name>/<media-id> -> (server_name, media_id)
    https://spec.matrix.org/v1.5/client-server-api/#matrix-content-mxc-uris
    """

    return tuple(mxc_url[6:].split('/'))


def get_download_url_for_media(server_name: str, media_id: str, access_token: str) -> str:
    return f'https://{server_name}/_matrix/media/v3/download/{server_name}/{media_id}?access_token={access_token}'
