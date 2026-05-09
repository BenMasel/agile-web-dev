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
