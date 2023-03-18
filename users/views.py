from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import TemplateView, ListView
from django.conf import settings
from django.http import Http404


class UsersView(ListView):
    template_name = 'users/users.html'
    paginate_by = 10

    # def sort_users(self, users: list, sort_by: str) -> list:
    #     """
    #     Just sort users list.
    #     """
    #
    #     # Sort by name
    #     if sort_by == 'name':
    #         users = sorted(users, key=lambda k: k['name'])
    #     elif sort_by == '-name':
    #         users = sorted(users, key=lambda k: k['name'], reverse=True)
    #
    #     # Sort by creation date
    #     if sort_by == 'creation_date':
    #         users = sorted(users, key=lambda k: k['creation_ts'])
    #     elif sort_by == '-creation_date':
    #         users = sorted(users, key=lambda k: k['creation_ts'], reverse=True)
    #
    #     # Sort by last seen
    #     if sort_by == 'last_seen':
    #         users = sorted(users, key=lambda k: k['last_seen_device']['last_seen_ts'])
    #     elif sort_by == '-last_seen':
    #         users = sorted(users, key=lambda k: k['last_seen_device']['last_seen_ts'], reverse=True)
    #
    #     return users

    def get_queryset(self) -> tuple:
        return tuple(cache.get(settings.CACHED_USERS, {}).values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.object_list, self.paginate_by)
        page: str = self.request.GET.get('page')

        try:
            users = paginator.get_page(page)
        except PageNotAnInteger:
            users = paginator.get_page(1)
        except EmptyPage:
            users = paginator.get_page(paginator.num_pages)

        context['users'] = users
        context['cached_users_updated_at'] = cache.get(settings.CACHED_USERS_UPDATED_AT, None)
        context['total_users'] = paginator.count

        context['users_page_active'] = True

        return context


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
