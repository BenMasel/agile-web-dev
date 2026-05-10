# Overview

stUwa is a student-built web application that acts as a middleman between UWA students and the information they need about their degree. Rather than navigating multiple university portals and scattered resources, students get one fast, searchable interface.

---

## Goals

- **Reduce friction** — surface unit details, degree requirements, clubs, resources, benefits, saved plans, public plans, and peer reviews in one place
- **Stay accurate** — all content lives in version-controlled YAML files that any contributor can update via a pull request
- **Stay fast** — search and planner interactions are client-side first, with account sync added only where persistence is useful
- **Stay open** — the project is fully open-source; UWA students are both the users and the contributors

---

## Philosophy

### Data as content

Rather than storing information in a database that only maintainers can edit, all unit, degree, club, and benefit data lives in human-readable YAML files under `data/`. Adding a new unit is as simple as creating a `.yaml` file and opening a pull request.

### No framework lock-in on the frontend

The frontend is plain HTML and CSS with [Tailwind CSS](https://tailwindcss.com/) loaded from a CDN. JavaScript is used where interactivity genuinely adds value: Fuse.js search, planner drag/drop, localStorage persistence, account sync, and share-link controls. There is no JavaScript build step.

### Lightweight by default

The backend is Flask with SQLAlchemy for account, planner, review, and preference data. Catalogue content stays in YAML so most content updates remain simple pull requests, while user-owned data can be stored safely in SQLite.

---

## Current Architecture

The Flask application factory lives in `app/__init__.py`. Most site routes currently live in `app/routes.py`, while the Markdown documentation area is served through the separate `docs` blueprint in `app/docs_bp.py`.

SQLAlchemy models live in `app/models.py`:

- `User` stores account identity, hashed passwords, and profile fields.
- `StudyPlan` stores one saved plan per user flow, including degree selection and public/private visibility.
- `StudyPlanUnit` stores planned or completed units with year, semester, status, and display order.
- `UnitReview` stores student reviews for unit pages and aggregate review stats.
- `NotificationPreference` stores the notification preference schema, ready for future persistence UI work.

YAML catalogue content remains the source of truth for units, degrees, clubs, benefits, and documentation-adjacent content. JSON schemas in `data/schemas/` and `scripts/validate_data.py` validate the catalogue and cross-reference unit/club links.

The planner is client-side first. It keeps a local browser draft in `localStorage`, lets users drag units between semesters, tracks completed units, and uses JSON fetch requests with CSRF headers to save/load/delete the authenticated account copy. Public plan sharing stores the public flag server-side and exposes read-only shared plan pages.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.14 + Flask |
| Database | SQLite + SQLAlchemy |
| Authentication | Flask-Login + Flask-WTF |
| Templating | Jinja2 |
| Styling | Tailwind CSS (browser build v4) |
| Search | Fuse.js (client-side) |
| Content | YAML files |
| Package manager | uv |

---

## Roadmap

### Near-term

- **Selenium coverage** — add live-browser tests for the main assessed journeys
- **Frontend quality sweep** — improve focus states, responsive checks, no-JavaScript empty states, and API key handling

### Medium-term

- **Timetable clash detection** — flag units that run in conflicting time slots
- **Prerequisite graph** — visual map of prerequisite chains for a given degree
- **Contribution workflow** — in-app form to suggest corrections to unit data, which opens a GitHub PR automatically

### Long-term

- **Mobile app** — React Native wrapper around the same data API
- **Notifications** — opt-in alerts for unit changes, new resources, and exam schedule updates
