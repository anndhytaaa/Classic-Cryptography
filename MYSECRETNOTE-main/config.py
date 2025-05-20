from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True)

    def __repr__(self):
        return f'<User id={self.id}, email={self.email}>'

    def generate_reset_token(self):
        # Generate a secure token
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(token=token, user=self)
        db.session.add(reset_token)
        db.session.commit()
        return token


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))

    def __repr__(self):
        return f'<PasswordResetToken id={self.id}, token={self.token}, user_id={self.user_id}>'

    @staticmethod
    def is_valid(token):
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token and reset_token.expires_at > datetime.utcnow():
            return reset_token
        return None
