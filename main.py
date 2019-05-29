from flask import Flask, render_template, request, url_for
from tasks import make_celery, MotorRunner
from flask_cors import CORS, cross_origin

import time

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
CORS(app)
celery = make_celery(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=['GET', 'POST'])
def index():
    targeto = 150
    if request.method == 'POST':
        targeto = request.get_json()
        runner.delay(targeto, time.time())
    return render_template('index.html',target=targeto)

@celery.task(name='main.runner')
def runner(targ, time):
    return MotorRunner(targ, time)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
