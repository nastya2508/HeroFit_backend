from django.db import models
import urllib.parse as urlparse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import math

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=1)
    hp = models.IntegerField(default=100)
    fire_points = models.IntegerField(default=0)
    total_exercises = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    avatar_image = models.URLField(null=True, blank=True)

    @property
    def epic_level(self):
        f, ex, d = self.fire_points, self.total_exercises, self.streak_days
        if f == 0 or ex == 0: return 1
        return round(math.sqrt(f * ex) * (1 + math.log10(d + 1)), 2)

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

    # метод для отримання ID відео
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