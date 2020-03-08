from django.conf.urls import url
from django.urls import path
from django.contrib import admin

app_name = 'teams'

from .views import (
    TeamCreateView,
    TeamDeleteView,
    TeamDetailView,
    TeamListView,
    TeamUpdateView,

    TeamMemberCreateView,
    TeamMemberDetailView,
    TeamMemberListView,
)

urlpatterns = [
    path('', TeamListView.as_view(), name='team_list'),
    path('create/', TeamCreateView.as_view(), name='team_create'),
    path('join/', TeamMemberCreateView.as_view(), name='team_join'),

    path('<slug:slug>/', TeamDetailView.as_view(), name='team_detail'),
    path('<slug:slug>/update/', TeamUpdateView.as_view(), name='team_update'),
    path('<slug:slug>/delete/', TeamDeleteView.as_view(), name='team_delete'),

    path('<slug:slug>/members/', TeamMemberListView.as_view(), name='member_list'),
    path('<slug:slug>/members/<int:pk>', TeamMemberDetailView.as_view(), name='member_detail'),
]

