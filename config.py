import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'neural-dreams-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///neural_dreams.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Dream categories
    DREAM_CATEGORIES = ['surreal', 'funny', 'scary', 'romantic', 'bizarre']
    
    # Points system
    STARTING_POINTS = 1000
    WEEKLY_BONUS_POINTS = 100
