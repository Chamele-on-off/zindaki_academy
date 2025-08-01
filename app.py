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
        return next((u for u in users if u['username'] == username), None)

    @staticmethod
    def save_user(username, email, password, role='student', is_active=True, phone=''):
        users = DB.get_users()
        if any(u['username'] == username for u in users):
            return False
        
        users.append({
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'is_active': is_active,
            'phone': phone,
            'created_at': datetime.now().isoformat(),
            'avatar': f'https://i.pravatar.cc/150?u={username}'
        })
        DB._save_db('users', users)
        return True

    @staticmethod
    def update_user(username, data):
        users = DB.get_users()
        for i, user in enumerate(users):
            if user['username'] == username:
                if 'email' in data:
                    users[i]['email'] = data['email']
                if 'phone' in data:
                    users[i]['phone'] = data['phone']
                if 'password' in data and data['password']:
                    users[i]['password'] = generate_password_hash(data['password'])
                if 'is_active' in data:
                    users[i]['is_active'] = data['is_active']
                if 'role' in data:
                    users[i]['role'] = data['role']
                if 'avatar' in data:
                    users[i]['avatar'] = data['avatar']
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
        return next((l for l in lessons if l['id'] == lesson_id), None)

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
        homeworks = DB._get_db('homeworks')
        # Автоматическое удаление заданий старше 2 недель
        now = datetime.now()
        homeworks = [hw for hw in homeworks if 
                    (now - datetime.fromisoformat(hw['created_at'])) < timedelta(weeks=2)]
        return homeworks

    @staticmethod
    def get_homework(homework_id):
        homeworks = DB.get_homeworks()
        return next((h for h in homeworks if h['id'] == homework_id), None)

    @staticmethod
    def save_homework(lesson_id, title, description, deadline, teacher, students=None, files=None, subject=None):
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
            'subject': subject,
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
    def delete_homework(homework_id):
        homeworks = DB.get_homeworks()
        homeworks = [hw for hw in homeworks if hw['id'] != homework_id]
        DB._save_db('homeworks', homeworks)
        return True

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

    # Конференции
    @staticmethod
    def get_conferences():
        return DB._get_db('conferences')

    @staticmethod
    def get_conference(room_name):
        conferences = DB.get_conferences()
        return next((c for c in conferences if c['room_name'] == room_name), None)

    @staticmethod
    def save_conference(room_name, host_username, is_active=True):
        conferences = DB.get_conferences()
        conference = next((c for c in conferences if c['room_name'] == room_name), None)
        
        if conference:
            conference['is_active'] = is_active
            conference['updated_at'] = datetime.now().isoformat()
        else:
            conference = {
                'room_name': room_name,
                'host': host_username,
                'participants': [],
                'is_active': is_active,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            conferences.append(conference)
        
        DB._save_db('conferences', conferences)
        return conference

    @staticmethod
    def add_participant(room_name, username):
        conferences = DB.get_conferences()
        conference = next((c for c in conferences if c['room_name'] == room_name), None)
        
        if conference and username not in conference['participants']:
            conference['participants'].append(username)
            conference['updated_at'] = datetime.now().isoformat()
            DB._save_db('conferences', conferences)
            return True
        return False

    @staticmethod
    def remove_participant(room_name, username):
        conferences = DB.get_conferences()
        conference = next((c for c in conferences if c['room_name'] == room_name), None)
        
        if conference and username in conference['participants']:
            conference['participants'].remove(username)
            conference['updated_at'] = datetime.now().isoformat()
            DB._save_db('conferences', conferences)
            return True
        return False

    @staticmethod
    def end_conference(room_name):
        conferences = DB.get_conferences()
        conference = next((c for c in conferences if c['room_name'] == room_name), None)
        
        if conference:
            conference['is_active'] = False
            conference['updated_at'] = datetime.now().isoformat()
            DB._save_db('conferences', conferences)
            return True
        return False

    @staticmethod
    def get_active_conference(host_username=None):
        conferences = DB.get_conferences()
        now = datetime.now().isoformat()
        
        if host_username:
            return [c for c in conferences 
                   if c['host'] == host_username 
                   and c['is_active'] 
                   and c['updated_at'] > (datetime.now() - timedelta(hours=1)).isoformat()]
        else:
            return [c for c in conferences 
                   if c['is_active'] 
                   and c['updated_at'] > (datetime.now() - timedelta(hours=1)).isoformat()]

# Инициализация базы данных
if not os.path.exists(f'{DB_FOLDER}/users.json'):
    initial_users = [
        {
            'username': 'admin',
            'email': 'admin@zindaki.academy',
            'password': generate_password_hash('admin123'),
            'role': 'teacher',
            'is_active': True,
            'phone': '+1234567890',
            'created_at': datetime.now().isoformat(),
            'avatar': 'https://i.pravatar.cc/150?u=admin'
        },
        {
            'username': 'student1',
            'email': 'student1@example.com',
            'password': generate_password_hash('student123'),
            'role': 'student',
            'is_active': True,
            'phone': '+9876543210',
            'created_name': datetime.now().isoformat(),
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
        }
    ]
    
    initial_homeworks = [
        {
            'id': 1,
            'lesson_id': 1,
            'title': 'Домашнее задание по английскому #1',
            'description': 'Выполнить упражнения 1-10 на странице 45 учебника. Подготовить рассказ о своем дне.',
            'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'teacher': 'admin',
            'students': ['student1'],
            'files': [],
            'subject': 'Английский язык',
            'created_at': datetime.now().isoformat(),
            'submissions': {}
        }
    ]
    
    initial_conferences = []
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
    DB._save_db('conferences', initial_conferences)
    DB._save_db('testimonials', initial_testimonials)

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
        data.get('is_active', True),
        data.get('phone', '')
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
            'phone': user.get('phone', ''),
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

@app.route('/api/users/<username>', methods=['GET'])
def api_get_user(username):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Проверяем, что пользователь запрашивает свой профиль или это учитель
    if session['user']['username'] != username and session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = DB.get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    safe_user = user.copy()
    safe_user.pop('password', None)
    
    return jsonify({'user': safe_user})

@app.route('/api/users/<username>', methods=['PUT'])
def api_update_user(username):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Проверяем, что пользователь обновляет свой профиль или это учитель
    if session['user']['username'] != username and session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    # Проверка пароля для любых изменений (кроме учителя)
    if session['user']['username'] == username:
        user = DB.get_user(username)
        if not check_password_hash(user['password'], data.get('current_password', '')):
            return jsonify({'error': 'Current password is incorrect'}), 400
    
    update_data = {}
    if 'email' in data:
        update_data['email'] = data['email']
    if 'phone' in data:
        update_data['phone'] = data['phone']
    if 'password' in data and data['password']:
        update_data['password'] = data['password']
    if 'is_active' in data and session['user']['role'] == 'teacher':
        update_data['is_active'] = data['is_active']
    if 'role' in data and session['user']['role'] == 'teacher':
        update_data['role'] = data['role']
    
    if DB.update_user(username, update_data):
        # Обновляем сессию, если пользователь обновляет свой профиль
        if session['user']['username'] == username:
            user = DB.get_user(username)
            session['user'] = {
                'username': user['username'],
                'email': user['email'],
                'phone': user.get('phone', ''),
                'role': user['role'],
                'avatar': user['avatar']
            }
        return jsonify({'success': True, 'user': session.get('user')})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/users/<username>/avatar', methods=['POST'])
def api_update_avatar(username):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Проверяем, что пользователь обновляет свой профиль или это учитель
    if session['user']['username'] != username and session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(f"{username}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        avatar_url = url_for('uploaded_file', filename=filename, _external=True)
        
        if DB.update_user(username, {'avatar': avatar_url}):
            # Обновляем сессию, если пользователь обновляет свой профиль
            if session['user']['username'] == username:
                session['user']['avatar'] = avatar_url
            
            return jsonify({'success': True, 'avatar': avatar_url})
    
    return jsonify({'error': 'Failed to update avatar'}), 500

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
        subject = request.form.get('subject')
        students = json.loads(request.form.get('students', '[]'))
        
        if not all([lesson_id, title, description, deadline, students, subject]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        homework = DB.save_homework(
            lesson_id=int(lesson_id),
            title=title,
            description=description,
            deadline=deadline,
            teacher=session['user']['username'],
            students=students,
            files=files,
            subject=subject
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

@app.route('/api/homework/<int:homework_id>', methods=['DELETE'])
def api_delete_homework(homework_id):
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    homework = DB.get_homework(homework_id)
    if not homework:
        return jsonify({'error': 'Homework not found'}), 404
    
    if homework['teacher'] != session['user']['username']:
        return jsonify({'error': 'Access denied'}), 403
    
    if DB.delete_homework(homework_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to delete homework'}), 500

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
        return redirect(url_for('dashboard'))
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

# Управление конференциями
@app.route('/api/conferences', methods=['POST'])
def api_conferences():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    required_fields = ['room_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conference = DB.save_conference(
        data['room_name'],
        session['user']['username'],
        data.get('is_active', True)
    )
    
    return jsonify({'success': True, 'conference': conference})

@app.route('/api/conferences/active', methods=['GET'])
def api_get_active_conferences():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    host_username = request.args.get('host')
    conferences = DB.get_active_conference(host_username)
    return jsonify({'conferences': conferences})

@app.route('/api/conferences/join', methods=['POST'])
def api_join_conference():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    required_fields = ['room_name', 'user_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Обновляем время последней активности конференции
    conference = DB.save_conference(
        data['room_name'],
        data.get('host', session['user']['username']),
        True
    )
    
    # Добавляем участника
    DB.add_participant(data['room_name'], data['user_name'])
    
    return jsonify({
        'success': True,
        'conference': conference,
        'join_url': f"https://conf.zindaki-edu.ru?room={data['room_name']}&user={data['user_name']}&name={data['user_name']}&autostart=1"
    })

@app.route('/api/conferences/<room_name>/participants', methods=['POST'])
def api_add_participant(room_name):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
    
    # Проверяем, что пользователь существует
    user = DB.get_user(data['username'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if DB.add_participant(room_name, data['username']):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to add participant'}), 500

@app.route('/api/conferences/<room_name>/participants/<username>', methods=['DELETE'])
def api_remove_participant(room_name, username):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Проверяем, что пользователь имеет права (учитель или сам участник)
    if session['user']['username'] != username and session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if DB.remove_participant(room_name, username):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to remove participant'}), 500

@app.route('/api/conferences/<room_name>/end', methods=['POST'])
def api_end_conference(room_name):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conference = DB.get_conference(room_name)
    if not conference:
        return jsonify({'error': 'Conference not found'}), 404
    
    # Проверяем, что пользователь - хост конференции или учитель
    if session['user']['username'] != conference['host'] and session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if DB.end_conference(room_name):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to end conference'}), 500

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