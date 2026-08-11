# Learning Quest API

FastAPI backend for a gamified learning application. It includes JWT authentication,
roadmaps and tests, matchmaking, knowledge points, daily streaks, and Pomodoro sessions.

## Requirements

- Python 3.11 or newer
- PowerShell on Windows, or an equivalent terminal

The application uses SQLite, so no separate database server is required.

## 1. Create and activate a virtual environment

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, the virtual environment can still be used directly by
running `.\.venv\Scripts\python.exe` in the commands below.

## 2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Configure the application

The application reads configuration from environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_PATH` | `learning_quest.db` in the project directory | SQLite database file |
| `JWT_SECRET` | Development-only fallback | Secret used to sign JWTs |
| `JWT_TTL_SECONDS` | `86400` | Token lifetime in seconds |

For local development, set a private JWT secret before starting the server:

```powershell
$env:JWT_SECRET = "replace-this-with-a-long-random-development-secret"
```

Optionally choose a different database location:

```powershell
$env:DATABASE_PATH = "C:\data\learning_quest.db"
```

These values apply to the current PowerShell window. Set them again in a new terminal.

## 4. Start the application

With the virtual environment activated:

```powershell
python -m uvicorn main:app --reload
```

Without activation:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Database setup

Database setup is automatic. On application startup, SQLAlchemy:

1. Creates the SQLite file if it does not exist.
2. Creates all required tables.
3. Seeds a `Programming Basics` roadmap with six units, resources, and test questions.

The default database file is:

```text
learning_quest.db
```

To start with a clean local database, stop the API, delete only that database file, and
start the API again. The schema and seed content will be recreated automatically.

This project currently uses automatic table creation rather than a migration tool. For a
production deployment, add Alembic before making schema changes against persistent data.

## Authentication example

Register a user from PowerShell:

```powershell
$auth = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/auth/register" `
  -ContentType "application/json" `
  -Body '{"nickname":"demo_user","password":"password123"}'
```

Use the returned JWT on a protected endpoint:

```powershell
$headers = @{ Authorization = "Bearer $($auth.token)" }
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/roadmaps" `
  -Headers $headers
```

All endpoints except `/auth/register` and `/auth/login` require:

```http
Authorization: Bearer <token>
```

The authentication middleware validates the token and stores its user ID in
`request.state.user_id`. No login cookies or HTTP sessions are used. SQLAlchemy database
sessions are short-lived database units of work and are unrelated to browser sessions.

The JetBrains HTTP client examples in `test_main.http` can also be used to call the API.

## Frontend usage

After login or registration, store the returned token and attach it to Axios requests:

```typescript
localStorage.setItem("token", response.data.token);

axios.get("http://127.0.0.1:8000/roadmaps", {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  },
});
```

If the frontend is served from another origin or port, configure FastAPI CORS middleware
for that frontend origin before making requests from the browser.

## Project structure

```text
contracts/requests/   Request bodies received by the API
contracts/responses/  Response bodies returned by the API
core/                 Internal application primitives such as Result
handlers/             FastAPI routes and HTTP-boundary handling
middleware/           JWT authentication middleware
models/               SQLAlchemy ORM entities
repositories/         Database access returning ORM entities
services/             Business logic and response-model mapping
database.py           SQLAlchemy engine and automatic database initialization
dependencies.py       FastAPI dependency-injection providers
main.py               FastAPI application entry point
```

## Production notes

- Always provide a strong `JWT_SECRET`; do not use the development fallback.
- Run without `--reload` in production.
- Restrict CORS to known frontend origins.
- Keep the SQLite database file and secrets out of source control.
- Consider PostgreSQL and Alembic when concurrency or persistent schema migrations become
  important.
