from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from datetime import datetime
import bcrypt
import re
from Response_Generation import get_qa_chain
import markdown
import os

app = Flask(__name__)

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# Session Secret key
app.secret_key = os.environ.get("SECRET_KEY")

# PostgreSQL Config
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load QA Chain
qa_chain = get_qa_chain()

# Database Models

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class ChatSession(db.Model):
    __tablename__ = 'chatsession'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    starttime = db.Column(db.DateTime, default=datetime.utcnow)
    endtime = db.Column(db.DateTime)

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sessionid = db.Column(db.Integer, db.ForeignKey('chatsession.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
    return render_template('index.html', user=user)


# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if len(username) < 6 or not username.isalnum():
            flash('Username must be at least 6 characters and contain only letters and numbers.', 'danger')
            return redirect(url_for('register'))

        # ===== Email Validation =====
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))

        # ===== Password Validation =====
        pass_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pass_pattern, password):
            flash('Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, one number, and one special character.', 'danger')
            return redirect(url_for('register'))

        # Check if user/email exists
        if User.query.filter(User.username == username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        if User.query.filter(User.email == email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))   
    
        hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt=bcrypt.gensalt()).decode('utf-8')

        # Save new user
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("User registered successfully. Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html', error=None)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_value = request.form['email'].strip()
        password = request.form['password'].strip()

        user = User.query.filter((User.username == input_value) | (User.email == input_value)).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            session['user_id'] = user.id
            print("Logged in! User ID:", user.id)
            return redirect(url_for('index'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


# Chat Route
@app.route('/chat', methods=['GET','POST'])
def chat():
    user_message = request.json.get('message')
    print("User Message:", user_message)
    bot_response = qa_chain.invoke(user_message)
    print("Bot Response:", bot_response)
    cleaned_response = bot_response['result']
    html_response = markdown.markdown(cleaned_response)

    print(" User ID in session:", session.get('user_id'))
    print(" Session ID:", session.get('session_id'))

    if 'user_id' in session:
        try:    
        # Start new chat session if not already in one
            if 'session_id' not in session:
                new_session = ChatSession(userid=session['user_id'])
                db.session.add(new_session)
                db.session.commit()
                session['session_id'] = new_session.id
                print(" New ChatSession created:", new_session.id)

            msg = Message(
            sessionid=session['session_id'],
            message=user_message,
            response=cleaned_response
            )
            db.session.add(msg)
            db.session.commit()
            print(" Message saved.")
        except Exception as e:
            print(" Error while saving message:", e)

    return jsonify({"response": html_response})

@app.route('/messages', methods=['GET'])
def get_messages():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']

    sessions = ChatSession.query.filter_by(userid=user_id).order_by(ChatSession.starttime).all()

    all_messages = []

    for chat_session in sessions:
        messages = Message.query.filter_by(sessionid=chat_session.id).order_by(Message.timestamp).all()

        for msg in messages:
            all_messages.append({
                "user": msg.message,
                "bot": msg.response,
                "timestamp": msg.timestamp.isoformat()
            })

    return jsonify(all_messages)


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))