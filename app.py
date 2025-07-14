<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Личный кабинет | Zindaki Academy</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/peerjs@1.4.7/dist/peerjs.min.js"></script>
    <style>
        :root {
            --primary: #4361ee;
            --primary-light: #4895ef;
            --primary-dark: #3a0ca3;
            --light: #f8f9fa;
            --lighter: #ffffff;
            --text: #2b2d42;
            --text-light: #8d99ae;
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
            --rounded-md: 12px;
            --rounded-lg: 16px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }
        
        body {
            background-color: var(--light);
            color: var(--text);
            line-height: 1.6;
        }
        
        .dashboard-container {
            max-width: 1200px;
            margin: 80px auto 0;
            padding: 2rem;
        }
        
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .user-greeting h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .user-greeting p {
            color: var(--text-light);
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: var(--rounded-md);
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn:hover {
            background-color: var(--primary-dark);
        }
        
        .btn-secondary {
            background-color: var(--light);
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        
        .btn-secondary:hover {
            background-color: var(--primary-light);
            color: white;
        }
        
        .btn-danger {
            background-color: #f72585;
        }
        
        .btn-danger:hover {
            background-color: #d1146e;
        }
        
        .btn-success {
            background-color: #4cc9f0;
        }
        
        .btn-success:hover {
            background-color: #3aa8cc;
        }
        
        .section {
            margin-top: 3rem;
            background: var(--lighter);
            padding: 1.5rem;
            border-radius: var(--rounded-lg);
            box-shadow: var(--shadow-md);
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--text);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .section-title .actions {
            display: flex;
            gap: 0.5rem;
        }
        
        /* Таблицы */
        .table-container {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        th {
            background-color: var(--light);
            font-weight: 600;
        }
        
        tr:hover {
            background-color: rgba(67, 97, 238, 0.05);
        }
        
        .status-active {
            color: #4cc9f0;
            font-weight: 600;
        }
        
        .status-inactive {
            color: var(--text-light);
        }
        
        .status-pending {
            color: #f8961e;
            font-weight: 600;
        }
        
        .status-accepted {
            color: #43aa8b;
            font-weight: 600;
        }
        
        .status-declined {
            color: #f94144;
            font-weight: 600;
        }
        
        /* Формы */
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid #e0e0e0;
            border-radius: var(--rounded-md);
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
        }
        
        .form-row .form-group {
            flex: 1;
        }
        
        /* Модальные окна */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background-color: white;
            padding: 2rem;
            border-radius: var(--rounded-lg);
            width: 100%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }
        
        .close-modal {
            position: absolute;
            top: 1rem;
            right: 1rem;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        /* Видеоконференция */
        .conference-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
            margin-bottom: 1.5rem;
            min-height: 500px;
            position: relative;
        }
        
        #remoteVideoContainer {
            width: 100%;
            height: 100%;
            background: #000;
            border-radius: var(--rounded-md);
            display: none;
        }
        
        #remoteVideo {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        #waitingMessage {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            color: var(--text-light);
            grid-column: 1 / -1;
            text-align: center;
            padding: 2rem;
        }
        
        .video-container {
            position: relative;
            background: #000;
            border-radius: var(--rounded-md);
            overflow: hidden;
            aspect-ratio: 16/9;
        }
        
        .video-container video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .video-controls {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.5rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .video-container:hover .video-controls {
            opacity: 1;
        }
        
        .video-control-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .video-control-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .video-label {
            position: absolute;
            bottom: 40px;
            left: 0;
            right: 0;
            color: white;
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
            background: rgba(0,0,0,0.5);
        }
        
        /* Локальное видео (маленькое в углу) */
        .local-video-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 200px;
            height: 150px;
            z-index: 100;
            background: #000;
            border-radius: var(--rounded-md);
            overflow: hidden;
        }
        
        .local-video-container video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .screen-container {
            grid-column: 1 / -1;
            background: #000;
            border-radius: var(--rounded-md);
            overflow: hidden;
            aspect-ratio: 16/9;
            position: relative;
            display: none;
        }
        
        .screen-container video {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .conference-controls {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .participants-list {
            margin-top: 1rem;
            padding: 1rem;
            background: var(--light);
            border-radius: var(--rounded-md);
        }
        
        .participant-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        .participant-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--primary-light);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        /* Домашние задания */
        .homework-status {
            padding: 0.25rem 0.5rem;
            border-radius: var(--rounded-md);
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .homework-status-not-submitted {
            background-color: #ffebee;
            color: #c62828;
        }
        
        .homework-status-submitted {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        
        /* Загрузка файлов */
        .file-upload {
            margin-top: 1rem;
        }
        
        .file-upload-preview {
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-light);
        }
        
        /* Приглашения */
        .invite-card {
            background: white;
            border-radius: var(--rounded-md);
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-md);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .invite-info {
            flex: 1;
        }
        
        .invite-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        /* Полноэкранный режим */
        .fullscreen-btn {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: rgba(0,0,0,0.5);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.25rem 0.5rem;
            cursor: pointer;
            z-index: 10;
        }
        
        .fullscreen-btn:hover {
            background: rgba(0,0,0,0.7);
        }
        
        /* Полезности */
        .utilities-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        
        .utility-card {
            background: white;
            border-radius: var(--rounded-md);
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            transition: transform 0.3s ease;
        }
        
        .utility-card:hover {
            transform: translateY(-5px);
        }
        
        .utility-card h3 {
            margin-bottom: 1rem;
            color: var(--primary);
        }
        
        .utility-card p {
            margin-bottom: 1rem;
            color: var(--text-light);
        }
        
        .utility-card .btn {
            margin-top: 0.5rem;
        }
        
        /* Адаптивность */
        @media (max-width: 768px) {
            .dashboard-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            
            .form-row {
                flex-direction: column;
                gap: 0;
            }
            
            .section-title {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            
            .section-title .actions {
                width: 100%;
                justify-content: flex-end;
            }
            
            .conference-controls {
                flex-direction: column;
            }
            
            .invite-card {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            
            .invite-actions {
                width: 100%;
                justify-content: flex-end;
            }
            
            .local-video-container {
                width: 120px;
                height: 90px;
                bottom: 10px;
                right: 10px;
            }
            
            .utilities-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <div class="user-greeting">
                <h1>Добро пожаловать, {{ user.username }}!</h1>
                <p>{{ 'Преподаватель' if user.role == 'teacher' else 'Студент' }} Zindaki Academy</p>
            </div>
            <button class="btn" id="logoutBtn">
                <i class="fas fa-sign-out-alt"></i> Выйти
            </button>
        </div>

        {% if is_teacher %}
        <!-- Управление пользователями -->
        <div class="section">
            <h2 class="section-title">
                Управление пользователями
                <div class="actions">
                    <button class="btn" id="addUserBtn">
                        <i class="fas fa-plus"></i> Добавить пользователя
                    </button>
                </div>
            </h2>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Имя пользователя</th>
                            <th>Email</th>
                            <th>Роль</th>
                            <th>Статус</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody id="usersTable">
                        <!-- Данные будут загружены через JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Домашние задания (для учителя) -->
        <div class="section">
            <h2 class="section-title">Назначенные домашние задания</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Урок</th>
                            <th>Задание</th>
                            <th>Срок сдачи</th>
                            <th>Ученики</th>
                            <th>Статус</th>
                        </tr>
                    </thead>
                    <tbody id="homeworksTable">
                        {% for hw in homeworks %}
                        <tr>
                            <td>{{ hw.title }}</td>
                            <td>{{ hw.description }}</td>
                            <td>{{ hw.deadline }}</td>
                            <td>{{ hw.students|join(', ') }}</td>
                            <td>
                                <span class="homework-status homework-status-{{ 'submitted' if hw.status == 'submitted' else 'not-submitted' }}">
                                    {{ 'Сдано' if hw.status == 'submitted' else 'Не сдано' }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Управление конференциями (для учителя) -->
        <div class="section" id="conferenceManagementSection">
            <h2 class="section-title">
                Управление конференциями
                <div class="actions">
                    <button class="btn" id="startConferenceBtn">
                        <i class="fas fa-video"></i> Начать конференцию
                    </button>
                    <button class="btn btn-secondary" id="inviteStudentBtn">
                        <i class="fas fa-user-plus"></i> Пригласить ученика
                    </button>
                </div>
            </h2>
            
            <div id="conferenceStatus" style="margin-bottom: 1rem; padding: 1rem; background: #f0f0f0; border-radius: var(--rounded-md);">
                <p>Конференция не активна</p>
            </div>
            
            <div id="invitesList">
                <h4>Отправленные приглашения:</h4>
                <!-- Список приглашений будет загружен через JavaScript -->
            </div>
        </div>
        {% else %}
        <!-- Для студентов -->
        <div class="section">
            <h2 class="section-title">Мои курсы</h2>
            
            {% if lessons %}
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Описание</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for lesson in lessons %}
                        <tr>
                            <td>{{ lesson.title }}</td>
                            <td>{{ lesson.description }}</td>
                            <td>
                                <button class="btn join-lesson-btn" data-lesson-id="{{ lesson.id }}">
                                    <i class="fas fa-video"></i> Присоединиться
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p>Вы пока не записаны ни на один курс</p>
            {% endif %}
            
            <!-- Альтернативные ссылки на конференции -->
            <div style="margin-top: 2rem;">
                <h3>Альтернативные платформы для конференций:</h3>
                <ul style="margin-top: 1rem; list-style-type: none; padding-left: 0;">
                    <li style="margin-bottom: 0.5rem;">
                        <a href="https://meet.google.com/eec-earm-gyd" target="_blank" class="btn btn-secondary" style="display: inline-flex; align-items: center;">
                            <i class="fab fa-google" style="margin-right: 0.5rem;"></i> Google Meet
                        </a>
                    </li>
                    <li>
                        <a href="https://teams.live.com/meet/9480976290023?p=wqOkR5Ye8VJMKmpq" target="_blank" class="btn btn-secondary" style="display: inline-flex; align-items: center;">
                            <i class="fab fa-microsoft" style="margin-right: 0.5rem;"></i> Microsoft Teams
                        </a>
                    </li>
                </ul>
            </div>
        </div>

        <!-- Приглашения на конференции (для студента) -->
        <div class="section" id="invitesSection">
            <h2 class="section-title">Приглашения на конференции</h2>
            <div id="studentInvitesList">
                <!-- Приглашения будут загружены через JavaScript -->
            </div>
        </div>

        <!-- Домашние задания (для студента) -->
        <div class="section">
            <h2 class="section-title">Домашние задания</h2>
            {% if homeworks %}
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Описание</th>
                            <th>Срок сдачи</th>
                            <th>Статус</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody id="studentHomeworkTable">
                        {% for hw in homeworks %}
                        <tr>
                            <td>{{ hw.title }}</td>
                            <td>{{ hw.description }}</td>
                            <td>{{ hw.deadline }}</td>
                            <td>
                                <span class="homework-status homework-status-{{ 'submitted' if hw.status == 'submitted' else 'not-submitted' }}">
                                    {{ 'Сдано' if hw.status == 'submitted' else 'Не сдано' }}
                                </span>
                            </td>
                            <td>
                                {% if hw.status != 'submitted' %}
                                <button class="btn" onclick="openSubmitHomeworkModal('{{ hw.id }}', '{{ hw.title }}', '{{ hw.description }}', '{{ hw.deadline }}')">
                                    <i class="fas fa-upload"></i> Сдать
                                </button>
                                {% else %}
                                <button class="btn btn-secondary">
                                    <i class="fas fa-check"></i> Проверено
                                </button>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p>Нет активных заданий</p>
            {% endif %}
        </div>
        {% endif %}

        <!-- Раздел "Полезности" -->
        <div class="section">
            <h2 class="section-title">Полезные ресурсы</h2>
            <div class="utilities-grid">
                <div class="utility-card">
                    <h3>VPN подключение</h3>
                    <p>Получите QR-код для подключения к нашему VPN серверу через WireGuard</p>
                    <button class="btn" id="getVpnBtn">
                        <i class="fas fa-qrcode"></i> Получить QR-код
                    </button>
                </div>
                
                <div class="utility-card">
                    <h3>Словари и переводчики</h3>
                    <p>Полезные ссылки на онлайн-словари и переводчики для изучения языков</p>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <a href="https://translate.yandex.ru/" target="_blank" class="btn btn-secondary">
                            <i class="fas fa-language"></i> Яндекс.Переводчик
                        </a>
                        <a href="https://www.lingvolive.com/" target="_blank" class="btn btn-secondary">
                            <i class="fas fa-book"></i> Lingvo
                        </a>
                    </div>
                </div>
                
                <div class="utility-card">
                    <h3>Образовательные ресурсы</h3>
                    <p>Дополнительные материалы для углубленного изучения предметов</p>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <a href="https://postnauka.ru/" target="_blank" class="btn btn-secondary">
                            <i class="fas fa-graduation-cap"></i> ПостНаука
                        </a>
                        <a href="https://arzamas.academy/" target="_blank" class="btn btn-secondary">
                            <i class="fas fa-history"></i> Арзамас
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Видеоконференция -->
        <div class="section" id="conferenceSection" style="display: none;">
            <h2 class="section-title">Видеоконференция</h2>
            
            <div class="conference-container" id="conferenceContainer">
                <!-- Основное видео (удаленный участник) -->
                <div class="video-container" id="remoteVideoContainer">
                    <video id="remoteVideo" autoplay playsinline></video>
                    <div class="video-label" id="remoteVideoLabel">Участник</div>
                    <div class="video-controls">
                        <button class="video-control-btn" onclick="toggleFullscreen('remoteVideo')">
                            <i class="fas fa-expand"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Сообщение об ожидании -->
                <div id="waitingMessage">
                    <p>Ожидаем подключения другого участника...</p>
                </div>
            </div>
            
            <!-- Маленькое окно с локальным видео (в правом нижнем углу) -->
            <div class="local-video-container" id="localVideoContainer">
                <video id="localVideo" autoplay muted playsinline></video>
                <div class="video-label">Вы ({{ user.username }})</div>
                <div class="video-controls">
                    <button class="video-control-btn" id="toggleVideoBtn">
                        <i class="fas fa-video"></i>
                    </button>
                    <button class="video-control-btn" id="toggleAudioBtn">
                        <i class="fas fa-microphone"></i>
                    </button>
                    <button class="video-control-btn" id="shareScreenBtn" style="display: none;">
                        <i class="fas fa-desktop"></i>
                    </button>
                    <button class="video-control-btn btn-danger" id="disconnectBtn">
                        <i class="fas fa-phone-slash"></i>
                    </button>
                </div>
            </div>
            
            {% if is_teacher %}
            <!-- Демонстрация экрана -->
            <div class="screen-container" id="screenContainer">
                <video id="screenShare" autoplay playsinline></video>
                <div class="video-label">Демонстрация экрана</div>
                <div class="video-controls">
                    <button class="video-control-btn" onclick="stopScreenSharing()">
                        <i class="fas fa-stop"></i>
                    </button>
                    <button class="video-control-btn" onclick="toggleFullscreen('screenShare')">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
            {% endif %}
            
            <div class="participants-list" id="participantsList">
                <h4>Участники:</h4>
                <!-- Список участников будет добавлен динамически -->
            </div>
            
            <div class="conference-controls">
                {% if is_teacher %}
                <button class="btn" id="teacherShareScreenBtn">
                    <i class="fas fa-desktop"></i> Демонстрация экрана
                </button>
                <button class="btn btn-danger" id="endConferenceBtn">
                    <i class="fas fa-stop"></i> Завершить конференцию
                </button>
                {% endif %}
                <button class="btn btn-danger" id="leaveConferenceBtn">
                    <i class="fas fa-phone-slash"></i> Покинуть конференцию
                </button>
            </div>
        </div>
    </div>

    <!-- Модальные окна -->
    <div class="modal" id="addUserModal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Добавить нового пользователя</h2>
            <form id="addUserForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="newUsername">Имя пользователя</label>
                        <input type="text" id="newUsername" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="newEmail">Email</label>
                        <input type="email" id="newEmail" class="form-control" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="newPassword">Пароль</label>
                        <input type="password" id="newPassword" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="confirmPassword">Подтвердите пароль</label>
                        <input type="password" id="confirmPassword" class="form-control" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="userRole">Роль</label>
                    <select id="userRole" class="form-control" required>
                        <option value="student">Ученик</option>
                        <option value="teacher">Преподаватель</option>
                    </select>
                </div>
                
                <div class="form-group" style="margin-top: 2rem;">
                    <button type="submit" class="btn">
                        <i class="fas fa-save"></i> Сохранить
                    </button>
                </div>
            </form>
        </div>
    </div>

    <div class="modal" id="submitHomeworkModal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Сдать домашнее задание</h2>
            <form id="submitHomeworkForm">
                <input type="hidden" id="homeworkId">
                
                <div class="form-group">
                    <label for="homeworkSubmissionTitle">Название задания</label>
                    <input type="text" id="homeworkSubmissionTitle" class="form-control" readonly>
                </div>
                
                <div class="form-group">
                    <label for="homeworkSubmissionDescription">Описание</label>
                    <textarea id="homeworkSubmissionDescription" class="form-control" rows="3" readonly></textarea>
                </div>
                
                <div class="form-group">
                    <label for="homeworkSubmissionDeadline">Срок сдачи</label>
                    <input type="text" id="homeworkSubmissionDeadline" class="form-control" readonly>
                </div>
                
                <div class="form-group">
                    <label for="homeworkSubmissionComment">Комментарий</label>
                    <textarea id="homeworkSubmissionComment" class="form-control" rows="3"></textarea>
                </div>
                
                <div class="form-group file-upload">
                    <label for="homeworkSubmissionFiles">Прикрепите файлы</label>
                    <input type="file" id="homeworkSubmissionFiles" class="form-control" multiple>
                    <div class="file-upload-preview" id="homeworkSubmissionFilesPreview"></div>
                </div>
                
                <div class="form-group" style="margin-top: 2rem;">
                    <button type="submit" class="btn">
                        <i class="fas fa-upload"></i> Отправить задание
                    </button>
                </div>
            </form>
        </div>
    </div>

    <div class="modal" id="inviteStudentModal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Пригласить ученика на конференцию</h2>
            <form id="inviteStudentForm">
                <div class="form-group">
                    <label for="inviteRoomName">Название комнаты</label>
                    <input type="text" id="inviteRoomName" class="form-control" value="ZindakiRoom_{{ user.username }}" readonly>
                </div>
                
                <div class="form-group">
                    <label for="inviteStudent">Выберите ученика</label>
                    <select id="inviteStudent" class="form-control" required>
                        <!-- Список учеников будет загружен через JavaScript -->
                    </select>
                </div>
                
                <div class="form-group" style="margin-top: 2rem;">
                    <button type="submit" class="btn">
                        <i class="fas fa-paper-plane"></i> Отправить приглашение
                    </button>
                </div>
            </form>
        </div>
    </div>

    <div class="modal" id="vpnModal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>VPN подключение</h2>
            <div id="vpnContent" style="text-align: center;">
                <p>Используйте этот QR-код для подключения к нашему VPN серверу через WireGuard</p>
                <div id="vpnQrCode" style="margin: 1rem auto; padding: 1rem; background: white; display: inline-block;">
                    <!-- QR-код будет сгенерирован здесь -->
                </div>
                <p>Или скачайте конфигурационный файл:</p>
                <button class="btn" id="downloadVpnConfig">
                    <i class="fas fa-download"></i> Скачать конфиг
                </button>
            </div>
        </div>
    </div>

    <script>
        // PeerJS конфигурация
        let peer = null;
        let currentPeerId = null;
        let connections = {};
        let localStream = null;
        let screenStream = null;
        let currentRoom = null;
        let isVideoEnabled = true;
        let isAudioEnabled = true;
        let isScreenSharing = false;
        let inviteCheckInterval = null;

        // Инициализация PeerJS
        function initPeerJS() {
            // Генерируем уникальный ID для пользователя
            const userId = '{{ user.username }}_' + Math.random().toString(36).substr(2, 9);
            currentPeerId = userId;
            
            // Создаем Peer объект с настройкой для локального сервера PeerJS
            peer = new Peer(userId, {
                host: 'localhost',
                port: 9001,
                secure: false,
                path: '/peerjs',
                debug: 3
            });
            
            peer.on('open', (id) => {
                console.log('PeerJS подключен с ID:', id);
                currentPeerId = id;
                
                // Для студента: запускаем проверку новых приглашений
                if (!{{ 'true' if is_teacher else 'false' }}) {
                    startCheckingInvites();
                }
            });
            
            peer.on('error', (err) => {
                console.error('PeerJS ошибка:', err);
            });
            
            // Обработка входящих соединений
            peer.on('call', (call) => {
                // Принимаем вызов и отвечаем своим потоком
                call.answer(localStream);
                
                call.on('stream', (remoteStream) => {
                    // Отображаем удаленный поток
                    handleRemoteStream(remoteStream, call.peer);
                });
                
                call.on('close', () => {
                    removeRemoteStream(call.peer);
                });
                
                call.on('error', (err) => {
                    console.error('Ошибка вызова:', err);
                    removeRemoteStream(call.peer);
                });
            });
            
            // Обработка входящих данных
            peer.on('connection', (conn) => {
                conn.on('data', (data) => {
                    handlePeerData(conn.peer, data);
                });
                
                conn.on('close', () => {
                    removePeerConnection(conn.peer);
                });
            });
        }

        // Для студента: периодическая проверка новых приглашений
        function startCheckingInvites() {
            // Останавливаем предыдущий интервал, если он был
            if (inviteCheckInterval) {
                clearInterval(inviteCheckInterval);
            }
            
            // Загружаем приглашения сразу
            loadStudentInvites();
            
            // Устанавливаем интервал проверки каждые 10 секунд
            inviteCheckInterval = setInterval(loadStudentInvites, 10000);
        }

        // Загрузка приглашений для студента
        async function loadStudentInvites() {
            try {
                const response = await fetch('/api/conference/invites');
                if (!response.ok) {
                    throw new Error('Ошибка загрузки приглашений');
                }
                const data = await response.json();
                
                const invitesList = document.getElementById('studentInvitesList');
                invitesList.innerHTML = '';
                
                if (data.invites && data.invites.length > 0) {
                    // Фильтруем только приглашения для текущего пользователя со статусом 'pending'
                    const userInvites = data.invites.filter(invite => 
                        invite.student === '{{ user.username }}' && invite.status === 'pending'
                    );
                    
                    if (userInvites.length === 0) {
                        invitesList.innerHTML = '<p>Нет новых приглашений</p>';
                        return;
                    }
                    
                    userInvites.forEach(invite => {
                        const inviteCard = document.createElement('div');
                        inviteCard.className = 'invite-card';
                        inviteCard.innerHTML = `
                            <div class="invite-info">
                                <p><strong>Преподаватель:</strong> ${invite.teacher}</p>
                                <p><small>Получено: ${new Date(invite.created_at).toLocaleString()}</small></p>
                            </div>
                            <div class="invite-actions">
                                <button class="btn btn-success" onclick="respondToInvite(${invite.id}, 'accept')">
                                    <i class="fas fa-check"></i> Принять
                                </button>
                                <button class="btn btn-danger" onclick="respondToInvite(${invite.id}, 'decline')">
                                    <i class="fas fa-times"></i> Отклонить
                                </button>
                            </div>
                        `;
                        invitesList.appendChild(inviteCard);
                    });
                } else {
                    invitesList.innerHTML = '<p>Нет новых приглашений</p>';
                }
            } catch (error) {
                console.error('Error loading invites:', error);
                document.getElementById('studentInvitesList').innerHTML = 
                    '<p>Ошибка загрузки приглашений. Пожалуйста, обновите страницу.</p>';
            }
        }

        // Ответ на приглашение (принять/отклонить)
        window.respondToInvite = async function(inviteId, action) {
            try {
                const response = await fetch(`/api/conference/invite/${inviteId}/respond`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ action })
                });
                
                const data = await response.json();
                if (data.success) {
                    if (action === 'accept') {
                        // Принятие приглашения - присоединяемся к конференции
                        initConference(data.room_name);
                    }
                    // Обновляем список приглашений
                    loadStudentInvites();
                } else {
                    alert(data.error || 'Ошибка при обработке приглашения');
                }
            } catch (error) {
                console.error('Error responding to invite:', error);
                alert('Произошла ошибка при обработке приглашения');
            }
        };

        // Инициализация видеоконференции с PeerJS
        async function initConference(roomName, isInitiator = false) {
            console.log('Initializing conference with PeerJS...');
            currentRoom = roomName;
            
            try {
                // Получаем доступ к камере и микрофону
                const constraints = {
                    video: {
                        width: { ideal: 640 },
                        height: { ideal: 480 },
                        frameRate: { ideal: 15, max: 20 }
                    },
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                };
                
                localStream = await navigator.mediaDevices.getUserMedia(constraints);
                
                // Отображаем локальное видео
                const localVideo = document.getElementById('localVideo');
                localVideo.srcObject = localStream;
                document.getElementById('localVideoContainer').style.display = 'block';
                
                // Подключаемся к другим участникам
                if (isInitiator) {
                    // Учитель ожидает подключения студентов
                    document.getElementById('waitingMessage').style.display = 'flex';
                } else {
                    // Студент подключается к учителю
                    const teacherId = await getTeacherPeerId(roomName);
                    if (teacherId) {
                        connectToPeer(teacherId);
                    } else {
                        alert('Преподаватель не найден в комнате');
                    }
                }
                
                document.getElementById('conferenceSection').style.display = 'block';
                document.getElementById('conferenceSection').scrollIntoView({ behavior: 'smooth' });
                
                // Для учителя показываем кнопку завершения конференции
                if ({{ 'true' if is_teacher else 'false' }}) {
                    document.getElementById('endConferenceBtn').style.display = 'inline-block';
                }
            } catch (error) {
                console.error('Error initializing conference:', error);
                alert('Ошибка при подключении к конференции: ' + error.message);
            }
        }

        // Получение Peer ID преподавателя
        async function getTeacherPeerId(roomName) {
            try {
                const response = await fetch(`/api/conference/${roomName}/host`);
                const data = await response.json();
                return data.peerId;
            } catch (error) {
                console.error('Error getting teacher peer ID:', error);
                return null;
            }
        }

        // Подключение к другому участнику
        function connectToPeer(peerId) {
            if (connections[peerId]) return;
            
            // Устанавливаем соединение для передачи данных
            const conn = peer.connect(peerId);
            connections[peerId] = conn;
            
            conn.on('open', () => {
                console.log('Соединение установлено с', peerId);
                // Отправляем информацию о себе
                conn.send({
                    type: 'user-info',
                    username: '{{ user.username }}',
                    isTeacher: {{ 'true' if is_teacher else 'false' }}
                });
            });
            
            conn.on('data', (data) => {
                handlePeerData(peerId, data);
            });
            
            conn.on('close', () => {
                removePeerConnection(peerId);
            });
            
            conn.on('error', (err) => {
                console.error('Ошибка соединения:', err);
                removePeerConnection(peerId);
            });
            
            // Устанавливаем видеозвонок
            const call = peer.call(peerId, localStream);
            call.on('stream', (remoteStream) => {
                handleRemoteStream(remoteStream, peerId);
            });
            
            call.on('close', () => {
                removeRemoteStream(peerId);
            });
            
            call.on('error', (err) => {
                console.error('Ошибка видеозвонка:', err);
                removeRemoteStream(peerId);
            });
        }

        // Обработка удаленного потока
        function handleRemoteStream(stream, peerId) {
            const remoteVideo = document.getElementById('remoteVideo');
            remoteVideo.srcObject = stream;
            document.getElementById('remoteVideoContainer').style.display = 'block';
            document.getElementById('waitingMessage').style.display = 'none';
            
            // Добавляем участника в список
            updateParticipantList(peerId, true);
        }

        // Удаление удаленного потока
        function removeRemoteStream(peerId) {
            const remoteVideo = document.getElementById('remoteVideo');
            if (remoteVideo.srcObject) {
                remoteVideo.srcObject.getTracks().forEach(track => track.stop());
                remoteVideo.srcObject = null;
            }
            
            document.getElementById('remoteVideoContainer').style.display = 'none';
            document.getElementById('waitingMessage').style.display = 'flex';
            
            // Удаляем участника из списка
            updateParticipantList(peerId, false);
        }

        // Обработка данных от других участников
        function handlePeerData(peerId, data) {
            switch (data.type) {
                case 'user-info':
                    updateParticipantList(peerId, true, data.username, data.isTeacher);
                    break;
                case 'screen-sharing':
                    if (data.active) {
                        document.getElementById('screenContainer').style.display = 'block';
                        const screenVideo = document.getElementById('screenShare');
                        screenVideo.srcObject = data.stream;
                    } else {
                        document.getElementById('screenContainer').style.display = 'none';
                    }
                    break;
                case 'conference-end':
                    alert('Конференция завершена преподавателем');
                    leaveConference();
                    break;
            }
        }

        // Удаление соединения с участником
        function removePeerConnection(peerId) {
            if (connections[peerId]) {
                connections[peerId].close();
                delete connections[peerId];
            }
            removeRemoteStream(peerId);
        }

        // Обновление списка участников
        function updateParticipantList(peerId, isConnected, username = null, isTeacher = false) {
            const participantsList = document.getElementById('participantsList');
            const participantItem = document.getElementById(`participant-${peerId}`);
            
            if (isConnected) {
                if (!participantItem) {
                    const item = document.createElement('div');
                    item.className = 'participant-item';
                    item.id = `participant-${peerId}`;
                    item.innerHTML = `
                        <div class="participant-avatar">${(username || peerId).charAt(0).toUpperCase()}</div>
                        <div>${username || peerId} ${isTeacher ? '(Преподаватель)' : ''}</div>
                    `;
                    participantsList.appendChild(item);
                }
            } else if (participantItem) {
                participantItem.remove();
            }
        }

        // Демонстрация экрана (для учителя)
        async function startScreenSharing() {
            if (isScreenSharing) {
                stopScreenSharing();
                return;
            }
            
            try {
                screenStream = await navigator.mediaDevices.getDisplayMedia({
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        frameRate: { ideal: 10, max: 15 }
                    },
                    audio: false
                });
                
                isScreenSharing = true;
                document.getElementById('screenContainer').style.display = 'block';
                document.getElementById('teacherShareScreenBtn').innerHTML = '<i class="fas fa-stop"></i> Остановить демонстрацию';
                
                const screenVideo = document.getElementById('screenShare');
                screenVideo.srcObject = screenStream;
                
                // Отправляем информацию о демонстрации экрана всем участникам
                Object.keys(connections).forEach(peerId => {
                    const call = peer.call(peerId, screenStream);
                    call.on('stream', (remoteStream) => {
                        // Участник получит наш экран
                    });
                    
                    connections[peerId].send({
                        type: 'screen-sharing',
                        active: true
                    });
                });
                
                screenStream.getVideoTracks()[0].onended = () => {
                    stopScreenSharing();
                };
                
            } catch (error) {
                console.error('Error starting screen sharing:', error);
                isScreenSharing = false;
                document.getElementById('screenContainer').style.display = 'none';
                document.getElementById('teacherShareScreenBtn').innerHTML = '<i class="fas fa-desktop"></i> Демонстрация экрана';
            }
        }

        // Остановка демонстрации экрана
        function stopScreenSharing() {
            if (screenStream) {
                screenStream.getTracks().forEach(track => track.stop());
                screenStream = null;
            }
            
            isScreenSharing = false;
            document.getElementById('screenContainer').style.display = 'none';
            document.getElementById('teacherShareScreenBtn').innerHTML = '<i class="fas fa-desktop"></i> Демонстрация экрана';
            
            // Уведомляем участников об остановке демонстрации
            Object.keys(connections).forEach(peerId => {
                connections[peerId].send({
                    type: 'screen-sharing',
                    active: false
                });
            });
        }

        // Выход из конференции
        async function leaveConference() {
            // Останавливаем все медиапотоки
            if (localStream) {
                localStream.getTracks().forEach(track => track.stop());
                localStream = null;
            }
            
            if (screenStream) {
                screenStream.getTracks().forEach(track => track.stop());
                screenStream = null;
            }
            
            // Закрываем все соединения
            Object.keys(connections).forEach(peerId => {
                connections[peerId].close();
            });
            connections = {};
            
            // Очищаем видеоэлементы
            document.getElementById('remoteVideo').srcObject = null;
            document.getElementById('localVideo').srcObject = null;
            document.getElementById('screenShare').srcObject = null;
            
            document.getElementById('waitingMessage').style.display = 'flex';
            document.getElementById('remoteVideoContainer').style.display = 'none';
            document.getElementById('localVideoContainer').style.display = 'none';
            document.getElementById('screenContainer').style.display = 'none';
            
            // Очищаем список участников
            document.getElementById('participantsList').innerHTML = '<h4>Участники:</h4>';
            
            if (currentRoom) {
                // Уведомляем сервер о выходе из комнаты
                await fetch(`/api/conference/${currentRoom}/leave`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                currentRoom = null;
            }
            
            document.getElementById('conferenceSection').style.display = 'none';
            document.getElementById('endConferenceBtn').style.display = 'none';
        }

        // Завершение конференции (для учителя)
        async function endConference() {
            if (confirm('Вы уверены, что хотите завершить конференцию для всех участников?')) {
                // Уведомляем всех участников о завершении
                Object.keys(connections).forEach(peerId => {
                    connections[peerId].send({
                        type: 'conference-end'
                    });
                });
                
                await leaveConference();
                
                if (currentRoom) {
                    await fetch(`/api/conference/${currentRoom}/end`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                }
                
                window.location.reload();
            }
        }

        // Переключение видео
        function toggleVideo() {
            isVideoEnabled = !isVideoEnabled;
            const btn = document.getElementById('toggleVideoBtn');
            
            if (isVideoEnabled) {
                btn.innerHTML = '<i class="fas fa-video"></i>';
                btn.title = 'Выключить видео';
            } else {
                btn.innerHTML = '<i class="fas fa-video-slash"></i>';
                btn.title = 'Включить видео';
            }
            
            if (localStream) {
                localStream.getVideoTracks()[0].enabled = isVideoEnabled;
            }
        }

        // Переключение аудио
        function toggleAudio() {
            isAudioEnabled = !isAudioEnabled;
            const btn = document.getElementById('toggleAudioBtn');
            
            if (isAudioEnabled) {
                btn.innerHTML = '<i class="fas fa-microphone"></i>';
                btn.title = 'Выключить микрофон';
            } else {
                btn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                btn.title = 'Включить микрофон';
            }
            
            if (localStream) {
                localStream.getAudioTracks()[0].enabled = isAudioEnabled;
            }
        }

        // Полноэкранный режим
        function toggleFullscreen(elementId) {
            const element = document.getElementById(elementId);
            
            if (!document.fullscreenElement) {
                if (element.requestFullscreen) {
                    element.requestFullscreen();
                } else if (element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if (element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
            }
        }

        // Обработчики кнопок
        document.getElementById('toggleVideoBtn').addEventListener('click', toggleVideo);
        document.getElementById('toggleAudioBtn').addEventListener('click', toggleAudio);
        document.getElementById('disconnectBtn').addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите отключиться от конференции?')) {
                leaveConference();
            }
        });

        document.getElementById('leaveConferenceBtn').addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите покинуть конференцию?')) {
                leaveConference().then(() => {
                    window.location.reload();
                });
            }
        });

        document.getElementById('endConferenceBtn').addEventListener('click', endConference);

        // Для учителя: кнопка демонстрации экрана
        if ({{ 'true' if is_teacher else 'false' }}) {
            document.getElementById('teacherShareScreenBtn').addEventListener('click', startScreenSharing);
            
            // Обновление статуса конференции
            async function updateConferenceStatus() {
                const roomName = `ZindakiRoom_{{ user.username }}`;
                const response = await fetch(`/api/conference/${roomName}/status`);
                const data = await response.json();
                
                const statusElement = document.getElementById('conferenceStatus');
                if (data.is_active) {
                    statusElement.innerHTML = `
                        <p>Конференция активна с ${new Date(data.conference.started_at).toLocaleString()}</p>
                        <p>Участников: ${data.conference.participants?.length || 0}</p>
                    `;
                    statusElement.style.backgroundColor = '#e8f5e9';
                } else {
                    statusElement.innerHTML = '<p>Конференция не активна</p>';
                    statusElement.style.backgroundColor = '#f0f0f0';
                }
            }
            
            // Загрузка отправленных приглашений
            async function loadTeacherInvites() {
                const response = await fetch('/api/conference/invites');
                const data = await response.json();
                
                const invitesList = document.getElementById('invitesList');
                invitesList.innerHTML = '<h4>Отправленные приглашения:</h4>';
                
                if (data.invites.length === 0) {
                    invitesList.innerHTML += '<p>Нет отправленных приглашений</p>';
                    return;
                }
                
                data.invites.forEach(invite => {
                    const inviteCard = document.createElement('div');
                    inviteCard.className = 'invite-card';
                    inviteCard.innerHTML = `
                        <div class="invite-info">
                            <p><strong>Ученик:</strong> ${invite.student}</p>
                            <p><strong>Статус:</strong> <span class="status-${invite.status}">${
                                invite.status === 'pending' ? 'Ожидает ответа' : 
                                invite.status === 'accepted' ? 'Принято' : 'Отклонено'
                            }</span></p>
                            <p><small>Отправлено: ${new Date(invite.created_at).toLocaleString()}</small></p>
                        </div>
                    `;
                    invitesList.appendChild(inviteCard);
                });
            }
            
            // Начало конференции
            document.getElementById('startConferenceBtn').addEventListener('click', async function() {
                const roomName = `ZindakiRoom_{{ user.username }}`;
                
                const response = await fetch(`/api/conference/${roomName}/start`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        peerId: currentPeerId
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    initConference(roomName, true);
                    updateConferenceStatus();
                } else {
                    alert(data.error || 'Ошибка при запуске конференции');
                }
            });
            
            // Отправка приглашения
            document.getElementById('inviteStudentBtn').addEventListener('click', function() {
                loadStudentsForSelect('inviteStudent');
                document.getElementById('inviteStudentModal').style.display = 'flex';
            });
            
            // Форма отправки приглашения
            document.getElementById('inviteStudentForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const studentUsername = document.getElementById('inviteStudent').value;
                const roomName = document.getElementById('inviteRoomName').value;
                
                const response = await fetch('/api/conference/invite', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        student_username: studentUsername,
                        room_name: roomName
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert('Приглашение отправлено!');
                    document.getElementById('inviteStudentModal').style.display = 'none';
                    document.getElementById('inviteStudentForm').reset();
                    loadTeacherInvites();
                } else {
                    alert(data.error || 'Ошибка отправки приглашения');
                }
            });
            
            // Инициализация
            updateConferenceStatus();
            loadTeacherInvites();
        } else {
            // Для студентов: загрузка приглашений
            loadStudentInvites();
        }
        
        // Обработка присоединения к уроку
        document.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('join-lesson-btn')) {
                e.preventDefault();
                const lessonId = e.target.getAttribute('data-lesson-id');
                
                fetch(`/api/lesson/${lessonId}/join`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            initConference(data.room_name);
                        } else {
                            alert(data.error || 'Ошибка подключения к конференции');
                        }
                    });
            }
        });

        // Для учителя: загрузка данных
        if ({{ 'true' if is_teacher else 'false' }}) {
            // Функция для добавления пользователя
            function addUser(userData) {
                fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadUsers();
                        document.getElementById('addUserModal').style.display = 'none';
                        document.getElementById('addUserForm').reset();
                    } else {
                        alert(data.error || 'Ошибка при добавлении пользователя');
                    }
                });
            }
            
            // Загрузка списка пользователей
            function loadUsers() {
                fetch('/api/users')
                    .then(response => {
                        if (!response.ok) throw new Error('Ошибка загрузки пользователей');
                        return response.json();
                    })
                    .then(data => {
                        const tableBody = document.getElementById('usersTable');
                        tableBody.innerHTML = '';
                        
                        data.users.forEach(user => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${user.username}</td>
                                <td>${user.email}</td>
                                <td>${user.role === 'teacher' ? 'Преподаватель' : 'Ученик'}</td>
                                <td class="${user.is_active ? 'status-active' : 'status-inactive'}">
                                    ${user.is_active ? 'Активен' : 'Неактивен'}
                                </td>
                                <td>
                                    <button class="btn btn-secondary" onclick="toggleUserStatus('${user.username}', ${!user.is_active})">
                                        ${user.is_active ? 'Деактивировать' : 'Активировать'}
                                    </button>
                                    <button class="btn btn-danger" onclick="deleteUser('${user.username}')">
                                        <i class="fas fa-trash"></i> Удалить
                                    </button>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Ошибка загрузки пользователей');
                    });
            }
            
            // Загрузка домашних заданий
            function loadHomeworks() {
                fetch('/api/homework')
                    .then(response => {
                        if (!response.ok) throw new Error('Ошибка загрузки домашних заданий');
                        return response.json();
                    })
                    .then(data => {
                        const tableBody = document.getElementById('homeworksTable');
                        tableBody.innerHTML = '';
                        
                        data.homeworks.forEach(hw => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${hw.title}</td>
                                <td>${hw.description}</td>
                                <td>${hw.deadline}</td>
                                <td>${hw.students.join(', ')}</td>
                                <td>
                                    <span class="homework-status homework-status-${hw.status || 'not-submitted'}">
                                        ${hw.status === 'submitted' ? 'Сдано' : 'Не сдано'}
                                    </span>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Ошибка загрузки домашних заданий');
                    });
            }
            
            // Загрузка списка учеников для выбора
            function loadStudentsForSelect(selectId) {
                fetch('/api/users?role=student')
                    .then(response => {
                        if (!response.ok) throw new Error('Ошибка загрузки учеников');
                        return response.json();
                    })
                    .then(data => {
                        const select = document.getElementById(selectId);
                        select.innerHTML = '';
                        
                        data.users.forEach(student => {
                            const option = document.createElement('option');
                            option.value = student.username;
                            option.textContent = student.username;
                            select.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Ошибка загрузки списка учеников');
                    });
            }
            
            // Управление пользователями
            window.toggleUserStatus = function(username, activate) {
                if (confirm(`Вы уверены, что хотите ${activate ? 'активировать' : 'деактивировать'} пользователя ${username}?`)) {
                    fetch(`/api/users/${username}/status`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ is_active: activate })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            loadUsers();
                        } else {
                            alert(data.error || 'Ошибка обновления статуса');
                        }
                    });
                }
            };
            
            window.deleteUser = function(username) {
                if (confirm(`Вы уверены, что хотите удалить пользователя ${username}?`)) {
                    fetch(`/api/users/${username}`, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            loadUsers();
                        } else {
                            alert(data.error || 'Ошибка удаления пользователя');
                        }
                    });
                }
            };
            
            // Модальные окна
            document.getElementById('addUserBtn').addEventListener('click', () => {
                document.getElementById('addUserModal').style.display = 'flex';
            });
            
            document.querySelectorAll('.close-modal').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.modal').forEach(modal => {
                        modal.style.display = 'none';
                    });
                });
            });
            
            // Форма добавления пользователя
            document.getElementById('addUserForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const username = document.getElementById('newUsername').value;
                const email = document.getElementById('newEmail').value;
                const password = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const role = document.getElementById('userRole').value;
                
                if (password !== confirmPassword) {
                    alert('Пароли не совпадают!');
                    return;
                }
                
                addUser({ username, email, password, role });
            });
            
            // Загрузка начальных данных
            loadUsers();
            loadHomeworks();
        } else {
            // Для учеников
            window.openSubmitHomeworkModal = function(homeworkId, title, description, deadline) {
                document.getElementById('homeworkId').value = homeworkId;
                document.getElementById('homeworkSubmissionTitle').value = title;
                document.getElementById('homeworkSubmissionDescription').value = description;
                document.getElementById('homeworkSubmissionDeadline').value = deadline;
                document.getElementById('submitHomeworkModal').style.display = 'flex';
            };
            
            // Форма сдачи домашнего задания
            document.getElementById('submitHomeworkForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const homeworkId = document.getElementById('homeworkId').value;
                const comment = document.getElementById('homeworkSubmissionComment').value;
                
                const filesInput = document.getElementById('homeworkSubmissionFiles');
                const files = filesInput.files;
                
                const formData = new FormData();
                formData.append('homework_id', homeworkId);
                formData.append('comment', comment);
                
                for (let i = 0; i < files.length; i++) {
                    formData.append('files', files[i]);
                }
                
                fetch('/api/homework/submit', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Домашнее задание успешно отправлено!');
                        document.getElementById('submitHomeworkModal').style.display = 'none';
                        document.getElementById('submitHomeworkForm').reset();
                        document.getElementById('homeworkSubmissionFilesPreview').innerHTML = '';
                        window.location.reload();
                    } else {
                        alert(data.error || 'Ошибка при отправке домашнего задания');
                    }
                });
            });
            
            // Превью загружаемых файлов (сдача ДЗ)
            document.getElementById('homeworkSubmissionFiles').addEventListener('change', function() {
                const preview = document.getElementById('homeworkSubmissionFilesPreview');
                preview.innerHTML = '';
                
                if (this.files.length > 0) {
                    preview.innerHTML = `Выбрано файлов: ${this.files.length}<br>`;
                    for (let i = 0; i < this.files.length; i++) {
                        preview.innerHTML += `${i+1}. ${this.files[i].name}<br>`;
                    }
                }
            });
        }

        // Получение VPN QR-кода
        document.getElementById('getVpnBtn').addEventListener('click', function() {
            // В реальной реализации здесь будет запрос к серверу для получения QR-кода
            // Сейчас просто демонстрация
            document.getElementById('vpnModal').style.display = 'flex';
            document.getElementById('vpnQrCode').innerHTML = '<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://wireguard.example.com/config/vpn-config" alt="VPN QR Code">';
        });

        // Скачивание VPN конфига
        document.getElementById('downloadVpnConfig').addEventListener('click', function() {
            // В реальной реализации здесь будет запрос к серверу для скачивания файла
            alert('Конфигурационный файл WireGuard будет скачан');
        });

        // Закрытие модальных окон при клике вне их
        window.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });

        // Обработка выхода
        document.getElementById('logoutBtn').addEventListener('click', function() {
            fetch('/api/logout')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/';
                    }
                });
        });

        // Инициализация PeerJS при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            initPeerJS();
        });
    </script>
</body>
</html>