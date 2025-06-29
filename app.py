from flask import Flask, render_template, request, session, redirect, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Конфигурация
UPLOAD_FOLDER = 'uploads'
DB_FOLDER = 'data'
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Мини-модели для работы с JSON
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
        return next((l for l in lessons if l['id'] == lesson_id), None)

    @staticmethod
    def save_lesson(title, description, teacher, schedule, duration=60, program_type='languages', students=[], recurrence=None):
        lessons = DB.get_lessons()
        lesson_id = max([l['id'] for l in lessons], default=0) + 1
        
        lesson_data = {
            'id': lesson_id,
            'title': title,
            'description': description,
            'teacher': teacher,
            'schedule': schedule,
            'duration': duration,
            'program_type': program_type,
            'students': students,
            'created_at': datetime.now().isoformat()
        }
        
        if recurrence:
            lesson_data['recurrence'] = recurrence
            lesson_data['recurrence_id'] = f"rec_{lesson_id}_{datetime.now().timestamp()}"
        
        lessons.append(lesson_data)
        DB._save_db('lessons', lessons)
        
        # Если есть повторения - создаем дополнительные занятия
        if recurrence and recurrence.get('type') != 'none':
            created_lessons = [lesson_data]
            start_date = datetime.fromisoformat(schedule)
            weekdays = recurrence.get('weekdays', [])
            end_type = recurrence.get('end_type')
            end_value = recurrence.get('end_value')
            
            if recurrence['type'] == 'weekly':
                interval = 1
            elif recurrence['type'] == 'biweekly':
                interval = 2
            else:
                interval = 1
            
            current_date = start_date
            created_count = 1
            
            while True:
                # Проверяем условия окончания
                if end_type == 'count' and created_count >= end_value:
                    break
                if end_type == 'date' and current_date > datetime.fromisoformat(end_value):
                    break
                
                # Добавляем неделю/две недели
                current_date += timedelta(weeks=interval)
                
                # Для еженедельных занятий проверяем дни недели
                if weekdays:
                    # Находим следующий подходящий день недели
                    while str(current_date.weekday()) not in weekdays:
                        current_date += timedelta(days=1)
                
                # Проверяем не превысили ли максимальное количество занятий
                if end_type == 'count' and created_count >= end_value:
                    break
                
                # Создаем копию урока с новой датой
                new_lesson = lesson_data.copy()
                new_lesson['id'] = max([l['id'] for l in lessons], default=0) + 1
                new_lesson['schedule'] = current_date.isoformat()
                new_lesson['recurrence_id'] = lesson_data['recurrence_id']
                
                lessons.append(new_lesson)
                created_lessons.append(new_lesson)
                created_count += 1
            
            DB._save_db('lessons', lessons)
            return created_lessons
        
        return [lesson_data]

    @staticmethod
    def delete_recurring_lessons(recurrence_id):
        lessons = DB.get_lessons()
        lessons = [l for l in lessons if l.get('recurrence_id') != recurrence_id]
        DB._save_db('lessons', lessons)
        return True

    @staticmethod
    def get_lessons_by_recurrence(recurrence_id):
        lessons = DB.get_lessons()
        return [l for l in lessons if l.get('recurrence_id') == recurrence_id]

    # Домашние задания
    @staticmethod
    def get_homeworks():
        return DB._get_db('homeworks')

    @staticmethod
    def get_homework(homework_id):
        homeworks = DB.get_homeworks()
        return next((h for h in homeworks if h['id'] == homework_id), None)

    @staticmethod
    def save_homework(lesson_id, title, description, deadline, teacher, students, files=[]):
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
    def submit_homework(homework_id, student_username, comment, files=[]):
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

# Инициализация базы данных при первом запуске
if not os.path.exists(f'{DB_FOLDER}/users.json'):
    # Создаем тестовых пользователей
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
            'schedule': (datetime.now() + timedelta(days=1)).isoformat(),
            'duration': 60,
            'program_type': 'languages',
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
    
    # Не возвращаем хеши паролей
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
        required_fields = ['title', 'schedule']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Обработка повторяющихся занятий
        recurrence = None
        if data.get('recurrence') and data['recurrence'].get('type') != 'none':
            recurrence = {
                'type': data['recurrence']['type'],
                'weekdays': data['recurrence'].get('weekdays', []),
                'end_type': data['recurrence'].get('end_type'),
                'end_value': data['recurrence'].get('end_value')
            }
            
            # Преобразуем дату окончания в ISO формат, если она есть
            if recurrence['end_type'] == 'date' and recurrence['end_value']:
                try:
                    recurrence['end_value'] = datetime.strptime(recurrence['end_value'], '%Y-%m-%d').isoformat()
                except:
                    return jsonify({'error': 'Invalid end date format'}), 400
        
        # Создаем урок(и)
        result = DB.save_lesson(
            data['title'],
            data.get('description', ''),
            session['user']['username'],
            data['schedule'],
            data.get('duration', 60),
            data.get('program_type', 'languages'),
            data.get('students', []),
            recurrence
        )
        
        if isinstance(result, list):
            return jsonify({'success': True, 'lesson_ids': [l['id'] for l in result]})
        else:
            return jsonify({'success': True, 'lesson_id': result['id']})
    
    # GET запрос
    if session['user']['role'] == 'teacher':
        lessons = DB.get_lessons(teacher=session['user']['username'])
    else:
        lessons = [l for l in DB.get_lessons() if session['user']['username'] in l.get('students', [])]
    
    # Форматируем дату для удобного отображения
    formatted_lessons = []
    for lesson in lessons:
        formatted_lesson = lesson.copy()
        try:
            lesson_date = datetime.fromisoformat(lesson['schedule'])
            formatted_lesson['schedule'] = lesson_date.isoformat()
            formatted_lesson['formatted_schedule'] = lesson_date.strftime('%d.%m.%Y %H:%M')
        except:
            formatted_lesson['formatted_schedule'] = lesson['schedule']
        
        formatted_lessons.append(formatted_lesson)
    
    return jsonify({'lessons': formatted_lessons})

@app.route('/api/lessons/<int:lesson_id>', methods=['DELETE'])
def api_delete_lesson(lesson_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    lesson = DB.get_lesson(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    if session['user']['role'] != 'teacher' or lesson['teacher'] != session['user']['username']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Если это повторяющееся занятие - удаляем всю серию
    if lesson.get('recurrence_id'):
        if DB.delete_recurring_lessons(lesson['recurrence_id']):
            return jsonify({'success': True})
    else:
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
    
    # Проверяем, имеет ли пользователь доступ к уроку
    if session['user']['role'] != 'teacher' and session['user']['username'] not in lesson.get('students', []):
        return jsonify({'error': 'Access denied'}), 403
    
    # Для учителя - фиксированная комната по имени пользователя
    if session['user']['role'] == 'teacher':
        room_name = f"ZindakiRoom_{session['user']['username']}"
    else:
        # Для ученика - комната учителя
        room_name = f"ZindakiRoom_{lesson['teacher']}"
    
    # Добавляем ученика к уроку, если его там еще нет
    if session['user']['role'] == 'student' and session['user']['username'] not in lesson.get('students', []):
        DB.add_student_to_lesson(lesson_id, session['user']['username'])
    
    return jsonify({
        'success': True,
        'conference_url': f'/conference/{room_name}',
        'room_name': room_name,
        'lesson': lesson
    })

# Видеоконференции
@app.route('/conference/<room_name>')
def conference(room_name):
    if 'user' not in session:
        return redirect('/#login')
    
    # Проверяем, имеет ли пользователь доступ к этой комнате
    if session['user']['role'] == 'teacher':
        if not room_name.endswith(session['user']['username']):
            return "Доступ запрещен", 403
    else:
        # Для студентов проверяем, есть ли у них уроки с этим учителем
        teacher_username = room_name.replace('ZindakiRoom_', '')
        lessons = DB.get_lessons()
        has_access = any(
            session['user']['username'] in lesson.get('students', []) and 
            lesson['teacher'] == teacher_username 
            for lesson in lessons
        )
        
        if not has_access:
            return "Доступ запрещен", 403
    
    return render_template('conference.html', 
                         room_name=room_name,
                         user=session['user'],
                         is_teacher=session['user']['role'] == 'teacher')

# Домашние задания
@app.route('/api/homework', methods=['GET', 'POST'])
def api_homework():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        if session['user']['role'] != 'teacher':
            return jsonify({'error': 'Only teachers can assign homework'}), 403
        
        # Обработка загруженных файлов
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
        
        # Получаем данные из формы
        lesson_id = request.form.get('lesson_id')
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        students = json.loads(request.form.get('students', '[]'))
        
        if not all([lesson_id, title, description, deadline, students]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Создаем домашнее задание
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
    
    # GET запрос
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
    
    # Проверяем доступ
    if session['user']['role'] == 'student' and session['user']['username'] not in homework['students']:
        return jsonify({'error': 'Access denied'}), 403
    if session['user']['role'] == 'teacher' and homework['teacher'] != session['user']['username']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'homework': homework})

@app.route('/api/homework/<int:homework_id>/submit', methods=['POST'])
def api_submit_homework(homework_id):
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    homework = DB.get_homework(homework_id)
    if not homework or session['user']['username'] not in homework['students']:
        return jsonify({'error': 'Homework not found or access denied'}), 404
    
    # Обработка загруженных файлов
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
    
    comment = request.form.get('comment', '')
    
    if DB.submit_homework(homework_id, session['user']['username'], comment, files):
        return jsonify({'success': True})
    
    return jsonify({'error': 'Failed to submit homework'}), 500

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
    
    # Форматируем даты для отображения
    formatted_lessons = []
    for lesson in lessons:
        formatted_lesson = lesson.copy()
        try:
            lesson_date = datetime.fromisoformat(lesson['schedule'])
            formatted_lesson['schedule'] = lesson_date.strftime('%Y-%m-%dT%H:%M')
            formatted_lesson['formatted_schedule'] = lesson_date.strftime('%d.%m.%Y %H:%M')
        except:
            formatted_lesson['formatted_schedule'] = lesson['schedule']
        
        formatted_lessons.append(formatted_lesson)
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         lessons=formatted_lessons,
                         homeworks=homeworks,
                         is_teacher=session['user']['role'] == 'teacher')

# Обработка контактной формы
@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        data = request.json
        # Здесь можно добавить логику обработки формы (отправка email и т.д.)
        return jsonify({'success': True, 'message': 'Ваше сообщение отправлено!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=os.environ.get('FLASK_DEBUG', False))