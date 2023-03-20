from celery import Celery
from django.conf import settings

from .helpers import load_media_statistics, load_server_map

app = Celery()


@app.task
def update_media_statistics_info() -> None:
    load_media_statistics(
        access_token=settings.MATRIX_ADMIN_TOKEN,
        server_name=settings.MATRIX_DOMAIN
    )


@app.task
def update_server_map() -> None:
    load_server_map(
        access_token=settings.MATRIX_ADMIN_TOKEN,
        server_name=settings.MATRIX_DOMAIN
    )
