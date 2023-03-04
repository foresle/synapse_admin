from datetime import datetime
from django.core.cache import cache
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.http import Http404

from users.helpers import load_user_devices


class UsersView(TemplateView):
    template_name = 'users/users.html'

    def sort_users(self, users: list, sort_by: str) -> list:
        """
        Just sort users list.
        """

        # Sort by name
        if sort_by == 'name':
            users = sorted(users, key=lambda k: k['name'])
        elif sort_by == '-name':
            users = sorted(users, key=lambda k: k['name'], reverse=True)

        # Sort by creation date
        if sort_by == 'creation_date':
            users = sorted(users, key=lambda k: k['creation_ts'])
        elif sort_by == '-creation_date':
            users = sorted(users, key=lambda k: k['creation_ts'], reverse=True)

        # Sort by last seen
        if sort_by == 'last_seen':
            users = sorted(users, key=lambda k: k['last_seen_device']['last_seen_ts'])
        elif sort_by == '-last_seen':
            users = sorted(users, key=lambda k: k['last_seen_device']['last_seen_ts'], reverse=True)

        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort_by = self.request.GET.get('sort_by', '-date_joined')
        context['users'] = self.sort_users(
            users=cache.get('users', {}).values(),
            sort_by=sort_by
        )
        context['sort_by'] = sort_by
        return context


class UpdateLastSeenView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        users = cache.get('users', {})

        for user in users.values():
            user['devices'] = load_user_devices(
                access_token=settings.MATRIX_ADMIN_TOKEN,
                server_name=settings.MATRIX_DOMAIN,
                username=user['name']
            )

            # Find last seen device
            devices = sorted(user['devices'], key=lambda k: k['last_seen_ts'], reverse=True)
            if len(devices) > 0:
                user['last_seen_device'] = devices[0]
            else:
                user['last_seen_device'] = {
                    'id': 'Unknown',
                    'name': 'Unknown',
                    'user_agent': 'Unknown',
                    'last_seen_ts': datetime.fromtimestamp(946684800),
                    'last_seen_ip': 'Unknown'
                }

        cache.set('users', users, 60 * 60 * 60 * 24)

        return super().get_redirect_url(*args, **kwargs)


class UserView(TemplateView):
    template_name = 'users/user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_id = self.kwargs['user_id']
        user = cache.get('users', {}).get(user_id, None)
        if user is None:
            raise Http404('User not found.')
        context['user'] = user

        return context
