from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import User, Dream, Purchase, Rating
from forms import ProfileForm
from dream_utils import get_user_stats

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/')
@login_required
def index():
    return redirect(url_for('profile.view_profile', username=current_user.username))

@profile_bp.route('/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get user's dreams
    dreams = Dream.query.filter_by(author_id=user.id).order_by(Dream.created_at.desc()).all()
    
    # Get user statistics
    stats = get_user_stats(user)
    
    # Get recent ratings received
    recent_ratings = db.session.query(Rating, Dream).join(Dream).filter(
        Dream.author_id == user.id
    ).order_by(Rating.created_at.desc()).limit(5).all()
    
    # Check if viewing own profile
    is_own_profile = current_user.is_authenticated and current_user.id == user.id
    
    # Get purchased dreams if viewing own profile
    purchased_dreams = []
    if is_own_profile:
        purchased_dreams = db.session.query(Dream, Purchase).join(Purchase).filter(
            Purchase.buyer_id == user.id
        ).order_by(Purchase.purchase_date.desc()).all()
    
    return render_template('profile.html', 
                         user=user, 
                         dreams=dreams, 
                         stats=stats,
                         recent_ratings=recent_ratings,
                         is_own_profile=is_own_profile,
                         purchased_dreams=purchased_dreams)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(current_user.username, current_user.email, obj=current_user)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        
        db.session.commit()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.view_profile', username=current_user.username))
    
    return render_template('edit_profile.html', form=form)

@profile_bp.route('/purchases')
@login_required
def purchases():
    page = request.args.get('page', 1, type=int)
    
    # Get purchases using traditional SQLAlchemy approach
    purchases_data = db.session.query(Purchase, Dream).join(Dream).filter(
        Purchase.buyer_id == current_user.id
    ).order_by(Purchase.purchase_date.desc())
    
    # Manual pagination
    total = purchases_data.count()
    purchases_list = purchases_data.offset((page - 1) * 10).limit(10).all()
    
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
            
        def iter_pages(self):
            for i in range(1, self.pages + 1):
                yield i
    
    purchases = SimplePagination(purchases_list, page, 10, total)
    
    return render_template('purchases.html', purchases=purchases)

@profile_bp.route('/sales')
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    
    # Get sales using traditional SQLAlchemy approach
    sales_data = db.session.query(Purchase, Dream).join(Dream).filter(
        Dream.author_id == current_user.id
    ).order_by(Purchase.purchase_date.desc())
    
    # Manual pagination
    total = sales_data.count()
    sales_list = sales_data.offset((page - 1) * 10).limit(10).all()
    
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
            
        def iter_pages(self):
            for i in range(1, self.pages + 1):
                yield i
    
    sales = SimplePagination(sales_list, page, 10, total)
    
    return render_template('sales.html', sales=sales)

@profile_bp.route('/ratings-given')
@login_required
def ratings_given():
    page = request.args.get('page', 1, type=int)
    
    from sqlalchemy import select
    ratings_query = select(Rating, Dream).join(Dream).filter(
        Rating.rater_id == current_user.id
    ).order_by(Rating.created_at.desc())
    ratings = db.paginate(ratings_query, page=page, per_page=10, error_out=False)
    
    return render_template('ratings_given.html', ratings=ratings)

@profile_bp.route('/ratings-received')
@login_required
def ratings_received():
    page = request.args.get('page', 1, type=int)
    
    from sqlalchemy import select
    ratings_query = select(Rating, Dream).join(Dream).filter(
        Dream.author_id == current_user.id
    ).order_by(Rating.created_at.desc())
    ratings = db.paginate(ratings_query, page=page, per_page=10, error_out=False)
    
    return render_template('ratings_received.html', ratings=ratings)
