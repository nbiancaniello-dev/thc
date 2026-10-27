# Take Home Challenge

You have to build a microservice that exposes a REST API with table: `users`. 
The table should be open to creation, deletion, or update. 
Every request must only set the `Content-Type: application/json`.

### Deployed App Running on RENDER

- [SWAGGER](https://thc-template.onrender.com/api)

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/82UCLJQ6A8o5rRSH4fZh65/ABWTL7PQ4uMpeh4uoHEsn9/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/82UCLJQ6A8o5rRSH4fZh65/ABWTL7PQ4uMpeh4uoHEsn9/tree/master) 

[![Coverage Status](https://coveralls.io/repos/github/nbiancaniello-dev/thc/badge.svg?branch=master)](https://coveralls.io/github/nbiancaniello-dev/thc?branch=master)

### How to run locally coveralls

```
COVERALLS_REPO_TOKEN=onrB7IhBLp4Ty5K3bmpEIkAGvTCZ2FXkd npm run test:cov
```

### Features
- Create new Users (`POST /api/users`)
- User Login / Token (`POST /api/users/token`)
- Current User Profile (`GET /api/users/me`)
- Get Users List (`GET /api/users`)
- Get User By ID (`GET /api/users/{user_id}`)
- Update User (`PATCH /api/users/{user_id}`)
- Delete User (`DELETE /api/users/{user_id}`)
- Update Dragon Ball IDs (`PATCH /api/users/{userid}/dragonball`)

## Pre-Requisites

- Docker installed without SUDO Permission
- Docker compose installed without SUDO
- Ports free: 3000 and 5432

## How to run the APP

```
chmod 771 ./up_dev.sh
./up_dev.sh
```

## How to run the tests

```
chmod 771 ./up_test.sh
./up_test.sh
```

## Areas to improve

- Data should be moved from tests to an external file
- Generic method should be used to mock endpoints
- Fix connection from DB IDE with error: `invalid value for parameter "TimeZone": "America/Buenos_Aires"`

## Techs

- uv: 0.13.4
- python: 3.14.7 
- fastapi: 0.148.0
- alembic: 1.20.0
- pytest: pytest-9.1.1
- postgres: 18.6 + psycopg

## Decisions made & Architecture
- **Clean Architecture (Modular Feature-First)**: Organized into feature modules (`users`) following the **Controller (Router) -> Service -> Repository** pattern.
  - **Routers / Controllers**: Exclusively manage HTTP transport, status codes, and schema validation.
  - **Services**: Encapsulate all domain rules and business logic; completely independent of web frameworks and database drivers.
  - **Repositories**: Abstract database persistence using SQLAlchemy async sessions.
  - **Core Exceptions**: Clean domain exceptions (`DuplicateResourceError`, `ResourceNotFoundError`, `ForbiddenError`, `InvalidCredentialsError`) mapped cleanly at the transport boundary.
- **Alembic**: Database migrations with version tracking for schema changes and demo seeds.
- **Docker & Compose**: Portable multi-container environment for development and testing.
- **Pytest**: Integration testing with transactional test fixtures and unit testing with mocked repositories (90%+ code coverage).

## Route

- : [![API Swagger] (https://localhost:3000/docs)]

## Env vars should be defined

To find an exmplae of the values you can use .env.example