from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, default=None)  # Name of the location (e.g., "New York City")
    latitude = models.FloatField(default=None)  # Latitude coordinate
    longitude = models.FloatField(default=None)  # Longitude coordinate
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='locations')

    def __str__(self):
        return self.name
