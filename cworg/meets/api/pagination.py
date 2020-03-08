from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
    )

class MeetLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10
    pass


class MeetPageNumberPagination(PageNumberPagination):
    page_size = 20
    pass

