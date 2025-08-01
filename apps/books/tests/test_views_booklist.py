import pytest
import json
from django.test import RequestFactory
from django.test.utils import override_settings
from apps.books.views import BookListView
from apps.books.models import Book


@pytest.mark.unit
def test_get_empty_book_list(db):
    """Returns empty list when no books exist"""
    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    if response.status_code == 500:
        print(f"Error: {data.get('error', 'No error message')}")

    assert response.status_code == 200
    assert data["data"] == []
    assert data["pagination"]["totalItems"] == 0
    assert data["status"] == 200


@pytest.mark.unit
def test_get_book_list_default_pagination(book_factory, category_factory):
    """Uses default pagination values"""
    category = category_factory()
    [book_factory.create(category=category) for _ in range(15)]

    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 10
    assert data["pagination"]["currentPage"] == 1
    assert data["pagination"]["limit"] == 10
    assert data["pagination"]["totalItems"] == 15


@pytest.mark.unit
def test_get_book_list_with_multiple_books(book_factory, category_factory):
    """Returns paginated books correctly"""
    category = category_factory()
    [book_factory.create(title=f"Book {i}", category=category) for i in range(15)]

    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 10
    assert data["pagination"]["totalPages"] == 2
    assert data["pagination"]["totalItems"] == 15
    assert data["pagination"]["hasNext"] is True
    assert data["pagination"]["hasPrevious"] is False


@pytest.mark.unit
def test_custom_page_and_limit(book_factory, category_factory):
    """Respects custom page and limit params"""
    category = category_factory()
    [book_factory.create(category=category) for _ in range(20)]

    factory = RequestFactory()
    request = factory.get("/books/?page=2&limit=5")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 5
    assert data["pagination"]["currentPage"] == 2
    assert data["pagination"]["limit"] == 5
    assert data["pagination"]["totalPages"] == 4


@pytest.mark.unit
def test_invalid_page_parameter(db):
    """Handles non-integer page gracefully"""
    factory = RequestFactory()
    request = factory.get("/books/?page=abc")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 400
    assert data["status"] == 400
    assert data["error"] == "Invalid page or limit parameter"
    assert data["data"] == []
    assert data["pagination"] is None


@pytest.mark.unit
def test_invalid_limit_parameter():
    """Handles non-integer limit gracefully"""
    factory = RequestFactory()
    request = factory.get("/books/?limit=xyz")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 400
    assert data["status"] == 400
    assert data["error"] == "Invalid page or limit parameter"


@pytest.mark.unit
def test_negative_page_number(book_factory):
    """Handles negative page numbers"""
    book_factory.create()

    factory = RequestFactory()
    request = factory.get("/books/?page=-1")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert data["pagination"]["currentPage"] == -1
    assert len(data["data"]) >= 0


@pytest.mark.unit
def test_page_exceeds_total_pages(book_factory, category_factory):
    """Handles out-of-range pages"""
    category = category_factory()
    [book_factory.create(category=category) for _ in range(5)]

    factory = RequestFactory()
    request = factory.get("/books/?page=999&limit=10")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 5


@pytest.mark.unit
def test_zero_or_negative_limit(book_factory, category_factory):
    """Handles invalid limit values"""
    category = category_factory()
    book_factory.create(category=category)

    factory = RequestFactory()
    request = factory.get("/books/?limit=0")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 500
    assert data["status"] == 500


@pytest.mark.unit
def test_filter_by_category_name(book_factory, category_factory):
    """Filters books by category name"""
    fiction = category_factory.create(name="Fiction")
    science = category_factory.create(name="Science")

    [book_factory.create(category=fiction) for _ in range(3)]
    [book_factory.create(category=science) for _ in range(2)]

    factory = RequestFactory()
    request = factory.get("/books/?category=Fiction")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 3
    assert data["pagination"]["totalItems"] == 3


@pytest.mark.unit
def test_filter_by_category_case_insensitive(book_factory, category_factory):
    """Category filter is case-insensitive"""
    fiction = category_factory.create(name="Fiction")
    [book_factory.create(category=fiction) for _ in range(3)]

    factory = RequestFactory()

    request1 = factory.get("/books/?category=fiction")
    response1 = BookListView().get(request1)
    data1 = json.loads(response1.content)

    request2 = factory.get("/books/?category=FICTION")
    response2 = BookListView().get(request2)
    data2 = json.loads(response2.content)

    assert len(data1["data"]) == len(data2["data"]) == 3
    assert data1["pagination"]["totalItems"] == data2["pagination"]["totalItems"] == 3


@pytest.mark.unit
def test_filter_by_nonexistent_category(db):
    """Handles filtering by non-existent category"""
    factory = RequestFactory()
    request = factory.get("/books/?category=InvalidCategory")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert data["data"] == []
    assert data["pagination"]["totalItems"] == 0


@pytest.mark.unit
def test_search_by_author_name(book_factory, category_factory):
    """Searches by author name"""
    category = category_factory()

    book_factory.create(author_name="John Smith", category=category)
    book_factory.create(author_name="Jane Smith", category=category)
    book_factory.create(author_name="Bob Johnson", category=category)

    factory = RequestFactory()
    request = factory.get("/books/?search=Smith")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 2
    assert all("Smith" in book["authorName"] for book in data["data"])


@pytest.mark.unit
def test_search_by_title(book_factory, category_factory):
    """Searches by book title"""
    category = category_factory()

    book_factory.create(title="Python Programming", category=category)
    book_factory.create(title="Learning Python", category=category)
    book_factory.create(title="Java Basics", category=category)

    factory = RequestFactory()
    request = factory.get("/books/?search=Python")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 2
    assert all("Python" in book["title"] for book in data["data"])


@pytest.mark.unit
def test_search_case_insensitive(book_factory, category_factory):
    """Search is case-insensitive"""
    category = category_factory()

    book_factory.create(title="Python Programming", category=category)
    book_factory.create(author_name="Python Expert", category=category)

    factory = RequestFactory()

    request1 = factory.get("/books/?search=python")
    data1 = json.loads(BookListView().get(request1).content)

    request2 = factory.get("/books/?search=PYTHON")
    data2 = json.loads(BookListView().get(request2).content)

    assert len(data1["data"]) == len(data2["data"]) == 2


@pytest.mark.unit
def test_search_partial_match(book_factory, category_factory):
    """Search supports partial matches"""
    category = category_factory()

    book_factory.create(title="Python Programming", category=category)
    book_factory.create(title="Complete Python Guide", category=category)

    factory = RequestFactory()
    request = factory.get("/books/?search=Pyth")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 2


@pytest.mark.unit
def test_search_matches_either_field(book_factory, category_factory):
    """Search matches author OR title"""
    category = category_factory()

    book_factory.create(title="Django Book", author_name="John Doe", category=category)
    book_factory.create(
        title="Flask Guide", author_name="Django Expert", category=category
    )
    book_factory.create(
        title="Ruby Rails", author_name="Other Author", category=category
    )

    factory = RequestFactory()
    request = factory.get("/books/?search=Django")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 2  # Matches both title and author


@pytest.mark.unit
def test_category_filter_with_pagination(book_factory, category_factory):
    """Combines category filter with pagination"""
    fiction = category_factory.create(name="Fiction")

    [book_factory.create(category=fiction) for _ in range(12)]

    factory = RequestFactory()
    request = factory.get("/books/?category=Fiction&page=2&limit=5")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 5
    assert data["pagination"]["currentPage"] == 2
    assert data["pagination"]["totalItems"] == 12
    assert data["pagination"]["totalPages"] == 3


@pytest.mark.unit
def test_search_with_pagination(book_factory, category_factory):
    """Combines search with pagination"""
    category = category_factory()

    for i in range(15):
        book_factory.create(title=f"Python Book {i}", category=category)

    factory = RequestFactory()
    request = factory.get("/books/?search=Python&page=2&limit=10")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 5
    assert data["pagination"]["currentPage"] == 2
    assert data["pagination"]["totalItems"] == 15


@pytest.mark.unit
def test_category_and_search_together(book_factory, category_factory):
    """Combines category filter and search"""
    fiction = category_factory.create(name="Fiction")
    science = category_factory.create(name="Science")

    book_factory.create(title="Python Fiction", category=fiction, author_name="Smith")
    book_factory.create(title="Java Fiction", category=fiction, author_name="Smith")
    book_factory.create(title="Python Science", category=science, author_name="Smith")

    factory = RequestFactory()
    request = factory.get("/books/?category=Fiction&search=Smith")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 2


@pytest.mark.unit
def test_response_structure(db):
    """Verifies correct JSON structure"""
    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert "data" in data
    assert isinstance(data["data"], list)
    assert "pagination" in data
    assert isinstance(data["pagination"], dict)
    assert "status" in data
    assert isinstance(data["status"], int)


@pytest.mark.unit
def test_pagination_metadata_complete(book_factory, category_factory):
    """All pagination fields present"""
    category = category_factory()
    book_factory.create(category=category)

    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    pagination = data["pagination"]
    assert "totalPages" in pagination
    assert "totalItems" in pagination
    assert "currentPage" in pagination
    assert "limit" in pagination
    assert "hasNext" in pagination
    assert "hasPrevious" in pagination


@pytest.mark.unit
def test_book_fields_camel_case(book_factory):
    """Book fields use camelCase"""
    book_factory.create(title="Test Book", author_name="Test Author", unit_price=29.99)

    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    book_data = data["data"][0]
    assert "authorName" in book_data
    assert "unitPrice" in book_data
    assert "author_name" not in book_data
    assert "unit_price" not in book_data


@pytest.mark.unit
def test_http_status_matches_response_status(db):
    """HTTP status matches response status field"""
    factory = RequestFactory()

    request1 = factory.get("/books/")
    response1 = BookListView().get(request1)
    data1 = json.loads(response1.content)
    assert response1.status_code == 200
    assert data1["status"] == 200

    request2 = factory.get("/books/?page=invalid")
    response2 = BookListView().get(request2)
    data2 = json.loads(response2.content)
    assert response2.status_code == 400
    assert data2["status"] == 400


@pytest.mark.unit
@pytest.mark.django_db
def test_no_n_plus_one_queries(
    book_factory, category_factory, django_assert_num_queries
):
    """Avoids N+1 query problems"""
    category = category_factory.create()
    [book_factory.create(category=category) for _ in range(10)]

    factory = RequestFactory()
    request = factory.get("/books/")
    view = BookListView()

    with django_assert_num_queries(2):
        response = view.get(request)
        data = json.loads(response.content)
        _ = data["data"]


@pytest.mark.unit
@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_large_dataset_pagination(book_factory, category_factory):
    """Handles large datasets efficiently"""
    category = category_factory.create()

    Book.objects.bulk_create(
        [
            Book(
                title=f"Book {i}",
                author_name=f"Author {i}",
                unit_price=10.00,
                category_id=category.id,
            )
            for i in range(100)
        ]
    )

    factory = RequestFactory()
    request = factory.get("/books/?page=5&limit=20")
    view = BookListView()

    response = view.get(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert len(data["data"]) == 20
    assert data["pagination"]["totalItems"] == 100
    assert data["pagination"]["totalPages"] == 5
