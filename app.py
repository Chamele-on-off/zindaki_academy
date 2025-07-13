from flask import Flask, render_template, request, session, redirect, jsonify, send_from_directory, Response
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import time
import logging
from collections import defaultdict, deque
import uuid

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Настройка SocketIO (оставляем для других функций, но не для видеоконференций)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация Jitsi
JITSI_DOMAIN = 'jitsi.zindaki-edu.ru'  # Замените на ваш домен Jitsi
JITSI_OPTIONS = {
    'roomName': 'ZindakiRoom',
    'width': '100%',
    'height': 500,
    'parentNode': None,
    'configOverwrite': {
        'startWithAudioMuted': False,
        'startWithVideoMuted': False,
        'enableWelcomePage': False,
        'enableClosePage': False
    },
    'interfaceConfigOverwrite': {
        'DISABLE_JOIN_LEAVE_NOTIFICATIONS': True,
        'SHOW_JITSI_WATERMARK': False,
        'SHOW_WATERMARK_FOR_GUESTS': False
    }
}

# Конфигурация приложения
UPLOAD_FOLDER = 'uploads'
DB_FOLDER = 'data'
INVITES_FOLDER = 'invites'
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INVITES_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

class DB:
    @staticmethod
    def _get_db(file):
        try:
            with open(f'{DB_FOLDER}/{file}.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def _save_db(file, data):
        with open(f'{DB_FOLDER}/{file}.json', 'w') as f:
            json.dump(data, f, indent=2)

    # Пользователи
    @staticmethod
    def get_users(role=None):
        users = DB._get_db('users')
        if role:
            return [u for u in users if u['role'] == role]
        return users

    @staticmethod
    def get_user(username):
        users = DB.get_users()
        return next((u for u in users if u['username'] == username), None

    @staticmethod
    def save_user(username, email, password, role='student', is_active=True):
        users = DB.get_users()
        if any(u['username'] == username for u in users):
            return False
        
        users.append({
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'is_active': is_active,
            'created_at': datetime.now().isoformat(),
            'avatar': f'https://i.pravatar.cc/150?u={username}'
        })
        DB._save_db('users', users)
        return True

    @staticmethod
    def update_user_status(username, is_active):
        users = DB.get_users()
        for user in users:
            if user['username'] == username:
                user['is_active'] = is_active
                DB._save_db('users', users)
                return True
        return False

    @staticmethod
    def delete_user(username):
        users = DB.get_users()
        users = [u for u in users if u['username'] != username]
        DB._save_db('users', users)
        return True

    # Уроки
    @staticmethod
    def get_lessons(teacher=None):
        lessons = DB._get_db('lessons')
        if teacher:
            return [l for l in lessons if l['teacher'] == teacher]
        return lessons

    @staticmethod
    def get_lesson(lesson_id):
        lessons = DB.get_lessons()
        return next((l for l in lessons if l['id'] == lesson_id), None

    @staticmethod
    def save_lesson(title, description, teacher, schedule, duration=60, subject=None, students=None):
        if students is None:
            students = []
        lessons = DB.get_lessons()
        lesson_id = max([l['id'] for l in lessons], default=0) + 1
        
        lesson_data = {
            'id': lesson_id,
            'title': title,
            'description': description,
            'teacher': teacher,
            'schedule': schedule,
            'duration': duration,
            'subject': subject,
            'students': students,
            'created_at': datetime.now().isoformat()
        }
        
        lessons.append(lesson_data)
        DB._save_db('lessons', lessons)
        return lesson_data

    @staticmethod
    def delete_lesson(lesson_id):
        lessons = DB.get_lessons()
        lessons = [l for l in lessons if l['id'] != lesson_id]
        DB._save_db('lessons', lessons)
        return True

    # Домашние задания
    @staticmethod
    def get_homeworks():
        return DB._get_db('homeworks')

    @staticmethod
    def get_homework(homework_id):
        homeworks = DB.get_homeworks()
        return next((h for h in homeworks if h['id'] == homework_id), None

    @staticmethod
    def save_homework(lesson_id, title, description, deadline, teacher, students=None, files=None):
        if students is None:
            students = []
        if files is None:
            files = []
        homeworks = DB.get_homeworks()
        homework_id = max([h['id'] for h in homeworks], default=0) + 1
        
        homework = {
            'id': homework_id,
            'lesson_id': lesson_id,
            'title': title,
            'description': description,
            'deadline': deadline,
            'teacher': teacher,
            'students': students,
            'files': files,
            'created_at': datetime.now().isoformat(),
            'submissions': {}
        }
        
        homeworks.append(homework)
        DB._save_db('homeworks', homeworks)
        return homework

    @staticmethod
    def submit_homework(homework_id, student_username, comment, files=None):
        if files is None:
            files = []
        homeworks = DB.get_homeworks()
        for hw in homeworks:
            if hw['id'] == homework_id and student_username in hw['students']:
                hw['submissions'][student_username] = {
                    'comment': comment,
                    'files': files,
                    'submitted_at': datetime.now().isoformat(),
                    'status': 'submitted'
                }
                DB._save_db('homeworks', homeworks)
                return True
        return False

    @staticmethod
    def get_student_homeworks(student_username):
        homeworks = DB.get_homeworks()
        return [hw for hw in homeworks if student_username in hw['students']]

    @staticmethod
    def get_teacher_homeworks(teacher_username):
        homeworks = DB.get_homeworks()
        return [hw for hw in homeworks if hw['teacher'] == teacher_username]

    # Отзывы
    @staticmethod
    def get_testimonials():
        return DB._get_db('testimonials')

    # Приглашения
    @staticmethod
    def get_invites():
        try:
            with open(f'{INVITES_FOLDER}/invites.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_invite(teacher_username, student_username, room_name, status='pending'):
        invites = DB.get_invites()
        invite_id = max([i.get('id', 0) for i in invites], default=0) + 1
        
        invite = {
            'id': invite_id,
            'teacher': teacher_username,
            'student': student_username,
            'room_name': room_name,
            'status': status,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        invites.append(invite)
        with open(f'{INVITES_FOLDER}/invites.json', 'w') as f:
            json.dump(invites, f, indent=2)
        return invite

    @staticmethod
    def update_invite_status(invite_id, status):
        invites = DB.get_invites()
        for invite in invites:
            if invite['id'] == invite_id:
                invite['status'] = status
                invite['updated_at'] = datetime.now().isoformat()
                with open(f'{INVITES_FOLDER}/invites.json', 'w') as f:
                    json.dump(invites, f, indent=2)
                return True
        return False

    @staticmethod
    def get_user_invites(username):
        invites = DB.get_invites()
        return [i for i in invites if i['student'] == username and i['status'] == 'pending']

    @staticmethod
    def get_teacher_invites(username):
        invites = DB.get_invites()
        return [i for i in invites if i['teacher'] == username]

# Инициализация базы данных
if not os.path.exists(f'{DB_FOLDER}/users.json'):
    initial_users = [
        {
            'username': 'admin',
            'email': 'admin@zindaki.academy',
            'password': generate_password_hash('admin123'),
            'role': 'teacher',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'avatar': 'https://i.pravatar.cc/150?u=admin'
        },
        {
            'username': 'student1',
            'email': 'student1@example.com',
            'password': generate_password_hash('student123'),
            'role': 'student',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'avatar': 'https://i.pravatar.cc/150?u=student1'
        }
    ]
    
    initial_lessons = [
        {
            'id': 1,
            'title': 'Вводный урок по английскому',
            'description': 'Основы грамматики и произношения',
            'teacher': 'admin',
            'schedule': 'Понедельник 13:00-14:00',
            'duration': 60,
            'subject': 'Английский язык',
            'students': ['student1'],
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 2,
            'title': 'Обществознание для начинающих',
            'description': 'Основные понятия и термины',
            'teacher': 'admin',
            'schedule': 'Четверг 14:00-15:30',
            'duration': 90,
            'subject': 'Обществознание',
            'students': ['student1'],
            'created_at': datetime.now().isoformat()
        }
    ]
    
    initial_homeworks = []
    
    initial_testimonials = [
        {
            "id": 1,
            "text": "Мой сын занимается с Галиной Петровной уже год. Несмотря на диагноз (аутизм), он начал говорить целыми предложениями!",
            "author": "Мария С.",
            "role": "Мама ученика",
            "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
        },
        {
            "id": 2,
            "text": "Спасибо Zindaki Academy за подготовку к ЕГЭ! Сдала английский на 94 балла и поступила в МГЛУ.",
            "author": "Анна К.",
            "role": "Выпускница",
            "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
        }
    ]
    
    DB._save_db('users', initial_users)
    DB._save_db('lessons', initial_lessons)
    DB._save_db('homeworks', initial_homeworks)
    DB._save_db('testimonials', initial_testimonials)

if not os.path.exists(f'{INVITES_FOLDER}/invites.json'):
    with open(f'{INVITES_FOLDER}/invites.json', 'w') as f:
        json.dump([], f)

# Главная страница и все SPA-роуты
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

# API Endpoints
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing fields'}), 400
    
    if DB.save_user(
        data['username'],
        data['email'],
        data['password'],
        data.get('role', 'student'),
        data.get('is_active', True)
    ):
        return jsonify({'success': True})
    return jsonify({'error': 'Username already exists'}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = DB.get_user(data['username'])
    
    if user and check_password_hash(user['password'], data['password']):
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
            
        session['user'] = {
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'avatar': user['avatar']
        }
        return jsonify({'success': True, 'user': session['user']})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout')
def api_logout():
    session.pop('user', None)
    return jsonify({'success': True})

# Управление пользователями
@app.route('/api/users', methods=['GET'])
def api_get_users():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    role = request.args.get('role')
    users = DB.get_users(role=role)
    
    safe_users = []
    for user in users:
        safe_user = user.copy()
        safe_user.pop('password', None)
        safe_users.append(safe_user)
    
    return jsonify({'users': safe_users})

@app.route('/api/users/<username>/status', methods=['PUT'])
def api_update_user_status(username):
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if DB.update_user_status(username, data.get('is_active', True)):
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/users/<username>', methods=['DELETE'])
def api_delete_user(username):
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if DB.delete_user(username):
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

# Управление уроками
@app.route('/api/lessons', methods=['GET', 'POST'])
def api_lessons():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        if session['user']['role'] != 'teacher':
            return jsonify({'error': 'Only teachers can create lessons'}), 403
            
        data = request.json
        required_fields = ['title', 'schedule', 'duration']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        lesson = DB.save_lesson(
            data['title'],
            data.get('description', ''),
            session['user']['username'],
            data['schedule'],
            data['duration'],
            data.get('subject'),
            data.get('students', [])
        )
        
        return jsonify({'success': True, 'lesson': lesson})
    
    if session['user']['role'] == 'teacher':
        lessons = DB.get_lessons(teacher=session['user']['username'])
    else:
        lessons = [l for l in DB.get_lessons() if session['user']['username'] in l.get('students', [])]
    
    return jsonify({'lessons': lessons})

@app.route('/api/lessons/<int:lesson_id>', methods=['DELETE'])
def api_delete_lesson(lesson_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    lesson = DB.get_lesson(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    if session['user']['role'] != 'teacher' or lesson['teacher'] != session['user']['username']:
        return jsonify({'error': 'Access denied'}), 403
    
    if DB.delete_lesson(lesson_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to delete lesson'}), 500

@app.route('/api/lesson/<int:lesson_id>/join')
def api_join_lesson(lesson_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    lesson = DB.get_lesson(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    if session['user']['role'] != 'teacher' and session['user']['username'] not in lesson.get('students', []):
        return jsonify({'error': 'Access denied'}), 403
    
    if session['user']['role'] == 'teacher':
        room_name = f"ZindakiRoom_{session['user']['username']}"
    else:
        room_name = f"ZindakiRoom_{lesson['teacher']}"
    
    return jsonify({
        'success': True,
        'conference_url': f'/conference/{room_name}',
        'room_name': room_name,
        'jitsi_domain': JITSI_DOMAIN,
        'jitsi_options': JITSI_OPTIONS,
        'lesson': lesson
    })

# API для конференций
@app.route('/api/conference/invite', methods=['POST'])
def send_conference_invite():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session['user']['role'] != 'teacher':
        return jsonify({'error': 'Only teacher can send invites'}), 403
    
    data = request.json
    student_username = data.get('student_username')
    room_name = data.get('room_name')
    
    if not student_username or not room_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    student = DB.get_user(student_username)
    if not student or student['role'] != 'student':
        return jsonify({'error': 'Student not found'}), 404
    
    invite = DB.save_invite(
        teacher_username=session['user']['username'],
        student_username=student_username,
        room_name=room_name
    )
    
    logger.info(f"Invite sent to {student_username} for room {room_name}")
    
    return jsonify({'success': True, 'invite': invite})

@app.route('/api/conference/invites', methods=['GET'])
def get_user_invites():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session['user']['role'] == 'student':
        invites = DB.get_user_invites(session['user']['username'])
    else:
        invites = DB.get_teacher_invites(session['user']['username'])
    
    return jsonify({'success': True, 'invites': invites})

@app.route('/api/conference/invite/<int:invite_id>/respond', methods=['POST'])
def respond_to_invite(invite_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session['user']['role'] != 'student':
        return jsonify({'error': 'Only student can respond to invites'}), 403
    
    data = request.json
    action = data.get('action')
    
    if action not in ['accept', 'decline']:
        return jsonify({'error': 'Invalid action'}), 400
    
    status = 'accepted' if action == 'accept' else 'declined'
    if DB.update_invite_status(invite_id, status):
        if action == 'accept':
            invites = DB.get_invites()
            invite = next((i for i in invites if i['id'] == invite_id), None)
            if invite:
                logger.info(f"Invite {invite_id} accepted by {session['user']['username']}")
                return jsonify({
                    'success': True,
                    'conference_url': f'/conference/{invite["room_name"]}',
                    'room_name': invite["room_name"],
                    'jitsi_domain': JITSI_DOMAIN,
                    'jitsi_options': JITSI_OPTIONS
                })
        logger.info(f"Invite {invite_id} {status} by {session['user']['username']}")
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invite not found'}), 404

# Видеоконференции
@app.route('/conference/<room_name>')
def conference(room_name):
    if 'user' not in session:
        return redirect('/#login')
    
    if session['user']['role'] == 'teacher':
        if not room_name.endswith(session['user']['username']):
            return "Доступ запрещен", 403
    else:
        teacher_username = room_name.replace('ZindakiRoom_', '')
        lessons = DB.get_lessons()
        has_access = any(
            session['user']['username'] in lesson.get('students', []) and 
            lesson['teacher'] == teacher_username 
            for lesson in lessons
        )
        
        if not has_access:
            invites = DB.get_user_invites(session['user']['username'])
            has_invite = any(invite['room_name'] == room_name for invite in invites)
            
            if not has_invite:
                return "Доступ запрещен", 403
    
    return render_template('dashboard.html', 
                         room_name=room_name,
                         user=session['user'],
                         is_teacher=session['user']['role'] == 'teacher',
                         jitsi_domain=JITSI_DOMAIN,
                         jitsi_options=JITSI_OPTIONS)

# Домашние задания
@app.route('/api/homework', methods=['GET', 'POST'])
def api_homework():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        if session['user']['role'] != 'teacher':
            return jsonify({'error': 'Only teachers can assign homework'}), 403
        
        files = []
        if 'files' in request.files:
            for file in request.files.getlist('files'):
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    files.append({
                        'name': filename,
                        'path': filepath,
                        'size': os.path.getsize(filepath)
                    })
        
        lesson_id = request.form.get('lesson_id')
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        students = json.loads(request.form.get('students', '[]'))
        
        if not all([lesson_id, title, description, deadline, students]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        homework = DB.save_homework(
            lesson_id=int(lesson_id),
            title=title,
            description=description,
            deadline=deadline,
            teacher=session['user']['username'],
            students=students,
            files=files
        )
        
        return jsonify({'success': True, 'homework': homework})
    
    if session['user']['role'] == 'teacher':
        homeworks = DB.get_teacher_homeworks(session['user']['username'])
    else:
        homeworks = DB.get_student_homeworks(session['user']['username'])
    
    return jsonify({'homeworks': homeworks})

@app.route('/api/homework/<int:homework_id>', methods=['GET'])
def api_get_homework(homework_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    homework = DB.get_homework(homework_id)
    if not homework:
        return jsonify({'error': 'Homework not found'}), 404
    
    if session['user']['role'] == 'student' and session['user']['username'] not in homework['students']:
        return jsonify({'error': 'Access denied'}), 403
    if session['user']['role'] == 'teacher' and homework['teacher'] != session['user']['username']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'homework': homework})

@app.route('/api/homework/<int:homework_id>/submit', methods=['POST'])
def api_submit_homework(homework_id):
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    student_username = session['user']['username']
    comment = request.form.get('comment', '')
    
    files = []
    if 'files' in request.files:
        for file in request.files.getlist('files'):
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                files.append({
                    'name': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath)
                })
    
    if DB.submit_homework(homework_id, student_username, comment, files):
        return jsonify({'success': True})
    return jsonify({'error': 'Homework not found or access denied'}), 404

# Загрузка файлов
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Личный кабинет
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/#login')
    
    if session['user']['role'] == 'teacher':
        lessons = DB.get_lessons(teacher=session['user']['username'])
        homeworks = DB.get_teacher_homeworks(session['user']['username'])
    else:
        lessons = [l for l in DB.get_lessons() if session['user']['username'] in l.get('students', [])]
        homeworks = DB.get_student_homeworks(session['user']['username'])
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         lessons=lessons,
                         homeworks=homeworks,
                         is_teacher=session['user']['role'] == 'teacher',
                         jitsi_domain=JITSI_DOMAIN,
                         jitsi_options=JITSI_OPTIONS)

# Обработка контактной формы
@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        data = request.json
        return jsonify({'success': True, 'message': 'Ваше сообщение отправлено!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__': 
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)