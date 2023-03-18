import datetime
from django.core.cache import cache
from django.views.generic import FormView
from django.contrib import messages

from .forms import SendServiceNoticeForm


class SendServerNoticeView(FormView):
    template_name = 'server_notices/send.html'
    form_class = SendServiceNoticeForm
    success_url = '/server_notices/'

    def form_valid(self, form):
        results: list = form.send_server_notice()
        results: str = f'{sum(results)} out of {len(results)} notices were sent.'
        messages.add_message(self.request, messages.SUCCESS, results)
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['server_notices_page_active'] = True

        return context
