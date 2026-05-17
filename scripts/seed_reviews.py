"""Seed fake student reviews into the dev database.

Usage:
    uv run python scripts/seed_reviews.py
    uv run python scripts/seed_reviews.py --units ENSC1002 CITS1401 --users 10
    uv run python scripts/seed_reviews.py --clear   # wipe seed data and re-seed
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import UnitReview, User

DEFAULT_UNITS = ['ENSC1002', 'ENSC2004', 'CITS1401', 'CITS3403', 'MATH1012']
DEFAULT_USERS = 8
SEED_EMAIL_PREFIX = 'seed'

REVIEW_BODIES = [
    'Enjoyed the content overall — the assignments were well structured and the lecturer was approachable.',
    'Heavy workload but rewarding. Make sure to start assignments early and attend all lectures.',
    'Pretty manageable unit if you keep up with the weekly content. Exams were fair.',
    'Challenging at times but the resources provided were excellent. Group project was the highlight.',
    'Interesting subject matter. The final exam covered a lot, so revise broadly.',
    'Straightforward unit with clear expectations. Good stepping stone to later units.',
    'Lectures were dense but the tutorials helped clarify things. Worth putting in the effort.',
    'Some parts felt rushed toward the end of semester, but overall a solid unit.',
]

SEMESTERS = ['Sem 1 2024', 'Sem 2 2024', 'Sem 1 2025']


def make_user(i):
    return {
        'email':        f'{SEED_EMAIL_PREFIX}{i:02d}000000@student.uwa.edu.au',
        'student_id':   f'2600{i:02d}00',
        'display_name': f'Seed User {i:02d}',
    }


def make_review(user_id, unit_code):
    # Weight ratings slightly toward middle values for realism
    rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 30, 35, 20])[0]
    return UnitReview(
        user_id=user_id,
        unit_code=unit_code,
        rating=rating,
        difficulty=random.randint(1, 5),
        exam_difficulty=random.randint(1, 5),
        group_work=random.randint(1, 5),
        time_commitment=random.randint(1, 5),
        rote_learning=random.randint(1, 5),
        would_recommend=random.random() < 0.6,
        workload_hours=random.randint(2, 25),
        semester_taken=random.choice(SEMESTERS),
        body=random.choice(REVIEW_BODIES),
    )


def clear_seed_data():
    seed_users = User.query.filter(User.email.like(f'{SEED_EMAIL_PREFIX}%')).all()
    count = 0
    for u in seed_users:
        for r in list(u.reviews):
            db.session.delete(r)
            count += 1
        db.session.delete(u)
    db.session.commit()
    print(f'Cleared {len(seed_users)} seed users and {count} reviews.')


def seed(unit_codes, n_users):
    users = []
    for i in range(n_users):
        spec = make_user(i)
        u = User.query.filter_by(email=spec['email']).first()
        if u is None:
            u = User(email=spec['email'], student_id=spec['student_id'], display_name=spec['display_name'])
            u.set_password('test')
            db.session.add(u)
        users.append(u)
    db.session.flush()

    review_count = 0
    for code in unit_codes:
        for u in users:
            existing = UnitReview.query.filter_by(user_id=u.id, unit_code=code).first()
            if existing is None:
                db.session.add(make_review(u.id, code))
                review_count += 1

    db.session.commit()
    print(f'Seeded {review_count} reviews across {len(unit_codes)} units ({n_users} users).')
    for code in unit_codes:
        n = UnitReview.query.filter_by(unit_code=code).count()
        print(f'  {code}: {n} total reviews')


def main():
    parser = argparse.ArgumentParser(description='Seed fake reviews into the dev DB.')
    parser.add_argument('--units', nargs='+', default=DEFAULT_UNITS, metavar='CODE',
                        help='Unit codes to seed (default: %(default)s)')
    parser.add_argument('--users', type=int, default=DEFAULT_USERS,
                        help='Number of fake users / reviews per unit (default: %(default)s)')
    parser.add_argument('--clear', action='store_true',
                        help='Delete all seed users/reviews first, then re-seed')
    args = parser.parse_args()

    app = create_app('config.DevelopmentConfig')
    with app.app_context():
        if args.clear:
            clear_seed_data()
        seed([c.upper() for c in args.units], args.users)


if __name__ == '__main__':
    main()
