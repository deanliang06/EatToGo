from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Task

@shared_task(bind=True, name="scrape_restaurant_task", max_retries=7*24)
def scrape_restaurant_task(self, restaurant_url):
    from .scraper import scrapeURL

    job, _ = Task.objects.get_or_create(task_id=self.request.id)
    results = scrapeURL(job, restaurant_url)
    # if not results:
    #     nextHour = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    #     self.retry(
    #         countdown=60*60,
    #         eta=nextHour
    #     )
    return {"hour": 24, "day_dif": 24}
