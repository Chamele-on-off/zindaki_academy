import os
from flask import Flask, render_template, request, session, redirect, jsonify, send_from_directory, url_for
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import logging
from collections import defaultdict, deque
import uuid

# Инициализация приложения
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'your-very-secret-key-12345')

# Настройка SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Конфигурация приложения
UPLOAD_FOLDER = 'uploads'
DB_FOLDER = 'data'
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище для комнат видеоконференций: {room_name: {user_id: user_data}}
video_rooms = defaultdict(dict)

class DB:
    # ... (все существующие методы DB остаются без изменений)
    # Добавляем только новые методы для видеоконференций если нужно

# Инициализация базы данных (остается без изменений)
if not os.path.exists(f'{DB_FOLDER}/users.json'):
    # ... (существующий код инициализации)

# ===== ВСТАВЛЯЕМ КОД ВИДЕОКОНФЕРЕНЦИЙ =====

@app.route('/video-conference')
def video_conference():
    if 'user' not in session:
        return redirect('/#login')
    
    room_name = request.args.get('room', session['user']['username'])
    user_name = session['user']['username']
    
    return render_template('video_conference.html', 
                         room_name=room_name, 
                         user_name=user_name,
                         user=session['user'])

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    # Удаляем пользователя из всех комнат при отключении
    for room_name, users in list(video_rooms.items()):
        for user_id, user_data in list(users.items()):
            if user_data.get('socket_id') == request.sid:
                leave_room_handler({'room_name': room_name, 'user_id': user_id})
                break

@socketio.on('join_room')
def join_room_handler(data):
    try:
        room_name = data.get('room_name')
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        
        if not all([room_name, user_id, user_name]):
            emit('error', {'message': 'Missing required fields'})
            return
        
        # Сохраняем информацию о пользователе
        video_rooms[room_name][user_id] = {
            'socket_id': request.sid,
            'user_name': user_name,
            'user_id': user_id
        }
        
        join_room(room_name)
        print(f'User {user_name} ({user_id}) joined room {room_name}')
        
        # Отправляем текущему пользователю список всех участников комнаты
        participants = {
            uid: {'user_name': data['user_name'], 'user_id': uid}
            for uid, data in video_rooms[room_name].items()
            if uid != user_id
        }
        
        emit('room_joined', {
            'room_name': room_name,
            'user_id': user_id,
            'participants': participants
        }, room=request.sid)
        
        # Уведомляем других участников о новом пользователе
        emit('user_joined', {
            'user_id': user_id,
            'user_name': user_name,
            'socket_id': request.sid
        }, room=room_name, include_self=False)
        
    except Exception as e:
        print(f'Error in join_room: {e}')
        emit('error', {'message': str(e)})

@socketio.on('leave_room')
def leave_room_handler(data):
    try:
        room_name = data.get('room_name')
        user_id = data.get('user_id')
        
        if room_name in video_rooms and user_id in video_rooms[room_name]:
            # Удаляем пользователя из комнаты
            del video_rooms[room_name][user_id]
            leave_room(room_name)
            
            print(f'User {user_id} left room {room_name}')
            
            # Если комната пуста, удаляем ее
            if not video_rooms[room_name]:
                del video_rooms[room_name]
                print(f'Room {room_name} deleted (empty)')
            
            # Уведомляем других участников
            emit('user_left', {
                'user_id': user_id
            }, room=room_name)
            
    except Exception as e:
        print(f'Error in leave_room: {e}')

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    try:
        offer = data.get('offer')
        target_user_id = data.get('target_user_id')
        caller_user_id = data.get('caller_user_id')
        room_name = data.get('room_name')
        
        if not all([offer, target_user_id, caller_user_id, room_name]):
            emit('error', {'message': 'Missing required fields for offer'})
            return
        
        # Находим socket_id целевого пользователя
        target_user = video_rooms[room_name].get(target_user_id)
        if not target_user:
            emit('error', {'message': f'Target user {target_user_id} not found'})
            return
        
        # Пересылаем offer целевому пользователю
        emit('webrtc_offer', {
            'offer': offer,
            'caller_user_id': caller_user_id,
            'target_user_id': target_user_id
        }, room=target_user['socket_id'])
        
        print(f'Forwarded WebRTC offer from {caller_user_id} to {target_user_id}')
        
    except Exception as e:
        print(f'Error handling WebRTC offer: {e}')
        emit('error', {'message': str(e)})

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    try:
        answer = data.get('answer')
        target_user_id = data.get('target_user_id')
        answerer_user_id = data.get('answerer_user_id')
        room_name = data.get('room_name')
        
        if not all([answer, target_user_id, answerer_user_id, room_name]):
            emit('error', {'message': 'Missing required fields for answer'})
            return
        
        # Находим socket_id целевого пользователя
        target_user = video_rooms[room_name].get(target_user_id)
        if not target_user:
            emit('error', {'message': f'Target user {target_user_id} not found'})
            return
        
        # Пересылаем answer целевому пользователю
        emit('webrtc_answer', {
            'answer': answer,
            'answerer_user_id': answerer_user_id,
            'target_user_id': target_user_id
        }, room=target_user['socket_id'])
        
        print(f'Forwarded WebRTC answer from {answerer_user_id} to {target_user_id}')
        
    except Exception as e:
        print(f'Error handling WebRTC answer: {e}')
        emit('error', {'message': str(e)})

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    try:
        candidate = data.get('candidate')
        target_user_id = data.get('target_user_id')
        sender_user_id = data.get('sender_user_id')
        room_name = data.get('room_name')
        
        if not all([candidate, target_user_id, sender_user_id, room_name]):
            emit('error', {'message': 'Missing required fields for ICE candidate'})
            return
        
        # Находим socket_id целевого пользователя
        target_user = video_rooms[room_name].get(target_user_id)
        if not target_user:
            emit('error', {'message': f'Target user {target_user_id} not found'})
            return
        
        # Пересылаем ICE candidate целевому пользователю
        emit('ice_candidate', {
            'candidate': candidate,
            'sender_user_id': sender_user_id,
            'target_user_id': target_user_id
        }, room=target_user['socket_id'])
        
        print(f'Forwarded ICE candidate from {sender_user_id} to {target_user_id}')
        
    except Exception as e:
        print(f'Error handling ICE candidate: {e}')
        emit('error', {'message': str(e)})

@socketio.on('screen_share_status')
def handle_screen_share_status(data):
    try:
        is_sharing = data.get('is_sharing')
        user_id = data.get('user_id')
        room_name = data.get('room_name')
        
        if not all([is_sharing is not None, user_id, room_name]):
            emit('error', {'message': 'Missing required fields for screen share status'})
            return
        
        # Обновляем статус демонстрации экрана
        if room_name in video_rooms and user_id in video_rooms[room_name]:
            video_rooms[room_name][user_id]['is_screen_sharing'] = is_sharing
            
            # Уведомляем других участников
            emit('screen_share_status', {
                'user_id': user_id,
                'is_sharing': is_sharing
            }, room=room_name, include_self=False)
            
            print(f'User {user_id} screen share status: {is_sharing}')
            
    except Exception as e:
        print(f'Error handling screen share status: {e}')
        emit('error', {'message': str(e)})

@app.route('/api/video/health')
def video_health_check():
    return jsonify({
        'status': 'ok', 
        'rooms_count': len(video_rooms),
        'total_users': sum(len(users) for users in video_rooms.values())
    })

# ===== КОНЕЦ КОДА ВИДЕОКОНФЕРЕНЦИЙ =====

# Все существующие маршруты онлайн-школы остаются без изменений
@app.route('/')
@app.route('/about')
@app.route('/teachers')
@app.route('/programs')
@app.route('/testimonials')
@app.route('/contact')
def home():
    scroll_to = request.path[1:] if request.path != '/' else None
    return render_template('index.html', 
                         user=session.get('user'),
                         teachers=DB.get_users(role='teacher')[:3],
                         testimonials=DB.get_testimonials(),
                         scroll_to=scroll_to)

# Все существующие API endpoints остаются без изменений
@app.route('/api/register', methods=['POST'])
def api_register():
    # ... существующий код

@app.route('/api/login', methods=['POST'])
def api_login():
    # ... существующий код

# ... все остальные существующие маршруты

# Обновляем dashboard для интеграции видеоконференции
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/#login')
    
    if session['user']['role'] == 'teacher':
        lessons = DB.get_lessons(teacher=session['user']['username'])
        homeworks = DB.get_teacher_homeworks(session['user']['username'])
        students = DB.get_users(role='student')
    else:
        lessons = [l for l in DB.get_lessons() if session['user']['username'] in l.get('students', [])]
        homeworks = DB.get_student_homeworks(session['user']['username'])
        students = []
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         lessons=lessons,
                         homeworks=homeworks,
                         students=students,
                         timedelta=timedelta,
                         is_teacher=session['user']['role'] == 'teacher')

if __name__ == '__main__':  
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)