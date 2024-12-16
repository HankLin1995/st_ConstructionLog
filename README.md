# FastAPI Quality Management System

A robust quality management system built with FastAPI framework for tracking and managing project quality test records.

## Features

- Project Management: Create, query, update, and delete project information
- Contract Management: Handle contract items related to projects
- Quality Testing: Record and track project quality test results
- RESTful API: Complete REST API interface
- Data Validation: Using Pydantic for data validation and serialization
- Data Persistence: SQLAlchemy ORM for database operations

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic
- Pytest
- Uvicorn
- SQLite

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

```bash
uvicorn main:app --reload
```

The application will run at http://localhost:8000

### 3. API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Projects
- `GET /projects/`: Get all projects
- `POST /projects/`: Create a new project
- `GET /projects/{project_id}`: Get a specific project
- `PUT /projects/{project_id}`: Update a project
- `DELETE /projects/{project_id}`: Delete a project

### Contract Items
- `GET /contract-items/`: Get all contract items
- `POST /contract-items/`: Create a new contract item
- `GET /contract-items/{item_id}`: Get a specific contract item

### Quality Tests
- `GET /quality-tests/`: Get all quality test records
- `POST /quality-tests/`: Create a new quality test record
- `GET /quality-tests/{test_id}`: Get a specific test record

## Development

### Running Tests

```bash
pytest
```

### Docker Deployment

```bash
docker build -t fastapi-quality-app .
docker run -d -p 8000:8000 fastapi-quality-app
```

## Project Structure

```
test_FastAPI/
├── main.py           # FastAPI application main file
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic models
├── database.py       # Database configuration
├── tests/            # Test files
│   ├── conftest.py   # Test configuration
│   └── test_api.py   # API tests
├── requirements.txt  # Project dependencies
└── Dockerfile       # Docker configuration
```

## Notes

- Ensure all dependencies are installed before running the application
- Development environment uses SQLite database, production environment can be configured with other databases as needed
- All API requests and responses use JSON format

## License

[MIT License](https://opensource.org/licenses/MIT)
