import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

class AdminUser(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return AdminUser()
    return None

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    favorite_quote = db.Column(db.Text)
    cover_image = db.Column(db.String(300))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    reviews = Review.query.order_by(Review.date_added.desc()).all()
    return render_template('index.html', reviews=reviews)

@app.route('/review/<int:review_id>')
def review_detail(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template('review_detail.html', review=review)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            login_user(AdminUser())
            return redirect(url_for('home'))
        return render_template('admin_login.html', error="Incorrect username or password")
    return render_template('admin_login.html', error=None)

@app.route('/admin-logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)