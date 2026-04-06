from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profile

from .serializers import ExerciseSerializer
from .models import Exercise
from rest_framework import generics

class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [] # Поки що роблю відкритим, щоб фронтенд міг легко протестувати

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated] # Тільки залогінені бачать це

    def get(self, request):
        profile = request.user.profile
        return Response({
            "username": request.user.username,
            "hp": profile.hp,
            "level": profile.level,
            "fire_points": profile.fire_points,
            "epic_level": profile.epic_level # моя формула!
        })

