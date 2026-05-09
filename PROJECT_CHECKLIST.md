# stUwa Project Checklist

This checklist maps the CITS3403 group project brief against the current stUwa Flask app. The app direction is a UWA student companion for searching units, browsing degree requirements, building a study planner, finding resources, seeing student benefits, and adding community knowledge around units.

## Progress Summary

- Last checked: 7 May 2026.
- Completion: **69** checked items out of **383** total checklist items (**18.0%**).
- Status note: The catalogue/search/planner/resources/benefits/docs frontend is in place, and real account registration/login/logout now works with SQLAlchemy, Flask-Login, Flask-WTF CSRF, and salted Werkzeug password hashes. The main remaining project risk is server-side planner persistence, shared user-generated data, broader model coverage, tests, and README/process evidence.

## Brief Requirements Snapshot

- [x] Client-server web application using Flask, HTML, CSS, JavaScript, and an allowed CSS framework.
- [x] User login and logout.
- [x] User data persisted between sessions.
- [ ] Users can view data from other users in some manner.
- [x] SQLite database accessed through SQLAlchemy.
- [x] Good navigation, useful purpose, intuitive UI, and strong visual design.
- [x] Valid, organised HTML with meaningful Jinja templates.
- [x] Maintainable responsive CSS using allowed framework/custom classes.
- [ ] Well formatted JavaScript with validation, DOM manipulation, and AJAX where appropriate.
- [x] Flask code performs non-trivial request handling, data manipulation, and page generation.
- [ ] Well considered database schema, authentication, and evidence of migrations.
- [ ] 5+ unit tests and 5+ Selenium tests against a live server.
- [x] Salted password hashes, CSRF protection for forms, and environment variable configuration.
- [ ] Public GitHub repo with README containing app purpose, group member table, launch instructions, and test instructions.
- [ ] Regular GitHub Issues, Pull Requests, commits, reviews, and checkpoint evidence.

## Current Repo State

- [x] Flask application factory in `app/__init__.py`.
- [x] Route blueprint in `app/routes.py`.
- [x] YAML-backed unit, degree, club, benefit, and docs content.
- [x] Jinja template structure with shared `base.html`, navbar, account menu, context menu, and page templates.
- [x] Client-side global search using Fuse.js.
- [x] Study planner UI with localStorage persistence.
- [x] Resources page using planner state and YouTube/channel metadata.
- [x] Benefits page with category filters.
- [x] Docs section rendered from Markdown.
- [x] Basic `/api/onboarding-data` JSON endpoint used by the onboarding modal.
- [x] `.gitignore` excludes `.env`, local config, `instance/`, SQLite files, Python caches, and `.venv`.
- [x] `run.py` launches the Flask app through the application factory.
- [x] Real authentication with register, login, logout, Flask-Login sessions, and hashed passwords.
- [x] SQLAlchemy `User` model and SQLite connection configured through Flask-SQLAlchemy.
- [ ] Server-side persistence for planner/settings/reviews.
- [ ] Shared user-visible data. Current content is global YAML, not user-generated/user-owned data.
- [ ] Tests.
- [ ] CSRF protection.
- [ ] README group member table and test instructions.
- [ ] Data schemas referenced by docs but not present in the repo.

## Phase 1: Scope And Team Setup

- [x] Confirm the final product statement: "stUwa helps UWA students plan their degree, save their study progress, and share unit advice with other students."
- [ ] Decide the minimum viable project features for marking:
  - [x] Search/browse units, degrees, clubs, benefits, and resources.
  - [x] Register, login, logout, and account settings.
  - [ ] Save a personal study plan to the database.
  - [x] Mark completed units and persist them between sessions.
  - [ ] Share a public study plan or profile summary.
  - [ ] Add unit reviews/comments visible to other users.
- [ ] Create GitHub Issues for each checklist section or major feature.
- [ ] Assign each issue to a group member.
- [ ] Agree on branch naming, PR review rules, and commit message style.
- [ ] Make sure every team member has correct Git config:
  - [ ] `git config user.name`
  - [ ] `git config user.email`
- [ ] Add checkpoint notes to `docs/` or GitHub Issues so process work is visible.

## Phase 2: Project Structure And Configuration

- [ ] Add a real configuration layer:
  - [x] `config.py` with development, testing, and production config classes.
  - [x] `SECRET_KEY` loaded from environment variables.
  - [x] `DATABASE_URL` or SQLite path loaded from environment variables.
  - [ ] YouTube API key loaded from environment variables instead of committed JS config.
- [x] Add `.env.example` documenting required environment variables.
- [ ] Add `.gitignore` entries for `.env`, `instance/`, SQLite files, generated coverage, and local browser test output.
- [ ] Replace or expand `app/db.py` so database access goes through SQLAlchemy.
- [ ] Decide whether to use:
  - [x] Flask-SQLAlchemy for models and sessions.
  - [ ] Flask-Migrate/Alembic for migrations.
  - [x] Flask-Login for session management.
  - [x] Flask-WTF for CSRF-protected forms.
- [x] Keep Tailwind as the CSS framework because it is allowed by the brief and already used.
- [ ] Remove unused placeholder entry points if they cause confusion:
  - [ ] Either make `main.py` launch the app or document that `run.py` is the app entry point.

## Phase 3: Database Models

- [ ] Design the SQLite schema using SQLAlchemy models.
- [x] Add `User` model:
  - [x] `id`
  - [x] `email`
  - [x] `student_id`
  - [x] `display_name`
  - [x] `password_hash`
  - [x] `faculty`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Add `StudyPlan` model:
  - [x] `id`
  - [x] `user_id`
  - [x] `name`
  - [x] `primary_degree_slug`
  - [x] `secondary_degree_slug`
  - [x] `start_year`
  - [x] `start_semester`
  - [x] `is_public`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Add `StudyPlanUnit` model:
  - [x] `id`
  - [x] `study_plan_id`
  - [x] `unit_code`
  - [x] `year`
  - [x] `semester`
  - [x] `status` such as planned, completed, removed.
  - [x] `position`
- [x] Add `UnitReview` model:
  - [x] `id`
  - [x] `user_id`
  - [x] `unit_code`
  - [x] `rating`
  - [x] `difficulty`
  - [x] `workload_hours`
  - [x] `semester_taken`
  - [x] `body`
  - [x] `created_at`
  - [x] `updated_at`
- [ ] Add `SavedBenefit` or `SavedResource` model if time allows:
  - [ ] Let users bookmark student benefits/resources.
  - [ ] Persist these bookmarks between sessions.
- [x] Add `NotificationPreference` model or JSON column:
  - [x] Planner reminders.
  - [x] Unit catalogue updates.
  - [x] Review replies or community replies.
  - [x] Weekly digest preference.
- [ ] Create initial migration.
- [ ] Add seed/demo data for development and testing.
- [ ] Document migration commands in the README.

## Phase 4: Authentication And Account Flow

- [x] Replace the frontend-only `/auth` stub with real backend forms.
- [x] Implement register:
  - [x] Validate `@student.uwa.edu.au` email.
  - [x] Validate student ID format.
  - [x] Validate password length and confirmation.
  - [x] Store passwords using Werkzeug salted password hashing.
  - [x] Prevent duplicate emails.
  - [x] Show useful form errors.
- [x] Implement login:
  - [x] Check email and password.
  - [x] Start a Flask-Login session.
  - [x] Redirect logged-in users back to planner/settings.
- [x] Implement logout:
  - [x] Add `/logout` route.
  - [x] Add logout option in account menu/navbar.
- [x] Implement authenticated account state:
  - [x] Navbar avatar shows initials/display name when signed in.
  - [x] Settings page shows saved account information.
  - [x] Auth page redirects if already logged in.
- [ ] Add CSRF protection to register, login, settings, review, planner save, and delete forms.
- [ ] Add password change or account edit if time allows.
- [ ] Add graceful handling for unauthenticated users:
  - [ ] Planner can still work locally.
  - [ ] Prompt users to sign in to sync/save server-side.

## Phase 5: Persist The Planner Server-Side

- [ ] Audit current planner localStorage shape in `app/templates/planner.html`.
- [ ] Create JSON API endpoints:
  - [ ] `GET /api/plans`
  - [ ] `POST /api/plans`
  - [ ] `GET /api/plans/<id>`
  - [ ] `PUT /api/plans/<id>`
  - [ ] `DELETE /api/plans/<id>`
  - [ ] `POST /api/plans/<id>/units`
  - [ ] `PATCH /api/plans/<id>/units/<unit_id>`
  - [ ] `DELETE /api/plans/<id>/units/<unit_id>`
- [ ] Require login for server-side plan save/update/delete.
- [ ] Keep localStorage as offline/guest draft storage.
- [ ] Add "Save to account" button on planner.
- [ ] Add "Load saved plan" control on planner.
- [ ] Add "Make public" toggle on planner.
- [ ] Add "Copy share link" for public plans.
- [ ] Add public plan page:
  - [ ] `/plans/<id>` or `/u/<username>/plans/<id>`.
  - [ ] Shows degree selections, planned units, completed units, and credits.
  - [ ] Hides private plans.
- [ ] Add conflict/prerequisite validation server-side so important rules are not only client-side.
- [ ] Add AJAX fetch calls with loading, success, and error states.

## Phase 6: Shared User Data And Community Features

- [ ] Add unit reviews to satisfy "users can view data from other users".
- [ ] Add review form on `app/templates/unit/detail.html`:
  - [ ] Rating.
  - [ ] Difficulty.
  - [ ] Workload estimate.
  - [ ] Semester taken.
  - [ ] Short written advice.
- [ ] Require login to create/edit/delete a review.
- [ ] Allow anyone to view approved/public reviews on unit pages.
- [ ] Show aggregate review data on unit pages:
  - [ ] Average rating.
  - [ ] Average difficulty.
  - [ ] Review count.
  - [ ] Common workload range.
- [ ] Add "My reviews" section in settings.
- [ ] Add edit/delete review controls for the review owner.
- [ ] Add basic moderation guardrails:
  - [ ] Character limits.
  - [ ] Empty/abusive placeholder validation.
  - [ ] Hide emails from public review display.
- [ ] Add public/shared study plan browsing if time allows:
  - [ ] "Shared Plans" page.
  - [ ] Filter by degree.
  - [ ] Link from unit pages to public plans containing that unit.

## Phase 7: Existing Feature Hardening

- [ ] Home/search:
  - [x] Ensure search result HTML is accessible and keyboard navigation works across browsers.
  - [ ] Add no-JavaScript fallback or graceful empty state.
  - [ ] Avoid duplicate Fuse.js script loading in `base.html` and `home.html`.
- [ ] Unit pages:
  - [ ] Add review/community section.
  - [ ] Show whether current user has planned/completed the unit.
  - [ ] Add "Add to planner" action for authenticated users.
- [ ] Degree pages:
  - [ ] Add call-to-action to create a plan from a degree.
  - [x] Show units grouped by year/semester from YAML data.
  - [ ] Link to public plans for the degree if implemented.
- [ ] Club pages:
  - [ ] Link clubs to related units and resources.
  - [ ] Add richer event/contact fields if available.
- [ ] Resources page:
  - [ ] Move `CONFIG.YOUTUBE_API_KEY` handling out of client-side committed files.
  - [ ] Add backend proxy endpoint for YouTube search if API keys must be hidden.
  - [ ] Show helpful setup message when API key is missing in development.
  - [ ] Persist saved/bookmarked resources for logged-in users if implemented.
- [ ] Benefits page:
  - [ ] Add "save benefit" for logged-in users if implemented.
  - [ ] Replace placeholder disclaimer data with verified entries or clearly label demo data.
- [ ] Settings page:
  - [x] Persist notification preferences to the database.
  - [x] Add import plan JSON if export remains.
  - [ ] Add account deletion or data clearing for logged-in users if time allows.
- [ ] Docs:
  - [ ] Update docs to match implemented database-backed behaviour.
  - [ ] Add schema docs for SQLAlchemy models.
  - [ ] Fix data schema docs if `data/schemas/` remains absent, or add the schema files.

## Phase 8: HTML, CSS, And Design Quality

- [ ] Validate rendered HTML for major pages:
  - [ ] Home.
  - [ ] Planner.
  - [ ] Unit detail.
  - [ ] Degree detail.
  - [ ] Resources.
  - [ ] Benefits.
  - [ ] Auth.
  - [ ] Settings.
- [ ] Review Jinja templates for repeated UI that should become components:
  - [ ] Form field component.
  - [ ] Flash message component.
  - [ ] Review card component.
  - [ ] Plan unit chip/card component.
- [ ] Ensure responsive layouts work on mobile, tablet, and desktop.
- [ ] Add visible focus states to interactive controls.
- [ ] Add labels or `aria-label` attributes for icon-only buttons.
- [ ] Replace inline SVG duplication with reusable components where practical.
- [ ] Keep Tailwind/custom CSS maintainable and avoid page-specific hacks where reusable utilities/components fit.
- [ ] Ensure text contrast is acceptable against the dark theme.
- [ ] Ensure buttons and links have clear hover/active/disabled states.

## Phase 9: JavaScript And AJAX Quality

- [ ] Split large inline scripts out of templates where practical:
  - [ ] Planner JS into `app/static/js/planner.js`.
  - [ ] Auth JS into `app/static/js/auth.js` if still needed.
  - [ ] Settings JS into `app/static/js/settings.js`.
- [ ] Add client-side validation for:
  - [ ] Registration.
  - [ ] Login.
  - [ ] Planner save/share.
  - [ ] Unit review submission.
  - [ ] Settings updates.
- [ ] Add AJAX helper for JSON requests with CSRF token support.
- [ ] Handle API errors consistently with visible page feedback.
- [ ] Keep server-side validation authoritative for all submitted data.
- [ ] Avoid exposing secrets in static JavaScript.
- [ ] Add debounce/throttle where user input triggers network calls.

## Phase 10: Flask Code Quality

- [ ] Split `app/routes.py` into focused blueprints:
  - [ ] `main` for home/catalogue.
  - [ ] `auth` for register/login/logout.
  - [ ] `planner` for planner pages and APIs.
  - [ ] `reviews` for unit review APIs.
  - [ ] `docs` already exists.
- [ ] Add `app/models.py` for SQLAlchemy models.
- [ ] Add `app/forms.py` for Flask-WTF forms.
- [ ] Add `app/services/` helpers for:
  - [ ] Loading YAML catalogue data.
  - [ ] Planner validation.
  - [ ] Review aggregation.
  - [ ] YouTube/resource search if proxied.
- [x] Keep YAML loading cached where safe.
- [ ] Add error handlers for 400, 403, 404, and 500.
- [ ] Add flash messages for form actions.
- [ ] Ensure all route functions return the right status codes.
- [ ] Add logging for important failures without leaking secrets.

## Phase 11: Data Integrity

- [ ] Add JSON schemas under `data/schemas/` or update docs if schema validation will not be used.
- [ ] Add validation script for YAML content:
  - [ ] Units.
  - [ ] Degrees.
  - [ ] Clubs.
  - [ ] Benefits.
- [ ] Add tests for YAML loader and search index generation.
- [ ] Check all YAML links, URLs, and unit references.
- [ ] Ensure planner units referenced by degrees exist in `data/units`.
- [ ] Ensure associated clubs referenced by units exist in `data/clubs`.
- [ ] Add official source URLs and last verified dates for unit data.
- [ ] Replace any known placeholder/inaccurate benefit data before final submission.

## Phase 12: Testing

- [x] Set up pytest dependency.
- [x] Add test configuration using an isolated in-memory SQLite database.
- [x] Add fixtures for app, client, and database.
- [ ] Unit tests, minimum 5:
  - [ ] Home route returns 200 and contains search data.
  - [ ] Unit detail route returns correct unit page and 404 for missing unit.
  - [x] Registration model support creates a user with a hashed password.
  - [ ] Login/logout changes session state correctly.
  - [ ] Planner API saves and reloads a user plan.
  - [ ] Unit review aggregation calculates average rating/difficulty.
  - [x] Onboarding/catalogue API includes units and degrees.
- [ ] Selenium tests, minimum 5, running against a live server:
  - [ ] User can register, log in, and log out.
  - [ ] User can search for a unit and open its detail page.
  - [ ] User can create/save a study plan and reload it after login.
  - [ ] User can submit a unit review and another browser/session can view it.
  - [ ] User can make a plan public and open the share link.
  - [ ] Resources/benefits navigation works on mobile viewport.
- [ ] Add test command to README.
- [ ] Add coverage command if time allows.
- [ ] Add CI workflow if time allows:
  - [ ] Install with `uv sync`.
  - [ ] Run lint/format checks.
  - [ ] Run unit tests.

## Phase 13: Security

- [ ] Store passwords only as salted hashes.
- [ ] Add CSRF protection to all state-changing forms and AJAX requests.
- [ ] Store secret keys and API keys in environment variables.
- [ ] Never commit `.env`, SQLite production data, or API keys.
- [ ] Use `login_required` on private routes.
- [ ] Enforce ownership checks:
  - [ ] Users can only edit/delete their own plans.
  - [ ] Users can only edit/delete their own reviews.
  - [ ] Private plans are not visible to other users.
- [ ] Escape user-generated content in templates.
- [ ] Validate all form and JSON input server-side.
- [ ] Rate-limit or add basic protection to login if time allows.
- [ ] Use secure session config for non-debug deployment notes.

## Phase 14: README And Documentation

- [ ] Update README purpose section to match final app.
- [ ] Add required group member table:
  - [ ] UWA ID.
  - [ ] Name.
  - [ ] GitHub username.
- [ ] Keep launch instructions current:
  - [ ] Install `uv`.
  - [ ] Copy `.env.example` to `.env`.
  - [ ] Run migrations.
  - [ ] Seed database if needed.
  - [ ] Start with `uv run python run.py`.
- [ ] Add test instructions:
  - [ ] Unit tests.
  - [ ] Selenium tests.
  - [ ] Any required browser driver setup.
- [ ] Add migration instructions.
- [ ] Add screenshots or short usage walkthrough if time allows.
- [ ] Update `docs/overview.md` with final implemented features.
- [ ] Update `docs/roadmap.md` so completed features are not described as future work.
- [ ] Add architecture notes:
  - [ ] Flask blueprints.
  - [ ] SQLAlchemy models.
  - [ ] YAML catalogue content.
  - [ ] Client-side planner/search behaviour.

## Phase 15: GitHub Agile Evidence

- [ ] Use GitHub Issues for each feature, bug, and checklist chunk.
- [ ] Make issues specific and testable.
- [ ] For bugs, include reproduction steps, expected result, and actual result.
- [ ] Use PRs for all non-trivial changes.
- [ ] Give PRs meaningful names such as "Add SQLAlchemy user model and auth flow".
- [ ] Link PRs to Issues.
- [ ] Add screenshots or short screen recordings to UI PRs.
- [ ] Review teammates' PRs with concrete feedback.
- [ ] Respond to review comments before merging.
- [ ] Keep commits regular and scoped.
- [ ] Avoid one giant final commit.
- [ ] Track checkpoint meeting outcomes in Issues, PRs, or docs.

## Phase 16: Final Polish And Submission Readiness

- [ ] Run full unit test suite.
- [ ] Run full Selenium suite against a live server.
- [ ] Manually test the main user journeys:
  - [x] Browse/search catalogue.
  - [ ] Register/login/logout.
  - [ ] Save and reload planner.
  - [ ] Share public plan.
  - [ ] Submit/view unit review.
  - [ ] Update settings.
  - [x] Browse resources and benefits.
- [ ] Test on desktop and mobile widths.
- [ ] Check all external links.
- [ ] Check empty/error/loading states.
- [ ] Check database migration from a clean checkout.
- [ ] Confirm no secrets are committed.
- [ ] Confirm README launch and test commands work from a fresh clone.
- [ ] Tag or mark the final submission commit.
- [ ] Prepare presentation demo flow:
  - [ ] Problem: UWA information is scattered.
  - [ ] Solution: stUwa centralises catalogue, planning, resources, and community advice.
  - [ ] Demo account login.
  - [ ] Search a unit.
  - [ ] Build/save a study plan.
  - [ ] Share public plan.
  - [ ] Add/view a unit review from another user.
  - [ ] Show tests and GitHub collaboration evidence.

## Recommended MVP Order

1. [ ] SQLAlchemy setup, migrations, config, and test database.
2. [ ] Real registration/login/logout with CSRF and password hashing.
3. [ ] Persist planner to the database for logged-in users.
4. [ ] Public plan sharing.
5. [ ] Unit reviews visible to other users.
6. [ ] Tests: at least 5 unit tests and 5 Selenium tests.
7. [ ] README and GitHub process cleanup.
8. [ ] UI polish, accessibility, and final presentation flow.
