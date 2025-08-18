from django.core.management.base import BaseCommand
from django.db import transaction
from apps.categories.tests.factories import CATEGORY_NAMES
from apps.books.tests.factories import BookFactory
from apps.accounts.tests.factories import AccountFactory
from apps.comments.tests.factories import CommentFactory
from apps.categories.models import Category
from apps.books.models import Book
from apps.accounts.models import Account
from apps.comments.models import Comment
import random


class Command(BaseCommand):
    help = "Seed the database with initial data using factories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--books",
            type=int,
            default=50,
            help="Number of books to create (default: 50)",
        )
        parser.add_argument(
            "--accounts",
            type=int,
            default=10,
            help="Number of accounts to create (default: 10)",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=100,
            help="Number of comments to create (default: 100)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Comment.objects.all().delete()
            Book.objects.all().delete()
            Category.objects.all().delete()
            Account.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data cleared successfully"))

        with transaction.atomic():
            self.stdout.write("Creating categories...")
            categories = self._create_categories()

            self.stdout.write("Creating books...")
            books = self._create_books(options["books"], categories)

            self.stdout.write("Creating accounts...")
            accounts = self._create_accounts(options["accounts"])

            self.stdout.write("Creating comments...")
            comments_created = self._create_comments(
                options["comments"], accounts, books
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully seeded database with:\n"
                    f"  - {len(categories)} categories\n"
                    f"  - {len(books)} books\n"
                    f"  - {len(accounts)} accounts\n"
                    f"  - {comments_created} comments"
                )
            )

    def _create_categories(self):
        """Create one category for each name in CATEGORY_NAMES"""
        categories = []

        for index, name in enumerate(CATEGORY_NAMES):
            category, created = Category.objects.get_or_create(
                name=name, defaults={"sort_order": (index + 1) * 10}
            )
            categories.append(category)
            if created:
                self.stdout.write(f"  Created category: {category.name}")
            else:
                self.stdout.write(f"  Category already exists: {category.name}")

        return categories

    def _create_books(self, count, categories):
        """Create books with random categories"""
        books = []
        for i in range(count):
            category = random.choice(categories)
            book = BookFactory.create(category=category)
            books.append(book)

        self.stdout.write(f"  Created {count} books")
        return books

    def _create_accounts(self, count):
        """Create test accounts"""
        accounts = []

        # Create admin account
        admin, created = Account.objects.get_or_create(
            email="admin@bookstore.com",
            defaults={
                "full_name": "Admin User",
                "phone": "+1234567890",
                "birthday": "1990-01-01",
                "is_active": True,
                "is_admin": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(
                "  Created admin account: admin@bookstore.com (password: admin123)"
            )
        accounts.append(admin)

        # Create regular user
        user, created = Account.objects.get_or_create(
            email="user@bookstore.com",
            defaults={
                "full_name": "Regular User",
                "phone": "+1234567891",
                "birthday": "1995-05-15",
                "is_active": True,
            },
        )
        if created:
            user.set_password("user123")
            user.save()
            self.stdout.write(
                "  Created regular account: user@bookstore.com (password: user123)"
            )
        accounts.append(user)

        # Create additional accounts using factory
        additional_count = max(0, count - 2)
        if additional_count > 0:
            additional_accounts = AccountFactory.create_batch(
                additional_count, active=True, password="password123"
            )
            accounts.extend(additional_accounts)
            self.stdout.write(
                f"  Created {additional_count} additional accounts (password: password123)"
            )

        return accounts

    def _create_comments(self, count, accounts, books):
        """Create comments ensuring unique account-book combinations"""
        created_comments = 0
        attempts = 0
        max_attempts = count * 3  # Allow more attempts since we have unique constraint

        while created_comments < count and attempts < max_attempts:
            attempts += 1
            account = random.choice(accounts)
            book = random.choice(books)

            # Check if this combination already exists
            if not Comment.objects.filter(account=account, book=book).exists():
                CommentFactory.create(account=account, book=book)
                created_comments += 1

        self.stdout.write(f"  Created {created_comments} comments")

        if created_comments < count:
            self.stdout.write(
                self.style.WARNING(
                    f"  Note: Could only create {created_comments} comments due to "
                    f"unique constraint (one comment per account-book pair)"
                )
            )

        return created_comments
