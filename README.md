# FastAPI Boilerplate

## Project Description
FastAPI boilerplate designed to provide a foundational structure for building scalable web APIs. It serves as a robust starting point for new projects, equipped with a variety of commonly required features for web applications.

## Features
- **Authentication System**: Implements JWT-based endpoints for secure registration, login, and password management.
- **User Management**: Provides a set of APIs for user operations, including CRUD functionalities.
- **File Upload**: Demonstrates file uploading mechanism (using S3 compatible storages like MinIO), exemplified with user photo uploads.
- **Email Integration**: Email system for account confirmation and password resets, supported by a dynamic email template management.
- **Role and Permission Management**: Role-based access control system with customizable permissions.
- **Asynchronous IO**: Utilizes FastAPI's asynchronous capabilities for enhanced performance.
- **Common Response Format**: Uniform API responses for consistency.
- **Rate Limiting**: Custom decorator for request rate limiting (using Redis).
- **Advanced Filtering**: Flexible query filters, capable of handling complex relationships from simple specifications.
- **Integrated Testing**: Comprehensive integration tests setup with database session management.
- **CORS Configuration**: Configurable Cross-Origin Resource Sharing (CORS) to specify which external domains can interact with the API.

## Technology Stack and Services

### Framework and Language
- **FastAPI**: A modern, fast web framework for building APIs.
- **Python**: The primary programming language.

### Database and Migrations
- **PostgreSQL**: The default database for data storage, managed via Docker Compose.
- **Alembic**: Handles database migrations.

### Testing
- **Pytest**: Used for writing and executing integration tests.

### Containerization
- **Docker and Docker Compose**: Facilitates containerization of the application and services for consistent environments.

### File Storage
- **MinIO/AWS**: In development, MinIO serves as a local AWS S3-compatible storage for file uploads. Configured via Docker Compose.

### Rate Limiting and Caching
- **Redis**: Used for application-level rate limiting and potential caching needs. Configured through Docker Compose.

### Email Testing
- **MailHog**: Simulates an SMTP server for email testing, capturing emails for review in a web interface.

## Getting Started
### Setting Up the Project
1. Clone the repository.
2. Create an environment file: `cp .env.example .env`.
3. Start the project: `docker-compose up -d --build`.

### Running Migrations
Execute database migrations:
```
docker compose exec web alembic upgrade head
```

### Running Tests
Run integration tests:
```
docker compose exec web pytest
```

## API Documentation
The auto-generated OpenAPI documentation is accessible at `http://127.0.0.1:8000/docs` (adjust as necessary based on `.env` settings).

## Configuration
Manage configuration settings via the `.env` file. See `.env.example` for a template.

## Contributions
Suggestions and improvements via issues or pull requests are welcome.

## License
Licensed under the MIT License. See [LICENSE.txt](LICENSE.txt) for details.
