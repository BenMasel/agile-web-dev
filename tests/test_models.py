from app.models import User


def test_user_password_hashing(db):
    user = User(email='12345678@student.uwa.edu.au')
    user.set_password('correct horse battery staple')

    assert user.password_hash != 'correct horse battery staple'
    assert user.check_password('correct horse battery staple')
    assert not user.check_password('wrong password')


def test_user_can_persist_to_database(db):
    user = User(
        email='87654321@student.uwa.edu.au',
        student_id='87654321',
        display_name='Test Student',
    )
    user.set_password('password123')

    db.session.add(user)
    db.session.commit()

    saved = User.query.filter_by(email='87654321@student.uwa.edu.au').one()
    assert saved.student_id == '87654321'
    assert saved.display_name == 'Test Student'
