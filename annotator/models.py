from django.conf import settings
from django.db import models

# Create your models here.
class Sentence(models.Model):
    source_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()

class Annotation(models.Model):
    annotator = models.ForeignKey(settings.AUTH_USER_MODEL)
    sentence = models.ForeignKey('Sentence')
    positions = models.CommaSeparatedIntegerField(max_length=500)

class Task(models.Model):
    annotator = models.ForeignKey(settings.AUTH_USER_MODEL)
    sentence = models.ForeignKey('Sentence')
    done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('annotator', 'sentence',)

class SingleConnective(models.Model):
    text = models.CharField(max_length=100, unique=True)

class PairConnective(models.Model):
    first_half = models.CharField(max_length=100)
    second_half = models.CharField(max_length=100)

    class Meta:
        unique_together = ('first_half', 'second_half',)
