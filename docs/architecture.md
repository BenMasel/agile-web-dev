# Architecture Notes

stUwa uses Flask as a small server-rendered application with progressive client-side interactivity.

## Route Structure

The application factory is in `app/__init__.py`. It creates the Flask app, loads configuration, initialises SQLAlchemy, Flask-Login, CSRF protection, and registers the route blueprints.

Most product routes currently live in the `main` blueprint in `app/routes.py`:

- catalogue pages: home, units, degrees, clubs, resources, and benefits
- account routes: register, login, logout, and settings
- planner routes: planner page and JSON save/load/delete endpoint
- review routes: create and delete unit reviews
- public plan routes: shared plan browsing and public plan detail pages

Documentation routes live in `app/docs_bp.py`, which renders Markdown files from `docs/` at `/docs`.

## Database Models

SQLAlchemy models live in `app/models.py`.

- `User` stores UWA student account details, display name, faculty, and salted Werkzeug password hashes.
- `StudyPlan` stores a user's saved planner metadata, selected degrees, start semester, and public/private state.
- `StudyPlanUnit` stores each planned or completed unit in a saved plan, including year, semester, status, and order.
- `UnitReview` stores student reviews for unit pages.
- `NotificationPreference` stores account notification preferences for planned future persistence.

The repository includes a Flask-Migrate/Alembic baseline in `migrations/`. For local development convenience, the app also creates missing tables with SQLAlchemy `create_all()` on startup.

## YAML Catalogue

Catalogue data lives under `data/`:

- `data/units/`
- `data/degrees/`
- `data/clubs/`
- `data/benefits/`

JSON schemas in `data/schemas/` define the required fields. `scripts/validate_data.py` validates the YAML files and checks important references, including degree unit references and associated club references.

## Planner And Search

Global search uses a server-generated JSON search index and Fuse.js in the browser. This keeps searches fast and avoids extra server requests after the page loads.

The planner keeps a local browser draft in `localStorage` so guests can still build a plan. Signed-in users can save, load, delete, and publish a server-side copy through JSON requests to `/api/planner`. Those requests include the CSRF token in the `X-CSRFToken` header.

Public plans are read-only pages at `/plans/<id>`. Private plans return a 404 to other users and anonymous visitors.
