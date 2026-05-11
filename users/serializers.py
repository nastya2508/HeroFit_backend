from rest_framework import serializers
from django.contrib.auth.models import User
# Додано Item в імпорти
from .models import Exercise, Hero, Profile, Item

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

# --- НОВИЙ КОД: Серіалізатор для Героя ---
class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = ['name', 'strength', 'stamina', 'intelligence', 'body_type', 'image_url']

# --- НОВИЙ КОД: Серіалізатор для Реєстрації з вибором форми тіла ---
class RegisterSerializer(serializers.ModelSerializer):
    # Поле для вибору типу тіла при реєстрації (фронтенд має передати 'NORMAL', 'MUSCULAR' або 'PLUMP')
    body_type = serializers.ChoiceField(choices=Hero.BODY_TYPE_CHOICES, write_only=True, default='NORMAL')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'body_type']

    def create(self, validated_data):
        body_type = validated_data.pop('body_type')
        
        # Створюємо базового користувача
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # Герой вже створився автоматично через твої сигнали в models.py!
        # Нам треба лише оновити йому тип тіла і призначити правильну картинку:
        hero = user.profile.hero
        hero.body_type = body_type
        
        if body_type == 'MUSCULAR':
            hero.image_url = 'image_9.png'  # Накачений
        elif body_type == 'PLUMP':
            hero.image_url = 'image_10.png' # Пухлий
        else:
            hero.image_url = 'image_11.png' # Звичайний
            
        hero.save()
        return user

# --- Серіалізатор для товарів винесено на правильний рівень (без зайвих відступів) ---
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'icon', 'is_skin', 'skin_image_url', 'strength_bonus', 'hp_bonus']