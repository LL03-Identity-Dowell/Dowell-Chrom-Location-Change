from rest_framework import serializers


class SearchSerializer(serializers.Serializer):
    location = serializers.CharField(required=True)
    keywords = serializers.CharField(required=True)

