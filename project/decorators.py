from django.shortcuts import redirect
from django.core.cache import cache


def check_auth(func):
    def wrapper(*args, **kwargs):
        value = cache.get('init_successful')

        if value is None:
            value = False
        else:
            value = bool(int(value))

        if value:
            return func(*args, **kwargs)
        else:
            return redirect('dashboard:init')

    return wrapper
