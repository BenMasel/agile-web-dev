# stUwa

> The middleman between you and your units — built by UWA students, for UWA students.

stUwa is a web app that aggregates UWA unit information, degrees, student clubs, resources, and benefits into a single searchable interface. It eliminates the need to hunt across multiple university portals by surfacing everything in one place.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
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

All content is stored as YAML files under `data/`, making it easy to add or update entries without touching application code.

---

## Getting Started

### Prerequisites

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) — Python package and project manager

### Running Locally

```bash
# 1. Clone the repository
git clone <repo-url>
cd agile-web-dev

# 2. Install dependencies
uv sync

# 3. Start the development server
uv run python run.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

> The development server runs with `debug=True`, which enables auto-reload on file changes and detailed error pages. Do not use this mode in production.

---

## Project Structure

```
agile-web-dev/
├── app/
│   ├── __init__.py        # Application factory (create_app)
│   ├── routes.py          # All route handlers and YAML data helpers
│   ├── docs_bp.py         # Docs blueprint — serves docs/ as /docs/<slug>
│   ├── db.py              # SQLite connection management
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── benefits.html
│   │   ├── resources.html
│   │   ├── docs/          # Docs page template
│   │   ├── unit/
│   │   ├── degree/
│   │   └── club/
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
| [SQLite](https://www.sqlite.org/) | Lightweight database (via Flask's `g` context) |

### Adding a documentation page

Create a new `.md` file in `docs/` — it will automatically appear in the sidebar at `/docs` with no further configuration needed. The first `# H1` in the file is used as the page title.
