"""Unit tests for community_stats_for() in app.routes."""
import pytest

from app.extensions import db
from app.models import UnitReview, User
from app.routes import community_stats_for


def _make_user(db, suffix='01'):
    u = User(
        email=f'test{suffix}000000@student.uwa.edu.au',
        student_id=f'2699{suffix}00',
        display_name=f'Test User {suffix}',
    )
    u.set_password('test')
    db.session.add(u)
    db.session.flush()
    return u


def _make_review(user_id, **kwargs):
    defaults = dict(
        unit_code='TEST1001',
        rating=4,
        difficulty=3,
        body='This is a test review body.',
    )
    defaults.update(kwargs)
    r = UnitReview(user_id=user_id, **defaults)
    db.session.add(r)
    return r


# ---------------------------------------------------------------------------
# Empty / no-review cases
# ---------------------------------------------------------------------------

def test_returns_none_with_no_reviews(app):
    assert community_stats_for('TEST1001', []) is None


def test_returns_none_for_empty_list(app):
    result = community_stats_for('XXXX0000', [])
    assert result is None


# ---------------------------------------------------------------------------
# Live badge and counts
# ---------------------------------------------------------------------------

def test_live_badge_from_first_review(app, db):
    u = _make_user(db)
    r = _make_review(u.id)
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    assert result['data_quality'] == 'live'


def test_counts_match_review_list(app, db):
    u = _make_user(db)
    reviews = [_make_review(u.id, rating=i % 5 + 1, difficulty=3) for i in range(5)]
    db.session.commit()

    result = community_stats_for('TEST1001', reviews)
    assert result['votes'] == 5
    assert result['reviews_count'] == 5


# ---------------------------------------------------------------------------
# Averages
# ---------------------------------------------------------------------------

def test_overall_rating_average(app, db):
    u = _make_user(db)
    reviews = [_make_review(u.id, rating=r) for r in [2, 4, 3]]
    db.session.commit()

    result = community_stats_for('TEST1001', reviews)
    assert result['overall_rating'] == round((2 + 4 + 3) / 3, 1)


def test_workload_average_ignores_nulls(app, db):
    u = _make_user(db)
    reviews = [
        _make_review(u.id, workload_hours=10),
        _make_review(u.id, workload_hours=20),
        _make_review(u.id, workload_hours=None),
    ]
    db.session.commit()

    result = community_stats_for('TEST1001', reviews)
    assert result['study_hours_per_week'] == 15.0


def test_workload_none_when_all_null(app, db):
    u = _make_user(db)
    reviews = [_make_review(u.id, workload_hours=None)]
    db.session.commit()

    result = community_stats_for('TEST1001', reviews)
    assert result['study_hours_per_week'] is None


# ---------------------------------------------------------------------------
# Radar normalisation
# ---------------------------------------------------------------------------

def test_radar_content_axis_normalised(app, db):
    u = _make_user(db)
    r = _make_review(u.id, difficulty=5)
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    # difficulty=5 → (5-1)/4 = 1.0
    assert result['radar_values'][0] == 1.0


def test_radar_content_axis_min(app, db):
    u = _make_user(db)
    r = _make_review(u.id, difficulty=1)
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    # difficulty=1 → (1-1)/4 = 0.0
    assert result['radar_values'][0] == 0.0


def test_radar_missing_optional_axes_are_zero(app, db):
    u = _make_user(db)
    # No exam_difficulty / group_work / time_commitment / rote_learning set
    r = _make_review(u.id, difficulty=3, workload_hours=None)
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    radar = result['radar_values']
    assert len(radar) == 6
    assert radar[1] == 0   # exams — no data
    assert radar[2] == 0   # workload — no workload_hours
    assert radar[3] == 0   # group work — no data
    assert radar[4] == 0   # time commit — no data, no workload proxy
    assert radar[5] == 0   # rote learning — no data


def test_radar_all_axes_populated(app, db):
    u = _make_user(db)
    r = _make_review(
        u.id,
        difficulty=3,
        exam_difficulty=4,
        group_work=2,
        time_commitment=5,
        rote_learning=1,
        workload_hours=16,
    )
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    radar = result['radar_values']
    assert radar[0] == round((3 - 1) / 4, 2)   # content
    assert radar[1] == round((4 - 1) / 4, 2)   # exams
    assert radar[2] == round(16 / 40.0, 2)      # workload
    assert radar[3] == round((2 - 1) / 4, 2)   # group work
    assert radar[4] == round((5 - 1) / 4, 2)   # time commit
    assert radar[5] == round((1 - 1) / 4, 2)   # rote learning


def test_radar_time_commit_falls_back_to_workload(app, db):
    u = _make_user(db)
    r = _make_review(u.id, workload_hours=20)   # no time_commitment set
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    radar = result['radar_values']
    assert radar[4] == round(20 / 40.0, 2)


# ---------------------------------------------------------------------------
# Would-recommend percentage
# ---------------------------------------------------------------------------

def test_would_recommend_pct(app, db):
    u = _make_user(db)
    reviews = [
        _make_review(u.id, would_recommend=True),
        _make_review(u.id, would_recommend=True),
        _make_review(u.id, would_recommend=False),
    ]
    db.session.commit()

    result = community_stats_for('TEST1001', reviews)
    assert result['would_recommend_pct'] == round(2 / 3 * 100)


def test_would_recommend_none_when_not_filled(app, db):
    u = _make_user(db)
    r = _make_review(u.id)   # would_recommend not set
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    assert result['would_recommend_pct'] is None


# ---------------------------------------------------------------------------
# No YAML-only fields in output
# ---------------------------------------------------------------------------

def test_no_yaml_only_fields(app, db):
    u = _make_user(db)
    r = _make_review(u.id)
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    for key in ('pass_rate', 'elective_pct', 'elective_label', 'core_rating', 'compare_unit'):
        assert key not in result, f"YAML-only field '{key}' should not appear in live stats"


# ---------------------------------------------------------------------------
# Rating bars
# ---------------------------------------------------------------------------

def test_content_difficulty_bar_always_present(app, db):
    u = _make_user(db)
    r = _make_review(u.id, difficulty=4)
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    bars = result['ratings']
    assert bars[0]['label'] == 'Content difficulty'
    assert bars[0]['value'] == round(4 * 2, 1)


def test_optional_bars_absent_without_data(app, db):
    u = _make_user(db)
    r = _make_review(u.id)   # no optional fields
    db.session.commit()

    result = community_stats_for('TEST1001', [r])
    labels = [b['label'] for b in result['ratings']]
    assert 'Exam difficulty' not in labels
    assert 'Group work' not in labels
