from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import os
import json
from datetime import datetime

job_portal_bp = Blueprint('job_portal', __name__)

# Пути к файлам с данными
VACANCIES_FILE = os.path.join('data', 'vacancies.json')
SAVED_VACANCIES_FILE = os.path.join('data', 'saved_vacancies.json')

def load_vacancies():
    try:
        with open(VACANCIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Проверяем структуру данных
            if isinstance(data, list):
                # Если данные в виде списка, преобразуем в нужный формат
                vacancies = data
            elif isinstance(data, dict) and 'vacancies' in data:
                # Если данные в виде словаря с ключом 'vacancies'
                vacancies = data['vacancies']
            else:
                # Если структура не соответствует ожидаемой, возвращаем пустой список
                return []
            
            # Добавляем id к каждой вакансии
            for i, vacancy in enumerate(vacancies):
                vacancy['id'] = i
            return vacancies
    except FileNotFoundError:
        return []

def save_vacancies(vacancies):
    os.makedirs(os.path.dirname(VACANCIES_FILE), exist_ok=True)
    with open(VACANCIES_FILE, 'w', encoding='utf-8') as f:
        json.dump({'vacancies': vacancies}, f, ensure_ascii=False, indent=4)

def load_saved_vacancies():
    if os.path.exists(SAVED_VACANCIES_FILE):
        with open(SAVED_VACANCIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_saved_vacancies(saved_vacancies):
    os.makedirs(os.path.dirname(SAVED_VACANCIES_FILE), exist_ok=True)
    with open(SAVED_VACANCIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(saved_vacancies, f, ensure_ascii=False, indent=4)

@job_portal_bp.route('/')
def index():
    vacancies = load_vacancies()
    categories = {}
    for vacancy in vacancies:
        if vacancy['category'] not in categories:
            categories[vacancy['category']] = 0
        categories[vacancy['category']] += 1
    
    categories = [{'name': name, 'count': count} 
                 for name, count in categories.items()]
    
    latest_vacancies = sorted(vacancies, key=lambda x: x['posted_date'], reverse=True)[:6]
    
    return render_template('job_portal/index.html', 
                         categories=categories,
                         latest_vacancies=latest_vacancies)

@job_portal_bp.route('/vacancy/<int:vacancy_id>')
def vacancy(vacancy_id):
    vacancies = load_vacancies()
    if 0 <= vacancy_id < len(vacancies):
        vacancy = vacancies[vacancy_id]
        saved_vacancies = load_saved_vacancies()
        is_saved = current_user.is_authenticated and str(vacancy_id) in saved_vacancies.get(current_user.email, [])
        return render_template('job_portal/vacancy.html', 
                             vacancy=vacancy,
                             is_saved=is_saved)
    flash('Вакансия не найдена', 'danger')
    return redirect(url_for('job_portal.index'))

@job_portal_bp.route('/search')
def search():
    query = request.args.get('query', '').lower()
    category = request.args.get('category', '')
    
    vacancies = load_vacancies()
    categories = {}
    for vacancy in vacancies:
        if vacancy['category'] not in categories:
            categories[vacancy['category']] = 0
        categories[vacancy['category']] += 1
    
    categories = [{'id': i, 'name': name, 'count': count} 
                 for i, (name, count) in enumerate(categories.items())]
    
    if query or category:
        filtered_vacancies = []
        for i, vacancy in enumerate(vacancies):
            if (not query or 
                query in vacancy['title'].lower() or 
                query in vacancy['company'].lower() or 
                any(query in keyword.lower() for keyword in vacancy['keywords'])):
                if not category or vacancy['category'] == categories[int(category)]['name']:
                    filtered_vacancies.append(vacancy)
        vacancies = filtered_vacancies
    
    return render_template('job_portal/search.html',
                         vacancies=vacancies,
                         categories=categories,
                         query=query,
                         category=category)

@job_portal_bp.route('/categories')
def categories():
    vacancies = load_vacancies()
    categories = {}
    for vacancy in vacancies:
        if vacancy['category'] not in categories:
            categories[vacancy['category']] = 0
        categories[vacancy['category']] += 1
    
    categories = [{'name': name, 'count': count} 
                 for name, count in categories.items()]
    
    return render_template('job_portal/categories.html', categories=categories)

@job_portal_bp.route('/category/<category_slug>')
def category(category_slug):
    vacancies = load_vacancies()
    category_vacancies = [v for v in vacancies if v['category'].lower() == category_slug.lower()]
    return render_template('job_portal/category.html',
                         category=category_slug,
                         vacancies=category_vacancies)

@job_portal_bp.route('/saved')
@login_required
def saved_vacancies():
    saved_vacancies = load_saved_vacancies()
    user_saved = saved_vacancies.get(current_user.email, [])
    
    vacancies = load_vacancies()
    saved_vacancies_list = [vacancies[int(vacancy_id)] for vacancy_id in user_saved]
    
    return render_template('job_portal/saved_vacancies.html',
                         saved_vacancies=saved_vacancies_list)

@job_portal_bp.route('/save/<int:vacancy_id>', methods=['POST'])
@login_required
def save_vacancy(vacancy_id):
    saved_vacancies = load_saved_vacancies()
    user_saved = saved_vacancies.get(current_user.email, [])
    
    if str(vacancy_id) not in user_saved:
        user_saved.append(str(vacancy_id))
        saved_vacancies[current_user.email] = user_saved
        save_saved_vacancies(saved_vacancies)
        flash('Вакансия сохранена', 'success')
    else:
        flash('Вакансия уже сохранена', 'info')
    
    return redirect(url_for('job_portal.vacancy', vacancy_id=vacancy_id))

@job_portal_bp.route('/unsave/<int:vacancy_id>', methods=['POST'])
@login_required
def unsave_vacancy(vacancy_id):
    saved_vacancies = load_saved_vacancies()
    user_saved = saved_vacancies.get(current_user.email, [])
    
    if str(vacancy_id) in user_saved:
        user_saved.remove(str(vacancy_id))
        saved_vacancies[current_user.email] = user_saved
        save_saved_vacancies(saved_vacancies)
        flash('Вакансия удалена из сохраненных', 'success')
    
    return redirect(url_for('job_portal.vacancy', vacancy_id=vacancy_id))

@job_portal_bp.route('/apply/<int:vacancy_id>')
@login_required
def apply(vacancy_id):
    vacancies = load_vacancies()
    if 0 <= vacancy_id < len(vacancies):
        flash('Ваша заявка успешно отправлена', 'success')
    else:
        flash('Вакансия не найдена', 'danger')
    
    return redirect(url_for('job_portal.vacancy', vacancy_id=vacancy_id))

@job_portal_bp.route('/add_vacancy', methods=['GET', 'POST'])
@login_required
def add_vacancy():
    if request.method == 'POST':
        vacancies = load_vacancies()
        
        # Создаем новую вакансию
        new_vacancy = {
            'id': len(vacancies),
            'title': request.form['title'],
            'company': request.form['company'],
            'location': request.form['location'],
            'description': request.form['description'],
            'requirements': request.form['requirements'],
            'responsibilities': request.form['responsibilities'],
            'conditions': request.form['conditions'],
            'keywords': [k.strip() for k in request.form['keywords'].split(',')],
            'salary': {
                'min': int(request.form['salary_min']),
                'max': int(request.form['salary_max'])
            },
            'experience': request.form['experience'],
            'employment_type': request.form['employment_type'],
            'schedule': request.form['schedule'],
            'category': request.form['category'],
            'posted_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Добавляем вакансию в список
        vacancies.append(new_vacancy)
        
        # Сохраняем обновленный список вакансий
        save_vacancies(vacancies)
        
        flash('Вакансия успешно добавлена!', 'success')
        return redirect(url_for('job_portal.index'))
    
    return render_template('job_portal/add_vacancy.html') 