from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    points = db.Column(db.Integer, default=1000)  # Starting points
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text)
    
    # Relationships
    dreams = db.relationship('Dream', backref='author', lazy=True, cascade='all, delete-orphan')
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)
    ratings = db.relationship('Rating', backref='rater', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_average_rating(self):
        """Calculate average rating for dreams sold by this user"""
        avg = db.session.query(func.avg(Dream.average_rating)).filter_by(author_id=self.id).scalar()
        return round(avg, 1) if avg else 0.0
    
    def get_total_sales(self):
        """Get total number of dreams sold"""
        return Purchase.query.filter_by(dream_id=Dream.id).join(Dream).filter_by(author_id=self.id).count()

class Dream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # surreal, funny, scary, romantic, bizarre
    price = db.Column(db.Integer, nullable=False)  # Price in points
    image_filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    average_rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    purchases = db.relationship('Purchase', backref='dream', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='dream', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Dream {self.title}>'
    
    def update_rating(self):
        """Update average rating based on all ratings"""
        ratings = Rating.query.filter_by(dream_id=self.id).all()
        if ratings:
            self.average_rating = sum(r.rating for r in ratings) / len(ratings)
            self.total_ratings = len(ratings)
        else:
            self.average_rating = 0.0
            self.total_ratings = 0
        db.session.commit()
    
    def is_purchased_by(self, user):
        """Check if dream is purchased by given user"""
        if not user.is_authenticated:
            return False
        return Purchase.query.filter_by(buyer_id=user.id, dream_id=self.id).first() is not None
    
    def get_user_rating(self, user):
        """Get rating given by specific user"""
        if not user.is_authenticated:
            return None
        rating = Rating.query.filter_by(rater_id=user.id, dream_id=self.id).first()
        return rating.rating if rating else None

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dream_id = db.Column(db.Integer, db.ForeignKey('dream.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    price_paid = db.Column(db.Integer, nullable=False)  # Points paid at time of purchase
    
    def __repr__(self):
        return f'<Purchase {self.buyer_id} -> {self.dream_id}>'

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dream_id = db.Column(db.Integer, db.ForeignKey('dream.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one rating per user per dream
    __table_args__ = (db.UniqueConstraint('rater_id', 'dream_id', name='unique_user_dream_rating'),)
    
    def __repr__(self):
        return f'<Rating {self.rating}/5 for Dream {self.dream_id}>'
