import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app
from models import Dream, Rating
from datetime import datetime, timedelta

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_dream_image(image_file):
    """Save uploaded image and return filename"""
    if image_file and allowed_file(image_file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + image_file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Resize and save image
        try:
            image = Image.open(image_file)
            # Resize image to max 800x600 while maintaining aspect ratio
            image.thumbnail((800, 600), Image.Resampling.LANCZOS)
            image.save(filepath, optimize=True, quality=85)
            return filename
        except Exception as e:
            current_app.logger.error(f"Error saving image: {e}")
            return None
    return None

def delete_dream_image(filename):
    """Delete dream image file"""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            current_app.logger.error(f"Error deleting image: {e}")

def calculate_dream_rating(dream_id):
    """Calculate and update average rating for a dream"""
    from app import db
    ratings = db.session.query(Rating).filter_by(dream_id=dream_id).all()
    if ratings:
        average = sum(r.rating for r in ratings) / len(ratings)
        return round(average, 1), len(ratings)
    return 0.0, 0

def get_dream_of_the_week():
    """Get the highest-rated dream from the past week"""
    from app import db
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get dreams from the past week with highest rating
    dream_of_week = db.session.query(Dream).filter(
        Dream.created_at >= week_ago,
        Dream.total_ratings > 0
    ).order_by(Dream.average_rating.desc(), Dream.total_ratings.desc()).first()
    
    # If no dreams this week, get overall highest rated
    if not dream_of_week:
        dream_of_week = db.session.query(Dream).filter(
            Dream.total_ratings > 0
        ).order_by(Dream.average_rating.desc(), Dream.total_ratings.desc()).first()
    
    return dream_of_week

def get_trending_dreams(limit=6):
    """Get trending dreams based on recent ratings and purchases"""
    from app import db
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Dreams with recent activity (ratings or purchases)
    trending = db.session.query(Dream).filter(
        Dream.created_at >= week_ago
    ).order_by(Dream.average_rating.desc(), Dream.total_ratings.desc()).limit(limit).all()
    
    return trending

def format_price(price):
    """Format price with dream points symbol"""
    return f"✨ {price:,} points"

def get_category_icon(category):
    """Get emoji icon for dream category"""
    icons = {
        'surreal': '🌀',
        'funny': '😄',
        'scary': '👻',
        'romantic': '💕',
        'bizarre': '🎭'
    }
    return icons.get(category, '💭')

def validate_purchase(user, dream):
    """Validate if user can purchase dream"""
    if not user.is_authenticated:
        return False, "Please log in to purchase dreams"
    
    if user.id == dream.author_id:
        return False, "You cannot purchase your own dreams"
    
    if user.points < dream.price:
        return False, f"Insufficient points. You need {dream.price - user.points} more points"
    
    # Check if already purchased
    from app import db
    from models import Purchase
    existing_purchase = db.session.query(Purchase).filter_by(buyer_id=user.id, dream_id=dream.id).first()
    if existing_purchase:
        return False, "You have already purchased this dream"
    
    return True, "Purchase valid"

def process_dream_purchase(buyer, dream):
    """Process dream purchase transaction"""
    from app import db
    from models import Purchase
    
    # Validate purchase
    is_valid, message = validate_purchase(buyer, dream)
    if not is_valid:
        return False, message
    
    try:
        # Deduct points from buyer
        buyer.points -= dream.price
        
        # Add points to seller
        dream.author.points += dream.price
        
        # Create purchase record
        purchase = Purchase()
        purchase.buyer_id = buyer.id
        purchase.dream_id = dream.id
        purchase.price_paid = dream.price
        
        db.session.add(purchase)
        db.session.commit()
        
        return True, "Dream purchased successfully!"
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Purchase error: {e}")
        return False, "An error occurred during purchase"

def get_user_stats(user):
    """Get comprehensive user statistics"""
    from models import Dream, Purchase, Rating
    from sqlalchemy import func
    
    stats = {
        'dreams_posted': Dream.query.filter_by(author_id=user.id).count(),
        'dreams_purchased': Purchase.query.filter_by(buyer_id=user.id).count(),
        'total_earnings': 0,
        'total_spent': 0,
        'average_rating_received': 0.0,
        'ratings_given': Rating.query.filter_by(rater_id=user.id).count()
    }
    
    # Calculate earnings
    earnings = db.session.query(func.sum(Purchase.price_paid)).join(Dream).filter(Dream.author_id == user.id).scalar()
    stats['total_earnings'] = earnings or 0
    
    # Calculate spending
    spending = db.session.query(func.sum(Purchase.price_paid)).filter(Purchase.buyer_id == user.id).scalar()
    stats['total_spent'] = spending or 0
    
    # Calculate average rating received
    avg_rating = db.session.query(func.avg(Dream.average_rating)).filter(
        Dream.author_id == user.id,
        Dream.total_ratings > 0
    ).scalar()
    stats['average_rating_received'] = round(avg_rating, 1) if avg_rating else 0.0
    
    return stats
