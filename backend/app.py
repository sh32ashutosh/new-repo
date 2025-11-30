import os
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import random
import string
import requests
from datetime import datetime

# --- CONFIGURATION ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sih-vlink-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vlink.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allow CORS for all domains
CORS(app, resources={r"/*": {"origins": "*"}})

# SocketIO
# FIXED: Changed async_mode to 'threading' to allow ssl_context='adhoc'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    roll_no = db.Column(db.String(20))

class Classroom(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    teacher_name = db.Column(db.String(100))
    code = db.Column(db.String(6), unique=True, nullable=False)
    status = db.Column(db.String(20), default='upcoming')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    class_id = db.Column(db.String(36), db.ForeignKey('classroom.id'))

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.String(36), db.ForeignKey('classroom.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    due_date = db.Column(db.DateTime)
    score = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=10)

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replies_count = db.Column(db.Integer, default=0)

class FileModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    size = db.Column(db.String(20))
    type = db.Column(db.String(20))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    offline = db.Column(db.Boolean, default=False)

# --- HELPER FUNCTIONS ---
def seed_database():
    if not User.query.first():
        print("🌱 Seeding Database with Default Users...")
        student = User(username="student", password="123", role="student", name="Student User", student_class="10th", roll_no="STU001")
        teacher = User(username="teacher", password="123", role="teacher", name="Dr. Ratnesh", designation="HOD Physics")
        db.session.add(student)
        db.session.add(teacher)
        db.session.commit()
        
        demo_class = Classroom(title="Physics - Motion", teacher_id=teacher.id, teacher_name=teacher.name, code="PHY101", status="live")
        db.session.add(demo_class)
        db.session.add(Assignment(title="Mathematics Basics", details="2 questions • 30 mins", status="pending"))
        db.session.add(Discussion(title="Doubt about Quadratic Eq", content="Can someone explain the formula?", author_name="Student A", replies_count=2))
        db.session.commit()
        print("✅ Database Seeded!")

# --- ROUTES ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username'), password=data.get('password')).first()
    if user:
        return jsonify({"success": True, "token": f"token-{user.id}", "user": {"id": user.id, "username": user.username, "role": user.role, "name": user.name}})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify({
        "dashboard": {
            "live": Classroom.query.filter_by(status='live').count(),
            "upcoming": Classroom.query.filter_by(status='upcoming').count(),
            "completed": Classroom.query.filter_by(status='completed').count(),
            "pending": Assignment.query.filter_by(status='pending').count()
        },
        "classes": [{"id": c.id, "title": c.title, "teacher": c.teacher_name, "status": c.status, "code": c.code, "participants": 0} for c in Classroom.query.all()],
        "assignments": [{"id": a.id, "title": a.title, "details": a.details, "status": a.status, "score": a.score, "total": a.total} for a in Assignment.query.all()],
        "files": [{"id": f.id, "name": f.name, "size": f.size, "type": f.type, "date": f.uploaded_at.strftime("%d/%m/%Y"), "offline": f.offline} for f in FileModel.query.all()],
        "discussions": [{"id": d.id, "title": d.title, "content": d.content, "author": d.author_name, "replies": d.replies_count} for d in Discussion.query.all()]
    })

@app.route('/api/classes/create', methods=['POST'])
def create_class():
    data = request.json
    teacher = User.query.filter_by(role='teacher').first()
    new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    new_class = Classroom(title=data.get('title'), teacher_id=teacher.id, teacher_name=teacher.name, code=new_code, status='live')
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"id": new_class.id, "title": new_class.title, "teacher": new_class.teacher_name, "code": new_class.code, "status": new_class.status})

@app.route('/api/classes/join', methods=['POST'])
def join_class():
    data = request.json
    found_class = Classroom.query.filter_by(code=data.get('code')).first()
    if found_class:
        return jsonify({"success": True, "classId": found_class.id})
    return jsonify({"success": False, "message": "Invalid Class Code"}), 404

@app.route('/api/stream-proxy')
def stream_proxy():
    video_url = request.args.get('url')
    if not video_url: return "Missing URL", 400
    req = requests.get(video_url, stream=True)
    return Response(stream_with_context(req.iter_content(chunk_size=4096)), headers={'Content-Type': req.headers.get('Content-Type')})

# --- SOCKET EVENTS ---
@socketio.on('connect')
def handle_connect():
    emit('me', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    emit('callEnded', broadcast=True)

@socketio.on('callUser')
def handle_call_user(data):
    emit('callUser', {'signalData': data['signalData'], 'from': data['from']}, broadcast=True, include_self=False)

@socketio.on('answerCall')
def handle_answer_call(data):
    emit('callAccepted', data['signal'], broadcast=True, include_self=False)

@socketio.on('draw_data')
def handle_draw_data(data):
    emit('draw_data', data, broadcast=True, include_self=False)

@socketio.on('stream-content')
def handle_stream_content(data):
    emit('stream-content', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    
    print("🚀  JAY SHREE RAM Vlink Backend Running SECURELY on https://0.0.0.0:5000")
    # UPDATED: ssl_context='adhoc' enables HTTPS on the backend
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')