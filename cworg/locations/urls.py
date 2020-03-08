from django.conf.urls import url
from django.urls import path
from django.contrib import admin

app_name = 'locations'

from .views import (
    LocationCreateView,
    LocationDeleteView,
    LocationDetailView,
    LocationListView,
    LocationUpdateView,
)

urlpatterns = [
    path('', LocationListView.as_view(), name='location_list'),
    path('create/', LocationCreateView.as_view(), name='location_create'),

    path('<slug:slug>/', LocationDetailView.as_view(), name='location_detail'),
    path('<slug:slug>/update/', LocationUpdateView.as_view(), name='location_update'),
    path('<slug:slug>/delete/', LocationDeleteView.as_view(), name='location_delete'),

]

