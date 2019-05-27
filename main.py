from flask import Flask
from tasks import make_celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)


@app.route('/process/<name>')
def process(name):
    reverse.delay(name)
    return "request sent"


@celery.task(name='main.reverse')
def reverse(string):
    return string[::-1]


if __name__ == '__main__':
    app.run()
