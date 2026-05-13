# stUwa Demo Flow

This run sheet is designed for the Week 12 presentation. Keep the live app demo under 10 minutes, involve all team members, and avoid walking through source code unless the assessor asks during Q&A.

## Submission And Timing Checklist

- Repository work stops before the submission cutoff.
- Public GitHub repository URL is the submitted artefact; no separate formal project upload is required if the unit team already has the URL.
- All team members attend the presentation.
- Five minutes before the timeslot:
  - app is launched on the demo machine
  - demo database is ready
  - browser is open at `http://localhost:5000`
  - terminal is ready to show test commands/results if asked
  - team has agreed how to distribute the 4 bonus contribution marks

## Demo Setup

Run these before the presentation:

```bash
uv sync
cp .env.example .env
FLASK_APP=run.py uv run flask db upgrade
uv run python scripts/seed_demo_data.py
uv run python run.py
```

In another terminal, confirm tests pass:

```bash
uv run pytest
uv run python scripts/validate_data.py
uv run python scripts/check_rendered_pages.py
```

Use a demo account such as:

- Email: `demo@student.uwa.edu.au`
- Student ID: `24000000`
- Password: `password123`
- Display name: `Demo Student`

If the account already exists, sign in with it. If not, register it at the start of the account section.

## 10 Minute Demonstration

### 0:00-0:45 - Opening And Problem

Speaker: Ben

Script:
> stUwa is a UWA student companion. The problem we are solving is that unit details, degree requirements, clubs, resources, benefits, and student advice are scattered across separate places. stUwa brings those into one searchable web app, then adds account-backed study planning and peer reviews.

Show:
- Home page
- Navigation bar
- Main search box

Criteria covered:
- clear app purpose
- intuitive navigation
- value to the user

### 0:45-2:00 - Catalogue Search And Unit Detail

Speaker: Kaushik

Steps:
1. Search `CITS3403` from the home page.
2. Open the Agile Web Development unit result.
3. Point out unit metadata, resources, associated clubs, and review summary.
4. Mention that catalogue content is YAML-backed and validated by scripts/tests.

Script:
> Students can quickly search units, degrees, and clubs. The result page combines official-style catalogue data with app-specific context like related clubs, resources, and student reviews.

Criteria covered:
- client-server app
- HTML/Jinja templates
- JavaScript search/AJAX behaviour
- useful application content

### 2:00-3:20 - Degree And Planner Entry

Speaker: Dhul

Steps:
1. Open a degree page, for example Computer Science or Engineering.
2. Show units grouped by year/semester.
3. Use the call-to-action to go to the planner.
4. Explain local draft behaviour for guests.

Script:
> Degree pages turn static course information into a planning workflow. The planner can work locally for guests, but signed-in users can sync the plan to the database.

Criteria covered:
- meaningful data manipulation
- responsive UI
- persistent user workflow

### 3:20-5:15 - Account, Planner Persistence, And Public Sharing

Speaker: Hridayesh

Steps:
1. Register or log in using the demo account.
2. Open Planner.
3. Add or confirm units in the plan.
4. Click `Save to account`.
5. Toggle public plan.
6. Click `Copy share link`.
7. Open the public plan link in a private/incognito window or after logging out.

Script:
> This is the core database-backed feature. The planner saves to SQLite through SQLAlchemy for authenticated users. Public sharing satisfies the requirement that users can view data from other users, while private plans remain hidden.

Criteria covered:
- login/logout
- persisted user data
- users viewing other users' data
- SQLite via SQLAlchemy
- JSON/AJAX planner sync
- access control for private/public data

### 5:15-6:45 - Unit Reviews And Shared Community Data

Speaker: Kaushik

Steps:
1. Return to `CITS3403` unit page while signed in.
2. Add a review with rating, difficulty, workload, semester, and advice.
3. Show aggregate review stats update.
4. Log out or use another browser session to show the review remains visible publicly.
5. Briefly show `Settings > My reviews`.

Script:
> Unit reviews add community knowledge. Reviews are stored in the database, displayed publicly without exposing emails, and ownership checks mean users can only delete their own reviews.

Criteria covered:
- data from other users
- persisted data
- form validation
- CSRF-protected state changes
- authentication and ownership checks

### 6:45-7:45 - Resources, Benefits, And Settings

Speaker: Ben

Steps:
1. Open Resources.
2. Show planner-aware resources and YouTube search setup message/search.
3. Open Benefits.
4. Open Settings and show account preferences / 2FA option.

Script:
> The supporting pages make the app broader than a planner. Resources and benefits help students act on their study plan, and settings shows account-backed preferences and optional two-factor authentication.

Criteria covered:
- broader app value
- environment-variable configuration for API keys
- account settings persistence
- security features

### 7:45-8:45 - Testing And Quality Evidence

Speaker: Dhul

Steps:
1. Show terminal output or run:
   ```bash
   uv run pytest
   uv run python scripts/validate_data.py
   uv run python scripts/check_rendered_pages.py
   ```
2. Mention that the pytest suite includes Selenium live-server journeys.
3. Open README testing section if needed.

Script:
> The automated suite covers routes, models, authentication, planner save/load/delete, public plan visibility, reviews, data validation, rendered pages, and Selenium browser journeys.

Criteria covered:
- 5+ unit tests
- 5+ Selenium tests against a live server
- README test instructions
- maintainability

### 8:45-9:45 - GitHub Process Evidence

Speaker: Hridayesh

Steps:
1. Open GitHub repository.
2. Show README group table.
3. Show commit history.
4. Show representative pull requests and issues/checkpoint notes.
5. Mention checkpoint notes in `docs/checkpoints.md`.

Script:
> The project was managed through GitHub with regular commits, pull requests, checkpoint notes, and documented setup/test instructions. Each member has visible contributions in the repository history.

Criteria covered:
- public GitHub repo
- README requirements
- Agile/GitHub process marks
- individual contribution evidence

### 9:45-10:00 - Close

Speaker: Ben

Script:
> In summary, stUwa meets the core brief by combining a Flask client-server app, account login/logout, persisted user data, shared user-visible data, SQLAlchemy models, CSRF and password security, and a tested student-focused workflow.

## Q&A Preparation

Likely questions and short answers:

- **Where is user data persisted?**  
  SQLite through SQLAlchemy models in `app/models.py`: `User`, `StudyPlan`, `StudyPlanUnit`, `UnitReview`, and `NotificationPreference`.

- **How do users see other users' data?**  
  Public study plans under `/plans` and unit reviews visible on unit pages.

- **How are passwords stored?**  
  Werkzeug salted password hashes, never plain text.

- **How is CSRF handled?**  
  Flask-WTF CSRF protection for forms and CSRF headers for JSON planner/settings requests.

- **What tests prove the app works?**  
  `uv run pytest` runs route/model/auth/planner/review/data/Selenium tests; the helper scripts validate YAML and rendered pages.

- **What would you improve with more time?**  
  Saved resources/benefits, more granular multi-plan APIs, extra accessibility polish, and splitting the large route/template scripts into smaller modules.

## Bonus Marks Discussion

Agree before entering the presentation how the 4 bonus contribution marks should be distributed. The assessor will not mediate arguments during the presentation. If everyone contributed equally, the simplest answer is one bonus mark per person.
