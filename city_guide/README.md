# City Guide API

City Guide API is a production-oriented FastAPI service that generates personalized travel routes using Google Maps data and GPT models.

## Features

- FastAPI application with async SQLAlchemy and PostgreSQL
- GPT-assisted POI selection and route ordering
- Google Places and Distance Matrix integrations
- Route constraint validation and persistence
- Async-first architecture with uvicorn/uvloop
- Extensive test suite and OpenAPI contract verification
- Docker and docker-compose for local development
- GitHub Actions workflow for linting and testing

## Getting Started

### Prerequisites

- Python 3.10+
- Poetry 1.7+
- Docker & Docker Compose

### Installation

```bash
poetry install
```

### Environment Variables

Copy `.env.example` to `.env` and adjust values as needed.

```bash
cp .env.example .env
```

### Database

Run database migrations and seed data:

```bash
make migrate
make seed
```

### Running the App

```bash
make dev
```

The API will be available at `http://localhost:8000`.

### Testing

```bash
make test
```

### Linting

```bash
make lint
```

## Project Structure

Refer to the `city_guide/` directory for application modules, Alembic migrations, and tests.

## License

MIT
