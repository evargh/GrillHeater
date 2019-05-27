from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

from GrillHeater import MotorRunner

from my_app.tasks import MotorRunner


app = Flask(__name__)

celery = make_celery(app)

@app.route('/index', methods=['GET', 'POST'])
def index():
    iterations = request.args.get('iterations', 1000)
    step = 10

    result = MotorRunner.delay_or_fail(
        target=150
    )
    return render_template('index.html', task_id=result.task_id)

if __name__ == '__main__':
    app.run()
