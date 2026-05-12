from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from django.contrib.auth.models import User
from django.http import HttpResponse

# Додали Notification в імпорт моделей
from .models import (
    Profile, Exercise, CompletedExercise, Hero, 
    UserActivity, Achievement, UserAchievement, Item, Inventory, Notification, Team
)
# ДОДАНО ItemSerializer
from .serializers import ExerciseSerializer, RegisterSerializer, ItemSerializer

# --- НОВИЙ КОД: Реєстрація з вибором типу тіла ---
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Користувача успішно створено!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [] 

# --- НОВИЙ КОД: Список товарів для магазину ---
class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [] 

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        hero = profile.hero
        
        # --- НОВИЙ КОД: Перевірка на лінь і зміна тіла ---
        # Спочатку перевіряємо, чи зміниться здоров'я
        old_hp = profile.hp
        profile.check_health() 
        
        # Якщо здоров'я зменшилося (штраф за лінь) і герой не пухлий
        if profile.hp < old_hp and hero.body_type != 'PLUMP':
            hero.body_type = 'PLUMP'
            hero.image_url = 'image_10.png'
            hero.save()
            Notification.objects.create(
                user=request.user,
                title="⚠️ Ваш персонаж змінився!",
                message="Ой! Ви давно не займалися. Ваш персонаж набрав вагу. Поверніться до тренувань, щоб відновити форму!"
            )
        
        return Response({
            "username": request.user.username,
            "hp": profile.hp,
            "level": profile.level,
            "fire_points": profile.fire_points,
            "total_exercises": profile.total_exercises,
            "epic_level": profile.epic_level,
            "streak_days": profile.streak_days,
            "hero": {
                "name": hero.name,
                "strength": hero.strength,
                "stamina": hero.stamina,
                "body_type": hero.body_type,      # Додано для фронтенду
                "image_url": hero.image_url       # Додано для фронтенду
            }
        })

# Функція перевірки ачивок + СПОВІЩЕННЯ
def check_achievements(user):
    profile = user.profile
    unlocked_ids = user.achievements.values_list('achievement_id', flat=True)
    potential_achievements = Achievement.objects.exclude(id__in=unlocked_ids)

    for ach in potential_achievements:
        is_unlocked = False
        if ach.requirement_type == 'xp' and profile.fire_points >= ach.requirement_value:
            is_unlocked = True
        elif ach.requirement_type == 'streak' and profile.streak_days >= ach.requirement_value:
            is_unlocked = True
        elif ach.requirement_type == 'exercises' and profile.total_exercises >= ach.requirement_value:
            is_unlocked = True

        if is_unlocked:
            UserAchievement.objects.create(user=user, achievement=ach)
            # --- Створюємо сповіщення про нову нагороду ---
            Notification.objects.create(
                user=user,
                title="🏆 Нова ачивка!",
                message=f"Вітаємо! Ви розблокували нагороду: {ach.name}"
            )

class CompleteExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            exercise = Exercise.objects.get(pk=pk)
            user = request.user
            profile = user.profile
            hero = profile.hero

            CompletedExercise.objects.create(user=user, exercise=exercise)
            UserActivity.objects.create(user=user, exercise_name=exercise.title, xp_gained=exercise.points_reward)

            profile.fire_points += exercise.points_reward
            profile.total_exercises += 1
            profile.save()

            hero.strength += 2
            hero.save()

            profile.update_streak() 
            check_achievements(user)
            
            # --- НОВИЙ КОД: Перевірка на накаченість або повернення у форму ---
            # Якщо стрік досяг 7 днів і герой ще не накачений
            if profile.streak_days >= 7 and hero.body_type != 'MUSCULAR':
                hero.body_type = 'MUSCULAR'
                hero.image_url = 'image_9.png'
                hero.save()
                Notification.objects.create(
                    user=user,
                    title="💪 Ви у чудовій формі!",
                    message="Чудова робота! Ваша регулярність дає плоди. Ви стали накаченим!"
                )
            # Якщо герой був пухким, але почав займатися, повертаємо його у звичайний стан
            elif profile.streak_days >= 1 and hero.body_type == 'PLUMP':
                hero.body_type = 'NORMAL'
                hero.image_url = 'image_11.png'
                hero.save()
                Notification.objects.create(
                    user=user,
                    title="🔥 Форма відновлюється!",
                    message="Ви повернулися до тренувань і скинули зайву вагу. Продовжуйте в тому ж дусі!"
                )

            return Response({
                "status": "success",
                "added_points": exercise.points_reward,
                "current_points": profile.fire_points, 
                "current_hp": profile.hp,
                "current_streak": profile.streak_days,
                "hero_image": hero.image_url # Повертаємо нову картинку, якщо вона змінилась
            }, status=status.HTTP_201_CREATED)

        except Exercise.DoesNotExist:
            return Response({"error": "Вправу не знайдено"}, status=status.HTTP_404_NOT_FOUND)

class PurchaseItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            item = Item.objects.get(pk=pk)
            profile = request.user.profile
            hero = profile.hero

            if profile.fire_points < item.price:
                return Response({"error": "Недостатньо вогняних балів!"}, status=status.HTTP_400_BAD_REQUEST)

            profile.fire_points -= item.price
            hero.strength += item.strength_bonus
            profile.hp = min(100, profile.hp + item.hp_bonus)
            
            # --- НОВИЙ КОД: Одягаємо костюм, якщо це скін ---
            if item.is_skin and item.skin_image_url:
                hero.image_url = item.skin_image_url

            profile.save()
            hero.save()

            Inventory.objects.create(user=request.user, item=item)

            # --- Створюємо сповіщення про покупку ---
            Notification.objects.create(
                user=request.user,
                title="🛍️ Покупка успішна",
                message=f"Ви придбали {item.name}. Бонуси активовані!"
            )

            return Response({
                "message": f"Ви купили {item.name}!",
                "remaining_points": profile.fire_points,
                "new_strength": hero.strength,
                "new_hp": profile.hp,
                "hero_image": hero.image_url # Відправляємо нову картинку на фронтенд
            }, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response({"error": "Предмет не знайдено"}, status=status.HTTP_404_NOT_FOUND)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notifications = request.user.notifications.all()[:20] 
        data = [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
        } for n in notifications]
        return Response(data)

class LeaderboardView(APIView):
    permission_classes = []

    def get(self, request):
        top_heroes = Hero.objects.select_related('profile__user').order_by('-strength')[:10]
        leaderboard_data = []
        for index, hero in enumerate(top_heroes):
            leaderboard_data.append({
                "rank": index + 1,
                "username": hero.profile.user.username,
                "strength": hero.strength,
                "level": hero.profile.level
            })
        return Response(leaderboard_data, status=status.HTTP_200_OK)
    
class CreateTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')
        
        if Team.objects.filter(name=name).exists():
            return Response({"error": "Команда з такою назвою вже існує"}, status=status.HTTP_400_BAD_REQUEST)

        team = Team.objects.create(
            name=name,
            description=description,
            captain=request.user
        )
        
        # Автоматично додаємо капітана в його ж команду
        profile = request.user.profile
        profile.team = team
        profile.save()

        return Response({"message": f"Команду '{name}' створено!", "team_id": team.id})

# Список команд для рейтингу
class TeamListView(APIView):
    def get(self, request):
        teams = Team.objects.all()
        # Сортуємо команди за їхнім спільним XP (через property або анотацію)
        sorted_teams = sorted(teams, key=lambda t: t.total_team_xp, reverse=True)
        
        data = [{
            "id": t.id,
            "name": t.name,
            "total_xp": t.total_team_xp,
            "members_count": t.members.count(),
            "captain": t.captain.username if t.captain else "Немає"
        } for t in sorted_teams]
        
        return Response(data)
    

def create_admin_once(request):
    if not User.objects.filter(username='nastya').exists():
        # ЗАМІНИ 'твій_пароль' на реальний пароль!
        User.objects.create_superuser('nastya', 'admin@example.com', 'твій_пароль')
        return HttpResponse("Адміна 'nastya' створено! Тепер видали цей код.")
    return HttpResponse("Адмін 'nastya' вже існує.")