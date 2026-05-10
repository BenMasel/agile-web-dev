# Checkpoint Notes

These notes summarise the implementation checkpoints visible in the repository history.

## Checkpoint 1: Catalogue Foundation

The project started with a Flask/Jinja catalogue for units, degrees, clubs, resources, benefits, and Markdown documentation. YAML files under `data/` became the source of truth for catalogue content, and Fuse.js powered client-side global search.

## Checkpoint 2: Backend Infrastructure And Data Integrity

The backend gained configuration classes, `.env.example`, SQLAlchemy models, JSON schemas under `data/schemas/`, and `scripts/validate_data.py`. Data validation now checks catalogue shape and important references before submission.

## Checkpoint 3: Accounts, CSRF, Planner Sync, And Reviews

The app added UWA student registration, login/logout, account settings, CSRF-protected forms, JSON planner sync, and server-rendered unit review create/delete flows. The planner still works locally while logged out and prompts users to sign in for account sync.

## Checkpoint 4: Testing, Review Polish, And Public Plans

The test suite now covers routes, models, catalogue validation, login/logout, planner save/load/delete, settings updates, review UI, review aggregation, review moderation, public plan visibility, and public plan filtering. Public plans can be shared through `/plans/<id>`, while private plans remain hidden.

## Remaining Evidence Needed

The main remaining process evidence is team-maintained GitHub Issues, linked PRs, review comments, screenshots or recordings for UI PRs, and final presentation/demo notes.
