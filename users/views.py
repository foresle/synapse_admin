from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import TemplateView, ListView, FormView
from django.conf import settings
from django.http import Http404
from django.contrib import messages

from .forms import DeactivateUserForm, ActivateUserForm, SetAdminForm, RevokeAdminForm


class UsersView(ListView):
    template_name = 'users/users.html'
    paginate_by = 10

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
        user = cache.get(settings.CACHED_USERS, {}).get(user_id, None)
        if user is None:
            raise Http404('User not found.')

        cache.get(settings.CACHED_MEDIA_STATISTICS, {})

        context['user'] = user

        return context


class DeactivateUserView(FormView):
    template_name = 'users/deactivate.html'
    form_class = DeactivateUserForm

    def get_form(self, form_class=None):
        form: DeactivateUserForm = super().get_form(form_class=form_class)

        form.fields['user_id'].initial = self.kwargs['user_id']

        return form

    def form_valid(self, form):
        result: bool = form.deactivate_user()
        user_id: str = form.cleaned_data['user_id']

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS if result else messages.ERROR,
            message=f'User {user_id} has been deactivated successfully!' if result else f'Deactivation unsuccessful.'
        )

        return super().form_valid(form=form)

    def get_success_url(self):
        return f'/users/deactivate/{self.kwargs["user_id"]}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class ActivateUserView(FormView):
    template_name = 'users/activate.html'
    form_class = ActivateUserForm

    def get_form(self, form_class=None):
        form: DeactivateUserForm = super().get_form(form_class=form_class)

        form.fields['user_id'].initial = self.kwargs['user_id']

        return form

    def form_valid(self, form):
        result: bool = form.activate_user()
        user_id: str = form.cleaned_data['user_id']

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS if result else messages.ERROR,
            message=f'User {user_id} has been activated successfully!' if result else f'Activation unsuccessful.'
        )

        return super().form_valid(form=form)

    def get_success_url(self):
        return f'/users/activate/{self.kwargs["user_id"]}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SetAdminView(FormView):
    template_name = 'users/set_admin.html'
    form_class = SetAdminForm

    def get_form(self, form_class=None):
        form: DeactivateUserForm = super().get_form(form_class=form_class)

        form.fields['user_id'].initial = self.kwargs['user_id']

        return form

    def form_valid(self, form):
        result: bool = form.set_admin()
        user_id: str = form.cleaned_data['user_id']

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS if result else messages.ERROR,
            message=f'Admin access has been granted for {user_id} successfully!' if result else f'Granting admin '
                                                                                                f'rights failed.'
        )

        return super().form_valid(form=form)

    def get_success_url(self):
        return f'/users/set_admin/{self.kwargs["user_id"]}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class RevokeAdminView(FormView):
    template_name = 'users/revoke_admin.html'
    form_class = RevokeAdminForm

    def get_form(self, form_class=None):
        form: DeactivateUserForm = super().get_form(form_class=form_class)

        form.fields['user_id'].initial = self.kwargs['user_id']

        return form

    def form_valid(self, form):
        result: bool = form.revoke_admin()
        user_id: str = form.cleaned_data['user_id']

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS if result else messages.ERROR,
            message=f'Admin access has been revoked for {user_id} successfully!' if result else f'Revoking admin '
                                                                                                f'rights failed.'
        )

        return super().form_valid(form=form)

    def get_success_url(self):
        return f'/users/set_admin/{self.kwargs["user_id"]}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
