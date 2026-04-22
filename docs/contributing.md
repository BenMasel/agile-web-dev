# Contributing

stUwa is an open-source project maintained by UWA students. All content and code contributions are welcome — you do not need to be a developer to contribute.

---

## Ways to Contribute

### Adding or correcting content

The fastest way to contribute is to edit a YAML file in the `data/` directory and open a pull request. No Python knowledge is required.

- **Units** — add a new file at `data/units/<CODE>.yaml` or correct fields in an existing one
- **Degrees** — add or update `data/degrees/<slug>.yaml`
- **Clubs** — add or update `data/clubs/<slug>.yaml`
- **Benefits** — edit `data/benefits/benefits.yaml`

### Fixing a bug or adding a feature

1. Fork the repository and create a branch from `main`
2. Make your changes
3. Run the app locally to verify (`uv run python run.py`)
4. Open a pull request with a clear description of what you changed and why

### Writing documentation

Documentation lives in `docs/` as Markdown files. Add a new `.md` file, register it in `docs/_sidebar.yaml`, and open a pull request.

---

## Development Setup

```bash
git clone <repo-url>
cd agile-web-dev
uv sync
uv run python run.py
```

The development server auto-reloads on file changes. Visit `http://localhost:5000`.

---

## Code Style

- Python — follow PEP 8; no type annotations required on new code
- Templates — keep logic in Python, not Jinja2; use `{% comment %}` style comments for non-obvious sections
- YAML — match the structure of existing files in the same directory; validate against the schema in `data/schemas/`

---

## Pull Request Guidelines

- Keep PRs focused — one concern per PR
- Write a brief description of the motivation, not just the change
- If you're adding a unit or club, include a source link (e.g. the UWA handbook URL) in the PR description so reviewers can verify the data
