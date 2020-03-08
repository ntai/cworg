from django.db.models import Q

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)


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

from meets.models import Meet, Attendee

from .pagination import MeetLimitOffsetPagination, MeetPageNumberPagination
from .permissions import IsOwnerOrReadOnly

from .serializers import (
    MeetCreateUpdateSerializer, 
    MeetDetailSerializer, 
    MeetListSerializer,
    AttendanceActionSerializer,
    )

############################################################################

class MeetDetailAPIView(RetrieveAPIView):
    queryset = Meet.objects.all()
    serializer_class = MeetDetailSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    pass


class MeetCreateAPIView(CreateAPIView):
    """
    Create API view
    """
    queryset = Meet.objects.all()
    serializer_class = MeetCreateUpdateSerializer
    #permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        pass

    pass



class MeetUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Meet.objects.all()
    serializer_class = MeetCreateUpdateSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]
    #lookup_url_kwarg = "abc"
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        #email send_email
        pass
    pass



class MeetDeleteAPIView(DestroyAPIView):
    queryset = Meet.objects.all()
    serializer_class = MeetDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]
    #lookup_url_kwarg = "abc"
    pass


class MeetListAPIView(ListAPIView):
    serializer_class = MeetListSerializer
    filter_backends= [SearchFilter, OrderingFilter]
    permission_classes = [AllowAny]
    search_fields = ['title', 'content', 'user__first_name']
    pagination_class = MeetPageNumberPagination #PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        #queryset_list = super(MeetListAPIView, self).get_queryset(*args, **kwargs)
        queryset_list = Meet.objects.all() #filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query)|
                    Q(content__icontains=query)|
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query)
                    ).distinct()
        return queryset_list
    pass

############################################################################



class AttendanceActionAPIView(RetrieveUpdateAPIView):
    queryset = Attendee.objects.all()
    serializer_class = AttendanceActionSerializer
    lookup_field = 'token'
    permission_classes = [IsOwnerOrReadOnly]
    lookup_url_kwarg = "token"
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        #email send_email
        pass
    pass

