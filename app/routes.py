import os
import yaml
from flask import Blueprint, render_template, abort


# All routes live on this blueprint. It is registered in app/__init__.py.
bp = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/videos')
def videos():
    return render_template('videos.html')


@bp.route('/unit/<code>')
def unit_detail(code):
    """
    Unit detail page.
    Loads unit data from data/units/<CODE>.yaml and the associated club
    stubs from data/clubs/<slug>.yaml so the template can render their icons.
    """
    unit = load_yaml('units', f'{code}.yaml')
    if unit is None:
        abort(404)

    # Load each associated club so the template has icon/accent info.
    clubs = []
    for slug in unit.get('associated_clubs', []):
        club = load_yaml('clubs', f'{slug}.yaml')
        if club:
            clubs.append(club)

    return render_template('unit/detail.html', unit=unit, clubs=clubs)


@bp.route('/degree/<slug>')
def degree_detail(slug):
    """
    Degree detail page.
    Loads degree data from data/degrees/<slug>.yaml.
    """
    degree = load_yaml('degrees', f'{slug}.yaml')
    if degree is None:
        abort(404)

    return render_template('degree/detail.html', degree=degree)


@bp.route('/club/<slug>')
def club_detail(slug):
    """
    Club detail page.
    Loads club data from data/clubs/<slug>.yaml.
    """
    club = load_yaml('clubs', f'{slug}.yaml')
    if club is None:
        abort(404)

    return render_template('club/detail.html', club=club)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
