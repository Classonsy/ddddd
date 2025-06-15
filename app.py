from flask import Flask, render_template
from flask_login import LoginManager
from datetime import timedelta
import os
from models import User

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
    
    # Инициализация Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from routes.auth import load_users
        users = load_users()
        for user_data in users.get('users', []):
            if str(user_data['id']) == str(user_id):
                return User(user_data)
        return None
    
    # Создаем необходимые директории
    os.makedirs('data', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('uploads/resumes', exist_ok=True)
    os.makedirs('uploads/avatars', exist_ok=True)
    
    # Регистрируем blueprints
    from routes.auth import auth_bp
    from routes.job_portal import job_portal_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(job_portal_bp)
    
    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    return app 