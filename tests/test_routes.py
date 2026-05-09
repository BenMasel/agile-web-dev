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
