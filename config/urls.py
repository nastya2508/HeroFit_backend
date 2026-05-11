from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Додали нові View в імпорт
from users.views import (
    LeaderboardView, UserProfileView, ExerciseListView, 
    CompleteExerciseView, PurchaseItemView, NotificationListView,
    CreateTeamView, TeamListView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Логін та токени
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Профіль та вправи
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/exercises/', ExerciseListView.as_view(), name='exercise-list'),
    path('api/exercises/<int:pk>/complete/', CompleteExerciseView.as_view(), name='complete-exercise'),
    
    # Рейтинг (Лідерборд)
    path('api/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # Магазин та Предмети
    path('api/shop/purchase/<int:pk>/', PurchaseItemView.as_view(), name='purchase-item'),

    # Сповіщення
    path('api/notifications/', NotificationListView.as_view(), name='notifications'),

    # Команди (Клани)
    path('api/teams/create/', CreateTeamView.as_view(), name='create-team'),
    path('api/teams/list/', TeamListView.as_view(), name='team-list'),

    # Документація (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]