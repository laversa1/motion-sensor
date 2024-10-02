from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database and Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///motion_sensor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '031121'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model to handle user information and authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Load the user from the database when needed
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Model for motion detection events, linked to the user who triggered it
class MotionEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<MotionEvent {self.id} at {self.timestamp}>'

# Create database tables if they don't already exist
with app.app_context():
    db.create_all()

# Route to handle motion detection; requires user login
@app.route('/motion', methods=['POST'])
@login_required
def motion_detected():
    new_event = MotionEvent(user_id=current_user.id)
    db.session.add(new_event)
    db.session.commit()

    return {'message': 'Motion detected!', 'timestamp': new_event.timestamp}, 201

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password before saving it to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password==password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('display_events'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Display motion events for the logged-in user
@app.route('/display')
@login_required
def display_events():
    events = MotionEvent.query.filter_by(user_id=current_user.id).all()
    return render_template('events.html', events=events)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
