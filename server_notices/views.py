import datetime

from django.core.cache import cache
from django.views.generic import FormView

from .forms import SendServiceNoticeForm


class SendServerNoticeView(FormView):
    template_name = 'server_notices/send.html'
    form_class = SendServiceNoticeForm
    success_url = '/server_notices/'

    def form_valid(self, form):
        cache.set('last_server_notice', {
            'result': form.send_server_notice(),
            'sending_at': datetime.datetime.now(),
            'payload': form.cleaned_data['payload']
        }, 60 * 60 * 60 * 24 * 7)
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['last_server_notice'] = cache.get('last_server_notice', None)

        return context
