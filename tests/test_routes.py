from pathlib import Path

import pytest
import yaml
from markupsafe import escape

from app.models import NotificationPreference, User
from app.routes import build_search_index


CLUB_DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'clubs'


def test_home_page_loads(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'stUwa' in response.data


def test_resources_page_loads(client):
    response = client.get('/resources')

    assert response.status_code == 200
    assert b'Resources' in response.data


def test_missing_unit_returns_404(client):
    response = client.get('/unit/NOPE9999')

    assert response.status_code == 404


def test_unit_detail_route_returns_unit_page(client):
    response = client.get('/unit/CITS3403')

    assert response.status_code == 200
    assert b'Agile Web Development' in response.data
    assert b'Student reviews' in response.data


def test_onboarding_data_contains_catalogue(client):
    response = client.get('/api/onboarding-data')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['units']
    assert payload['degrees']


def test_notification_preferences_require_login(client):
    response = client.post('/api/notification-prefs', json={'weekly_digest': True})

    assert response.status_code == 401


def test_authenticated_user_can_update_notification_preferences(client, db):
    user = User(
        email='12345678@student.uwa.edu.au',
        student_id='12345678',
        display_name='Route Test',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)
        session['_fresh'] = True

    response = client.post('/api/notification-prefs', json={
        'planner_reminders': False,
        'weekly_digest': True,
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['prefs']['planner_reminders'] is False
    assert payload['prefs']['weekly_digest'] is True

    prefs = NotificationPreference.query.filter_by(user_id=user.id).one()
    assert prefs.planner_reminders is False
    assert prefs.weekly_digest is True


def test_authenticated_settings_page_renders_notification_preferences(client, db):
    user = User(
        email='23456789@student.uwa.edu.au',
        student_id='23456789',
        display_name='Settings Test',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)
        session['_fresh'] = True

    response = client.get('/settings')

    assert response.status_code == 200
    assert b'Email notifications' in response.data
    assert b'weekly_digest' in response.data


def test_youtube_search_reports_missing_server_key(client):
    response = client.get('/api/youtube/search?channelId=abc&q=flask')

    assert response.status_code == 503
    assert response.get_json()['error'] == 'YouTube search is not configured on this server.'


def test_login_and_logout_change_session_state(client, db):
    from app.models import User

    user = User(
        email='33333333@student.uwa.edu.au',
        student_id='33333333',
        display_name='Session Tester',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_response = client.post('/login', data={
        'action': 'login',
        'login-email': '33333333@student.uwa.edu.au',
        'login-password': 'password123',
    }, follow_redirects=True)
    assert login_response.status_code == 200
    assert b'Session Tester' in login_response.data

    logout_response = client.post('/logout', follow_redirects=True)
    assert logout_response.status_code == 200
    assert b'Sign in' in logout_response.data


def test_planner_api_saves_loads_and_deletes_plan(client, db):
    from app.models import StudyPlan, User

    user = User(
        email='44444444@student.uwa.edu.au',
        student_id='44444444',
        display_name='Planner Tester',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={
        'action': 'login',
        'login-email': '44444444@student.uwa.edu.au',
        'login-password': 'password123',
    })

    payload = {
        'state': {
            'degrees': ['BS-CS'],
            'startYear': 2026,
            'startSem': 1,
            'plan': {'2026-1': ['CITS1401']},
            'done': ['CITS1401'],
        },
        'name': 'Test plan',
    }
    save_response = client.post('/api/planner', json=payload)
    assert save_response.status_code == 200
    assert StudyPlan.query.count() == 1

    load_response = client.get('/api/planner')
    assert load_response.status_code == 200
    loaded = load_response.get_json()['plan']
    assert loaded['degrees'] == ['BS-CS']
    assert loaded['done'] == ['CITS1401']
    assert loaded['plan']['2026-1'] == ['CITS1401']

    delete_response = client.delete('/api/planner')
    assert delete_response.status_code == 200
    assert StudyPlan.query.count() == 0


def test_settings_account_update(client, db):
    from app.models import User

    user = User(
        email='55555555@student.uwa.edu.au',
        student_id='55555555',
        display_name='Original Name',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={
        'action': 'login',
        'login-email': '55555555@student.uwa.edu.au',
        'login-password': 'password123',
    })

    response = client.post('/settings', data={
        'display_name': 'Updated Name',
        'faculty': 'Science',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Updated Name' in response.data

    saved = db.session.get(User, user.id)
    assert saved.display_name == 'Updated Name'
    assert saved.faculty == 'Science'


def test_unit_review_ui_create_display_and_delete(client, db):
    from app.models import UnitReview, User

    user = User(
        email='12345678@student.uwa.edu.au',
        student_id='12345678',
        display_name='Review Tester',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_response = client.post('/login', data={
        'action': 'login',
        'login-email': '12345678@student.uwa.edu.au',
        'login-password': 'password123',
    })
    assert login_response.status_code == 302

    create_response = client.post('/unit/CITS3403/reviews', data={
        'rating': '5',
        'difficulty': '3',
        'workload_hours': '8',
        'semester_taken': 'S1 2026',
        'body': 'Helpful practical unit with useful project work.',
    }, follow_redirects=True)
    assert create_response.status_code == 200
    assert b'Helpful practical unit with useful project work.' in create_response.data
    assert b'Review Tester' in create_response.data

    review = UnitReview.query.filter_by(unit_code='CITS3403').one()
    delete_response = client.post(f'/reviews/{review.id}/delete', follow_redirects=True)
    assert delete_response.status_code == 200
    assert UnitReview.query.count() == 0


def test_review_delete_requires_owner(client, db):
    from app.models import UnitReview, User

    owner = User(
        email='11111111@student.uwa.edu.au',
        student_id='11111111',
        display_name='Owner',
    )
    owner.set_password('password123')
    other = User(
        email='22222222@student.uwa.edu.au',
        student_id='22222222',
        display_name='Other',
    )
    other.set_password('password123')
    db.session.add_all([owner, other])
    db.session.commit()

    review = UnitReview(
        user_id=owner.id,
        unit_code='CITS3403',
        rating=5,
        difficulty=3,
        workload_hours=8,
        semester_taken='S1 2026',
        body='Owner review should not be deleted by another user.',
    )
    db.session.add(review)
    db.session.commit()

    login_response = client.post('/login', data={
        'action': 'login',
        'login-email': '22222222@student.uwa.edu.au',
        'login-password': 'password123',
    })
    assert login_response.status_code == 302

    delete_response = client.post(f'/reviews/{review.id}/delete', follow_redirects=True)
    assert delete_response.status_code == 200
    assert UnitReview.query.count() == 1


def test_unit_review_aggregation_is_shown_on_unit_page(client, db):
    from app.models import UnitReview, User

    user = User(
        email='88888888@student.uwa.edu.au',
        student_id='88888888',
        display_name='Review Stats',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()
    db.session.add_all([
        UnitReview(
            user_id=user.id,
            unit_code='CITS3403',
            rating=5,
            difficulty=3,
            workload_hours=8,
            body='Great project structure and useful weekly practice.',
        ),
        UnitReview(
            user_id=user.id,
            unit_code='CITS3403',
            rating=3,
            difficulty=5,
            workload_hours=12,
            body='Busy semester but the team project helped a lot.',
        ),
    ])
    db.session.commit()

    response = client.get('/unit/CITS3403')

    assert response.status_code == 200
    assert b'Average rating' in response.data
    assert b'Difficulty' in response.data
    assert b'Review count' in response.data
    assert b'Workload range' in response.data
    assert b'4.0' in response.data
    assert b'8-12 hrs/wk' in response.data


def test_settings_lists_current_users_reviews(client, db):
    from app.models import UnitReview, User

    user = User(
        email='99999999@student.uwa.edu.au',
        student_id='99999999',
        display_name='My Review User',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()
    db.session.add(UnitReview(
        user_id=user.id,
        unit_code='CITS3403',
        rating=4,
        difficulty=3,
        workload_hours=10,
        body='This is my settings-visible unit review.',
    ))
    db.session.commit()

    client.post('/login', data={
        'action': 'login',
        'login-email': '99999999@student.uwa.edu.au',
        'login-password': 'password123',
    })
    response = client.get('/settings')

    assert response.status_code == 200
    assert b'My reviews' in response.data
    assert b'CITS3403' in response.data
    assert b'This is my settings-visible unit review.' in response.data


def test_placeholder_unit_review_is_rejected(client, db):
    from app.models import UnitReview, User

    user = User(
        email='10101010@student.uwa.edu.au',
        student_id='10101010',
        display_name='Placeholder User',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={
        'action': 'login',
        'login-email': '10101010@student.uwa.edu.au',
        'login-password': 'password123',
    })
    response = client.post('/unit/CITS3403/reviews', data={
        'rating': 3,
        'difficulty': 3,
        'workload_hours': 10,
        'semester_taken': 'Sem 1 2026',
        'body': 'placeholder review',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Please write a specific review that helps other students.' in response.data
    assert UnitReview.query.count() == 0


def test_public_plan_is_visible_and_private_plan_is_hidden(client, db):
    from app.models import StudyPlan, StudyPlanUnit, User

    user = User(
        email='12121212@student.uwa.edu.au',
        student_id='12121212',
        display_name='Plan Sharer',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()
    public_plan = StudyPlan(
        user_id=user.id,
        name='Public CITS plan',
        primary_degree_slug='BS-CS',
        start_year=2026,
        start_semester=1,
        is_public=True,
    )
    private_plan = StudyPlan(
        user_id=user.id,
        name='Private CITS plan',
        primary_degree_slug='BS-CS',
        start_year=2026,
        start_semester=1,
        is_public=False,
    )
    db.session.add_all([public_plan, private_plan])
    db.session.flush()
    db.session.add(StudyPlanUnit(
        study_plan_id=public_plan.id,
        unit_code='CITS3403',
        year=2026,
        semester=1,
        status='planned',
        position=0,
    ))
    db.session.commit()

    public_response = client.get(f'/plans/{public_plan.id}')
    private_response = client.get(f'/plans/{private_plan.id}')

    assert public_response.status_code == 200
    assert b'Public CITS plan' in public_response.data
    assert b'CITS3403' in public_response.data
    assert private_response.status_code == 404


def test_planner_api_saves_public_state_and_share_url(client, db):
    from app.models import StudyPlan, User

    user = User(
        email='13131313@student.uwa.edu.au',
        student_id='13131313',
        display_name='Public Saver',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={
        'action': 'login',
        'login-email': '13131313@student.uwa.edu.au',
        'login-password': 'password123',
    })
    response = client.post('/api/planner', json={
        'state': {
            'degrees': ['BS-CS'],
            'startYear': 2026,
            'startSem': 1,
            'plan': {'2026-1': ['CITS3403']},
            'done': [],
        },
        'is_public': True,
    })

    assert response.status_code == 200
    payload = response.get_json()
    plan = StudyPlan.query.filter_by(user_id=user.id).one()
    assert plan.is_public is True
    assert payload['plan']['is_public'] is True
    assert payload['plan']['share_url'] == f'/plans/{plan.id}'


def test_public_plans_can_filter_by_degree(client, db):
    from app.models import StudyPlan, User

    user = User(
        email='14141414@student.uwa.edu.au',
        student_id='14141414',
        display_name='Plan Browser',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()
    db.session.add_all([
        StudyPlan(
            user_id=user.id,
            name='Computer Science Plan',
            primary_degree_slug='BS-CS',
            start_year=2026,
            start_semester=1,
            is_public=True,
        ),
        StudyPlan(
            user_id=user.id,
            name='Other Public Plan',
            primary_degree_slug='OTHER',
            start_year=2026,
            start_semester=1,
            is_public=True,
        ),
    ])
    db.session.commit()

    response = client.get('/plans?degree=BS-CS')

    assert response.status_code == 200
    assert b'Computer Science Plan' in response.data
    assert b'Other Public Plan' not in response.data


def test_deleting_saved_plan_does_not_delete_another_users_plan(client, db):
    from app.models import StudyPlan, User

    owner = User(
        email='15151515@student.uwa.edu.au',
        student_id='15151515',
        display_name='Owner Plan',
    )
    owner.set_password('password123')
    other = User(
        email='16161616@student.uwa.edu.au',
        student_id='16161616',
        display_name='Other Plan',
    )
    other.set_password('password123')
    db.session.add_all([owner, other])
    db.session.flush()
    db.session.add_all([
        StudyPlan(user_id=owner.id, name='Owner private plan', start_year=2026, start_semester=1),
        StudyPlan(user_id=other.id, name='Other private plan', start_year=2026, start_semester=1),
    ])
    db.session.commit()

    client.post('/login', data={
        'action': 'login',
        'login-email': '16161616@student.uwa.edu.au',
        'login-password': 'password123',
    })
    response = client.delete('/api/planner')

    assert response.status_code == 200
    remaining = StudyPlan.query.all()
    assert len(remaining) == 1
    assert remaining[0].user_id == owner.id


@pytest.mark.parametrize('club_file', sorted(CLUB_DATA_DIR.glob('*.yaml')), ids=lambda path: path.stem)
def test_all_local_club_pages_load(client, club_file):
    club = yaml.safe_load(club_file.read_text(encoding='utf-8'))

    response = client.get(f"/club/{club['slug']}")

    assert response.status_code == 200
    assert str(escape(club['name'])).encode() in response.data


def test_search_index_includes_every_local_club():
    expected_slugs = {
        yaml.safe_load(path.read_text(encoding='utf-8'))['slug']
        for path in CLUB_DATA_DIR.glob('*.yaml')
    }

    indexed_slugs = {
        item['url'].removeprefix('/club/')
        for item in build_search_index()
        if item['type'] == 'club'
    }

    assert expected_slugs <= indexed_slugs
