# stUwa Project Checklist

This checklist maps the CITS3403 group project brief against the current stUwa Flask app. The app direction is a UWA student companion for searching units, browsing degree requirements, building a study planner, finding resources, seeing student benefits, and adding community knowledge around units.

## Progress Summary

- Last checked: 8 May 2026.
- Completion: **265** checked items out of **383** total checklist items (**69.2%**).
- Status note: The catalogue/search/planner/resources/benefits/docs frontend is in place, and real account registration/login/logout now works with SQLAlchemy, Flask-Login, Flask-WTF CSRF, and salted Werkzeug password hashes. The main remaining project risk is server-side planner persistence, shared user-generated data, broader model coverage, tests, and README/process evidence.

## Brief Requirements Snapshot

- [x] Client-server web application using Flask, HTML, CSS, JavaScript, and an allowed CSS framework.
- [x] User login and logout.
- [x] User data persisted between sessions.
- [x] Users can view data from other users in some manner.
- [x] SQLite database accessed through SQLAlchemy.
- [x] Good navigation, useful purpose, intuitive UI, and strong visual design.
- [x] Valid, organised HTML with meaningful Jinja templates.
- [x] Maintainable responsive CSS using allowed framework/custom classes.
- [x] Well formatted JavaScript with validation, DOM manipulation, and AJAX where appropriate.
- [x] Flask code performs non-trivial request handling, data manipulation, and page generation.
- [x] Well considered database schema, authentication, and evidence of migrations.
- [ ] 5+ unit tests and 5+ Selenium tests against a live server.
- [x] Salted password hashes, CSRF protection for forms, and environment variable configuration.
- [x] Public GitHub repo with README containing app purpose, group member table, launch instructions, and test instructions.
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
- [x] Server-side persistence for planner/settings/reviews.
- [x] Shared user-visible data. Current content is global YAML, not user-generated/user-owned data.
- [x] Tests.
- [x] CSRF protection.
- [x] README group member table and test instructions.
- [x] Data schemas referenced by docs but not present in the repo.

## Phase 1: Scope And Team Setup

- [x] Confirm the final product statement: "stUwa helps UWA students plan their degree, save their study progress, and share unit advice with other students."
- [ ] Decide the minimum viable project features for marking:
  - [x] Search/browse units, degrees, clubs, benefits, and resources.
  - [x] Register, login, logout, and account settings.
  - [x] Save a personal study plan to the database.
  - [x] Mark completed units and persist them between sessions.
  - [x] Share a public study plan or profile summary.
  - [x] Add unit reviews/comments visible to other users.
- [ ] Create GitHub Issues for each checklist section or major feature.
- [ ] Assign each issue to a group member.
- [ ] Agree on branch naming, PR review rules, and commit message style.
- [ ] Make sure every team member has correct Git config:
  - [ ] `git config user.name`
  - [ ] `git config user.email`
- [x] Add checkpoint notes to `docs/` or GitHub Issues so process work is visible.

## Phase 2: Project Structure And Configuration

- [x] Add a real configuration layer:
  - [x] `config.py` with development, testing, and production config classes.
  - [x] `SECRET_KEY` loaded from environment variables.
  - [x] `DATABASE_URL` or SQLite path loaded from environment variables.
  - [x] YouTube API key loaded from environment variables instead of committed JS config.
- [x] Add `.env.example` documenting required environment variables.
- [x] Add `.gitignore` entries for `.env`, `instance/`, SQLite files, generated coverage, and local browser test output.
- [ ] Replace or expand `app/db.py` so database access goes through SQLAlchemy.
- [x] Decide whether to use:
  - [x] Flask-SQLAlchemy for models and sessions.
  - [x] Flask-Migrate/Alembic for migrations.
  - [x] Flask-Login for session management.
  - [x] Flask-WTF for CSRF-protected forms.
- [x] Keep Tailwind as the CSS framework because it is allowed by the brief and already used.
- [x] Remove unused placeholder entry points if they cause confusion:
  - [x] Either make `main.py` launch the app or document that `run.py` is the app entry point.

## Phase 3: Database Models

- [x] Design the SQLite schema using SQLAlchemy models.
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
- [x] Create initial migration.
- [ ] Add seed/demo data for development and testing.
- [x] Document migration commands in the README.

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
- [x] Add CSRF protection to register, login, settings, review, planner save, and delete forms.
- [x] Add password change or account edit if time allows.
- [x] Add graceful handling for unauthenticated users:
  - [x] Planner can still work locally.
  - [x] Prompt users to sign in to sync/save server-side.

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
- [x] Require login for server-side plan save/update/delete.
- [x] Keep localStorage as offline/guest draft storage.
- [x] Add "Save to account" button on planner.
- [x] Add "Load saved plan" control on planner.
- [x] Add "Make public" toggle on planner.
- [x] Add "Copy share link" for public plans.
- [x] Add public plan page:
  - [x] `/plans/<id>` or `/u/<username>/plans/<id>`.
  - [x] Shows degree selections, planned units, completed units, and credits.
  - [x] Hides private plans.
- [ ] Add conflict/prerequisite validation server-side so important rules are not only client-side.
- [x] Add AJAX fetch calls with loading, success, and error states.

## Phase 6: Shared User Data And Community Features

- [x] Add unit reviews to satisfy "users can view data from other users".
- [x] Add review form on `app/templates/unit/detail.html`:
  - [x] Rating.
  - [x] Difficulty.
  - [x] Workload estimate.
  - [x] Semester taken.
  - [x] Short written advice.
- [x] Require login to create/edit/delete a review.
- [x] Allow anyone to view approved/public reviews on unit pages.
- [x] Show aggregate review data on unit pages:
  - [x] Average rating.
  - [x] Average difficulty.
  - [x] Review count.
  - [x] Common workload range.
- [x] Add "My reviews" section in settings.
- [x] Add edit/delete review controls for the review owner.
- [x] Add basic moderation guardrails:
  - [x] Character limits.
  - [x] Empty/abusive placeholder validation.
  - [x] Hide emails from public review display.
- [x] Add public/shared study plan browsing if time allows:
  - [x] "Shared Plans" page.
  - [x] Filter by degree.
  - [ ] Link from unit pages to public plans containing that unit.

## Phase 7: Existing Feature Hardening

- [ ] Home/search:
  - [x] Ensure search result HTML is accessible and keyboard navigation works across browsers.
  - [ ] Add no-JavaScript fallback or graceful empty state.
  - [x] Avoid duplicate Fuse.js script loading in `base.html` and `home.html`.
- [ ] Unit pages:
  - [x] Add review/community section.
  - [ ] Show whether current user has planned/completed the unit.
  - [ ] Add "Add to planner" action for authenticated users.
- [ ] Degree pages:
  - [x] Add call-to-action to create a plan from a degree.
  - [x] Show units grouped by year/semester from YAML data.
  - [x] Link to public plans for the degree if implemented.
- [ ] Club pages:
  - [ ] Link clubs to related units and resources.
  - [ ] Add richer event/contact fields if available.
- [ ] Resources page:
  - [x] Move `CONFIG.YOUTUBE_API_KEY` handling out of client-side committed files.
  - [x] Add backend proxy endpoint for YouTube search if API keys must be hidden.
  - [x] Show helpful setup message when API key is missing in development.
  - [ ] Persist saved/bookmarked resources for logged-in users if implemented.
- [ ] Benefits page:
  - [ ] Add "save benefit" for logged-in users if implemented.
  - [ ] Replace placeholder disclaimer data with verified entries or clearly label demo data.
- [ ] Settings page:
  - [ ] Persist notification preferences to the database.
  - [x] Add import plan JSON if export remains.
  - [ ] Add account deletion or data clearing for logged-in users if time allows.
- [x] Docs:
  - [x] Update docs to match implemented database-backed behaviour.
  - [x] Add schema docs for SQLAlchemy models.
  - [x] Fix data schema docs if `data/schemas/` remains absent, or add the schema files.

## Phase 8: HTML, CSS, And Design Quality

- [x] Validate rendered HTML for major pages:
  - [x] Home.
  - [x] Planner.
  - [x] Unit detail.
  - [x] Degree detail.
  - [x] Resources.
  - [x] Benefits.
  - [x] Auth.
  - [x] Settings.
- [ ] Review Jinja templates for repeated UI that should become components:
  - [ ] Form field component.
  - [ ] Flash message component.
  - [ ] Review card component.
  - [ ] Plan unit chip/card component.
- [ ] Ensure responsive layouts work on mobile, tablet, and desktop.
- [x] Add visible focus states to interactive controls.
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
- [x] Add AJAX helper for JSON requests with CSRF token support.
- [x] Handle API errors consistently with visible page feedback.
- [x] Keep server-side validation authoritative for all submitted data.
- [x] Avoid exposing secrets in static JavaScript.
- [ ] Add debounce/throttle where user input triggers network calls.

## Phase 10: Flask Code Quality

- [ ] Split `app/routes.py` into focused blueprints:
  - [ ] `main` for home/catalogue.
  - [ ] `auth` for register/login/logout.
  - [ ] `planner` for planner pages and APIs.
  - [ ] `reviews` for unit review APIs.
  - [ ] `docs` already exists.
- [x] Add `app/models.py` for SQLAlchemy models.
- [x] Add `app/forms.py` for Flask-WTF forms.
- [ ] Add `app/services/` helpers for:
  - [ ] Loading YAML catalogue data.
  - [ ] Planner validation.
  - [ ] Review aggregation.
  - [ ] YouTube/resource search if proxied.
- [x] Keep YAML loading cached where safe.
- [x] Add error handlers for 400, 403, 404, and 500.
- [x] Add flash messages for form actions.
- [x] Ensure all route functions return the right status codes.
- [x] Add logging for important failures without leaking secrets.

## Phase 11: Data Integrity

- [x] Add JSON schemas under `data/schemas/` or update docs if schema validation will not be used.
- [x] Add validation script for YAML content:
  - [x] Units.
  - [x] Degrees.
  - [x] Clubs.
  - [x] Benefits.
- [x] Add tests for YAML loader and search index generation.
- [x] Check all YAML links, URLs, and unit references.
- [x] Ensure planner units referenced by degrees exist in `data/units`.
- [x] Ensure associated clubs referenced by units exist in `data/clubs`.
- [x] Add official source URLs and last verified dates for unit data.
- [ ] Replace any known placeholder/inaccurate benefit data before final submission.

## Phase 12: Testing

- [x] Set up pytest dependency.
- [x] Add test configuration using an isolated in-memory SQLite database.
- [x] Add fixtures for app, client, and database.
- [x] Unit tests, minimum 5:
  - [x] Home route returns 200 and contains search data.
  - [x] Unit detail route returns correct unit page and 404 for missing unit.
  - [x] Registration model support creates a user with a hashed password.
  - [x] Login/logout changes session state correctly.
  - [x] Planner API saves and reloads a user plan.
  - [x] Unit review aggregation calculates average rating/difficulty.
  - [x] Onboarding/catalogue API includes units and degrees.
- [ ] Selenium tests, minimum 5, running against a live server:
  - [ ] User can register, log in, and log out.
  - [ ] User can search for a unit and open its detail page.
  - [ ] User can create/save a study plan and reload it after login.
  - [ ] User can submit a unit review and another browser/session can view it.
  - [ ] User can make a plan public and open the share link.
  - [ ] Resources/benefits navigation works on mobile viewport.
- [x] Add test command to README.
- [ ] Add coverage command if time allows.
- [x] Add CI workflow if time allows:
  - [x] Install with `uv sync`.
  - [ ] Run lint/format checks.
  - [x] Run unit tests.

## Phase 13: Security

- [x] Store passwords only as salted hashes.
- [x] Add CSRF protection to all state-changing forms and AJAX requests.
- [x] Store secret keys and API keys in environment variables.
- [x] Never commit `.env`, SQLite production data, or API keys.
- [x] Use `login_required` on private routes.
- [x] Enforce ownership checks:
  - [x] Users can only edit/delete their own plans.
  - [x] Users can only edit/delete their own reviews.
  - [x] Private plans are not visible to other users.
- [x] Escape user-generated content in templates.
- [x] Validate all form and JSON input server-side.
- [ ] Rate-limit or add basic protection to login if time allows.
- [x] Use secure session config for non-debug deployment notes.

## Phase 14: README And Documentation

- [x] Update README purpose section to match final app.
- [x] Add required group member table:
  - [x] UWA ID.
  - [x] Name.
  - [x] GitHub username.
- [ ] Keep launch instructions current:
  - [x] Install `uv`.
  - [x] Copy `.env.example` to `.env`.
  - [x] Run migrations.
  - [ ] Seed database if needed.
  - [x] Start with `uv run python run.py`.
- [x] Add test instructions:
  - [x] Unit tests.
  - [x] Selenium tests.
  - [x] Any required browser driver setup.
- [x] Add migration instructions.
- [ ] Add screenshots or short usage walkthrough if time allows.
- [x] Update `docs/overview.md` with final implemented features.
- [x] Update `docs/roadmap.md` so completed features are not described as future work.
- [x] Add architecture notes:
  - [x] Flask blueprints.
  - [x] SQLAlchemy models.
  - [x] YAML catalogue content.
  - [x] Client-side planner/search behaviour.

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
- [x] Track checkpoint meeting outcomes in Issues, PRs, or docs.

## Phase 16: Final Polish And Submission Readiness

- [x] Run full unit test suite.
- [ ] Run full Selenium suite against a live server.
- [ ] Manually test the main user journeys:
  - [x] Browse/search catalogue.
  - [x] Register/login/logout.
  - [x] Save and reload planner.
  - [ ] Share public plan.
  - [x] Submit/view unit review.
  - [x] Update settings.
  - [x] Browse resources and benefits.
- [ ] Test on desktop and mobile widths.
- [ ] Check all external links.
- [ ] Check empty/error/loading states.
- [x] Check database migration from a clean checkout.
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
  - [x] Add/view a unit review from another user.
  - [ ] Show tests and GitHub collaboration evidence.

## Recommended MVP Order

1. [ ] SQLAlchemy setup, migrations, config, and test database.
2. [ ] Real registration/login/logout with CSRF and password hashing.
3. [x] Persist planner to the database for logged-in users.
4. [ ] Public plan sharing.
5. [x] Unit reviews visible to other users.
6. [ ] Tests: at least 5 unit tests and 5 Selenium tests.
7. [ ] README and GitHub process cleanup.
8. [ ] UI polish, accessibility, and final presentation flow.
