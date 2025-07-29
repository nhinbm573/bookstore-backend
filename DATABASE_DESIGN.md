# Database Design

## Introduction

This document outlines the database schema for the e-commerce book system, designed to support the functional and data requirements specified. The database will be built using PostgreSQL, aligning with the project's technical constraints.

## Entity-Relationship Diagram (ERD)

[ERD will be inserted here after schema definition]

## Schema Definition

Below are the detailed definitions for each table, including column names, data types, constraints, and relationships.

### Table: `Users`

This table stores information about registered users of the system.

| Column Name             | Data Type                  | Constraints                             | Description                                                  |
| ----------------------- | -------------------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`                    | `UUID`                     | `PRIMARY KEY`                           | Unique identifier for the user.                              |
| `email`                 | `VARCHAR(255)`             | `NOT NULL`, `UNIQUE`                    | User's email address, used for login and account activation. |
| `password`              | `VARCHAR(255)`             | `NOT NULL`                              | Hashed password for the user.                                |
| `phone`                 | `VARCHAR(20)`              | `NULLABLE`                              | User's phone number.                                         |
| `full_name`             | `VARCHAR(255)`             | `NOT NULL`                              | User's full name.                                            |
| `birthday`              | `DATE`                     | `NULLABLE`                              | User's date of birth.                                        |
| `account_creation_date` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Date and time when the account was created.                  |
| `is_active`             | `BOOLEAN`                  | `NOT NULL`, `DEFAULT FALSE`             | Indicates if the user's account is activated.                |
| `is_admin`              | `BOOLEAN`                  | `NOT NULL`, `DEFAULT FALSE`             | Indicates if the user has administrative privileges.         |

### Table: `Categories`

This table organizes books into different categories.

| Column Name  | Data Type      | Constraints          | Description                                 |
| ------------ | -------------- | -------------------- | ------------------------------------------- |
| `id`         | `UUID`         | `PRIMARY KEY`        | Unique identifier for the category.         |
| `name`       | `VARCHAR(255)` | `NOT NULL`, `UNIQUE` | Name of the category.                       |
| `sort_order` | `INTEGER`      | `NOT NULL`, `UNIQUE` | Determines the display order of categories. |

### Table: `Books`

This table stores details about each book available in the system.

| Column Name          | Data Type        | Constraints                           | Description                                       |
| -------------------- | ---------------- | ------------------------------------- | ------------------------------------------------- |
| `id`                 | `UUID`           | `PRIMARY KEY`                         | Unique identifier for the book.                   |
| `title`              | `VARCHAR(255)`   | `NOT NULL`                            | Title of the book.                                |
| `description`        | `TEXT`           | `NULLABLE`                            | Detailed description of the book.                 |
| `author_name`        | `VARCHAR(255)`   | `NOT NULL`                            | Author(s) of the book.                            |
| `publisher_name`     | `VARCHAR(255)`   | `NULLABLE`                            | Publisher of the book.                            |
| `published_date`     | `DATE`           | `NULLABLE`                            | Date when the book was published.                 |
| `unit_price`         | `DECIMAL(10, 2)` | `NOT NULL`, `CHECK (unit_price >= 0)` | Price of a single unit of the book.               |
| `photo_path`         | `VARCHAR(255)`   | `NULLABLE`                            | Path to the book's cover photo on the web server. |
| `total_rating_value` | `INTEGER`        | `NOT NULL`, `DEFAULT 0`               | Sum of all ratings given to this book.            |
| `total_rating_count` | `INTEGER`        | `NOT NULL`, `DEFAULT 0`               | Total number of ratings received for this book.   |

### Junction Table: `BookCategories`

This table handles the many-to-many relationship between `Books` and `Categories`.

| Column Name   | Data Type | Constraints                                            | Description                                     |
| ------------- | --------- | ------------------------------------------------------ | ----------------------------------------------- |
| `book_id`     | `UUID`    | `PRIMARY KEY`, `FOREIGN KEY REFERENCES Books(id)`      | Foreign key referencing the `Books` table.      |
| `category_id` | `UUID`    | `PRIMARY KEY`, `FOREIGN KEY REFERENCES Categories(id)` | Foreign key referencing the `Categories` table. |

### Table: `Comments`

This table stores user comments and ratings for books.

| Column Name    | Data Type                  | Constraints                                       | Description                                |
| -------------- | -------------------------- | ------------------------------------------------- | ------------------------------------------ |
| `id`           | `UUID`                     | `PRIMARY KEY`                                     | Unique identifier for the comment.         |
| `rating`       | `INTEGER`                  | `NOT NULL`, `CHECK (rating >= 1 AND rating <= 5)` | Rating given by the user (1 to 5).         |
| `content`      | `TEXT`                     | `NULLABLE`                                        | Content of the comment.                    |
| `user_id`      | `UUID`                     | `NOT NULL`, `FOREIGN KEY REFERENCES Users(id)`    | Foreign key referencing the `Users` table. |
| `book_id`      | `UUID`                     | `NOT NULL`, `FOREIGN KEY REFERENCES Books(id)`    | Foreign key referencing the `Books` table. |
| `comment_date` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`           | Date and time when the comment was made.   |

### Table: `Orders`

This table stores information about customer orders.

| Column Name        | Data Type                  | Constraints                                    | Description                                |
| ------------------ | -------------------------- | ---------------------------------------------- | ------------------------------------------ |
| `id`               | `UUID`                     | `PRIMARY KEY`                                  | Unique identifier for the order.           |
| `order_date`       | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`        | Date and time when the order was placed.   |
| `user_id`          | `UUID`                     | `NOT NULL`, `FOREIGN KEY REFERENCES Users(id)` | Foreign key referencing the `Users` table. |
| `shipping_address` | `TEXT`                     | `NOT NULL`                                     | Shipping address for the order.            |
| `total_amount`     | `DECIMAL(10, 2)`           | `NULLABLE`, `CHECK (total_amount >= 0)`        | Total amount of the order.                 |

### Table: `OrderLines`

This table stores individual items within an order.

| Column Name  | Data Type        | Constraints                                     | Description                                 |
| ------------ | ---------------- | ----------------------------------------------- | ------------------------------------------- |
| `id`         | `UUID`           | `PRIMARY KEY`                                   | Unique identifier for the order line item.  |
| `order_id`   | `UUID`           | `NOT NULL`, `FOREIGN KEY REFERENCES Orders(id)` | Foreign key referencing the `Orders` table. |
| `book_id`    | `UUID`           | `NOT NULL`, `FOREIGN KEY REFERENCES Books(id)`  | Foreign key referencing the `Books` table.  |
| `unit_price` | `DECIMAL(10, 2)` | `NOT NULL`, `CHECK (unit_price >= 0)`           | Price of the book at the time of order.     |
| `quantity`   | `INTEGER`        | `NOT NULL`, `CHECK (quantity > 0)`              | Quantity of the book in the order.          |

### Table: `ShoppingCarts`

This table stores information about active shopping carts.

| Column Name  | Data Type                  | Constraints                                              | Description                                                           |
| ------------ | -------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------- |
| `id`         | `UUID`                     | `PRIMARY KEY`                                            | Unique identifier for the shopping cart.                              |
| `user_id`    | `UUID`                     | `NULLABLE`, `UNIQUE`, `FOREIGN KEY REFERENCES Users(id)` | Foreign key referencing the `Users` table (NULL for anonymous users). |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                  | Timestamp when the cart was created.                                  |
| `expires_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`                                               | Timestamp when the cart expires (3 hours for anonymous users).        |

### Table: `ShoppingCartItems`

This table stores individual items within a shopping cart.

| Column Name  | Data Type        | Constraints                                            | Description                                        |
| ------------ | ---------------- | ------------------------------------------------------ | -------------------------------------------------- |
| `id`         | `UUID`           | `PRIMARY KEY`                                          | Unique identifier for the shopping cart item.      |
| `cart_id`    | `UUID`           | `NOT NULL`, `FOREIGN KEY REFERENCES ShoppingCarts(id)` | Foreign key referencing the `ShoppingCarts` table. |
| `book_id`    | `UUID`           | `NOT NULL`, `FOREIGN KEY REFERENCES Books(id)`         | Foreign key referencing the `Books` table.         |
| `quantity`   | `INTEGER`        | `NOT NULL`, `CHECK (quantity > 0)`                     | Quantity of the book in the cart.                  |
| `unit_price` | `DECIMAL(10, 2)` | `NOT NULL`, `CHECK (unit_price >= 0)`                  | Price of the book when added to the cart.          |

## Relationships

- **Users to Comments**: One-to-Many (One user can make many comments)
- **Users to Orders**: One-to-Many (One user can place many orders)
- **Users to ShoppingCarts**: One-to-One (One user can have one shopping cart, but a shopping cart can exist without a user for anonymous users)
- **Books to Comments**: One-to-Many (One book can have many comments)
- **Books to OrderLines**: One-to-Many (One book can appear in many order lines)
- **Books to ShoppingCartItems**: One-to-Many (One book can appear in many shopping cart items)
- **Categories to Books**: Many-to-Many (Handled by `BookCategories` junction table)
- **Orders to OrderLines**: One-to-Many (One order can have many order line items)
- **ShoppingCarts to ShoppingCartItems**: One-to-Many (One shopping cart can have many items)

## Data Seeding

Categories can be pre-populated into the system through a seed file. This will be implemented as part of the backend development.

## Future Considerations

- **Payment System Integration**: The `Orders` table has a `total_amount` field, which can be used for future payment gateway integration.
- **User Roles**: The `Users` table includes an `is_admin` flag, allowing for role-based access control.
- **Scalability**: UUIDs are used for primary keys to facilitate distributed systems and prevent ID collisions in a scaled environment.
