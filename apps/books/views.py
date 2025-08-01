from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from .models import Book
from .serializers import BookSerializer


class BookListView(View):
    def get(self, request):
        try:
            # QUERY PARAMETERS
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            category_name = request.GET.get("category", None)
            search_term = request.GET.get("search", None)

            # GET ALL BOOKS
            queryset = Book.objects.all()

            # FEATURE: FILTER BY CATEGORY
            if category_name:
                queryset = queryset.filter(category__name__iexact=category_name)

            # FEATURE: SEARCH BY TITLE OR AUTHER_NAME
            if search_term:
                queryset = queryset.filter(
                    Q(author_name__icontains=search_term)
                    | Q(title__icontains=search_term)
                )

            # FEATURE: PAGINATION
            paginator = Paginator(queryset, limit)
            page_obj = paginator.get_page(page)

            books_data = [BookSerializer.serialize(book) for book in page_obj]
            response_data = {
                "data": books_data,
                "pagination": {
                    "totalPages": paginator.num_pages,
                    "totalItems": paginator.count,
                    "currentPage": page,
                    "limit": limit,
                    "hasNext": page_obj.has_next(),
                    "hasPrevious": page_obj.has_previous(),
                },
                "status": 200,
            }
            return JsonResponse(response_data, safe=False)

        except ValueError:
            return JsonResponse(
                {
                    "data": [],
                    "pagination": None,
                    "status": 400,
                    "error": "Invalid page or limit parameter",
                },
                status=400,
            )

        except Exception as e:
            return JsonResponse(
                {"data": [], "pagination": None, "status": 500, "error": str(e)},
                status=500,
            )
