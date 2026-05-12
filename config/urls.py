from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Додали ItemListView в імпорт
from users.views import (
    RegisterView, LeaderboardView, UserProfileView, ExerciseListView, 
    CompleteExerciseView, PurchaseItemView, NotificationListView,
    CreateTeamView, TeamListView, ItemListView, create_admin_once
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Реєстрація
    path('api/register/', RegisterView.as_view(), name='register'),
    
    # Логін та токени
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Профіль та вправи
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/exercises/', ExerciseListView.as_view(), name='exercise-list'),
    path('api/exercises/<int:pk>/complete/', CompleteExerciseView.as_view(), name='complete-exercise'),
    
    # Рейтинг (Лідерборд)
    path('api/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # --- МАГАЗИН ---
    path('api/shop/items/', ItemListView.as_view(), name='item-list'), # Шлях до списку товарів
    path('api/shop/purchase/<int:pk>/', PurchaseItemView.as_view(), name='purchase-item'),

    # Сповіщення
    path('api/notifications/', NotificationListView.as_view(), name='notifications'),

    # Команди (Клани)
    path('api/teams/create/', CreateTeamView.as_view(), name='create-team'),
    path('api/teams/list/', TeamListView.as_view(), name='team-list'),

    # Документація (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


    # Цей шлях видає ОБИДВА токени при логіні
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Цей шлях видає НОВИЙ access токен, якщо ти даєш йому refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('create-admin-secret-link/', create_admin_once),
]