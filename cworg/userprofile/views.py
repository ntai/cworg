from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django import forms
from django.template import Template
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.utils.datastructures import MultiValueDict
from django.urls import reverse

from django.views.generic.edit import FormMixin, ModelFormMixin

from meets.models import Meet, Attendee, Assignment
from teams.models import Team, TeamMember
from .models import UserProfile

# CWOrg's library

from common.views import ListModelView, DetailModelView, UpdateModelView
from material import Layout, Row, Column, Fieldset

from cwlog import logger
from .forms import UserLoginForm, UserRegisterForm

import datetime

from common.utils import get_today, get_month_range
    

def redirect_to_current_user(request):
    if request.user.is_authenticated:
        # Generally, user profile and Django user record's primary keys are 1-to-1,
        # but in rare occasion, that's not the case. So, do the right thing.
        userprofile = UserProfile.objects.get(user_id=request.user.id)
        to = '/users/{}/'.format(userprofile.id)
    else:
        to = redirect('/login')
        pass
    return redirect(to)


class UserDetailForm(forms.ModelForm):
    # user = forms.CharField(label='User name')

    class Meta:
        model = UserProfile
        fields = ['user', 'image', 'sms', 'phone', 'fullname']
        pass
    pass



class UserProfileView(LoginRequiredMixin, UpdateModelView):
    '''Summery of user's activities.'''

    model = UserProfile
    form = UserDetailForm

    layout = Layout( Fieldset('User',
                              Row('user', 'image'),
                              Row('fullname'),),
                     Fieldset('Contacts',
                              Row('sms', 'phone')))

    def __init__(self, *args, **kwargs):
        super(UserProfileView, self).__init__(*args, **kwargs)
        pass

    def get_object_data(self, **kwargs):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        logger.debug("UserProfile {}".format(self.object))
        return super().get_object_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        context['user'] = user
        logger.debug("Profile {}, User {}".format(self.object, user))
        return context

    def get_success_url(self):
        """Redirect back to the detail view."""
        opts = self.model._meta
        return reverse('{}:user_detail'.format(opts.app_label), args=[self.object.pk])

    def has_object_permission(self, request, obj):
        # work when your access /item/item_id/
        # Instance must have an attribute named `owner`.
        return obj.user == request.user

    def has_update_permission(self, request, obj):
        return self.has_object_permission(request, obj)
    pass


from .forms import UserLoginForm, UserRegisterForm

def login_view(request):
    next = request.GET.get('next')
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        auth.login(request, user)
        if next:
            return redirect(next)
        return redirect("/")
    context = {
        "form": form,
        "title": title,
    }
    return render(request, "accounts/form.html", context)


def register_view(request):
    next = request.GET.get('next')
    title = "Register"
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = auth.authenticate(username=user.username, password=password)
        auth.login(request, new_user)
        if next:
            return redirect(next)
        return redirect("/")

    context = {
        "form": form,
        "title": title,
    }
    return render(request, "accounts/form.html", context)


def logout_view(request):
    auth.logout(request)
    return redirect("/")

############################################################################

class PasswordResetView(auth.views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'

# FIXME - templates
class PasswordResetDoneView(auth.views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class PasswordResetConfirmView(auth.views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'

class PasswordResetCompleteView(auth.views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

class PasswordChangeView(auth.views.PasswordChangeView):
    template_name = 'registration/password_change_form.html'

class PasswordChangeDoneView(auth.views.PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'
    
    
