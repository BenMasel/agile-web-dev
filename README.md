# stUwa

> The middleman between you and your units — built by UWA students, for UWA students.

stUwa is a web app that aggregates UWA unit information, degrees, student clubs, resources, benefits, account-backed study planning, public plan sharing, and student unit reviews into a single searchable interface. It eliminates the need to hunt across multiple university portals by surfacing everything in one place.

---

## Table of Contents

- [Overview](#overview)
- [Group Members](#group-members)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Tooling](#tooling)

---

## Overview

stUwa provides:

- **Unit pages** — credit points, level, semester, associated clubs, and curated learning resources (YouTube channels, platforms, textbooks)
- **Degree pages** — faculty, duration, and credit point requirements
- **Club pages** — descriptions, icons, and accent theming per club
- **Student benefits** — categorised discounts and perks available to UWA students
- **Global search** — client-side fuzzy search powered by [Fuse.js](https://fusejs.io/) across all units, degrees, and clubs with no round-trips to the server
- **Study planner** — an interactive planner for mapping units across semesters, tracking degree progress, syncing plans to an account, and sharing public plans
- **Accounts** — UWA student registration, login/logout, settings, and server-side persistence for planner and review data
- **Unit reviews** — student advice with rating, difficulty, workload, aggregate stats, owner delete controls, and a personal review list in settings

All content is stored as YAML files under `data/`, making it easy to add or update entries without touching application code.

The current app combines a YAML-backed catalogue with database-backed user features. Catalogue content remains easy to review in pull requests, while account data, saved plans, public plan visibility, and reviews are stored through SQLAlchemy.

---

## Group Members

| UWA ID | Name | GitHub username |
|--------|------|-----------------|
| 24357423 | Ben Masel | BenMasel |
| 24483753 | Kaushik Oril | Kaushik-Oril |
| 24518484 | Dhul Ratnayaka Ratnayaka Mudiyanselage | dhulrat |
| 24729724 | Hridayesh Sharma | Hri-Sh |

---

## Getting Started

### Prerequisites

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) — Python package and project manager

### Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/BenMasel/agile-web-dev.git
cd agile-web-dev

# 2. Install dependencies
uv sync

# 3. Create local environment config
cp .env.example .env

# 4. Apply database migrations
FLASK_APP=run.py uv run flask db upgrade

# 5. Start the development server
uv run python run.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

> The development server runs with `debug=True`, which enables auto-reload on file changes and detailed error pages. Do not use this mode in production.

### Environment Variables

The project should be configured through environment variables rather than hard-coded secrets. The expected local setup is:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session and CSRF signing key |
| `DATABASE_URL` | SQLite database path for SQLAlchemy |
| `YOUTUBE_API_KEY` | Optional YouTube Data API key for resource search |

Copy `.env.example` to `.env` and replace the placeholder values for local development.

### Database setup

The project includes a Flask-Migrate/Alembic migration baseline under `migrations/`.

```bash
# Apply database migrations
FLASK_APP=run.py uv run flask db upgrade

# Create a new migration after model changes
FLASK_APP=run.py uv run flask db migrate -m "Describe the model change"
```

For development convenience, the app also calls SQLAlchemy `create_all()` during startup so a fresh local SQLite database is created automatically if migrations have not been run yet.

---

## Running Tests

The automated test suite uses `pytest` for route, model, data validation, authentication, planner, review, and public plan coverage.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Validate YAML catalogue data
uv run python scripts/validate_data.py

# Check major pages render valid core HTML through Flask
uv run python scripts/check_rendered_pages.py
```

The repository also includes a GitHub Actions workflow at `.github/workflows/tests.yml` that installs dependencies with `uv sync` and runs `uv run pytest` on pushes and pull requests.

Selenium live-browser tests are still a later hardening step. When they are added, they should run against a live development server:

```bash
# Terminal 1
uv run python run.py

# Terminal 2
uv run pytest tests/selenium
```

Install the matching browser driver for the browser used by the Selenium tests. For Chrome-based tests, use a Chrome/Chromium version with a compatible ChromeDriver available on `PATH`; for Firefox-based tests, use GeckoDriver.

---

## Project Structure

```
agile-web-dev/
├── app/
│   ├── __init__.py        # Application factory (create_app)
│   ├── routes.py          # All route handlers and YAML data helpers
│   ├── docs_bp.py         # Docs blueprint — serves docs/ as /docs/<slug>
│   ├── models.py          # SQLAlchemy models for users, plans, reviews, preferences
│   ├── forms.py           # Flask-WTF forms and validators
│   ├── db.py              # Legacy SQLite helper retained for compatibility
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── benefits.html
│   │   ├── resources.html
│   │   ├── docs/          # Docs page template
│   │   ├── unit/
│   │   ├── degree/
│   │   ├── club/
│   │   └── plans/         # Public study plan pages
│   └── static/            # CSS, JS, icons, and images
│       ├── css/
│       ├── js/
│       ├── icons/
│       └── img/
├── data/                  # YAML content files (source of truth)
│   ├── units/             # One .yaml file per unit (e.g. CITS1001.yaml)
│   ├── degrees/           # One .yaml file per degree
│   ├── clubs/             # One .yaml file per club
│   ├── benefits/          # Student benefits data
│   └── schemas/           # JSON schemas for validating YAML files
├── docs/                  # Markdown documentation (rendered at /docs)
│   └── overview.md        # Project overview, goals, philosophy, roadmap
├── run.py                 # Entry point — creates and runs the Flask app
├── pyproject.toml         # Project metadata and dependencies
└── uv.lock                # Locked dependency versions
```

---

## Tooling

| Tool | Purpose |
|------|---------|
| [Python 3.14](https://www.python.org/) | Language runtime |
| [Flask](https://flask.palletsprojects.com/) | Web framework and routing |
| [Jinja2](https://jinja.palletsprojects.com/) | Server-side HTML templating (bundled with Flask) |
| [PyYAML](https://pyyaml.org/) | Parsing YAML content files |
| [jsonschema](https://python-jsonschema.readthedocs.io/) | Validating YAML data against schemas |
| [Python-Markdown](https://python-markdown.github.io/) | Rendering `docs/*.md` files as HTML at `/docs` |
| [uv](https://docs.astral.sh/uv/) | Dependency management and virtual environment |
| [Fuse.js](https://fusejs.io/) | Client-side fuzzy search |
| [Highlight.js](https://highlightjs.org/) | Syntax highlighting for code blocks in docs (CDN) |
| [SQLite](https://www.sqlite.org/) | Lightweight development database |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | ORM for account, planner, review, and preference models |
| [Flask-Login](https://flask-login.readthedocs.io/) | User session management |
| [Flask-WTF](https://flask-wtf.readthedocs.io/) | Forms and CSRF protection |

### Adding a documentation page

Create a new `.md` file in `docs/` — it will automatically appear in the sidebar at `/docs` with no further configuration needed. The first `# H1` in the file is used as the page title.
