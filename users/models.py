from django.db import models
import urllib.parse as urlparse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import math
from django.utils import timezone
from datetime import timedelta

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва команди")
    description = models.TextField(blank=True, verbose_name="Опис команди")
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captain_of')
    logo_icon = models.CharField(max_length=50, default="🛡️")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_team_xp(self):
        # Рахуємо суму fire_points усіх учасників команди
        return sum(member.fire_points for member in self.members.all())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=1)
    hp = models.IntegerField(default=100)
    fire_points = models.IntegerField(default=0)
    total_exercises = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    avatar_image = models.URLField(null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    @property
    def epic_level(self):
        f, ex, d = self.fire_points, self.total_exercises, self.streak_days
        if f == 0 or ex == 0: return 1
        return round(math.sqrt(f * ex) * (1 + math.log10(d + 1)), 2)

    def update_streak(self):
        last_activity = self.user.activities.order_by('-created_at').first()
        if not last_activity:
            self.streak_days = 1
        else:
            today = timezone.now().date()
            last_date = last_activity.created_at.date()
            if last_date == today:
                pass
            elif last_date == today - timedelta(days=1):
                self.streak_days += 1
            else:
                self.streak_days = 1
        self.save()

    def save(self, *args, **kwargs):
        new_level = (self.fire_points // 200) + 1
        if new_level > self.level:
            self.level = new_level
            self.hp = 100 
        super().save(*args, **kwargs)

    def check_health(self):
        """Перевірка на занедбаність: якщо пропуск > 2 днів, знімаємо HP"""
        last_activity = self.user.activities.order_by('-created_at').first()
        
        if last_activity:
            now = timezone.now()
            diff = now - last_activity.created_at
            
            if diff > timedelta(hours=48):
                days_missed = diff.days
                penalty = days_missed * 10 
                self.hp = max(0, self.hp - penalty)
                self.save()    

class Hero(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='hero')
    name = models.CharField(max_length=100, default="Мій Герой")
    strength = models.IntegerField(default=10)   
    stamina = models.IntegerField(default=10)    
    intelligence = models.IntegerField(default=10) 
    
    def __str__(self):
        return f"Герой: {self.name} (Власник: {self.profile.user.username})"

# Сигнали
@receiver(post_save, sender=Profile)
def create_hero(sender, instance, created, **kwargs):
    if created:
        Hero.objects.create(profile=instance)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Exercise(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()
    points_reward = models.IntegerField(default=50)
    difficulty = models.CharField(max_length=50, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])

    @property
    def video_id(self):
        url_data = urlparse.urlparse(self.video_url)
        query = urlparse.parse_qs(url_data.query)
        video = query.get("v")
        if video:
            return video[0]
        return None

    def __str__(self):
        return self.title

class CompletedExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    date_completed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} виконав {self.exercise.title}"

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    exercise_name = models.CharField(max_length=255, verbose_name="Назва вправи")
    xp_gained = models.IntegerField(verbose_name="Отримано XP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата та час")

    class Meta:
        verbose_name = "Активність користувача"
        verbose_name_plural = "Історія активностей"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} (+{self.xp_gained} XP) - {self.exercise_name}"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="🏆")
    requirement_type = models.CharField(max_length=50) 
    requirement_value = models.IntegerField()

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_unlocked = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} отримав {self.achievement.name}"


class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва предмета")
    description = models.TextField(verbose_name="Опис")
    price = models.IntegerField(default=100, verbose_name="Ціна (Fire Points)")
    strength_bonus = models.IntegerField(default=0, verbose_name="Бонус до сили")
    hp_bonus = models.IntegerField(default=0, verbose_name="Бонус до здоров'я")
    icon = models.CharField(max_length=50, default="🛡️")

    def __str__(self):
        return f"{self.name} ({self.price} FP)"

class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Інвентар"
        verbose_name_plural = "Інвентарі користувачів"

    def __str__(self):
        return f"{self.user.username} має {self.item.name}"
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Текст повідомлення")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Сповіщення для {self.user.username}: {self.title}"    