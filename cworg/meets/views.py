from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django import forms
from django.utils import timezone
from django.db.models import Q

# From rest 
from rest_framework import viewsets
from rest_framework import status as reststatus
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions

from django.utils.translation import ugettext_lazy as _

# CWOrg's library
from cwlog import logger

# User profile
from userprofile.models import UserProfile
from django.contrib.auth.models import User

from teams.models import Team, TeamMember

# CWOrg's library
from .models import Meet, Attendee, Assignment

from common.views import ListModelView, DetailModelView, UpdateModelView, CreateModelView, DeleteModelView
from common.utils import get_today
from common.sitemodule import module_registry

from material import Layout, Row, Column, Fieldset


class MeetListView(ListModelView):
    """
    List of all meets, or create a new meet.
    """
    template = "meets/meet_list.html"
    model = Meet
    paginated_by = 100
    allow_empty = True

    list_display = ["name", "team", "starttime", "location", "manager"]
    list_display_links = ["name", "starttime"]

    _team_module = module_registry.get_module("teams")
    _location_module = module_registry.get_module("locations")
    _userprof_module = module_registry.get_module("userprofile")

    def __init__(self, *args, **kwargs):
        super(MeetListView, self).__init__(*args, **kwargs)
        self.selfadd_url = reverse('{}:{}_create'.format(self.model._meta.app_label, self.model._meta.model_name))
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_item_url(self, item):
        """Link to object detail to `list_display_links` columns."""
        opts = self.model._meta
        return reverse(
            '{}:{}_detail'.format(opts.app_label, opts.model_name),
            args=[item.slug])


    def has_view_permission(self, request):
        return request.user.is_authenticated


    def has_add_permission(self, request):
        """Object add permission check.

        If view had a `viewset`, the `viewset.has_add_permission` used.
        """
        # If I'm an owner of team, I can add a meet.
        user=request.user
        return user.is_superuser or super().has_add_permission(request) or Team.objects.filter(owner=user).count() > 0


    def get_field_url(self, item, field_name, value):
        '''Override this to generate a link for field value'''
        field_verb = 'update' if self.request.user.is_superuser else 'detail'
        if field_name == "team" and item.team:
            return self._team_module.get_absolute_url(item.team, 'team', field_verb)
        elif field_name == "location" and item.location:
            return self._location_module.get_absolute_url(item.location, 'location', field_verb)
        elif field_name == "manager" and item.manager:
            manager = UserProfile.objects.get(user=item.manager)
            if manager:
                return self._userprof_module.get_absolute_url(manager, 'user', 'detail')
            pass

        return None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return Meet.objects.filter(team__teammember__member=self.request.user)

    pass


class MeetDetailForm(forms.ModelForm):

    class Meta:
        model = Meet
        fields = ['name', 'team', 'group', 'starttime', 'duration', 'location', 'manager', 'min_attendees', 'max_attendees']
        pass

    pass


class MeetDetailView(DetailModelView):
    """
    Retrieve, update or delete a meet instance.
    """
    template_name = "meets/meet_detail_form.html"
    model = Meet
    form_class = MeetDetailForm

    layout = Layout('name',
                    Row('team', 'group'),
                    Row('starttime', 'duration', 'location'),
                    Fieldset('Attendees',
                             Row('manager'),
                             Row('min_attendees', 'max_attendees')))

    def get_object_data(self, **kwargs):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        #logger.debug(self.object._meta.fields)
        return super().get_object_data()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendees_header'] = [('object', 'player'), ('attendance', 'attendance'), ('substitute', 'substitute') ]
        context['attendee_display_links'] = ['name']
        context['attendees'] = Attendee.objects.filter(meet__id=self.object.pk)
        context['manage_attendees'] = self.request.user.is_superuser or  self.object.manager == self.request.user
        return context

    def has_object_permission(self, request, obj):
        # work when your access /item/item_id/
        # Instance must have an attribute named `owner`.
        perm = obj.manager == request.user or obj.team.owner == request.user 
        return perm

    def has_update_permission(self, request, obj):
        return self.has_object_permission(request, obj)

    def has_delete_permission(self, request, obj):
        return self.has_object_permission(request, obj)

    def has_view_permission(self, request, obj):
        return TeamMember.objects.filter(team=obj.team).filter(member=self.request.user).count() > 0

    pass


class MeetUpdateView(UpdateModelView):
    """
    Retrieve, update or delete a meet instance.
    """
    template_name = "meets/meet_update_form.html"
    model = Meet
    form_class = MeetDetailForm

    layout = Layout('name',
                    Row('team', 'group'),
                    Row('starttime', 'duration', 'location'),
                    Fieldset('Attendees',
                             Row('manager'),
                             Row('min_attendees', 'max_attendees')))

    def get_object_data(self, **kwargs):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        #logger.debug(self.object._meta.fields)
        return super().get_object_data()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendees_header'] = [('object', 'player'), ('attendance', 'attendance'), ('substitute', 'substitute') ]
        context['attendee_display_links'] = ['name']
        return context

    pass


class MeetCreateForm(forms.ModelForm):

    name = forms.CharField(label='Meet name')
    team = forms.ModelChoiceField(queryset=Team.objects.all(), label=_('Team'))
    template_name = "meets/meet_create.html"

    def __init__(self, *args, **kwargs):
        #logger.debug("MeetCreateForm \nargs {}\nkwargs {}".format(args, kwargs))
        user = kwargs.pop('current_user')
        super().__init__(*args, **kwargs)
        if user.is_superuser:
            self.fields['team'].queryset = Team.objects.all()
            self.fields['team'].initial = Team.objects.all().first()
        else:
            self.fields['team'].queryset = Team.objects.filter(owner=user)
            self.fields['team'].initial = Team.objects.filter(owner=user).first()
            pass
        t0 = timezone.datetime.now()
        starttime = timezone.datetime(t0.year, t0.month, t0.day, t0.hour) + timezone.timedelta(0, 24 * 3600)
        self.fields['starttime'].initial = starttime
        if self.fields['team'].initial:
            self.fields['manager'].initial =  self.fields['team'].initial.owner
            pass
        pass


    class Meta:
        model = Meet
        exclude = ['slug']
        pass

    layout = Layout('name',
                    Row('team', 'group'),
                    Row('starttime', 'duration', 'location'),
                    Fieldset('Attendees',
                             Row('manager', 'min_attendees', 'max_attendees')))

    pass


class MeetCreateView(CreateModelView):

    model = Meet
    form_class = MeetCreateForm


    def get_success_url(self):
        return self.get_absolute_url(self.object, "detail")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def has_add_permission(self, request):
        if request.user.is_superuser or super().has_add_permission(request):
            return True
        # This way, I may be able to avoid a query
        user=request.user
        return Team.objects.filter(owner=user).count() > 0

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    pass



class MeetDeleteView(DeleteModelView):

    model = Meet

    def get_success_url(self):
        """Redirect back to the detail view if no `success_url` is configured."""
        opts = self.model._meta
        return reverse('{}:list'.format(opts.app_label))

    pass


class AttendeeListView(ListModelView):
    """
    List of attendees for the meet.
    """
    model = Attendee
    allow_empty = True
    # template_name = "meets/attendee_list.html"
    list_display = ["player", "attendance", "substitute"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meet_slug = self.kwargs.get('slug')
        meet = get_object_or_404(Meet, slug=meet_slug)
        if meet:
            context['meet'] = meet
            pass
        return context

    def get_queryset(self):
        """
        Get the attendees for the meet.
        """
        meet_slug = self.kwargs.get('slug')
        get_object_or_404(Meet, slug=meet_slug)
        queryset = super().get_queryset()
        return queryset.filter(meet__slug=meet_slug)

    def get_item_url(self, item):
        """Link to object detail to `list_display_links` columns."""
        opts = self.model._meta
        if self.request.user.is_staff or item.player==self.request.user:
            return reverse('{}:{}_update'.format(opts.app_label, opts.model_name),
                           args=[item.meet.slug, item.pk])
        else:
            return reverse('{}:{}_detail'.format(opts.app_label, opts.model_name),
                           args=[item.meet.slug, item.pk])


    def has_view_permission(self, request):
        meet_slug = self.kwargs.get('slug')
        meet = get_object_or_404(Meet, slug=meet_slug)
        return Team.objects.filter(id=meet.team.id, teammember__member=request.user).count() > 0


    pass


class AttendeeForm(forms.ModelForm):
    player = forms.ModelChoiceField(queryset=User.objects.all(), label=_('Player'))
    attendance = forms.ChoiceField(label=_('Attendance'))
    substitute = forms.ModelChoiceField(queryset=User.objects.all(), label=_('Substitute'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        meet = self.instance.meet
        team = meet.team
        members = TeamMember.objects.filter(team=team)
        self.fields['player'].queryset = User.objects.filter(id__in=members)
        self.fields['player'].initial = self.instance.player
        if self.instance.player:
            self.fields['substitute'].queryset = User.objects.filter(id__in=members).filter(~Q(id=self.instance.player.id))
        else:
            self.fields['substitute'].queryset = User.objects.none()
            pass
        self.fields['substitute'].initial = self.instance.substitute
        self.fields['attendance'].initial = self.instance.attendance
        pass

    class Meta:
        model = Attendee
        fields = ['player', 'attendance', 'substitute']
        pass

    layout = Layout(Row('player', 'attendance', 'substitute'),)
    pass


class AttendeeUpdateFormSet(forms.BaseFormSet):
    def clean(self):
        """ check that there is no player dupes """
        if any(self.errors):
            return
        players = {}
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            player = form.cleaned_data.get("player")
            if player in players:
                raise forms.ValidationError("duped players.")
            palyers[players] = True
            pass
        pass
    
                                            
    class Meta:
        model = Attendee
        fields = ['player', 'attendance', 'substitute']
        pass
    pass


def attendeelist_update(request, slug=None):
    """
    Update list of attendees for the meet.
    """
    AttendeeFormSet = forms.modelformset_factory(Attendee, form=AttendeeForm, extra=0, exclude=["meet"])
    # formset=AttendeeUpdateFormSet,

    if request.method == 'POST':
        formset = AttendeeFormSet(request.POST)
        if formset.is_valid():
            # do something with the formset.cleaned_data
            pass
        pass
    else:
        meet = get_object_or_404(Meet, slug=slug)
        formset = AttendeeFormSet(queryset=Attendee.objects.filter(meet=meet))
        pass
    return render(request, 'meets/update_attendees.html', {'attendee_formset': formset})



class AttendeePermissonMixin:
    
    def has_object_permission(self, request, obj):
        # work when your access /item/item_id/
        # Instance must have an attribute named `owner`.
        return obj.player == request.user or obj.meet.manager == request.user or request.user == obj.meet.team.owner

    def has_update_permission(self, request, obj):
        if obj.player == request.user:
            return True
        if obj.meet and obj.meet.manager == request.user:
            return True
        if obj.meet and obj.meet.team and obj.meet.team.owner == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj):
        return obj.meet.manager == request.user or request.user == obj.meet.team.owner

    def has_view_permission(self, request, obj):
        return TeamMember.objects.filter(team=obj.meet.team).filter(member=self.request.user).count() > 0


    pass


class AttendeeDetailView(AttendeePermissonMixin, DetailModelView):
    """
    Retrieve, update or delete a meet instance.
    """
    #template_name = "meets/attendee_detail.html"
    model = Attendee
    #form_class = AttendeeDetailForm
    fields = ['meet', 'player', 'attendance', 'substitute']

    def get_context_data(self, **kwargs):
        attendee = super().get_object()
        context = super().get_context_data(**kwargs)
        context['meet'] = attendee.meet
        return context

    def get_success_url(self):
        """Redirect back to the detail view if no `success_url` is configured."""
        return reverse(self.get_named_url('detail'), args=[self.object.meet.slug, self.object.pk])

    pass


class AttendeeDetailForm(forms.ModelForm):
    layout = Layout('meet', 'player', 'attendance', 'substitute')
    class Meta:
        model = Attendee
        fields = ['meet', 'player', 'attendance', 'substitute']
        pass
    pass


class AttendeeUpdateView(AttendeePermissonMixin, UpdateModelView):
    """
    Retrieve, update or delete a meet instance.
    """
    template_name = "meets/attendee_update.html"
    model = Attendee
    form_class = AttendeeDetailForm

    layout = Layout('meet', 'player', 'attendance', 'substitute')

    def get_context_data(self, **kwargs):
        attendee = super().get_object()
        context = super().get_context_data(**kwargs)
        context['meet'] = attendee.meet
        return context

    def get_success_url(self):
        """Redirect back to the detail view if no `success_url` is configured."""
        return reverse(self.get_named_url('list'), args=[self.object.meet.slug])


    pass
