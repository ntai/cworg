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
from userprofile.models import UserProfile

# CWOrg's library

from cwlog import logger
import datetime

from common.utils import get_today, get_month_range
    

class DashboardView(LoginRequiredMixin, generic.DetailView):
    '''Summery of user's activities.'''

    template_name = "dashboard/dashboard.html"

    def __init__(self, *args, **kwargs):
        super(DashboardView, self).__init__(*args, **kwargs)
        pass

    def get_object(self):
        user = self.request.user
        return UserProfile.objects.get(user=user)


    def get_object_data(self, **kwargs):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        user = self.request.user
        return UserProfile.objects.get(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user

        today = get_today()
        daterange = get_month_range()

        teams = Team.objects.filter(teammember__member=user)
        context['teams'] = teams

        meets = Meet.objects.filter(team__teammember__member=user).filter(starttime__gte=today).order_by('starttime')[:5]
        attendees = Attendee.objects.filter(meet__in=meets)

        #
        meet_headers = [ ("name", "meet", "", "Meet"),
                         ("team", "team", "", "Team"),
                         ("starttime", "datetime", "", "Date"),
        ]
        context['meet_headers'] = meet_headers
        upcoming = []

        for meet in meets:
            mrow = []
            url = "meets/{}".format( meet.slug)

            for field, col, cls, ttl in meet_headers:
                value = getattr(meet, field)
                mrow.append( (value, url) )
                url = None
                pass
            upcoming.append(mrow)
            pass
        context['meet_data'] = upcoming

        # Assemble the team list
        team_headers = [ ("name", "name", "", "Team"),
                         ("owner", "owner", "", "Owner"),
        ]
        context['team_headers'] = team_headers

        myteams = []
        for team in teams:
            mrow = []
            url = "teams/{}".format(team.slug)
            for field, col, cls, ttl in team_headers:
                value = getattr(team, field)
                mrow.append( (value, url) )
                url = None
                pass
            myteams.append(mrow)
            pass
        context['teams'] = myteams

        return context


    def has_object_permission(self, request, obj):
        # work when your access /item/item_id/
        # Instance must have an attribute named `owner`.
        return obj.user == request.user

    def has_update_permission(self, request, obj):
        return self.has_object_permission(request, obj)


    pass
