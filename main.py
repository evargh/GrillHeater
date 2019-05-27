from flask import Flask
from tasks import make_celery, MotorRunner

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)


@app.route('/')
def index():
    runner.delay()
    return 'cool stuff'


@celery.task(name='main.runner')
def runner():
    MotorRunner()
    return


if __name__ == '__main__':
    app.run()
