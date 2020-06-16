from bothub.celery import app


@app.task()
def test_task():
    return True
