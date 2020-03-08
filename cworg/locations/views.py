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

from .models import Location
from common.views import ListModelView, DetailModelView, UpdateModelView, CreateModelView, DeleteModelView
from common.sitemodule import module_registry
from material import Layout, Row, Column, Fieldset

from userprofile.models import UserProfile
from django.db.models import Q

from cwlog import logger

from common.views.list import ModelAttr
from .apps import LocationsConfig


class LocationListView(ListModelView):
    """
    List of all locations, or create a new location.
    """
    template_name = "location/location_list.html"
    model = Location
    paginated_by = 50
    allow_empty = True

    list_display = ["name", "address", "googlemap_url", "phone", "homepage", ]

    def get_item_url(self, item):
        """Link to object detail to `list_display_links` columns."""
        return self.get_absolute_url(item, 'detail')

    def has_add_permission(self, request):
        """Object add permission check.

        If view had a `viewset`, the `viewset.has_add_permission` used.
        """
        return request.user.is_superuser or super().has_add_permission(request)

    def has_view_permission(self, request):
        return request.user.is_authenticated

    pass


class LocationDetailForm(forms.ModelForm):
    layout = Layout(Fieldset('Info',
                             Row('name', 'phone'),
                             'homepage'),
                    Fieldset('Navigation',
                             'address',
                             Row('googlemap_url', 'coordinates'),
                    ),
                    Fieldset('Note',
                             'description',
                    ),
    )

    class Meta:
        model = Location
        fields = ['name', 'address', 'coordinates', 'googlemap_url', 'phone', 'homepage', 'description']
        pass

    pass


class LocationDetailView(DetailModelView):
    """
    Retrieve, update or delete a location instance.
    """
    model = Location
    form_class = LocationDetailForm

    def has_view_permission(self, request, obj):
        return request.user.is_authenticated
    pass


class LocationUpdateView(UpdateModelView):
    """
    Retrieve, update or delete a location instance.
    """
    model = Location
    form_class = LocationDetailForm

    pass


class LocationCreateView(CreateModelView):
    model = Location
    form_class = LocationDetailForm

    pass



class LocationDeleteView(DeleteModelView):
    model = Location
    pass
