from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Настройки почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sploispy@gmail.com'
app.config['MAIL_PASSWORD'] = 'drunroobepjsqvcb'

mail = Mail(app)

from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Файл с базой данных
db = SQLAlchemy(app)

# Описываем таблицу пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        users[email] = {
            "username": request.form.get('username'),
            "password": request.form.get('password')
        }
        return "Регистрация прошла успешно! <a href='/login'>Войти</a>"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in users and users[email]['password'] == password:
            session['email'] = email
            return redirect(url_for('cabinet'))
        return "Ошибка: Неверный email или пароль. <a href='/login'>Назад</a>"
    return render_template('login.html')

@app.route('/cabinet')
def cabinet():
    if 'email' in session:
        user = users.get(session['email'])
        return f"Привет, {user['username']}! Ты в личном кабинете. <a href='/logout'>Выйти</a>"
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in users:
            password = users[email]['password']
            try:
                msg = Message("Восстановление пароля", sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f"Ваш пароль от IT-Help: {password}"
                mail.send(msg)
                return "Письмо с паролем отправлено на ваш email!"
            except Exception as e:
                return f"Ошибка отправки: {e}"
        return "Email не найден."
    return '<form method="POST"><input name="email" placeholder="Email" required><button>Отправить</button></form>'

if __name__ == '__main__':
    app.run(debug=True)