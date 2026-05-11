from django.contrib import admin
from .models import (
    Profile, Exercise, Hero, CompletedExercise, 
    UserActivity, Achievement, UserAchievement,
    Item, Inventory, Notification, Team # ДОДАЛИ Notification в імпорт
)

admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(Hero)                
admin.site.register(CompletedExercise)

# Реєстрація історії активності
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise_name', 'xp_gained', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('exercise_name', 'user__username')

# Реєстрація ачивок
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'requirement_type', 'requirement_value')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'date_unlocked')
    list_filter = ('date_unlocked', 'achievement')

# Реєстрація магазину та інвентарю
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'price', 'strength_bonus', 'hp_bonus')
    list_editable = ('price', 'strength_bonus', 'hp_bonus')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'purchased_at')
    list_filter = ('purchased_at', 'item')

# --- НОВЕ: РЕЄСТРАЦІЯ СПОВІЩЕНЬ ---

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Відображаємо заголовок, користувача, статус прочитання та дату
    list_display = ('title', 'user', 'is_read', 'created_at')
    # Додаємо можливість фільтрувати за статусом прочитання
    list_filter = ('is_read', 'created_at')
    # Пошук за заголовком або іменем користувача
    search_fields = ('title', 'user__username')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'captain', 'created_at')
    search_fields = ('name',)    