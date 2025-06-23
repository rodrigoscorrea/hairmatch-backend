from rest_framework import serializers
from .models import Preferences

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = ['id', 'name', 'picture']

class PreferencesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = ['name']