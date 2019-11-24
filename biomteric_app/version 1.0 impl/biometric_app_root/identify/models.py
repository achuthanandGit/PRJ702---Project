from django.db import models

# Create your models here.
class Identify(models.Model):
    imageId = models.IntegerField(primary_key=True)
    image = models.ImageField(upload_to='images/', blank=False)
    username = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    submitted = models.DateField(auto_now_add=True)
    population = models.CharField(max_length=100, blank=True)
    tank = models.CharField(max_length=100, blank=False)
    matchingImageId = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    pitTag = models.CharField(max_length=50, blank=True)
    def str(self):
        return str(self.imageId)

class FishData(models.Model):
    imageId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    imageUrl = models.ImageField(upload_to='dataset/', blank=True)
    spots = models.TextField(blank=True)
    refNose = models.TextField(blank=True)
    refHead = models.TextField(blank=True)
    refTail = models.TextField(blank=True)
    population = models.CharField(max_length=100, blank=True)
    tank = models.CharField(max_length=100, blank=False)
    date = models.CharField(max_length=50, blank=True)
    time = models.CharField(max_length=50, blank=True)
    baseTag = models.CharField(max_length=50, blank=True)
    pitTag = models.CharField(max_length=50, blank=True)
    report = models.CharField(max_length=50, blank=True)

    def str(self):
        return str(self.imageId)