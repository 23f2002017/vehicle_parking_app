from celery import Celery, Task

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app = Celery(
        app.name, 
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/1",
        timezone='Asia/Kolkata',
        task_cls=FlaskTask
    )
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app 