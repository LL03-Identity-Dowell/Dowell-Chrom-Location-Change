from rest_framework import serializers
from .models import Coordinates

class CoordinatesSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    def create(self, validated_data):
   
        return Coordinates.objects.create(**validated_data)