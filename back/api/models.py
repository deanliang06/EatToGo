from django.db import models
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    results = models.JSONField(null=True, blank=True)

    def addResult(self, result):
        if self.results is None:
            self.results = []
        self.results.append(result)
        self.save()


    def __str__(self):
        return f"Task {self.task_id} - Status: {self.status}"

class ScrapeResult(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='scrape_task')
    timeOfAccess = models.TimeField(default=timezone.now)
    latestTime = models.TimeField(default=timezone.now)