from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from celery import Celery
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

mail = Mail(app)

# Configuración de Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configuración de Redis
redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/')
def index():
    return render_template('index.html')


@celery.task
def send_email(recipient, subject, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)


@app.route('/send_recipe', methods=['POST'])
def send_recipe():
    if request.method == 'POST':
        recipe = request.form['recipe']
        recipient = request.form['recipient']
        subject = 'Receta'
        body = f'Aquí tienes la receta: {recipe}'

        # Guardar la receta en Redis
        redis_db.set('recipe', recipe)

        # Enviar la receta por correo electrónico usando Celery
        send_email.delay(recipient, subject, body)
        flash('Receta enviada por correo electrónico correctamente.', 'success')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
