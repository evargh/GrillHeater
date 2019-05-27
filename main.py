from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from flask_celery import make_celery

from tasks import MotorRunner
from celery import Celery, current_task
from celery.result import AsyncResult

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = make_celery(app)


@app.route('/index', methods=['GET', 'POST'])
def index():
    runner.delay()
    return render_template('index.html')


@celery.task(name='tasks.MotorRunner')
def runner():
    MotorRunner()


if __name__ == '__main__':
    app.run()
