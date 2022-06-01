from rest_framework import serializers

from analyze.models import Event


class EventSerializer(serializers.ModelSerializer):

    name = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = Event
        fields = ('name',)
