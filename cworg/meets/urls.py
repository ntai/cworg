from django.urls import path
from django.contrib import admin

app_name = 'meets'

from .views import (
    MeetListView,
    MeetDetailView,
    MeetUpdateView,
    MeetCreateView,
    MeetDeleteView,
    AttendeeListView,
    AttendeeDetailView,
    AttendeeUpdateView,
    attendeelist_update,
)

urlpatterns = [
    path('', MeetListView.as_view(), name='meet_list'),
    path('create/', MeetCreateView.as_view(), name='meet_create'),
    path('<slug:slug>/attendees/<int:pk>/', AttendeeDetailView.as_view(), name='attendee_detail'),
    path('<slug:slug>/attendees/<int:pk>/update/', AttendeeUpdateView.as_view(), name='attendee_update'),
    path('<slug:slug>/attendees/', AttendeeListView.as_view(), name='attendee_list'),
    path('<slug:slug>/attendees/update/', attendeelist_update, name='attendee_list_update'),

    path('<slug:slug>/update/', MeetUpdateView.as_view(), name='meet_update'),
    path('<slug:slug>/delete/', MeetDeleteView.as_view(), name='meet_delete'),
    path('<slug:slug>/', MeetDetailView.as_view(), name='meet_detail'),
]
