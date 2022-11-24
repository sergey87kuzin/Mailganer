import sys
from celery import Celery
from celery.schedules import crontab

app = Celery('celery_tasks', include=['mail_service'])

app.conf.beat_schedule = {
   'monday-statistics-email': {
       'task': 'mail_service.mailing_list',
       'schedule': crontab(day_of_week=int(sys.argv[2]), hour=7),
   },
}
