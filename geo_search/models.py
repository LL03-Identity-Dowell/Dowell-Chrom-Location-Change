from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255,default=None)  # Name of the location (e.g., "New York City")
    latitude = models.FloatField(default=None)           # Latitude coordinate
    longitude = models.FloatField(default=None)          # Longitude coordinate

    def __str__(self):
        return self.name