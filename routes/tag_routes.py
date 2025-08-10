"""
Tag management routes for Neural Dreams Inc.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from user_tags import (
    update_all_user_tags, 
    get_tag_leaderboard, 
    get_users_by_tag,
    DREAM_TAGS,
    ACHIEVEMENT_TAGS
)
from models import User
from app import db

tag_bp = Blueprint('tags', __name__, url_prefix='/tags')

@tag_bp.route('/')
def tag_leaderboard():
    """Display tag leaderboard and statistics"""
    leaderboard = get_tag_leaderboard()
    
    # Get all available tags for filtering
    all_tags = {**DREAM_TAGS, **ACHIEVEMENT_TAGS}
    
    return render_template('tags/leaderboard.html', 
                         leaderboard=leaderboard, 
                         all_tags=all_tags)

@tag_bp.route('/category/<category>')
def users_by_category(category):
    """Display users with a specific tag"""
    users = get_users_by_tag(category)
    
    # Get tag info
    tag_info = None
    if category in DREAM_TAGS:
        tag_info = DREAM_TAGS[category]
        tag_info['type'] = 'category'
    elif category in ACHIEVEMENT_TAGS:
        tag_info = ACHIEVEMENT_TAGS[category]
        tag_info['type'] = 'achievement'
    
    if not tag_info:
        flash('Tag not found', 'error')
        return redirect(url_for('tags.tag_leaderboard'))
    
    return render_template('tags/category_users.html', 
                         users=users, 
                         category=category, 
                         tag_info=tag_info)

@tag_bp.route('/update-all', methods=['POST'])
@login_required
def update_all_tags():
    """Update tags for all users (admin function)"""
    if current_user.username != 'admin':  # Simple admin check
        flash('Access denied', 'error')
        return redirect(url_for('tags.tag_leaderboard'))
    
    updated_count = update_all_user_tags()
    flash(f'Updated tags for {updated_count} users', 'success')
    return redirect(url_for('tags.tag_leaderboard'))

@tag_bp.route('/my-tag')
@login_required
def my_tag():
    """Display current user's tag information"""
    from user_tags import get_user_tag_info, analyze_user_dream_preferences
    
    tag_info = get_user_tag_info(current_user)
    preferences = analyze_user_dream_preferences(current_user.id)
    
    return render_template('tags/my_tag.html', 
                         tag_info=tag_info, 
                         preferences=preferences,
                         all_tags={**DREAM_TAGS, **ACHIEVEMENT_TAGS})