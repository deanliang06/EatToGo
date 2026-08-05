from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Task
import time

@shared_task(bind=True, name="scrape_restaurant_task", max_retries=7*24)
def restaurant_task(self, restaurant_url, reservationFor=None):
    from .scraper import scrapeTime, selectTime

    job, _ = Task.objects.get_or_create(task_id=self.request.id, reservationFor=reservationFor)
    results = {}
    
    if job.status == 'PENDING':
        results = scrapeTime(job, restaurant_url)
        if time.time() + int(results.get('dayDif', 0)) * 3600 * 24 > time.mktime(time.strptime(reservationFor, "%H:%M:%S %m/%d/%Y")):
            print("This executes right?")
            job.status = 'SCHEDUALED'
            job.save(update_fields=['status'])

    if job.status == 'SCHEDUALED':
        results = selectTime(job, restaurant_url, reservationFor)
        if results.get('done', False):
            job.status = 'COMPLETED'
            job.save(update_fields=['status'])

    if results.get("done", False) is False:
        nextHour = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        self.retry(
            countdown=60*60,
            eta=nextHour
        )

    return results
