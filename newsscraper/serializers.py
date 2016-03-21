from rest_framework import serializers
from newsscraper.models import ScrapeTask


class ScrapeTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScrapeTask
        fields = 'task'
