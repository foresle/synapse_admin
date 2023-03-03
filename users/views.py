from datetime import datetime
from django.core.cache import cache
from django.views.generic import TemplateView
from django.conf import settings


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
