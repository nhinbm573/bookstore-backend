## Django Apps Architecture

### Authentication App (`apps/authentication/`)

This app handles user authentication, registration, password reset, and account activation.

**Models**: None (uses Django's built-in User model extended by the users app)

**Views**:

- `RegisterView`: Handles user registration
- `LoginView`: Handles user login with JWT token generation
- `LogoutView`: Handles user logout and token invalidation
- `ActivateAccountView`: Handles account activation via email token
- `ForgotPasswordView`: Initiates password reset process
- `ResetPasswordView`: Handles password reset with token validation
- `RefreshTokenView`: Refreshes JWT access tokens

**Serializers**:

- `UserRegistrationSerializer`: Validates registration data
- `LoginSerializer`: Validates login credentials
- `PasswordResetSerializer`: Validates password reset requests
- `PasswordResetConfirmSerializer`: Validates password reset confirmation

**URLs**:

- `POST /api/auth/register/`: User registration
- `POST /api/auth/login/`: User login
- `POST /api/auth/logout/`: User logout
- `GET /api/auth/activate/<token>/`: Account activation
- `POST /api/auth/forgot-password/`: Request password reset
- `POST /api/auth/reset-password/`: Confirm password reset
- `POST /api/auth/refresh-token/`: Refresh JWT token

### Users App (`apps/users/`)

This app manages user profiles and user-related operations.

**Models**:

- `User`: Extended Django User model with additional fields
- `UserProfile`: Additional user information (phone, birthday, etc.)

**Views**:

- `UserProfileView`: Retrieve and update user profile
- `ChangePasswordView`: Change user password
- `UserOrdersView`: Retrieve user's order history

**Serializers**:

- `UserSerializer`: User basic information
- `UserProfileSerializer`: Complete user profile information
- `ChangePasswordSerializer`: Password change validation

**URLs**:

- `GET /api/users/profile/`: Get user profile
- `PUT /api/users/profile/`: Update user profile
- `POST /api/users/change-password/`: Change password
- `GET /api/users/orders/`: Get user orders

### Categories App (`apps/categories/`)

This app manages book categories.

**Models**:

- `Category`: Book category with name and sort order

**Views**:

- `CategoryListView`: List all categories
- `CategoryDetailView`: Get category details with books

**Serializers**:

- `CategorySerializer`: Category information
- `CategoryWithBooksSerializer`: Category with associated books

**URLs**:

- `GET /api/categories/`: List all categories
- `GET /api/categories/<id>/`: Get category details

### Books App (`apps/books/`)

This app manages books, book details, and book-related operations.

**Models**:

- `Book`: Book information and details
- `BookCategory`: Many-to-many relationship between books and categories

**Views**:

- `BookListView`: List books with pagination and filtering
- `BookDetailView`: Get detailed book information
- `BookSearchView`: Search books by title, author, or category
- `BookAdminView`: Admin operations for books (CRUD)

**Serializers**:

- `BookSerializer`: Basic book information
- `BookDetailSerializer`: Detailed book information with ratings and comments
- `BookAdminSerializer`: Admin book operations

**URLs**:

- `GET /api/books/`: List books with pagination
- `GET /api/books/<id>/`: Get book details
- `GET /api/books/search/`: Search books
- `POST /api/books/`: Create book (admin only)
- `PUT /api/books/<id>/`: Update book (admin only)
- `DELETE /api/books/<id>/`: Delete book (admin only)

### Comments App (`apps/comments/`)

This app manages book comments and ratings.

**Models**:

- `Comment`: User comments and ratings for books

**Views**:

- `CommentListView`: List comments for a book
- `CommentCreateView`: Create a new comment
- `CommentUpdateView`: Update user's own comment
- `CommentDeleteView`: Delete user's own comment

**Serializers**:

- `CommentSerializer`: Comment information
- `CommentCreateSerializer`: Comment creation validation

**URLs**:

- `GET /api/comments/book/<book_id>/`: List comments for a book
- `POST /api/comments/`: Create a comment
- `PUT /api/comments/<id>/`: Update a comment
- `DELETE /api/comments/<id>/`: Delete a comment

### Shopping Cart App (`apps/shopping_cart/`)

This app manages shopping cart functionality.

**Models**:

- `ShoppingCart`: Shopping cart information
- `ShoppingCartItem`: Items in the shopping cart

**Views**:

- `ShoppingCartView`: Get current user's shopping cart
- `AddToCartView`: Add item to shopping cart
- `UpdateCartItemView`: Update cart item quantity
- `RemoveFromCartView`: Remove item from cart
- `ClearCartView`: Clear entire cart

**Serializers**:

- `ShoppingCartSerializer`: Shopping cart with items
- `ShoppingCartItemSerializer`: Individual cart item
- `AddToCartSerializer`: Add item validation

**URLs**:

- `GET /api/cart/`: Get shopping cart
- `POST /api/cart/add/`: Add item to cart
- `PUT /api/cart/item/<id>/`: Update cart item
- `DELETE /api/cart/item/<id>/`: Remove cart item
- `DELETE /api/cart/clear/`: Clear cart

### Orders App (`apps/orders/`)

This app manages order processing and order history.

**Models**:

- `Order`: Order information
- `OrderLine`: Individual items in an order

**Views**:

- `OrderCreateView`: Create a new order from cart
- `OrderListView`: List user's orders
- `OrderDetailView`: Get order details
- `OrderAdminView`: Admin order management

**Serializers**:

- `OrderSerializer`: Order information
- `OrderDetailSerializer`: Detailed order with items
- `OrderCreateSerializer`: Order creation validation

**URLs**:

- `POST /api/orders/`: Create order
- `GET /api/orders/`: List user orders
- `GET /api/orders/<id>/`: Get order details
- `GET /api/admin/orders/`: Admin order list

### Common App (`apps/common/`)

This app contains shared utilities, mixins, and common functionality.

**Components**:

- `BaseModel`: Abstract model with common fields (id, created_at, updated_at)
- `CustomPagination`: Custom pagination class
- `PermissionMixins`: Common permission mixins
- `ResponseMixins`: Standardized API response mixins
- `ValidationMixins`: Common validation utilities

## API Design Principles

### RESTful API Standards

The backend follows RESTful API design principles with consistent URL patterns, HTTP methods, and response formats. All endpoints return JSON responses with standardized error handling.

### Authentication and Authorization

The system uses JWT (JSON Web Tokens) for authentication. The authentication flow includes:

1. **Registration**: Users register with email, password, and personal information
2. **Email Activation**: Users must activate their accounts via email
3. **Login**: Authenticated users receive access and refresh tokens
4. **Token Refresh**: Access tokens can be refreshed using refresh tokens
5. **Logout**: Tokens are invalidated on logout

**JWT Configuration**:

- Access token expiry: 15 minutes
- Refresh token expiry: 7 days
- Token rotation: Refresh tokens are rotated on use
- Blacklisting: Logout invalidates tokens

**Permission Classes**:

- `IsAuthenticated`: Requires valid JWT token
- `IsOwnerOrReadOnly`: Users can only modify their own resources
- `IsAdminUser`: Admin-only operations
- `AllowAny`: Public endpoints

### Request/Response Format

**Standard Response Format**:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "errors": null,
  "pagination": {
    "count": 100,
    "next": "http://api.example.com/books/?page=2",
    "previous": null,
    "page_size": 10
  }
}
```

**Error Response Format**:

```json
{
  "success": false,
  "data": null,
  "message": "Validation failed",
  "errors": {
    "email": ["This field is required."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

### Pagination

All list endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

### Filtering and Searching

Book endpoints support filtering and searching:

- `category`: Filter by category ID
- `search`: Search in title and author name
- `min_price`, `max_price`: Price range filtering
- `ordering`: Sort by price, rating, or date

## Database Integration

### Django ORM Configuration

The backend uses Django ORM with PostgreSQL as the database. Model definitions follow the database schema outlined in the database design document.

**Database Settings**:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### Migrations Strategy

Database migrations will be managed through Django's migration system:

- Initial migration creates all tables
- Data migrations handle category seeding
- Schema migrations handle future changes
- Migration rollback procedures for production

### Query Optimization

Performance optimization strategies:

- `select_related()` for foreign key relationships
- `prefetch_related()` for many-to-many relationships
- Database indexing on frequently queried fields
- Query result caching for expensive operations
- Pagination to limit result sets

## Security Implementation

### Input Validation

All user inputs are validated using Django REST Framework serializers:

- Email format validation
- Password strength requirements
- Phone number format validation
- Date validation for birthday and published dates
- Price validation for positive values

### CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured to allow frontend access:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Development frontend
    "https://yourdomain.com",  # Production frontend
]

CORS_ALLOW_CREDENTIALS = True
```

### Rate Limiting

API rate limiting prevents abuse:

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Login attempts: 5 attempts per 15 minutes per IP

### File Upload Security

Book photo uploads are secured:

- File type validation (JPEG, PNG only)
- File size limits (max 5MB)
- Virus scanning integration
- Secure file storage with unique names

## Middleware Configuration

### Custom Middleware

**Authentication Middleware**: Handles JWT token validation and user context
**CORS Middleware**: Manages cross-origin requests
**Rate Limiting Middleware**: Implements API rate limiting
**Logging Middleware**: Logs all API requests and responses
**Error Handling Middleware**: Standardizes error responses

### Third-Party Middleware

- `django.middleware.security.SecurityMiddleware`: Security headers
- `django.contrib.sessions.middleware.SessionMiddleware`: Session management
- `django.middleware.common.CommonMiddleware`: Common functionality
- `django.middleware.csrf.CsrfViewMiddleware`: CSRF protection
- `django.contrib.auth.middleware.AuthenticationMiddleware`: Authentication
- `django.contrib.messages.middleware.MessageMiddleware`: Messages framework

## Background Tasks

### Celery Integration

Background tasks are handled using Celery with Redis as the message broker:

**Task Types**:

- Email sending (registration, password reset)
- Shopping cart cleanup (expired carts)
- Order processing notifications
- Database maintenance tasks

**Celery Configuration**:

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### Email Configuration

Email sending is configured for production use:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

## Testing Strategy

### Unit Tests

Each app includes comprehensive unit tests:

- Model tests for data validation
- View tests for API endpoints
- Serializer tests for data transformation
- Utility function tests

### Integration Tests

Integration tests cover:

- Authentication flow end-to-end
- Order creation process
- Shopping cart functionality
- Email sending workflows

### API Testing

API endpoints are tested using Django REST Framework's test client:

- Request/response validation
- Authentication and permission testing
- Error handling verification
- Performance testing

## Deployment Configuration

### Environment Settings

Different settings for different environments:

- **Development**: Debug enabled, local database, console email backend
- **Testing**: In-memory database, mock external services
- **Production**: Debug disabled, production database, real email backend

### Heroku Deployment

Configuration for Heroku deployment:

- `Procfile`: Defines web and worker processes
- `runtime.txt`: Specifies Python version
- Environment variables for sensitive configuration
- Static file serving configuration
- Database URL parsing

### CI/CD Integration

CircleCI configuration for continuous integration:

- Automated testing on pull requests
- Code quality checks (linting, formatting)
- Security vulnerability scanning
- Automated deployment to staging/production
