from django.db import models
import time

# Create your models here.
class Task(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    results = models.JSONField(null=True, blank=True)

    def addResult(self, result):
        resultsList = list(self.results if self.results else [])
        resultsList.append(result)
        self.results = resultsList
        self.save(update_fields=['results'])


    def __str__(self):
        return f"Task {self.task_id} - Status: {self.status}"

class ScrapeResult(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='scrape_task')
    timeOfAccess = models.BigIntegerField(default=int(time.time())) 
    latestTime = models.BigIntegerField(default=int(time.time()))