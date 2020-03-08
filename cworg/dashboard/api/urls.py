from django.urls import path
from django.contrib import admin

from .views import (
    DashboardMeetListXmlView,
    DashboardMeetListJsonView,
    )


from teams.models import Team, TeamMember

urlpatterns = [
    path('<int:pk>/calendar.xml', DashboardMeetListXmlView.as_view()),
    path('<int:pk>/calendar/<int:year>/<int:month>/', DashboardMeetListJsonView.as_view()),
]
