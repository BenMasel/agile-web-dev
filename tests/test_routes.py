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
