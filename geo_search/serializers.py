from rest_framework import serializers
from .models import Location


class SearchSerializer(serializers.Serializer):
    location = serializers.CharField(required=True)
    keywords = serializers.CharField(required=True)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'