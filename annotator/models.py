from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Annotator(AbstractUser):
    is_task_mode = models.BooleanField(default=False)

class Sentence(models.Model):
    source_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()

class Annotation(models.Model):
    annotator = models.ForeignKey(Annotator)
    sentence = models.ForeignKey('Sentence')
    positions = models.CommaSeparatedIntegerField(max_length=500)

class Task(models.Model):
    annotator = models.ForeignKey(Annotator)
    sentence = models.ForeignKey('Sentence')
    is_done = models.BooleanField(default=False)
    finished_times = models.CommaSeparatedIntegerField(max_length=500, blank=True, default='')

    class Meta:
        unique_together = ('annotator', 'sentence',)

class SingleConnective(models.Model):
    text = models.CharField(max_length=100, unique=True)

class PairConnective(models.Model):
    first_half = models.CharField(max_length=100)
    second_half = models.CharField(max_length=100)

    class Meta:
        unique_together = ('first_half', 'second_half',)
