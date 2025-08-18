import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
import random
from apps.books.models import Book
from apps.categories.tests.factories import CategoryFactory

fake = Faker()


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text", max_nb_chars=500)
    author_name = factory.Faker("name")
    publisher_name = factory.Faker("company")
    published_date = factory.Faker("date_between", start_date="-10y", end_date="today")
    unit_price = factory.LazyFunction(
        lambda: Decimal(f"{random.uniform(9.99, 99.99):.2f}")
    )
    photo_path = factory.LazyAttribute(
        lambda obj: f"https://picsum.photos/id/{random.randint(1, 1000)}/200/300"
    )
    total_rating_value = 0
    total_rating_count = 0
    category = factory.SubFactory(CategoryFactory)
