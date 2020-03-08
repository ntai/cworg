from django.urls import path
from django.contrib import admin

from .views import (
    UserMeetListXmlView,
    UserMeetListJsonView,
    )


from teams.models import Team, TeamMember

urlpatterns = [
    path('<int:pk>/calendar.xml', UserMeetListXmlView.as_view()),
    path('<int:pk>/calendar/<int:year>/<int:month>/', UserMeetListJsonView.as_view()),
]
