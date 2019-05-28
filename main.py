from flask import Flask, render_template
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
    return render_template('index.html')


@celery.task(name='main.runner')
def runner():
    MotorRunner()


if __name__ == '__main__':
    app.run()
