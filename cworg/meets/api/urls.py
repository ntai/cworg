from django.urls import path
from django.contrib import admin

from .views import (
    MeetCreateAPIView,
    MeetDeleteAPIView,
    MeetDetailAPIView,
    MeetListAPIView,
    MeetUpdateAPIView,
    AttendanceActionAPIView,
    )

urlpatterns = [
    path('', MeetListAPIView.as_view(), name='meet_api_list'),
    path('create/', MeetCreateAPIView.as_view(), name='meet_api_create'),
    path('<slug:slug>/', MeetDetailAPIView.as_view(), name='meet_api_detail'),
    path('<slug:slug>/update/', MeetUpdateAPIView.as_view(), name='meet_api_update'),
    path('<slug:slug>/delete/', MeetDeleteAPIView.as_view(), name='meet_api_delete'),

    path('attendance/<str:token>/update', AttendanceActionAPIView.as_view()),
]
