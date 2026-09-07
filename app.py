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
@app.route('/admin/new-review', methods=['GET', 'POST'])
@login_required
def new_review():
    if request.method == 'POST':
        review = Review(
            title=request.form.get('title'),
            author=request.form.get('author'),
            review_text=request.form.get('review_text'),
            favorite_quote=request.form.get('favorite_quote'),
            cover_image=request.form.get('cover_image')
        )
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_review.html')
@app.route('/admin/new-journal', methods=['GET', 'POST'])
@login_required
def new_journal():
    if request.method == 'POST':
        entry = JournalEntry(
            title=request.form.get('title'),
            body=request.form.get('body')
        )
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_journal.html')
@app.route('/journal')
def journal():
    entries = JournalEntry.query.order_by(JournalEntry.date_posted.desc()).all()
    return render_template('journal.html', entries=entries)

@app.route('/quotes')
def quotes():
    reviews = Review.query.filter(Review.favorite_quote.isnot(None), Review.favorite_quote != '').all()
    return render_template('quotes.html', reviews=reviews)

class AboutInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(300))
@app.route('/about')
def about():
    info = AboutInfo.query.first()
    return render_template('about.html', info=info)

@app.route('/admin/edit-about', methods=['GET', 'POST'])
@login_required
def edit_about():
    info = AboutInfo.query.first()
    if not info:
        info = AboutInfo()
        db.session.add(info)

    if request.method == 'POST':
        info.bio = request.form.get('bio')
        info.photo_url = request.form.get('photo_url')
        db.session.commit()
        return redirect(url_for('about'))

    return render_template('edit_about.html', info=info)
if __name__ == '__main__':
    app.run(debug=True)