from flask import Flask, render_template, request
from tasks import make_celery, MotorRunner

import time

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        targeto = request.get_json()
        runner.delay(targeto, time.time())
        return render_template('index.html',target=targeto)
    else:
        return render_template('index.html',target=150)

@celery.task(name='main.runner')
def runner(targ, time):
    return targ


if __name__ == '__main__':
    app.run()
