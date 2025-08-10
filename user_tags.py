"""
User Tag System for Neural Dreams Inc.
Analyzes user behavior and assigns appropriate dream tags
"""
from app import db
from sqlalchemy import func
from collections import Counter

# Dream tag definitions with descriptions and thresholds
DREAM_TAGS = {
    'scary': {
        'name': 'Nightmare Weaver',
        'icon': '👹',
        'description': 'Master of spine-chilling dreams and dark fantasies',
        'color': '#8B0000'
    },
    'romantic': {
        'name': 'Love Dreamer',
        'icon': '💕',
        'description': 'Creator of romantic visions and heart-warming tales',
        'color': '#FF69B4'
    },
    'surreal': {
        'name': 'Reality Bender',
        'icon': '🌀',
        'description': 'Artist of impossible worlds and mind-bending experiences',
        'color': '#9932CC'
    },
    'funny': {
        'name': 'Dream Comedian',
        'icon': '😂',
        'description': 'Bringer of laughter and whimsical adventures',
        'color': '#FFD700'
    },
    'bizarre': {
        'name': 'Chaos Architect',
        'icon': '🎭',
        'description': 'Creator of strange and wonderfully weird experiences',
        'color': '#FF4500'
    }
}

# Special tags for achievements
ACHIEVEMENT_TAGS = {
    'dream_master': {
        'name': 'Dream Master',
        'icon': '👑',
        'description': 'Created 20+ highly-rated dreams',
        'color': '#FFD700',
        'threshold': 20
    },
    'top_seller': {
        'name': 'Dream Merchant',
        'icon': '💰',
        'description': 'Earned 10,000+ points from dream sales',
        'color': '#32CD32',
        'threshold': 10000
    },
    'dream_collector': {
        'name': 'Dream Collector',
        'icon': '🛍️',
        'description': 'Purchased 50+ dreams',
        'color': '#4169E1',
        'threshold': 50
    },
    'generous_rater': {
        'name': 'Dream Critic',
        'icon': '⭐',
        'description': 'Rated 100+ dreams',
        'color': '#FF6347',
        'threshold': 100
    },
    'versatile_dreamer': {
        'name': 'Versatile Visionary',
        'icon': '🎨',
        'description': 'Created dreams in all categories',
        'color': '#9370DB',
        'threshold': 5  # All 5 categories
    }
}

def analyze_user_dream_preferences(user_id):
    """Analyze user's dream creation and purchase patterns"""
    from models import User, Dream, Purchase
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Get user's created dreams
    created_dreams = Dream.query.filter_by(author_id=user_id).all()
    
    # Get user's purchased dreams
    purchased_dreams = db.session.query(Dream).join(Purchase).filter(Purchase.buyer_id == user_id).all()
    
    # Combine creation and purchase preferences (weighted: 70% creation, 30% purchase)
    creation_categories = [dream.category for dream in created_dreams]
    purchase_categories = [dream.category for dream in purchased_dreams]
    
    # Count categories with weights
    category_scores = Counter()
    
    # Weight created dreams more heavily
    for category in creation_categories:
        category_scores[category] += 0.7
    
    # Add purchase preferences
    for category in purchase_categories:
        category_scores[category] += 0.3
    
    return category_scores

def get_primary_dream_tag(user_id):
    """Get the primary dream tag for a user based on their preferences"""
    preferences = analyze_user_dream_preferences(user_id)
    
    if not preferences:
        return None
    
    # Get the most common category
    primary_category = preferences.most_common(1)[0][0]
    
    return DREAM_TAGS.get(primary_category)

def check_achievement_tags(user_id):
    """Check if user qualifies for any achievement tags"""
    from models import User, Dream, Purchase, Rating
    user = User.query.get(user_id)
    if not user:
        return []
    
    achievements = []
    
    # Dream Master - 20+ dreams with good ratings
    dream_count = Dream.query.filter_by(author_id=user_id).filter(Dream.average_rating >= 3.5).count()
    if dream_count >= ACHIEVEMENT_TAGS['dream_master']['threshold']:
        achievements.append('dream_master')
    
    # Top Seller - check earnings
    total_earnings = db.session.query(func.sum(Purchase.price_paid)).join(Dream).filter(Dream.author_id == user_id).scalar() or 0
    if total_earnings >= ACHIEVEMENT_TAGS['top_seller']['threshold']:
        achievements.append('top_seller')
    
    # Dream Collector - 50+ purchases
    purchase_count = Purchase.query.filter_by(buyer_id=user_id).count()
    if purchase_count >= ACHIEVEMENT_TAGS['dream_collector']['threshold']:
        achievements.append('dream_collector')
    
    # Generous Rater - 100+ ratings given
    rating_count = Rating.query.filter_by(rater_id=user_id).count()
    if rating_count >= ACHIEVEMENT_TAGS['generous_rater']['threshold']:
        achievements.append('generous_rater')
    
    # Versatile Dreamer - dreams in all 5 categories
    user_categories = db.session.query(Dream.category).filter_by(author_id=user_id).distinct().all()
    unique_categories = len([cat[0] for cat in user_categories])
    if unique_categories >= ACHIEVEMENT_TAGS['versatile_dreamer']['threshold']:
        achievements.append('versatile_dreamer')
    
    return achievements

def update_user_tag(user_id):
    """Update a user's dream tag based on their current activity"""
    from models import User
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Check for achievement tags first (higher priority)
    achievements = check_achievement_tags(user_id)
    
    if achievements:
        # Use the first achievement tag found
        primary_achievement = achievements[0]
        user.dream_tag = primary_achievement
    else:
        # Fall back to category-based tag
        primary_tag = get_primary_dream_tag(user_id)
        if primary_tag:
            # Store the category name in the tag field
            preferences = analyze_user_dream_preferences(user_id)
            primary_category = preferences.most_common(1)[0][0]
            user.dream_tag = primary_category
        else:
            user.dream_tag = None
    
    db.session.commit()
    return True

def get_user_tag_info(user):
    """Get formatted tag information for display"""
    if not user.dream_tag:
        return None
    
    # Check if it's an achievement tag
    if user.dream_tag in ACHIEVEMENT_TAGS:
        tag_info = ACHIEVEMENT_TAGS[user.dream_tag].copy()
        tag_info['type'] = 'achievement'
        return tag_info
    
    # Check if it's a category tag
    if user.dream_tag in DREAM_TAGS:
        tag_info = DREAM_TAGS[user.dream_tag].copy()
        tag_info['type'] = 'category'
        return tag_info
    
    return None

def update_all_user_tags():
    """Update tags for all users (useful for batch processing)"""
    from models import User
    users = User.query.all()
    updated_count = 0
    
    for user in users:
        if update_user_tag(user.id):
            updated_count += 1
    
    return updated_count

def get_users_by_tag(tag_name):
    """Get all users with a specific tag"""
    from models import User
    return User.query.filter_by(dream_tag=tag_name).all()

def get_tag_leaderboard():
    """Get a leaderboard of users grouped by their tags"""
    from models import User
    tag_counts = db.session.query(User.dream_tag, func.count(User.id)).filter(User.dream_tag.isnot(None)).group_by(User.dream_tag).all()
    
    leaderboard = []
    for tag, count in tag_counts:
        tag_info = get_tag_info_by_name(tag)
        if tag_info:
            leaderboard.append({
                'tag': tag,
                'info': tag_info,
                'user_count': count,
                'users': User.query.filter_by(dream_tag=tag).limit(5).all()
            })
    
    return sorted(leaderboard, key=lambda x: x['user_count'], reverse=True)

def get_tag_info_by_name(tag_name):
    """Get tag info by tag name"""
    if tag_name in ACHIEVEMENT_TAGS:
        info = ACHIEVEMENT_TAGS[tag_name].copy()
        info['type'] = 'achievement'
        return info
    elif tag_name in DREAM_TAGS:
        info = DREAM_TAGS[tag_name].copy()
        info['type'] = 'category'
        return info
    return None