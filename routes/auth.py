from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
from models import User

auth_bp = Blueprint('auth', __name__)

def load_users():
    if os.path.exists('data/users.json'):
        with open('data/users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'users': []}

def save_users(users):
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('job_portal.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_users()
        user_data = next((u for u in users['users'] if u['email'] == email), None)
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            flash('Вы успешно вошли в систему', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('job_portal.index'))
        
        flash('Неверный email или пароль', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('job_portal.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        users = load_users()
        
        if any(u['email'] == email for u in users['users']):
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('auth/register.html')
        
        new_user = {
            'id': len(users['users']) + 1,
            'name': name,
            'email': email,
            'phone': phone,
            'password': generate_password_hash(password),
            'role': 'user',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        users['users'].append(new_user)
        save_users(users)
        
        flash('Регистрация успешно завершена', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('job_portal.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        users = load_users()
        user_data = next((u for u in users['users'] if u['id'] == current_user.id), None)
        
        if not user_data or not check_password_hash(user_data['password'], current_password):
            flash('Неверный текущий пароль', 'danger')
            return render_template('auth/edit_profile.html', user=current_user)
        
        if new_password:
            if new_password != confirm_password:
                flash('Пароли не совпадают', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            user_data['password'] = generate_password_hash(new_password)
        
        user_data['name'] = name
        user_data['phone'] = phone
        
        if email != current_user.email:
            if any(u['email'] == email for u in users['users']):
                flash('Пользователь с таким email уже существует', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            user_data['email'] = email
        
        save_users(users)
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=current_user) 