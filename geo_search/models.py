from django.db import models

class Location(models.Model):
    city = models.CharField(max_length=255, null=True)
    language = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='locations',default=None)
    state = models.CharField(max_length=255, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return self.city

class Language(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name