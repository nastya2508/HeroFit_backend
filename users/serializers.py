from rest_framework import serializers
from .models import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    video_id = serializers.ReadOnlyField()

    class Meta:
        model = Exercise
        fields = [
            'id', 
            'title', 
            'description', 
            'video_url', 
            'video_id', 
            'points_reward', 
            'difficulty'
        ]