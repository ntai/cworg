from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, NoReverseMatch
from django.views import generic
import django.views.generic.detail as generic_detail
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import Team, TeamMember
from common.views import ListModelView, DetailModelView, UpdateModelView, CreateModelView, DeleteModelView
from common.sitemodule import module_registry
from material import Layout, Row, Column, Fieldset

from userprofile.models import UserProfile
from django.db.models import Q

from cwlog import logger

from common.views.list import ModelAttr
from .apps import TeamsConfig

class RelatedAttr(ModelAttr):
    def __init__(self, model, name, callback, label=None):  # noqa D102
        super().__init__(model, name, label=label)
        self.callback = callback
        pass

    def get_value(self, obj):  # noqa D102
        return self.callback(self, obj)

    def get_formatted_string(self, obj):  # noqa D102
        return self.callback(self, obj)

    pass

class TeamListView(ListModelView):
    """
    List of all teams, or create a new team.
    """
    template_name = "team/team_list.html"
    model = Team
    paginated_by = 100
    allow_empty = True

    list_display = ["name", "owner", "description", "joined"]

    def __init__(self, *args, **kwargs):
        super(TeamListView, self).__init__(*args, **kwargs)
        pass
    
    def get_context_data(self, **kwargs):
        """Additional context data for team list view.

        :keyword add_url: Link to the add view
        :keyword join_url: Link to the team member create view (aka joining a team)
        """

        context = super(TeamListView, self).get_context_data(**kwargs)
        # opts = self.object_list.model._meta
        join_name = self.get_named_url('join')
        try:
            context['join_url'] = reverse(join_name)
            pass
        except NoReverseMatch:
            logger.debug("TeamListView::get_context_data join_url '{}' doesn't have reverse.".format(join_name))
            pass
        return context


    def get_item_url(self, item):
        """Link to object detail to `list_display_links` columns."""
        return self.get_absolute_url(item, 'detail')

    
    def get_headers_data(self):
        """Readable column titles."""
        for field_name in self.get_list_display():
            if field_name in ["joined"]:
                yield field_name, field_name
                continue
            attr = self.get_data_attr(field_name)
            yield field_name, attr.label
            pass
        pass
    
    def get_data_attr(self, attr_name):
        if attr_name != "joined":
            return super().get_data_attr(attr_name)
        user = self.request.user
        return RelatedAttr(self.object_list.model, attr_name, lambda attr, team: TeamMember.objects.filter(team__id=team.id, member__id=user.id).count()>0)

    def has_view_permission(self, request):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        """Object add permission check.

        If view had a `viewset`, the `viewset.has_add_permission` used.
        """
        return request.user.is_superuser or super().has_add_permission(request)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Team.objects.all()
        else:
            teams=TeamMember.objects.filter(member=user).values('team')
            queryset = Team.objects.filter(id__in=teams)
            pass
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
                pass
            queryset = queryset.order_by(*ordering)
            pass
        return queryset
    pass


class TeamDetailForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'join_password', 'description', 'owner']
        pass


class TeamDetailView(DetailModelView):
    """
    Retrieve, update or delete a team instance.
    """
    template_name = "team/team_detail.html"
    model = Team
    form_class = TeamDetailForm

    layout = Layout('name',
                    Row('owner', 'join_password'),
                    'description',
    )

    def get_object_data(self, **kwargs):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        #logger.debug(self.object._meta.fields)
        return super(TeamDetailView, self).get_object_data()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['members_header'] = [('object', 'member') ]
        context['member_display_links'] = ['name']
        context['members'] = TeamMember.objects.filter(team=self.object)

        return context

    def has_view_permission(self, request, obj):
        return request.user.is_authenticated
    pass


class TeamUpdateView(UpdateModelView):
    """
    Retrieve, update or delete a team instance.
    """
    #template_name = "teams/team_detail_form.html"
    model = Team
    form_class = TeamDetailForm

    layout = Layout(Row('name', 'join_password', 'owner',),
                    'description',
    )

    def get_object_data(self, **kwargs):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        #logger.debug(self.object._meta.fields)
        return super(TeamUpdateView, self).get_object_data()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    pass


class TeamCreateView(CreateModelView):

    model = Team
    form_class = TeamDetailForm

    layout = Layout('name',
                    Row('owner', 'join_password'),
                    'description',
    )

    pass



class TeamDeleteView(DeleteModelView):
    model = Team
    pass



class TeamMemberListView(ListModelView):
    """
    List of members on a team
    """
    model = TeamMember
    allow_empty = True
    list_display = ["member"]
    template_name = 'team/member_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_slug = self.kwargs.get('slug')
        team = get_object_or_404(Team, slug=team_slug)
        if team:
            context['team'] = team
            pass
        return context

    def get_queryset(self):
        """
        Get the team members of team.
        """
        team_slug = self.kwargs.get('slug')
        team = get_object_or_404(Team, slug=team_slug)
        queryset = super().get_queryset()
        return queryset.filter(team=team)

    def has_view_permission(self, request):
        return request.user.is_authenticated
    pass



class TeamMemberDetailForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['team', 'rating', 'rating', 'played', 'wins', 'losses']
        pass

    pass


class TeamMemberDetailView(DetailModelView):
    model = TeamMember
    form_class = TeamMemberDetailForm
    template_name = 'team/member_detail.html'

    layout = Layout(Row('team'),
                    Row('rating'),
                    Row('played', 'wins', 'losses')
    )

    def has_view_permission(self, request, obj):
        return request.user.is_staff or obj.member == request.user
    pass

class TeamMemberCreateForm(forms.ModelForm):
    password = forms.CharField(max_length=100, help_text="Team's join password")
    class Meta:
        model = TeamMember
        fields = ['team', 'rating', 'password']
        pass

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        my_teams = TeamMember.objects.filter(member=self.user).values('team')
        self.fields['team'].queryset = Team.objects.filter(~Q(id__in=my_teams))
        pass

    
    def clean(self):
        cleaned_date = super().clean()
        join_password = cleaned_date.get('password')
        team = cleaned_date.get('team')

        if team.join_password != join_password:
            raise forms.ValidationError('Password to join the team is incorrect')
        pass

    def save(self):
        self.instance.member = self.user
        return super().save()

    pass


class TeamMemberCreateView(CreateModelView):
    model = TeamMember
    form_class = TeamMemberCreateForm
    template_name = 'team/member_join.html'

    layout = Layout(Row('team'),
                    Row('password'),
                    Row('rating'),
    )

    def get_form_kwargs(self, **kwargs):
        '''pass current user to form'''
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def has_add_permission(self, request):
        """Anyone can join a team as long as you know the password.
        """
        return True

    def get_success_url(self):
        '''When a team registration is done, go back to the list of teams.'''
        team_model = Team
        opts = team_model._meta
        module = module_registry.get_module(opts.app_label)
        return reverse(module.get_named_url(opts.model_name, 'list'))
    pass

