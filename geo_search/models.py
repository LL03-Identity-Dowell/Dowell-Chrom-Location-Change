from django.db import models

class Location(models.Model):
    city = models.CharField(max_length=255, null=True)
    languages = models.CharField(max_length=255,null=True)  # You can also use a ManyToManyField if you expect multiple languages
    language_abbreviations = models.CharField(max_length=255,null=True)  # You can also use a ManyToManyField if you expect multiple abbreviations
    state = models.CharField(max_length=255,null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return self.city