from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
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
