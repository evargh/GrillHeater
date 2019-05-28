from flask import Flask, render_template, request
from tasks import make_celery, MotorRunner

import time

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        targeto = request.get_json()
        runner.delay(int(float(targeto)), time.time())
        return render_template('index.html')
    else:
        return render_template('index.html')


@celery.task(name='main.runner')
def runner(targ, time):
    MotorRunner(targ, time)


if __name__ == '__main__':
    app.run()
