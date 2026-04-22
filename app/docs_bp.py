import os
import subprocess
import yaml
import markdown
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, abort

docs_bp = Blueprint('docs', __name__)

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
REPO_ROOT = os.path.dirname(DOCS_DIR)

# Markdown extensions:
#   fenced_code  — ``` code blocks
#   tables       — GFM-style tables
#   toc          — generates a TOC and adds id= anchors to headings
#   attr_list    — lets authors add HTML attributes to elements
MD_EXTENSIONS = ['fenced_code', 'tables', 'toc', 'attr_list']


# ---------------------------------------------------------------------------
# Sidebar / page structure
# ---------------------------------------------------------------------------

def _title_from_file(slug):
    """Read the first H1 line from docs/<slug>.md as the page title."""
    path = os.path.join(DOCS_DIR, f'{slug}.md')
    if not os.path.exists(path):
        return slug.replace('-', ' ').replace('_', ' ').title()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
    return slug.replace('-', ' ').replace('_', ' ').title()


def _load_sidebar():
    """
    Load docs/_sidebar.yaml and return a list of section dicts:
      [{'title': str, 'pages': [{'slug': str, 'title': str}, ...]}, ...]

    Falls back to a single auto-discovered flat section if _sidebar.yaml
    does not exist.
    """
    config_path = os.path.join(DOCS_DIR, '_sidebar.yaml')

    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        sections = []
        for section in config.get('sections', []):
            pages = [
                {'slug': slug, 'title': _title_from_file(slug)}
                for slug in section.get('pages', [])
                if os.path.exists(os.path.join(DOCS_DIR, f'{slug}.md'))
            ]
            if pages:
                sections.append({'title': section['title'], 'pages': pages})
        return sections

    # Fallback — alphabetical flat list of all .md files
    pages = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if filename.endswith('.md'):
            slug = filename[:-3]
            pages.append({'slug': slug, 'title': _title_from_file(slug)})
    return [{'title': 'Documentation', 'pages': pages}] if pages else []


def _flat_pages(sections):
    """Flatten sections into a linear ordered list for prev/next navigation."""
    return [page for section in sections for page in section['pages']]


# ---------------------------------------------------------------------------
# Last-updated timestamp
# ---------------------------------------------------------------------------

def _last_updated(slug):
    """
    Return the last git commit date for docs/<slug>.md, formatted as
    'D/M/YY, H:MM am/pm' (e.g. '16/4/26, 11:46 pm').
    Returns None if git is unavailable or the file has no commits.
    """
    path = os.path.join(DOCS_DIR, f'{slug}.md')
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ci', path],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        raw = result.stdout.strip()
        if result.returncode != 0 or not raw:
            return None
        dt = datetime.strptime(raw[:19], '%Y-%m-%d %H:%M:%S')
        hour = dt.hour % 12 or 12
        ampm = 'am' if dt.hour < 12 else 'pm'
        return f"{dt.day}/{dt.month}/{str(dt.year)[-2:]}, {hour}:{dt.strftime('%M')} {ampm}"
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@docs_bp.route('/docs')
@docs_bp.route('/docs/')
def index():
    """Redirect /docs to the first page defined in _sidebar.yaml."""
    sections = _load_sidebar()
    flat = _flat_pages(sections)
    if not flat:
        abort(404)
    return redirect(url_for('docs.page', slug=flat[0]['slug']))


@docs_bp.route('/docs/<slug>')
def page(slug):
    """Render a single docs page from docs/<slug>.md."""
    path = os.path.join(DOCS_DIR, f'{slug}.md')
    if not os.path.exists(path):
        abort(404)

    with open(path, encoding='utf-8') as f:
        source = f.read()

    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    content_html = md.convert(source)
    toc_html = getattr(md, 'toc', '')

    sections = _load_sidebar()
    flat = _flat_pages(sections)
    slugs = [p['slug'] for p in flat]

    idx = slugs.index(slug) if slug in slugs else -1
    prev_page = flat[idx - 1] if idx > 0 else None
    next_page = flat[idx + 1] if 0 <= idx < len(flat) - 1 else None

    return render_template(
        'docs/page.html',
        content=content_html,
        toc=toc_html,
        slug=slug,
        sections=sections,
        prev_page=prev_page,
        next_page=next_page,
        last_updated=_last_updated(slug),
    )
