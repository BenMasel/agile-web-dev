import os
import re
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
import yaml
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import AccountForm, LoginForm, RegisterForm, UnitReviewForm
from app.models import StudyPlan, StudyPlanUnit, UnitReview, User


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
    reviews = UnitReview.query.filter_by(unit_code=code.upper()).order_by(UnitReview.created_at.desc()).all()
    review_form = UnitReviewForm()
    return render_template(
        'unit/detail.html',
        unit=unit,
        clubs=clubs,
        git_meta=git_meta,
        reviews=reviews,
        review_stats=review_stats_for(reviews),
        review_form=review_form,
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
    if current_user.is_authenticated:
        my_reviews = UnitReview.query.filter_by(user_id=current_user.id).order_by(UnitReview.updated_at.desc()).all()
    return render_template('settings.html', account_form=account_form, my_reviews=my_reviews)


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
# Error handlers
# ---------------------------------------------------------------------------

@bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
