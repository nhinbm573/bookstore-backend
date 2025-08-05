from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from .models import Book
from .serializers import BookSerializer


class BookPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "pagination": {
                    "totalPages": self.page.paginator.num_pages,
                    "totalItems": self.page.paginator.count,
                    "currentPage": self.page.number,
                    "limit": self.get_page_size(self.request),
                    "hasNext": self.page.has_next(),
                    "hasPrevious": self.page.has_previous(),
                },
                "status": 200,
            }
        )


class BookFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="iexact"
    )

    class Meta:
        model = Book
        fields = ["category"]


class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BookFilter
    search_fields = ["author_name", "title"]

    def _validate_pagination_params(self, request):
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")

        if page is not None:
            try:
                page_num = int(page)
                if page_num < 1:
                    return Response(
                        {
                            "data": [],
                            "pagination": None,
                            "status": 400,
                            "error": "Invalid page parameter. Page must be a positive integer.",
                        },
                        status=400,
                    )
            except ValueError:
                return Response(
                    {
                        "data": [],
                        "pagination": None,
                        "status": 400,
                        "error": "Invalid page parameter. Page must be an integer.",
                    },
                    status=400,
                )

        if limit is not None:
            try:
                limit_num = int(limit)
                if limit_num <= 0:
                    return Response(
                        {
                            "data": [],
                            "pagination": None,
                            "status": 400,
                            "error": "Invalid limit parameter. Limit must be a positive integer.",
                        },
                        status=400,
                    )
            except ValueError:
                return Response(
                    {
                        "data": [],
                        "pagination": None,
                        "status": 400,
                        "error": "Invalid limit parameter. Limit must be an integer.",
                    },
                    status=400,
                )
        return None

    def list(self, request, *args, **kwargs):
        validation_response = self._validate_pagination_params(request)
        if validation_response:
            return validation_response

        try:
            return super().list(request, *args, **kwargs)
        except NotFound as e:
            if "Invalid page" in str(e):
                return Response(
                    {
                        "data": [],
                        "pagination": None,
                        "status": 404,
                        "error": "The requested page does not exist.",
                    },
                    status=404,
                )
            raise
