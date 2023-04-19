from celery import Celery
from django.conf import settings

from .helpers import load_rooms

app = Celery()


@app.task
def update_rooms_info() -> None:
    load_rooms(
        access_token=settings.MATRIX_ADMIN_TOKEN,
        server_name=settings.MATRIX_DOMAIN
    )
