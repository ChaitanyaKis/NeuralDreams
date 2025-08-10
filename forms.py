from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User
from config import Config

class SignupForm(FlaskForm):
    username = StringField('Dream Walker Name', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Enter the Dream Realm')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This dream walker name is already taken. Please choose another.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    username = StringField('Dream Walker Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter Dreams')

class DreamForm(FlaskForm):
    title = StringField('Dream Title', validators=[
        DataRequired(),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ])
    description = TextAreaField('Dream Description', validators=[
        DataRequired(),
        Length(min=20, message='Description must be at least 20 characters')
    ])
    category = SelectField('Dream Category', 
                          choices=[(cat, cat.title()) for cat in Config.DREAM_CATEGORIES],
                          validators=[DataRequired()])
    price = IntegerField('Price (Dream Points)', validators=[
        DataRequired(),
        NumberRange(min=1, max=10000, message='Price must be between 1 and 10,000 points')
    ])
    image = FileField('Dream Visualization', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Please upload an image file (jpg, jpeg, png, gif)')
    ])
    submit = SubmitField('Share Your Dream')

class RatingForm(FlaskForm):
    rating = SelectField('Rating', 
                        choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                        coerce=int,
                        validators=[DataRequired()])
    review = TextAreaField('Review (Optional)', validators=[Length(max=500)])
    dream_id = HiddenField()
    submit = SubmitField('Submit Rating')

class SearchForm(FlaskForm):
    query = StringField('Search Dreams...')
    category = SelectField('Category', 
                          choices=[('', 'All Categories')] + [(cat, cat.title()) for cat in Config.DREAM_CATEGORIES])
    min_price = IntegerField('Min Price', validators=[NumberRange(min=0)])
    max_price = IntegerField('Max Price', validators=[NumberRange(min=0)])
    sort_by = SelectField('Sort By', 
                         choices=[('newest', 'Newest First'), 
                                ('oldest', 'Oldest First'),
                                ('price_low', 'Price: Low to High'),
                                ('price_high', 'Price: High to Low'),
                                ('rating_high', 'Highest Rated'),
                                ('rating_low', 'Lowest Rated')])
    submit = SubmitField('Search Dreams')

class ProfileForm(FlaskForm):
    username = StringField('Dream Walker Name', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This dream walker name is already taken.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already registered.')
