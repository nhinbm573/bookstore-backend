import os
import subprocess
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import django

from apps.categories.tests.factories import CategoryFactory
from apps.books.tests.factories import BookFactory
from apps.accounts.tests.factories import AccountFactory
from apps.comments.tests.factories import CommentFactory


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
django.setup()


@pytest.fixture(scope="function")
def setup_test_data(django_db_blocker):
    with django_db_blocker.unblock():
        from django.db import transaction

        with transaction.atomic():
            categories = [
                CategoryFactory.create(name="Fiction"),
                CategoryFactory.create(name="Non-Fiction"),
                CategoryFactory.create(name="Science"),
            ]

            users = [
                AccountFactory.create(
                    email="test1@example.com",
                    full_name="Test User 1",
                    active=True,
                    password="testpass123",
                ),
                AccountFactory.create(
                    email="test2@example.com",
                    full_name="Test User 2",
                    active=True,
                    password="testpass123",
                ),
            ]

            books = []
            for i in range(10):
                book = BookFactory.create(
                    title=f"Test Book {i + 1}", category=categories[i % len(categories)]
                )
                books.append(book)

            for book in books[:5]:
                for user in users:
                    CommentFactory.create(
                        book=book,
                        account=user,
                        rating=4,
                        content=f"Great book! - {user.full_name}",
                    )

        from apps.books.models import Book

        print(f"Created {Book.objects.count()} books in database")

    yield {"categories": categories, "users": users, "books": books}

    with django_db_blocker.unblock():
        from apps.comments.models import Comment
        from apps.books.models import Book
        from apps.accounts.models import Account
        from apps.categories.models import Category

        Comment.objects.all().delete()
        Book.objects.all().delete()
        Account.objects.filter(
            email__in=["test1@example.com", "test2@example.com"]
        ).delete()
        Category.objects.filter(name__in=["Fiction", "Non-Fiction", "Science"]).delete()


@pytest.fixture(scope="function")
def django_server():
    """Start Django development server for the entire test session."""
    import requests
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from decouple import config

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    db_name = config("TEST_DB_NAME", default="test_db")
    db_user = config("TEST_DB_USER", default="test_user")
    db_password = config("TEST_DB_PASSWORD", default="test_password")
    db_host = config("TEST_DB_HOST", default="localhost")

    try:
        conn = psycopg2.connect(
            dbname="postgres", user=db_user, password=db_password, host=db_host
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Created test database '{db_name}'")
        else:
            print(f"Test database '{db_name}' already exists")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Warning: Could not create database: {e}")

    print("Running migrations...")
    migrate_result = subprocess.run(
        ["python", "manage.py", "migrate"],
        cwd=project_root,
        capture_output=True,
        text=True,
        env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings.testing"},
    )

    if migrate_result.returncode != 0:
        print(f"Migration output: {migrate_result.stdout}")
        print(f"Migration errors: {migrate_result.stderr}")

    print("Starting Django development server...")
    server_process = subprocess.Popen(
        ["python", "manage.py", "runserver"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=project_root,
        env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings.testing"},
    )

    server_url = "http://localhost:8000"
    max_attempts = 30
    for i in range(max_attempts):
        try:
            if server_process.poll() is not None:
                output = server_process.stdout.read().decode()
                raise RuntimeError(f"Django server terminated unexpectedly:\n{output}")

            response = requests.get(f"{server_url}/api/", timeout=1)
            if response.status_code in [200, 404]:  # Server is responding
                print(f"Django server is ready at {server_url}")
                break
        except (requests.ConnectionError, requests.Timeout):
            if i == max_attempts - 1:
                output = ""
                if server_process.stdout:
                    try:
                        import select

                        while select.select([server_process.stdout], [], [], 0)[0]:
                            line = server_process.stdout.readline()
                            if line:
                                output += line.decode()
                    except Exception:
                        pass
                server_process.terminate()
                raise RuntimeError(
                    f"Django server failed to start after {max_attempts} "
                    f"attempts.\nOutput:\n{output}"
                )
            time.sleep(1)

    yield server_process

    server_process.terminate()
    server_process.wait()


@pytest.fixture(scope="function")
def driver(django_server):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver_instance = webdriver.Chrome(service=service, options=chrome_options)
    driver_instance.implicitly_wait(10)

    yield driver_instance

    driver_instance.quit()
