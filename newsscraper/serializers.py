from django.contrib.auth.models import User
from djcelery.models import TaskState
from rest_framework import serializers
from newsscraper.models import ScrapeTask


class TaskStateSerializer(serializers.ModelSerializer):

     class Meta:
         model = TaskState


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class ScrapeTaskSerializer(serializers.ModelSerializer):

    task = TaskStateSerializer()

    class Meta:
        model = ScrapeTask
        fields = ('task', )
