# Bookstore Backend Development - Week 1 & 2 Daily Tasks

## Week 1: Foundation & Core Features

### Day 1 - Database Schema Setup
- [X] **Account model**: Implemented custom `Account` model based on `AbstractBaseUser` with UUID and email login
- [X] **Account manager**: Implemented custom `AccountManager` for handling user creation logic
- [X] **Category model**: Created with name and `sort_order` fields
- [X] **Book model**: Implemented with pricing, ratings, and many-to-many relationship with `Category`
- [X] **Comment model**: Created with foreign keys to `Account` and `Book`, and content field
- [X] **Factories**: Added model factories for `Account`, `Category`, `Book`, and `Comment`
- [X] **Fixtures**: Configured `conftest.py` with reusable fixtures for all models
- [X] **Model tests**: Wrote unit tests covering fields, constraints, and relationships for all models
- [X] **Migrations**: Ran initial migrations and confirmed development database setup

### Day 2 - Browse Books Feature (Setup)
- [X] **BookSerializer**: Implemented to serialize `Book` model data
- [X] **BookListView**: Created a view for listing books with the following features:
    - [X] **Search**: Added functionality to search by `author_name` or `title`
    - [X] **Filter**: Included filtering capability by `Category` name
    - [X] **Pagination**: Implemented pagination with a default `page` of 1 and `limit` of 10
- [X] **Tests**: Wrote unit tests to cover the functionality of the `BookSerializer` and the `BookListView`

### Day 3 - Browse Books Feature (Integration Test)
- [X] **Integration tests**: Wrote tests for the book list features:
    - [X] Integration test for book list
    - [X] Integration test for searching by title or author_name
    - [X] Integration test for filtering by category
    - [X] Integration test for pagination on the book list

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
