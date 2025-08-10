from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User
from forms import LoginForm, SignupForm
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            flash(f'Welcome back to the dream realm, {user.username}!', 'success')
            
            # Redirect to next page if specified
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid dream walker name or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Create new user
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        user.points = Config.STARTING_POINTS
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Welcome to Neural Dreams Inc., {user.username}! You start with {Config.STARTING_POINTS} dream points.', 'success')
        login_user(user, remember=True)
        return redirect(url_for('home'))
    
    return render_template('signup.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f'Goodbye {username}, may your dreams be ever surreal!', 'info')
    return redirect(url_for('home'))
