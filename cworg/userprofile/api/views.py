import datetime
from django.db.models import Q
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
    )

from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView, 
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

    )

from common.xml_renderer import XMLRenderer
User = get_user_model()

from common.utils import get_today, get_month_range
from teams.models import Team, TeamMember
from meets.models import Meet, Attendee, Assignment


from .serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    )

from ..models import UserProfile


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]




class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            return Response(new_data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class MonthlyXMLRenderer(XMLRenderer):
    root_tag_name = 'monthly'
    pass

class UserMeetListXmlView(APIView):
    renderer_classes = (MonthlyXMLRenderer,)

    def get(self, request, pk=None, format=None):
        if pk:
            user = User.objects.get(pk=pk)
        else:
            user = request.user
            pass
        my_teams = TeamMember.objects.filter(member=user).values('team')
        teams = Team.objects.filter(id__in=my_teams)
        months = get_month_range()
        meets = Meet.objects.filter(team__in=teams).filter(starttime__gte=months[0]).filter(starttime__lt=months[1]).order_by("starttime")

        content = []
        for meet in meets:
            content.append({ "event":
                             { "id": meet.id,
                               "name": meet.name,
                               "startdate": meet.starttime,
                               "enddate": meet.starttime + meet.duration,
                               "color": "tomato",
                               "url": "meets/{}".format(meet.slug)
                             }})
            pass

        return Response(content)
    pass


class UserMeetListJsonView(APIView):
    def get(self, request, pk=None, year=None, month=None, format=None):
        if pk:
            user = User.objects.get(pk=pk)
        else:
            user = request.user
            pass

        my_teams = TeamMember.objects.filter(member=user).values('team')
        teams = Team.objects.filter(id__in=my_teams)
        months = get_month_range(datetime.datetime(year, month, 1))
        meets = Meet.objects.filter(team__in=teams).filter(starttime__gte=months[0]).filter(starttime__lt=months[1]).order_by("starttime")

        events = []
        for meet in meets:
            events.append( { "id": meet.id,
                              "name": meet.name,
                              "date": meet.starttime,
                              "type": "meet",
                              "startdate": meet.starttime,
                              "enddate": meet.starttime + meet.duration,
                              "color": "tomato",
                              "url": "meets/{}".format(meet.slug),
            }
            )
            pass

        return Response({"monthly": events})
    pass
