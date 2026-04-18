import os
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
import yaml
from flask import Blueprint, render_template, redirect, url_for


# All routes live on this blueprint. It is registered in app/__init__.py.
bp = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))


def relative_time(dt):
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    days = delta.days
    if days < 1:
        return 'today'
    if days < 7:
        return f'{days}d ago'
    if days < 30:
        return f'{days // 7}w ago'
    if days < 365:
        return f'{days // 30}mo ago'
    return f'{days // 365}y ago'


@lru_cache(maxsize=512)
def git_last_modified(filepath):
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ai\t%an', '--', filepath],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=3,
        )
        line = result.stdout.strip()
        if not line:
            return None
        parts = line.split('\t', 1)
        dt = datetime.fromisoformat(parts[0].strip()[:19])
        author = parts[1].strip() if len(parts) > 1 else None
        return {'date': dt, 'author': author, 'relative': relative_time(dt)}
    except Exception:
        return None


def load_yaml(subfolder, filename):
    """
    Load and parse a YAML file from the data directory.
    Returns the parsed dict, or None if the file doesn't exist.
    """
    path = os.path.join(DATA_DIR, subfolder, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_all_yaml(subfolder):
    """
    Load every .yaml file in a data subfolder.
    Returns a list of parsed dicts, skipping any that fail to parse.
    """
    directory = os.path.join(DATA_DIR, subfolder)
    if not os.path.exists(directory):
        return []
    items = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.yaml'):
            data = load_yaml(subfolder, filename)
            if data:
                items.append(data)
    return items


def build_search_index():
    """
    Flatten all units, degrees, and clubs into a single list of dicts
    suitable for Fuse.js. Each item carries a 'type' and 'url' field so
    the frontend knows how to render and navigate to it.
    """
    index = []

    for u in load_all_yaml('units'):
        index.append({
            'type':          'unit',
            'code':          u.get('code', ''),
            'title':         u.get('title', ''),
            'faculty':       u.get('faculty', ''),
            'credit_points': u.get('credit_points', ''),
            'level':         u.get('level', ''),
            'semester':      u.get('semester', ''),
            'url':           f'/unit/{u["code"]}',
        })

    for d in load_all_yaml('degrees'):
        index.append({
            'type':           'degree',
            'title':          d.get('title', ''),
            'faculty':        d.get('faculty', ''),
            'duration_years': d.get('duration_years', ''),
            'credit_points':  d.get('credit_points', ''),
            'url':            f'/degree/{d["slug"]}',
        })

    for c in load_all_yaml('clubs'):
        index.append({
            'type':         'club',
            'name':         c.get('name', ''),
            'abbreviation': c.get('abbreviation', ''),
            'description':  str(c.get('description', '')).replace('\n', ' ').strip(),
            'accent_color': c.get('accent_color', '#ffffff'),
            'url':          f'/club/{c["slug"]}',
        })

    return index


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route('/')
def home():
    """
    Home page — passes the full search index to the template as JSON so
    Fuse.js can run client-side search with no round-trips.
    """
    return render_template('home.html', search_data=build_search_index())


@bp.route('/resources')
def resources():
    """
    Resources page — aggregates youtube_channels, platforms, and textbooks
    from all unit YAML files and passes them as JSON to the template.
    The JS layer reads pinned units from localStorage and filters accordingly.
    """
    unit_resources = [
        {
            'code':      u['code'],
            'title':     u['title'],
            'resources': u.get('resources', {}),
        }
        for u in load_all_yaml('units')
        if u.get('resources')
    ]
    return render_template('resources.html', unit_resources=unit_resources)


@bp.route('/benefits')
def benefits():
    """
    Student benefits page — loads categories and benefits from
    data/benefits/benefits.yaml and passes them to the template.
    """
    data = load_yaml('benefits', 'benefits.yaml') or {}
    return render_template('benefits.html', categories=data.get('categories', []))


@bp.route('/videos')
def videos():
    return redirect(url_for('main.resources'))


@bp.route('/unit/<code>')
def unit_detail(code):
    """
    Unit detail page.
    Loads unit data from data/units/<CODE>.yaml and the associated club
    stubs from data/clubs/<slug>.yaml so the template can render their icons.
    """
    unit = load_yaml('units', f'{code}.yaml')
    if unit is None:
        return render_template('404.html', category='unit'), 404

    clubs = []
    for slug in unit.get('associated_clubs', []):
        club = load_yaml('clubs', f'{slug}.yaml')
        if club:
            clubs.append(club)

    filepath = os.path.join('data', 'units', f'{code}.yaml')
    git_meta = git_last_modified(filepath)
    return render_template('unit/detail.html', unit=unit, clubs=clubs, git_meta=git_meta)


@bp.route('/degree/<slug>')
def degree_detail(slug):
    """
    Degree detail page.
    Loads degree data from data/degrees/<slug>.yaml.
    """
    degree = load_yaml('degrees', f'{slug}.yaml')
    if degree is None:
        return render_template('404.html', category='degree'), 404

    filepath = os.path.join('data', 'degrees', f'{slug}.yaml')
    git_meta = git_last_modified(filepath)
    return render_template('degree/detail.html', degree=degree, git_meta=git_meta)


@bp.route('/planner')
def planner():
    """
    Study planner page.
    Passes all degrees and unit data as JSON so the client-side planner
    can compute prerequisite chains and render the semester timeline.
    """
    degrees = load_all_yaml('degrees')
    units = {u['code']: u for u in load_all_yaml('units')}
    return render_template('planner.html', degrees=degrees, units=units)


@bp.route('/club/<slug>')
def club_detail(slug):
    """
    Club detail page.
    Loads club data from data/clubs/<slug>.yaml.
    """
    club = load_yaml('clubs', f'{slug}.yaml')
    if club is None:
        return render_template('404.html', category='club'), 404

    return render_template('club/detail.html', club=club)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
