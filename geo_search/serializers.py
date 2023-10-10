from rest_framework import serializers
from .models import Location,Country


class SearchSerializer(serializers.Serializer):
    location = serializers.CharField(required=True)
    keywords = serializers.CharField(required=True)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True)  # Assuming LocationSerializer is correctly defined

    class Meta:
        model = Country
        fields = ['id', 'name', 'locations']
