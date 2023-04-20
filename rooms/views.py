from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.views.generic import ListView, TemplateView

from .helpers import load_rooms
from django.conf import settings


class RoomsView(ListView):
    template_name = 'rooms/rooms.html'
    paginate_by = 30

    def get_queryset(self) -> tuple:
        return tuple(cache.get(settings.CACHED_ROOMS, {}).values())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.object_list, self.paginate_by)
        page: str = self.request.GET.get('page')

        try:
            rooms = paginator.get_page(page)
        except PageNotAnInteger:
            rooms = paginator.get_page(1)
        except EmptyPage:
            rooms = paginator.get_page(paginator.num_pages)

        context['rooms'] = rooms
        context['cached_rooms_updated_at'] = cache.get(settings.CACHED_USERS_UPDATED_AT, None)
        context['total_rooms'] = paginator.count

        context['rooms_page_active'] = True

        return context


class RoomView(TemplateView):
    template_name = 'rooms/room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        room_id = self.kwargs['room_id']
        room = cache.get(settings.CACHED_ROOMS, {}).get(room_id, None)
        if room is None:
            raise Http404('User not found.')

        context['room'] = room

        return context
