import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Настройки почты (лучше использовать переменные окружения, но для теста оставим здесь)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sploispy@gmail.com'
app.config['MAIL_PASSWORD'] = 'drunroobepjsqvcb'

mail = Mail(app)

# Настройки БД
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Создание таблиц
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        # Проверяем, есть ли такой пользователь
        if User.query.filter_by(email=email).first():
            return "Этот email уже зарегистрирован!"
        
        new_user = User(
            email=email,
            username=request.form.get('username'),
            password=request.form.get('password')
        )
        db.session.add(new_user)
        db.session.commit()
        return "Регистрация успешна! <a href='/login'>Войти</a>"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.password == request.form.get('password'):
            session['email'] = user.email
            return redirect(url_for('cabinet'))
        return "Неверный email или пароль. <a href='/login'>Назад</a>"
    return render_template('login.html')

@app.route('/cabinet')
def cabinet():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return f"Привет, {user.username}! Ты в кабинете. <a href='/logout'>Выйти</a>"
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            msg = Message("Ваш пароль", sender=app.config['MAIL_USERNAME'], recipients=[user.email])
            msg.body = f"Ваш пароль: {user.password}"
            mail.send(msg)
            return "Письмо отправлено!"
        return "Email не найден."
    return '<form method="POST"><input name="email" required><button>Отправить пароль</button></form>'

if __name__ == '__main__':
    app.run()
