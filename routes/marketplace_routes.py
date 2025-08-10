from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from models import Dream, Purchase, Rating, User
from forms import DreamForm, RatingForm, SearchForm
from dream_utils import save_dream_image, delete_dream_image, process_dream_purchase, validate_purchase
from sqlalchemy import or_, and_

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
def index():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Dream.query
    
    # Apply search filters
    search_query = request.args.get('query', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    sort_by = request.args.get('sort_by', 'newest')
    
    if search_query:
        query = query.filter(or_(
            Dream.title.contains(search_query),
            Dream.description.contains(search_query)
        ))
        form.query.data = search_query
    
    if category:
        query = query.filter(Dream.category == category)
        form.category.data = category
    
    if min_price is not None:
        query = query.filter(Dream.price >= min_price)
        form.min_price.data = min_price
    
    if max_price is not None:
        query = query.filter(Dream.price <= max_price)
        form.max_price.data = max_price
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(Dream.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Dream.created_at.asc())
    elif sort_by == 'price_low':
        query = query.order_by(Dream.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Dream.price.desc())
    elif sort_by == 'rating_high':
        query = query.order_by(Dream.average_rating.desc())
    elif sort_by == 'rating_low':
        query = query.order_by(Dream.average_rating.asc())
    
    form.sort_by.data = sort_by
    
    # Paginate results
    dreams = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('marketplace.html', dreams=dreams, form=form)

@marketplace_bp.route('/dream/<int:id>')
def dream_detail(id):
    dream = Dream.query.get_or_404(id)
    rating_form = RatingForm()
    rating_form.dream_id.data = id
    
    # Get user's existing rating
    user_rating = None
    if current_user.is_authenticated:
        user_rating = dream.get_user_rating(current_user)
        if user_rating:
            rating_form.rating.data = user_rating
    
    # Get all ratings for this dream
    ratings = Rating.query.filter_by(dream_id=id).order_by(Rating.created_at.desc()).all()
    
    # Check if user can purchase
    can_purchase = False
    purchase_message = ""
    if current_user.is_authenticated:
        can_purchase, purchase_message = validate_purchase(current_user, dream)
    
    return render_template('dream_detail.html', 
                         dream=dream, 
                         rating_form=rating_form,
                         user_rating=user_rating,
                         ratings=ratings,
                         can_purchase=can_purchase,
                         purchase_message=purchase_message)

@marketplace_bp.route('/post', methods=['GET', 'POST'])
@login_required
def post_dream():
    form = DreamForm()
    
    if form.validate_on_submit():
        # Save image if uploaded
        image_filename = None
        if form.image.data:
            image_filename = save_dream_image(form.image.data)
            if not image_filename:
                flash('Error uploading image. Please try again.', 'danger')
                return render_template('post_dream.html', form=form)
        
        # Create dream
        dream = Dream()
        dream.title = form.title.data
        dream.description = form.description.data
        dream.category = form.category.data
        dream.price = form.price.data
        dream.image_filename = image_filename
        dream.author_id = current_user.id
        
        db.session.add(dream)
        db.session.commit()
        
        flash('Your dream has been shared with the world!', 'success')
        return redirect(url_for('marketplace.dream_detail', id=dream.id))
    
    return render_template('post_dream.html', form=form)

@marketplace_bp.route('/buy/<int:id>', methods=['POST'])
@login_required
def buy_dream(id):
    dream = Dream.query.get_or_404(id)
    
    success, message = process_dream_purchase(current_user, dream)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('marketplace.dream_detail', id=id))

@marketplace_bp.route('/rate/<int:id>', methods=['POST'])
@login_required
def rate_dream(id):
    dream = Dream.query.get_or_404(id)
    form = RatingForm()
    
    # Check if user purchased the dream
    if not dream.is_purchased_by(current_user):
        flash('You can only rate dreams you have purchased.', 'danger')
        return redirect(url_for('marketplace.dream_detail', id=id))
    
    if form.validate_on_submit():
        # Check for existing rating
        existing_rating = Rating.query.filter_by(
            rater_id=current_user.id,
            dream_id=id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = form.rating.data
            existing_rating.review = form.review.data
        else:
            # Create new rating
            rating = Rating()
            rating.rater_id = current_user.id
            rating.dream_id = id
            rating.rating = form.rating.data
            rating.review = form.review.data
            db.session.add(rating)
        
        db.session.commit()
        
        # Update dream's average rating
        dream.update_rating()
        
        flash('Thank you for rating this dream!', 'success')
    else:
        flash('Error submitting rating. Please try again.', 'danger')
    
    return redirect(url_for('marketplace.dream_detail', id=id))

@marketplace_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dream(id):
    dream = Dream.query.get_or_404(id)
    
    # Check if user owns the dream
    if dream.author_id != current_user.id:
        flash('You can only edit your own dreams.', 'danger')
        return redirect(url_for('marketplace.dream_detail', id=id))
    
    form = DreamForm(obj=dream)
    
    if form.validate_on_submit():
        # Handle image update
        if form.image.data:
            # Delete old image
            if dream.image_filename:
                delete_dream_image(dream.image_filename)
            
            # Save new image
            image_filename = save_dream_image(form.image.data)
            if image_filename:
                dream.image_filename = image_filename
        
        # Update dream data
        dream.title = form.title.data
        dream.description = form.description.data
        dream.category = form.category.data
        dream.price = form.price.data
        
        db.session.commit()
        
        flash('Your dream has been updated!', 'success')
        return redirect(url_for('marketplace.dream_detail', id=id))
    
    return render_template('post_dream.html', form=form, dream=dream, edit_mode=True)

@marketplace_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_dream(id):
    dream = Dream.query.get_or_404(id)
    
    # Check if user owns the dream
    if dream.author_id != current_user.id:
        flash('You can only delete your own dreams.', 'danger')
        return redirect(url_for('marketplace.dream_detail', id=id))
    
    # Delete associated image
    if dream.image_filename:
        delete_dream_image(dream.image_filename)
    
    # Delete dream (cascades to ratings and purchases)
    db.session.delete(dream)
    db.session.commit()
    
    flash('Your dream has been deleted.', 'info')
    return redirect(url_for('profile.index'))
