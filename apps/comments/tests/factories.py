import factory
from factory.django import DjangoModelFactory
import random
from apps.comments.models import Comment
from apps.accounts.tests.factories import AccountFactory
from apps.books.tests.factories import BookFactory


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    rating = factory.LazyFunction(lambda: random.randint(1, 5))
    content = factory.Faker("paragraph", nb_sentences=3)
    account = factory.SubFactory(AccountFactory, active=True)
    book = factory.SubFactory(BookFactory)
