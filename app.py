import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "neural-dreams-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neural_dreams.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message = 'Please log in to access this dreamy marketplace.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes.auth_routes import auth_bp
from routes.marketplace_routes import marketplace_bp
from routes.profile_routes import profile_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
app.register_blueprint(profile_bp, url_prefix='/profile')

# Main routes
from flask import render_template, redirect, url_for
from models import Dream, User
from dream_utils import get_dream_of_the_week

@app.route('/')
def home():
    dream_of_week = get_dream_of_the_week()
    recent_dreams = Dream.query.order_by(Dream.created_at.desc()).limit(6).all()
    top_sellers = User.query.join(Dream).group_by(User.id).order_by(db.func.avg(Dream.average_rating).desc()).limit(5).all()
    
    return render_template('home.html', 
                         dream_of_week=dream_of_week,
                         recent_dreams=recent_dreams,
                         top_sellers=top_sellers)

@app.route('/leaderboard')
def leaderboard():
    # Get top sellers by average rating
    top_sellers = db.session.query(User, db.func.avg(Dream.average_rating).label('avg_rating'), db.func.count(Dream.id).label('dream_count')) \
        .join(Dream) \
        .group_by(User.id) \
        .having(db.func.count(Dream.id) > 0) \
        .order_by(db.func.avg(Dream.average_rating).desc()) \
        .limit(20).all()
    
    return render_template('leaderboard.html', top_sellers=top_sellers)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    import models
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
