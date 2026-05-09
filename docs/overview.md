# Overview

stUwa is a student-built web application that acts as a middleman between UWA students and the information they need about their degree. Rather than navigating multiple university portals and scattered resources, students get one fast, searchable interface.

---

## Goals

- **Reduce friction** — surface unit details, degree requirements, clubs, resources, benefits, and peer reviews in one place
- **Stay accurate** — all content lives in version-controlled YAML files that any contributor can update via a pull request
- **Stay fast** — search is client-side (Fuse.js), so there are no round-trips to a server after the page loads
- **Stay open** — the project is fully open-source; UWA students are both the users and the contributors

---

## Philosophy

### Data as content

Rather than storing information in a database that only maintainers can edit, all unit, degree, club, and benefit data lives in human-readable YAML files under `data/`. Adding a new unit is as simple as creating a `.yaml` file and opening a pull request.

### No framework lock-in on the frontend

The frontend is plain HTML and CSS with [Tailwind CSS](https://tailwindcss.com/) loaded from a CDN. JavaScript is only used where interactivity genuinely adds value (search, pin state, keyboard navigation). There is no JavaScript build step.

### Lightweight by default

The backend is Flask with SQLAlchemy for account and community data. Catalogue content stays in YAML so most content updates remain simple pull requests, while user-owned data can be stored safely in SQLite.

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

- **Server-side study plans** — save, reload, delete, and optionally share plans from authenticated accounts
- **Review management** — let students manage their own reviews and show aggregate review data
- **Migrations** — add a repeatable Flask-Migrate setup for clean database creation and upgrades

### Medium-term

- **Timetable clash detection** — flag units that run in conflicting time slots
- **Prerequisite graph** — visual map of prerequisite chains for a given degree
- **Contribution workflow** — in-app form to suggest corrections to unit data, which opens a GitHub PR automatically

### Long-term

- **Mobile app** — React Native wrapper around the same data API
- **Notifications** — opt-in alerts for unit changes, new resources, and exam schedule updates
