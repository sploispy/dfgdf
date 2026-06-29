import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Настройки почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sploispy@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/cabinet')
def cabinet():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        # Важно: используем render_template для отображения cabinet.html
        return render_template('cabinet.html', username=user.username)
    return redirect(url_for('login'))

@app.route('/submit-request', methods=['POST'])
def submit_request():
    problem = request.form.get('problem')
    payment = request.form.get('payment_method')
    user_email = session.get('email', 'Гость')
    try:
        msg = Message("Новая заявка IT-HELP", sender=app.config['MAIL_USERNAME'], recipients=['sploispy@gmail.com'])
        msg.body = f"Пользователь: {user_email}\nПроблема: {problem}\nМетод оплаты: {payment}\nСвязаться: +7 778 693 25 74 / +7 778 676 6600"
        mail.send(msg)
        return redirect(url_for('payment_wait'))
    except Exception as e:
        return f"Ошибка: {str(e)}"

@app.route('/payment-wait')
def payment_wait():
    return render_template('wait.html')

# (Остальные маршруты: /, /register, /login, /logout, /forgot-password)
if __name__ == '__main__':
    app.run()
