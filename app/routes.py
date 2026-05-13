import os
import re
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import yaml
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

import base64
import io

import pyotp
import qrcode
from flask import session
from app.extensions import db
from app.forms import AccountForm, LoginForm, RegisterForm, TwoFASetupForm, TwoFAVerifyForm, UnitReviewForm
from app.models import NotificationPreference, StudyPlan, StudyPlanUnit, UnitReview, User


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
            'availability':  u.get('availability', ''),
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


def review_stats_for(reviews):
    count = len(reviews)
    if count == 0:
        return {
            'count': 0,
            'average_rating': None,
            'average_difficulty': None,
            'workload_range': None,
        }

    workloads = [review.workload_hours for review in reviews if review.workload_hours is not None]
    if workloads:
        workload_range = {'min': min(workloads), 'max': max(workloads)}
    else:
        workload_range = None

    return {
        'count': count,
        'average_rating': round(sum(review.rating for review in reviews) / count, 1),
        'average_difficulty': round(sum(review.difficulty for review in reviews) / count, 1),
        'workload_range': workload_range,
    }


_RADAR_LABELS = ['Content', 'Exams', 'Workload', 'Group work', 'Time commit', 'Rote learning']


def community_stats_for(unit_code, reviews):
    """Build a community stats dict entirely from live DB reviews.
    Returns None when there are no reviews — no YAML fallback."""
    if not reviews:
        return None

    count = len(reviews)

    avg_rating     = round(sum(r.rating for r in reviews) / count, 1)
    avg_difficulty = round(sum(r.difficulty for r in reviews) / count, 1)
    workloads = [r.workload_hours for r in reviews if r.workload_hours is not None]
    avg_workload = round(sum(workloads) / len(workloads), 1) if workloads else None

    def _avg(attr):
        vals = [getattr(r, attr) for r in reviews if getattr(r, attr, None) is not None]
        return round(sum(vals) / len(vals), 1) if vals else None

    avg_exam  = _avg('exam_difficulty')
    avg_group = _avg('group_work')
    avg_time  = _avg('time_commitment')
    avg_rote  = _avg('rote_learning')
    rec_vals  = [r.would_recommend for r in reviews if getattr(r, 'would_recommend', None) is not None]
    recommend_pct = round(sum(rec_vals) / len(rec_vals) * 100) if rec_vals else None

    def norm15(v):   # 1–5 → 0.0–1.0
        return round((v - 1) / 4, 2) if v is not None else 0
    def norm_wl(v):  # workload hours → 0.0–1.0  (40 hrs = max)
        return round(min(v / 40.0, 1.0), 2) if v is not None else 0
    def bar_color(v15):
        return 'red' if v15 >= 3.5 else 'amber' if v15 >= 2.5 else 'green'

    # Radar: missing optional axes collapse to 0 (visually signals no data)
    radar_values = [
        norm15(avg_difficulty),
        norm15(avg_exam),
        norm_wl(avg_workload),
        norm15(avg_group),
        norm15(avg_time) if avg_time is not None else norm_wl(avg_workload),
        norm15(avg_rote),
    ]

    # Rating bars — only include axes with actual data
    bars = [{'label': 'Content difficulty', 'value': round(avg_difficulty * 2, 1), 'color': bar_color(avg_difficulty)}]
    if avg_exam     is not None: bars.append({'label': 'Exam difficulty',  'value': round(avg_exam  * 2, 1), 'color': bar_color(avg_exam)})
    if avg_workload is not None:
        wl_proxy = max(1.0, min(5.0, avg_workload / 8.0))
        bars.append({'label': 'Workload', 'value': round(wl_proxy * 2, 1), 'color': bar_color(wl_proxy)})
    if avg_group    is not None: bars.append({'label': 'Group work',       'value': round(avg_group * 2, 1), 'color': bar_color(avg_group)})
    if avg_time     is not None: bars.append({'label': 'Time commitment',  'value': round(avg_time  * 2, 1), 'color': bar_color(avg_time)})
    if avg_rote     is not None: bars.append({'label': 'Rote learning',    'value': round(avg_rote  * 2, 1), 'color': bar_color(avg_rote)})

    return {
        'data_quality':        'live',
        'votes':               count,
        'reviews_count':       count,
        'overall_rating':      avg_rating,
        'study_hours_per_week': avg_workload,
        'would_recommend_pct': recommend_pct,
        'radar_labels':        _RADAR_LABELS,
        'radar_values':        radar_values,
        'ratings':             bars,
    }


def review_body_is_placeholder(body):
    compact = re.sub(r'[^a-z0-9]+', '', body.lower())
    if len(set(compact)) <= 2:
        return True
    return compact in {
        'testreview',
        'placeholder',
        'placeholderreview',
        'asdfasdfasdf',
        'qwertyqwerty',
        'noreviewyet',
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route('/')
def home():
    return render_template('home.html')


def _score_search_results(index, query):
    """
    Score and sort search index items against a lowercased query string.
    Returns a list of matching items sorted by score then type priority.

    Scoring tiers (mirrors Fuse.js field weights):
      100 — exact code/abbreviation match
       80 — primary field (title/name/code) starts with query
       50 — primary field contains query
       25 — secondary field (faculty/description) contains query
    """
    scored = []
    for item in index:
        score = 0

        if item['type'] == 'unit':
            code = item['code'].lower()
            primary = f"{item['code']} {item['title']}".lower()
            secondary = item.get('faculty', '').lower()

            if code == query:
                score = 100
            elif primary.startswith(query):
                score = 80
            elif query in primary:
                score = 50
            elif query in secondary:
                score = 25

        elif item['type'] == 'degree':
            primary = item['title'].lower()
            secondary = item.get('faculty', '').lower()

            if primary.startswith(query):
                score = 80
            elif query in primary:
                score = 50
            elif query in secondary:
                score = 25

        elif item['type'] == 'club':
            abbr = (item.get('abbreviation') or '').lower()
            primary = f"{item['name']} {abbr}".lower()
            secondary = item.get('description', '').lower()

            if abbr == query:
                score = 100
            elif primary.startswith(query):
                score = 80
            elif query in primary:
                score = 50
            elif query in secondary:
                score = 25

        if score > 0:
            scored.append((item, score))

    type_priority = {'unit': 3, 'degree': 2, 'club': 1}
    scored.sort(key=lambda x: (-x[1], -type_priority.get(x[0]['type'], 0)))
    return [item for item, _ in scored]


@bp.route('/search')
def search():
    """
    Server-side search endpoint for no-JavaScript fallback.
    Performs basic substring matching on the search index.
    """
    query = request.args.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return render_template('search_results.html', query=query, results=[])

    results = _score_search_results(build_search_index(), query)
    return render_template('search_results.html', query=query, results=results[:50])


@bp.route('/api/search')
def api_search():
    """JSON search endpoint used by the home page AJAX search."""
    query = request.args.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return jsonify([])

    all_results = _score_search_results(build_search_index(), query)

    # Cap per type so a flood of unit matches can't push out degrees/clubs.
    caps = {'unit': 8, 'degree': 4, 'club': 4}
    counts: dict[str, int] = {}
    results = []
    for item in all_results:
        t = item['type']
        if counts.get(t, 0) < caps.get(t, 5):
            results.append(item)
            counts[t] = counts.get(t, 0) + 1

    return jsonify(results)


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
    Student benefits page — loads category metadata and individual benefit files
    from data/benefits/<category>/, attaching git timestamps to each benefit.
    """
    benefits_dir = os.path.join(DATA_DIR, 'benefits')
    categories = []

    for cat_id in sorted(os.listdir(benefits_dir)):
        cat_dir = os.path.join(benefits_dir, cat_id)
        if not os.path.isdir(cat_dir):
            continue

        cat_data = load_yaml(f'benefits/{cat_id}', '_category.yaml')
        if not cat_data:
            continue

        cat_benefits = []
        for filename in sorted(os.listdir(cat_dir)):
            if filename.startswith('_') or not filename.endswith('.yaml'):
                continue
            benefit = load_yaml(f'benefits/{cat_id}', filename)
            if not benefit:
                continue
            filepath = os.path.join('data', 'benefits', cat_id, filename)
            benefit['git_meta'] = git_last_modified(filepath)
            cat_benefits.append(benefit)

        cat_data['benefits'] = cat_benefits
        categories.append(cat_data)

    return render_template('benefits.html', categories=categories)


@bp.route('/videos')
def videos():
    return redirect(url_for('main.resources'))


@bp.route('/unit/<code>')
def unit_detail(code):
    """
    Unit detail page.
    Loads unit data from data/units/<CODE>.yaml and the associated club
    stubs from data/clubs/<slug>.yaml so the template can render their icons.
    Shows the user's current status (planned/completed) if authenticated.
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
    user_status = None
    if current_user.is_authenticated:
        plan_units = db.session.query(StudyPlanUnit).filter(
            StudyPlanUnit.unit_code == code,
            StudyPlanUnit.study_plan.has(user_id=current_user.id)
        ).all()

        if plan_units:
            statuses = [pu.status for pu in plan_units]
            if 'completed' in statuses:
                user_status = 'completed'
            elif 'planned' in statuses:
                user_status = 'planned'

    reviews = UnitReview.query.filter_by(unit_code=code.upper()).order_by(UnitReview.created_at.desc()).all()
    unit['community'] = community_stats_for(code.upper(), reviews)
    review_form = UnitReviewForm()
    return render_template(
        'unit/detail.html',
        unit=unit,
        clubs=clubs,
        git_meta=git_meta,
        reviews=reviews,
        review_stats=review_stats_for(reviews),
        review_form=review_form,
        user_status=user_status,
    )


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


def serialize_plan(plan):
    state = {
        'degrees': [slug for slug in [plan.primary_degree_slug, plan.secondary_degree_slug] if slug],
        'startYear': plan.start_year,
        'startSem': plan.start_semester,
        'plan': {},
        'done': [],
        'substitutions': {},
        'is_public': plan.is_public,
        'share_url': url_for('main.public_plan_detail', plan_id=plan.id),
    }
    for unit in plan.units:
        key = f'{unit.year}-{unit.semester}'
        state['plan'].setdefault(key, []).append(unit.unit_code)
        if unit.status == 'completed' and unit.unit_code not in state['done']:
            state['done'].append(unit.unit_code)
    return state


@bp.route('/api/planner', methods=['GET'])
@login_required
def planner_saved():
    plan = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.updated_at.desc()).first()
    return jsonify({'plan': serialize_plan(plan) if plan else None})


@bp.route('/api/planner', methods=['POST'])
@login_required
def planner_save():
    payload = request.get_json(silent=True) or {}
    state = payload.get('state') or {}
    degrees = state.get('degrees') or []
    plan_data = state.get('plan') or {}
    done = set(state.get('done') or [])

    try:
        start_year = int(state.get('startYear') or datetime.now().year)
        start_semester = int(state.get('startSem') or 1)
    except (TypeError, ValueError):
        return jsonify({'error': 'Planner start year or semester is invalid.'}), 400

    plan = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.updated_at.desc()).first()
    if not plan:
        plan = StudyPlan(user_id=current_user.id, start_year=start_year, start_semester=start_semester)
        db.session.add(plan)

    plan.name = payload.get('name') or 'My study plan'
    plan.primary_degree_slug = degrees[0] if len(degrees) >= 1 else None
    plan.secondary_degree_slug = degrees[1] if len(degrees) >= 2 else None
    plan.start_year = start_year
    plan.start_semester = start_semester
    plan.is_public = bool(payload.get('is_public', False))
    plan.units.clear()

    position = 0
    for key, codes in plan_data.items():
        try:
            year_text, semester_text = key.split('-', 1)
            year = int(year_text)
            semester = int(semester_text)
        except (AttributeError, ValueError):
            continue
        for code in codes or []:
            if not code:
                continue
            plan.units.append(StudyPlanUnit(
                unit_code=str(code).upper(),
                year=year,
                semester=semester,
                status='completed' if code in done else 'planned',
                position=position,
            ))
            position += 1

    db.session.commit()
    return jsonify({'message': 'Planner saved to your account.', 'plan': serialize_plan(plan)})


@bp.route('/api/planner', methods=['DELETE'])
@login_required
def planner_delete():
    for plan in StudyPlan.query.filter_by(user_id=current_user.id).all():
        db.session.delete(plan)
    db.session.commit()
    return jsonify({'message': 'Saved planner deleted.'})


@bp.route('/plans')
def public_plans():
    degree = request.args.get('degree')
    query = StudyPlan.query.filter_by(is_public=True)
    if degree:
        query = query.filter(
            (StudyPlan.primary_degree_slug == degree) | (StudyPlan.secondary_degree_slug == degree)
        )
    plans = query.order_by(StudyPlan.updated_at.desc()).all()
    degrees = {d['slug']: d for d in load_all_yaml('degrees')}
    units = {u['code']: u for u in load_all_yaml('units')}
    return render_template('plans/index.html', plans=plans, degrees=degrees, units=units, selected_degree=degree)


@bp.route('/plans/<int:plan_id>')
def public_plan_detail(plan_id):
    plan = db.session.get(StudyPlan, plan_id)
    if plan is None or not plan.is_public:
        return render_template('404.html', category='plan'), 404

    degrees = {d['slug']: d for d in load_all_yaml('degrees')}
    units = {u['code']: u for u in load_all_yaml('units')}
    return render_template('plans/detail.html', plan=plan, degrees=degrees, units=units)


@bp.route('/api/onboarding-data')
def onboarding_data():
    units = [
        {
            'code':  u.get('code', ''),
            'title': u.get('title', ''),
        }
        for u in load_all_yaml('units')
        if u.get('code')
    ]
    degrees = []
    for d in load_all_yaml('degrees'):
        codes = []
        for yr in (d.get('years') or []):
            for sm in (yr.get('semesters') or []):
                for u in (sm.get('units') or []):
                    if u.get('code'):
                        codes.append(u['code'])
        degrees.append({
            'slug':  d.get('slug', ''),
            'title': d.get('title', ''),
            'codes': codes,
        })
    return jsonify({'units': units, 'degrees': degrees})


@bp.route('/api/youtube/search')
def youtube_search():
    api_key = current_app.config.get('YOUTUBE_API_KEY')
    if not api_key:
        return jsonify({'error': 'YouTube search is not configured on this server.'}), 503

    channel_id = (request.args.get('channelId') or '').strip()
    query = (request.args.get('q') or '').strip()
    if not channel_id or not query:
        return jsonify({'error': 'channelId and q are required.'}), 400
    if len(query) > 120:
        return jsonify({'error': 'Search query is too long.'}), 400

    params = urlencode({
        'part': 'snippet',
        'type': 'video',
        'maxResults': '12',
        'channelId': channel_id,
        'q': query,
        'key': api_key,
    })
    youtube_url = f'https://www.googleapis.com/youtube/v3/search?{params}'
    try:
        req = Request(youtube_url, headers={'Accept': 'application/json'})
        with urlopen(req, timeout=8) as response:
            data = yaml.safe_load(response.read().decode('utf-8'))
    except Exception:
        current_app.logger.exception('YouTube search failed')
        return jsonify({'error': 'YouTube search failed. Please try again later.'}), 502

    items = data.get('items') or []
    videos = []
    for item in items:
        snippet = item.get('snippet') or {}
        thumbnails = snippet.get('thumbnails') or {}
        medium = thumbnails.get('medium') or {}
        video_id = (item.get('id') or {}).get('videoId')
        if not video_id:
            continue
        videos.append({
            'id': video_id,
            'title': snippet.get('title', ''),
            'thumbnail': medium.get('url', ''),
            'channelTitle': snippet.get('channelTitle', ''),
            'publishedAt': snippet.get('publishedAt', ''),
        })
    return jsonify({'videos': videos})


@bp.route('/auth', methods=['GET', 'POST'])
@bp.route('/login', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('main.settings'))

    login_form = LoginForm(prefix='login')
    register_form = RegisterForm(prefix='register')
    mode = request.args.get('mode', 'signin')

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'register':
            mode = 'signup'
            if register_form.validate_on_submit():
                email = register_form.email.data.strip().lower()
                student_id = register_form.student_id.data.strip()
                existing = User.query.filter(
                    (User.email == email) | (User.student_id == student_id)
                ).first()
                if existing:
                    flash('An account already exists for that email or student ID.', 'error')
                else:
                    user = User(
                        email=email,
                        student_id=student_id,
                        display_name=register_form.display_name.data.strip(),
                        faculty=(register_form.faculty.data or '').strip() or None,
                    )
                    user.set_password(register_form.password.data)
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                    flash('Account created. You are signed in.', 'success')
                    return redirect(url_for('main.settings'))
            else:
                flash('Please fix the highlighted registration fields.', 'error')

        elif action == 'login':
            mode = 'signin'
            if login_form.validate_on_submit():
                email = login_form.email.data.strip().lower()
                user = User.query.filter_by(email=email).first()
                if user and user.check_password(login_form.password.data):
                    if user.two_fa_enabled:
                        # Password is correct but we do NOT call login_user() yet.
                        # Instead we park the user's id in the server-side session
                        # and redirect to the TOTP verification step. The user is
                        # only fully logged in once they supply a valid 6-digit code
                        # in verify_2fa(). Using the server session (not a cookie
                        # visible to the browser) means the pending state can't be
                        # tampered with or skipped by the client.
                        session['2fa_pending_user_id'] = user.id
                        session['2fa_next'] = request.args.get('next', url_for('main.settings'))
                        return redirect(url_for('main.verify_2fa'))
                    login_user(user)
                    flash('Signed in successfully.', 'success')
                    next_url = request.args.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect(url_for('main.settings'))
                flash('Email or password is incorrect.', 'error')
            else:
                flash('Please enter your email and password.', 'error')

    return render_template(
        'auth.html',
        login_form=login_form,
        register_form=register_form,
        mode=mode,
    )


@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    flash('Signed out successfully.', 'success')
    return redirect(url_for('main.home'))


@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    account_form = AccountForm(obj=current_user if current_user.is_authenticated else None)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please sign in before updating account settings.', 'error')
            return redirect(url_for('main.auth', next=url_for('main.settings')))
        if account_form.validate_on_submit():
            current_user.display_name = account_form.display_name.data.strip()
            current_user.faculty = (account_form.faculty.data or '').strip() or None
            db.session.commit()
            flash('Account settings updated.', 'success')
            return redirect(url_for('main.settings'))
        flash('Please fix the highlighted account fields.', 'error')
    my_reviews = []
    prefs = None
    if current_user.is_authenticated:
        my_reviews = UnitReview.query.filter_by(user_id=current_user.id).order_by(UnitReview.updated_at.desc()).all()
        prefs = NotificationPreference.query.filter_by(user_id=current_user.id).first()
        if not prefs:
            prefs = NotificationPreference(user_id=current_user.id)
            db.session.add(prefs)
            db.session.commit()
    return render_template(
        'settings.html',
        account_form=account_form,
        my_reviews=my_reviews,
        notification_prefs=prefs,
    )


@bp.route('/api/notification-prefs', methods=['POST'])
def update_notification_prefs():
    """Update user's notification preferences."""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    prefs = NotificationPreference.query.filter_by(user_id=current_user.id).first()
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)

    data = request.get_json(silent=True) or {}
    allowed_keys = (
        'planner_reminders',
        'unit_catalogue_updates',
        'community_replies',
        'weekly_digest',
    )
    for key in allowed_keys:
        if key in data:
            if not isinstance(data[key], bool):
                return jsonify({'error': f'{key} must be true or false'}), 400
            setattr(prefs, key, data[key])

    db.session.add(prefs)
    db.session.commit()

    return jsonify({'success': True, 'prefs': {
        'planner_reminders': prefs.planner_reminders,
        'unit_catalogue_updates': prefs.unit_catalogue_updates,
        'community_replies': prefs.community_replies,
        'weekly_digest': prefs.weekly_digest,
    }})


@bp.route('/unit/<code>/reviews', methods=['POST'])
@login_required
def create_review(code):
    unit = load_yaml('units', f'{code}.yaml')
    if unit is None:
        return render_template('404.html', category='unit'), 404

    form = UnitReviewForm()
    if form.validate_on_submit():
        body = form.body.data.strip()
        if review_body_is_placeholder(body):
            flash('Please write a specific review that helps other students.', 'error')
            return redirect(url_for('main.unit_detail', code=code.upper()))
        review = UnitReview(
            user_id=current_user.id,
            unit_code=code.upper(),
            rating=form.rating.data,
            difficulty=form.difficulty.data,
            exam_difficulty=form.exam_difficulty.data,
            group_work=form.group_work.data,
            time_commitment=form.time_commitment.data,
            rote_learning=form.rote_learning.data,
            would_recommend=form.would_recommend.data if form.would_recommend.data is not None else None,
            workload_hours=form.workload_hours.data,
            semester_taken=(form.semester_taken.data or '').strip() or None,
            body=body,
        )
        db.session.add(review)
        db.session.commit()
        flash('Review posted. Other students can view it now.', 'success')
    else:
        flash('Please fix the highlighted review fields.', 'error')
    return redirect(url_for('main.unit_detail', code=code.upper()))


@bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = db.session.get(UnitReview, review_id)
    if review is None:
        return render_template('404.html', category='review'), 404
    if review.user_id != current_user.id:
        flash('You can only delete your own reviews.', 'error')
        return redirect(url_for('main.unit_detail', code=review.unit_code))

    code = review.unit_code
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('main.unit_detail', code=code))


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
# Two-factor authentication
# ---------------------------------------------------------------------------

@bp.route('/auth/2fa', methods=['GET', 'POST'])
def verify_2fa():
    """
    Second step of login for users with 2FA enabled.
    Expects '2fa_pending_user_id' to be in the Flask session.
    """
    user_id = session.get('2fa_pending_user_id')
    if not user_id:
        return redirect(url_for('main.auth'))

    user = db.session.get(User, user_id)
    if not user:
        session.pop('2fa_pending_user_id', None)
        return redirect(url_for('main.auth'))

    form = TwoFAVerifyForm()
    if form.validate_on_submit():
        if user.verify_totp(form.code.data.strip()):
            session.pop('2fa_pending_user_id', None)
            next_url = session.pop('2fa_next', url_for('main.settings'))
            login_user(user)
            flash('Signed in successfully.', 'success')
            return redirect(next_url if next_url.startswith('/') else url_for('main.settings'))
        flash('Incorrect code. Please try again.', 'error')

    return render_template('auth/verify_2fa.html', form=form)


@bp.route('/settings/2fa/setup', methods=['GET'])
@login_required
def setup_2fa():
    """
    Step 1 of enabling 2FA: generate a secret and show the QR code.

    A fresh secret is generated on every GET so that if the user
    abandons the setup and comes back later they always get a clean one.
    The secret is held in the server session — NOT saved to the DB yet.
    It only gets written to the DB in enable_2fa() once the user proves
    their authenticator app actually scanned it correctly.

    QR code pipeline:
      secret (base32 string)
        → otpauth:// URI  (pyotp.TOTP.provisioning_uri)
        → QR code image   (qrcode.make → PIL Image)
        → PNG bytes       (img.save to BytesIO buffer)
        → base64 string   (embedded directly in the <img> src tag)
    This avoids writing any files to disk.
    """
    secret = pyotp.random_base32()
    session['2fa_pending_secret'] = secret

    # Build the provisioning URI and render as a QR code PNG → base64
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name='stUwa',
    )
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    form = TwoFASetupForm()
    return render_template('auth/setup_2fa.html', form=form, qr_b64=qr_b64, secret=secret)


@bp.route('/settings/2fa/enable', methods=['POST'])
@login_required
def enable_2fa():
    """
    Step 2 of enabling 2FA: validate the first code, then persist the secret.

    We verify against the session-stored secret (not the DB, since it hasn't
    been saved yet). Only if the code is correct do we write the secret to
    the DB and set two_fa_enabled = True. This ensures we never enable 2FA
    with a secret the user's app didn't successfully import — which would
    lock them out of their account.
    """
    secret = session.get('2fa_pending_secret')
    if not secret:
        flash('Setup session expired. Please try again.', 'error')
        return redirect(url_for('main.setup_2fa'))

    form = TwoFASetupForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(secret)
        if totp.verify(form.code.data.strip(), valid_window=1):
            current_user.totp_secret = secret
            current_user.two_fa_enabled = True
            db.session.commit()
            session.pop('2fa_pending_secret', None)
            flash('Two-factor authentication is now enabled.', 'success')
            return redirect(url_for('main.settings'))
        flash('Incorrect code. Make sure your authenticator app is synced and try again.', 'error')
        return redirect(url_for('main.setup_2fa'))

    flash('Invalid request.', 'error')
    return redirect(url_for('main.setup_2fa'))


@bp.route('/settings/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """
    Disable 2FA for the current user and clear their TOTP secret.
    """
    current_user.two_fa_enabled = False
    current_user.totp_secret = None
    db.session.commit()
    flash('Two-factor authentication has been disabled.', 'success')
    return redirect(url_for('main.settings'))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@bp.app_errorhandler(400)
def bad_request(e):
    current_app.logger.warning('Bad request: %s', e)
    return render_template('404.html', category='request'), 400


@bp.app_errorhandler(403)
def forbidden(e):
    current_app.logger.warning('Forbidden request: %s', e)
    return render_template('404.html', category='permission'), 403


@bp.app_errorhandler(500)
def server_error(e):
    current_app.logger.exception('Unhandled server error')
    return render_template('404.html', category='server'), 500
