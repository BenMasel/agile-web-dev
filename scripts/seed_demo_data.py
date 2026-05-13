"""Seed a realistic local demo database for presentation use.

The script is intentionally idempotent: it removes only the demo accounts
defined below, then recreates their plans, reviews, and notification settings.
It does not touch non-demo accounts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import create_app
from app.extensions import db
from app.models import NotificationPreference, StudyPlan, StudyPlanUnit, UnitReview, User


DEMO_PASSWORD = 'password123'


@dataclass(frozen=True)
class DemoUser:
    email: str
    student_id: str
    display_name: str
    faculty: str
    planner_reminders: bool = True
    unit_catalogue_updates: bool = False
    community_replies: bool = True
    weekly_digest: bool = False


USERS = [
    DemoUser('demo@student.uwa.edu.au', '24000000', 'Demo Student', 'Engineering, Computer Science and Mathematics'),
    DemoUser('alex.chen@student.uwa.edu.au', '24000001', 'Alex Chen', 'Engineering, Computer Science and Mathematics', weekly_digest=True),
    DemoUser('maya.patel@student.uwa.edu.au', '24000002', 'Maya Patel', 'Science', unit_catalogue_updates=True),
    DemoUser('jordan.lee@student.uwa.edu.au', '24000003', 'Jordan Lee', 'Business and Law', planner_reminders=False, weekly_digest=True),
    DemoUser('sophie.nguyen@student.uwa.edu.au', '24000004', 'Sophie Nguyen', 'Engineering, Computer Science and Mathematics'),
    DemoUser('noah.williams@student.uwa.edu.au', '24000005', 'Noah Williams', 'Science', community_replies=False),
    DemoUser('priya.singh@student.uwa.edu.au', '24000006', 'Priya Singh', 'Engineering, Computer Science and Mathematics', unit_catalogue_updates=True, weekly_digest=True),
    DemoUser('ethan.brown@student.uwa.edu.au', '24000007', 'Ethan Brown', 'Engineering, Computer Science and Mathematics'),
]


PLANS = {
    'demo@student.uwa.edu.au': {
        'name': 'Demo Computer Science plan',
        'primary_degree_slug': 'BS-CS',
        'secondary_degree_slug': None,
        'start_year': 2026,
        'start_semester': 1,
        'is_public': True,
        'units': [
            ('CITS1003', 2026, 1, 'completed'),
            ('CITS1401', 2026, 1, 'completed'),
            ('CITS1402', 2026, 1, 'completed'),
            ('CITS2002', 2026, 2, 'planned'),
            ('CITS2200', 2026, 2, 'planned'),
            ('CITS2211', 2026, 2, 'planned'),
            ('CITS3002', 2027, 1, 'planned'),
            ('CITS3403', 2027, 1, 'planned'),
            ('CITS3001', 2027, 2, 'planned'),
            ('CITS3200', 2027, 2, 'planned'),
        ],
    },
    'alex.chen@student.uwa.edu.au': {
        'name': 'Software-heavy CS pathway',
        'primary_degree_slug': 'BS-CS',
        'secondary_degree_slug': None,
        'start_year': 2025,
        'start_semester': 1,
        'is_public': True,
        'units': [
            ('CITS1003', 2025, 1, 'completed'),
            ('CITS1401', 2025, 1, 'completed'),
            ('CITS1402', 2025, 1, 'completed'),
            ('CITS2002', 2025, 2, 'completed'),
            ('CITS2200', 2025, 2, 'completed'),
            ('CITS3001', 2026, 1, 'planned'),
            ('CITS3002', 2026, 1, 'planned'),
            ('CITS3403', 2026, 1, 'planned'),
            ('CITS3200', 2026, 2, 'planned'),
        ],
    },
    'maya.patel@student.uwa.edu.au': {
        'name': 'Engineering first-year plan',
        'primary_degree_slug': 'BE-mechanical',
        'secondary_degree_slug': None,
        'start_year': 2026,
        'start_semester': 1,
        'is_public': True,
        'units': [
            ('ENSC1002', 2026, 1, 'planned'),
            ('GENG1000', 2026, 1, 'planned'),
            ('MATH1011', 2026, 1, 'planned'),
            ('PHYS1001', 2026, 1, 'planned'),
            ('ENSC2003', 2026, 2, 'planned'),
            ('GENG1010', 2026, 2, 'planned'),
            ('MATH1012', 2026, 2, 'planned'),
            ('PHYS1002', 2026, 2, 'planned'),
        ],
    },
    'jordan.lee@student.uwa.edu.au': {
        'name': 'Private catch-up plan',
        'primary_degree_slug': 'BS-CS',
        'secondary_degree_slug': None,
        'start_year': 2026,
        'start_semester': 2,
        'is_public': False,
        'units': [
            ('CITS1401', 2026, 2, 'planned'),
            ('CITS1402', 2026, 2, 'planned'),
            ('CITS2002', 2027, 1, 'planned'),
            ('CITS2200', 2027, 1, 'planned'),
        ],
    },
    'priya.singh@student.uwa.edu.au': {
        'name': 'Electrical engineering plan',
        'primary_degree_slug': 'BE-EEE',
        'secondary_degree_slug': None,
        'start_year': 2025,
        'start_semester': 1,
        'is_public': True,
        'units': [
            ('ENSC1002', 2025, 1, 'completed'),
            ('ELEC1303', 2025, 1, 'completed'),
            ('MATH1011', 2025, 1, 'completed'),
            ('PHYS1001', 2025, 1, 'completed'),
            ('ELEC2311', 2025, 2, 'completed'),
            ('ELEC3014', 2026, 1, 'planned'),
            ('ELEC3015', 2026, 1, 'planned'),
            ('ELEC3020', 2026, 2, 'planned'),
            ('ELEC4402', 2027, 1, 'planned'),
        ],
    },
}


REVIEWS = [
    ('alex.chen@student.uwa.edu.au', 'CITS3403', 5, 4, 10, 'Sem 1 2026', 'The project is the main learning vehicle. Start early, keep PRs small, and make sure everyone can run the app locally.'),
    ('demo@student.uwa.edu.au', 'CITS3403', 5, 3, 8, 'Sem 1 2026', 'Very practical unit. The labs line up well with the final project if you keep improving the same app each week.'),
    ('sophie.nguyen@student.uwa.edu.au', 'CITS3403', 4, 4, 9, 'Sem 1 2025', 'The workload is manageable with steady commits. Selenium tests took longer than expected but caught real UI issues.'),
    ('priya.singh@student.uwa.edu.au', 'CITS3403', 4, 3, 7, 'Sem 1 2026', 'Good unit for learning how Flask, templates, forms, and databases fit together. Team communication matters.'),
    ('ethan.brown@student.uwa.edu.au', 'CITS2002', 4, 4, 9, 'Sem 2 2025', 'Systems programming is challenging but useful. Pointers and memory layout become much clearer by the end.'),
    ('alex.chen@student.uwa.edu.au', 'CITS2002', 5, 5, 11, 'Sem 2 2025', 'Do the labs before the deadline week. The C content builds quickly and debugging skill makes a big difference.'),
    ('maya.patel@student.uwa.edu.au', 'CITS1401', 5, 2, 6, 'Sem 1 2025', 'A friendly first programming unit. Weekly practice is enough if you keep up with the worksheets.'),
    ('jordan.lee@student.uwa.edu.au', 'CITS1402', 4, 3, 7, 'Sem 1 2026', 'SQL clicks once you model the relationships on paper first. The examples are useful revision material.'),
    ('noah.williams@student.uwa.edu.au', 'CITS2200', 4, 4, 8, 'Sem 2 2025', 'Algorithms-heavy but fair. Drawing trees and graphs before coding helped a lot.'),
    ('sophie.nguyen@student.uwa.edu.au', 'CITS3002', 4, 4, 8, 'Sem 1 2026', 'Networking concepts are abstract at first, but packet examples and diagrams make the unit easier to follow.'),
    ('priya.singh@student.uwa.edu.au', 'ELEC1303', 4, 3, 7, 'Sem 1 2025', 'Solid introduction to electrical systems. Keep formulas organised and revise circuit analysis weekly.'),
    ('maya.patel@student.uwa.edu.au', 'ENSC1002', 4, 3, 6, 'Sem 1 2026', 'Broad engineering introduction with a good mix of theory and design thinking. Team tasks are important.'),
    ('ethan.brown@student.uwa.edu.au', 'MATH1011', 3, 4, 9, 'Sem 1 2025', 'Fast-paced maths unit. Past papers and tutorial questions are the best preparation.'),
    ('noah.williams@student.uwa.edu.au', 'PHYS1001', 4, 3, 7, 'Sem 1 2025', 'The labs help connect the equations to real examples. Do not leave lab prep until the morning of class.'),
]


def reset_demo_users() -> None:
    for email in [user.email for user in USERS]:
        existing = User.query.filter_by(email=email).first()
        if existing:
            db.session.delete(existing)
    db.session.commit()


def create_users() -> dict[str, User]:
    created = {}
    for demo in USERS:
        user = User(
            email=demo.email,
            student_id=demo.student_id,
            display_name=demo.display_name,
            faculty=demo.faculty,
        )
        user.set_password(DEMO_PASSWORD)
        db.session.add(user)
        db.session.flush()
        db.session.add(NotificationPreference(
            user_id=user.id,
            planner_reminders=demo.planner_reminders,
            unit_catalogue_updates=demo.unit_catalogue_updates,
            community_replies=demo.community_replies,
            weekly_digest=demo.weekly_digest,
        ))
        created[demo.email] = user
    db.session.commit()
    return created


def create_plans(users: dict[str, User]) -> None:
    for email, plan_data in PLANS.items():
        user = users[email]
        plan = StudyPlan(
            user_id=user.id,
            name=plan_data['name'],
            primary_degree_slug=plan_data['primary_degree_slug'],
            secondary_degree_slug=plan_data['secondary_degree_slug'],
            start_year=plan_data['start_year'],
            start_semester=plan_data['start_semester'],
            is_public=plan_data['is_public'],
        )
        db.session.add(plan)
        db.session.flush()
        for position, (code, year, semester, status) in enumerate(plan_data['units']):
            db.session.add(StudyPlanUnit(
                study_plan_id=plan.id,
                unit_code=code,
                year=year,
                semester=semester,
                status=status,
                position=position,
            ))
    db.session.commit()


def create_reviews(users: dict[str, User]) -> None:
    for email, unit_code, rating, difficulty, workload, semester, body in REVIEWS:
        db.session.add(UnitReview(
            user_id=users[email].id,
            unit_code=unit_code,
            rating=rating,
            difficulty=difficulty,
            workload_hours=workload,
            semester_taken=semester,
            body=body,
        ))
    db.session.commit()


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()
        reset_demo_users()
        users = create_users()
        create_plans(users)
        create_reviews(users)

        print('Seeded demo database.')
        print(f'Users: {len(USERS)}')
        print(f'Plans: {len(PLANS)} ({sum(1 for plan in PLANS.values() if plan["is_public"])} public)')
        print(f'Reviews: {len(REVIEWS)}')
        print(f'Demo login: demo@student.uwa.edu.au / {DEMO_PASSWORD}')


if __name__ == '__main__':
    main()
