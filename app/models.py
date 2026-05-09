from datetime import datetime, timezone

import pyotp
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class User(TimestampMixin, UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    student_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.String(120), nullable=True)
    two_fa_enabled = db.Column(db.Boolean, nullable=False, default=False)
    totp_secret = db.Column(db.String(64), nullable=True)

    study_plans = db.relationship('StudyPlan', back_populates='user', cascade='all, delete-orphan')
    reviews = db.relationship('UnitReview', back_populates='user', cascade='all, delete-orphan')
    notification_preferences = db.relationship(
        'NotificationPreference',
        back_populates='user',
        cascade='all, delete-orphan',
        uselist=False,
    )

    @property
    def initials(self):
        parts = [p for p in self.display_name.strip().split() if p]
        if parts:
            return ''.join(p[0] for p in parts[:2]).upper()
        return self.email[:2].upper()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_totp_secret(self):
        """Generate and return a new TOTP secret without saving it yet."""
        return pyotp.random_base32()

    def verify_totp(self, code):
        """Check a 6-digit TOTP code against the user's stored secret."""
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(code, valid_window=1)

    def get_totp_uri(self):
        """Return the otpauth URI used to generate the QR code."""
        return pyotp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='stUwa',
        )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class StudyPlan(TimestampMixin, db.Model):
    __tablename__ = 'study_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, default='My study plan')
    primary_degree_slug = db.Column(db.String(120), nullable=True)
    secondary_degree_slug = db.Column(db.String(120), nullable=True)
    start_year = db.Column(db.Integer, nullable=False)
    start_semester = db.Column(db.Integer, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='study_plans')
    units = db.relationship(
        'StudyPlanUnit',
        back_populates='study_plan',
        cascade='all, delete-orphan',
        order_by='StudyPlanUnit.position',
    )


class StudyPlanUnit(TimestampMixin, db.Model):
    __tablename__ = 'study_plan_units'

    id = db.Column(db.Integer, primary_key=True)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False, index=True)
    unit_code = db.Column(db.String(16), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(24), nullable=False, default='planned')
    position = db.Column(db.Integer, nullable=False, default=0)

    study_plan = db.relationship('StudyPlan', back_populates='units')


class UnitReview(TimestampMixin, db.Model):
    __tablename__ = 'unit_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    unit_code = db.Column(db.String(16), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    workload_hours = db.Column(db.Integer, nullable=True)
    semester_taken = db.Column(db.String(32), nullable=True)
    body = db.Column(db.Text, nullable=False)

    user = db.relationship('User', back_populates='reviews')


class NotificationPreference(TimestampMixin, db.Model):
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    planner_reminders = db.Column(db.Boolean, nullable=False, default=True)
    unit_catalogue_updates = db.Column(db.Boolean, nullable=False, default=False)
    community_replies = db.Column(db.Boolean, nullable=False, default=False)
    weekly_digest = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='notification_preferences')
