# BookStore: Backend (Django)

## 1. Project Structure

The Django backend will be organized into multiple apps, each handling specific functionality domains. This modular approach promotes code reusability, maintainability, and follows Django best practices. You can look at frontend code base: https://github.com/nhinbm573/bookstore-frontend

```
bookstore-backend/
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── .env
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── celery.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── core/          # For seed data
│   ├── accounts/
│   ├── books/
│   ├── categories/
│   └── comments/
├── scripts/           # Setup and running scripts
└── e2e-tests/         # End-to-end backend tests
```

## 2. Getting Started

Run the setup script to get started quickly:

```bash
# Make the script executable (if needed)
chmod +x scripts/setup_dev.sh

# Run the setup script
./scripts/setup_dev.sh
```

After the setup completes:
1. **Activate the virtual environment**

    ```bash
    source ven/bin/activate
    ```

2. **Start the development server**

    ```bash
    python manage.py runserver
    ```

3. **Make sure Redis is running**

    Celery requires Redis as the message broker. Make sure Redis is installed and running on your system:
    ```bash
    # Check if Redis is running
    redis-cli ping

    # You should get a response: PONG
    ```

    > If you don’t have Redis, [install it here](https://redis.io/topics/quickstart).

4. **Start Celery worker**

    In a new terminal (with the virtual environment activated):

    ```bash
    celery -A config worker -l info
    ```

5. **Environment Setup**
```commandline
# TESTING ENVIRONMENT
TEST_DB_NAME=
TEST_DB_USER=
TEST_DB_PASSWORD=
TEST_DB_HOST=
TEST_DB_PORT=

# DEVELOPMENT ENVIRONMENT
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# FRONTEND DOMAIN
FRONTEND_DOMAIN=

# EMAIL (Production)
EMAIL_BACKEND=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# CAPTCHA
SITE_KEY=
SECRET_KEY=

# GOOGLE OAUTH
GOOGLE_CLIENT_ID=

# REDIS
REDIS_URL=
```

## 3. Features

#### Functional requirements

- [x] **Register**
- [x] **Activation**
- [x] **Forgot password**
- [x] **Login**
  - [x] Trigger reCaptcha v2 after failing 3 times.
  - [x] Google SSO
- [x] **Edit personal information**
- [x] **Browse for books**
- [x] **Search for books** : `django-filter` which uses SQL queries internally for searching/filtering.
- [x] **Pagination supports browsing & search features**
- [ ] **View book details**
- [ ] **Add rating and comment**
- [ ] **Add books to shopping cart and View shopping cart**
- [ ] **Checkout & confirm an order**
- [ ] **View past orders**
- [ ] **Admin interface**

Although I haven’t completed all the functional requirements yet, this project has helped me learn:

- How to configure linting, formatting, and pre-commit hooks.
- How to separate configurations for different environments.
- How to set up CI workflows for continuous integration.
