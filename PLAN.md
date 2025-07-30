# Bookstore Backend Development - Week 1 & 2 Daily Tasks

## Week 1: Foundation & Core Features

### Day 1 - Database Schema Setup
- [X] Implement User model (custom AbstractUser with UUID, email login)
- [X] Create Category model with sort_order
- [ ] Implement Book model with pricing, ratings, and M2M categories
- [ ] Create supporting models (Comment, Order, OrderLine, ShoppingCart, ShoppingCartItem)
- [ ] Write comprehensive model tests for all entities
- [ ] Configure Django admin interface
- [ ] Run migrations and verify database setup

### Day 2 - Basic API Endpoints
- [ ] Set up Django REST Framework serializers for all models
- [ ] Create ViewSets for CRUD operations (User, Book, Category)
- [ ] Implement URL routing for API endpoints
- [ ] Add basic authentication and permissions
- [ ] Write API endpoint tests
- [ ] Test API endpoints with Postman/curl

### Day 3 - Browse Books Feature Setup
- [ ] Implement Books list API with filtering by category
- [ ] Add pagination support for book listings
- [ ] Create book search functionality (by title/author)
- [ ] Implement sorting options (price, rating, date)
- [ ] Add book detail API endpoint
- [ ] Write unit tests for book browsing features

### Day 4 - Browse Books Integration Test
- [ ] Create end-to-end test for complete browse books workflow
- [ ] Test category filtering functionality
- [ ] Test search and sorting features
- [ ] Verify pagination works correctly
- [ ] Test API response formats and error handling
- [ ] Document API endpoints

### Day 5 - Testing & Documentation
- [ ] Run full test suite and achieve >90% coverage
- [ ] Fix any failing tests or bugs found
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Set up development environment documentation
- [ ] Code review and refactoring if needed

## Week 2: Advanced Features & User Management

### Day 6 - User Authentication System
- [ ] Implement user registration API with email validation
- [ ] Create login/logout endpoints with JWT tokens
- [ ] Add password reset functionality
- [ ] Implement email verification system
- [ ] Write authentication tests
- [ ] Test user account activation flow

### Day 7 - User Profile Management
- [ ] Create user profile API endpoints (GET, PUT)
- [ ] Implement user preferences and settings
- [ ] Add user avatar upload functionality
- [ ] Create user order history endpoint
- [ ] Write user profile tests
- [ ] Test file upload and validation

### Day 8 - Shopping Cart System
- [ ] Implement shopping cart creation and management
- [ ] Add items to cart API endpoints
- [ ] Create cart persistence for logged-in users
- [ ] Handle anonymous user carts with session/cookies
- [ ] Implement cart expiration logic
- [ ] Write shopping cart tests

### Day 9 - Order Management
- [ ] Create order placement API endpoint
- [ ] Implement order validation and processing
- [ ] Add order status tracking
- [ ] Create order history for users
- [ ] Implement order cancellation logic
- [ ] Write order management tests

### Day 10 - Comments & Ratings System
- [ ] Implement book rating and review API endpoints
- [ ] Add comment moderation system
- [ ] Create rating aggregation logic
- [ ] Implement user comment history
- [ ] Add rating validation and constraints
- [ ] Write comment system tests and integration tests

## Deliverables by End of Week 2:
- Complete database schema with all models
- Full CRUD API for all entities
- User authentication and profile management
- Browse books feature with search/filter/pagination
- Shopping cart and order management system
- Comments and ratings functionality
- Comprehensive test suite (>90% coverage)
- API documentation
- Ready for frontend integration
