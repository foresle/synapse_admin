import markdown as markdown
import requests

from project.helpers import spent_time_counter


@spent_time_counter
def send_server_notice(access_token: str, server_name: str, payload: str, user_id: str) -> bool:
    response = requests.post(url=f'https://{server_name}/_synapse/admin/v1/send_server_notice',
                             headers={
                                 'Authorization': f'Bearer {access_token}'
                             },
                             json={
                                 'user_id': user_id,
                                 'content': {
                                     'body': payload,
                                     'format': 'org.matrix.custom.html',
                                     'formatted_body': markdown.markdown(payload),
                                     'msgtype': 'm.text'
                                 }
                             }
                             )

    if response.status_code != 200:
        return False

    return True
