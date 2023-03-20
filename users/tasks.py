from celery import Celery
from django.conf import settings

from .helpers import load_users

app = Celery()


@app.task
def update_users_info() -> None:
    load_users(
        access_token=settings.MATRIX_ADMIN_TOKEN,
        server_name=settings.MATRIX_DOMAIN
    )
