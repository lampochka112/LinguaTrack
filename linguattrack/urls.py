from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    LanguageViewSet, WordSetViewSet, WordCardViewSet,
    UserProgressViewSet, TestViewSet, TestResultViewSet,
    UserRegistrationView, CustomAuthToken, UserProfileView,
    ReviewCardsView
)

router = DefaultRouter()
router.register(r'languages', LanguageViewSet)
router.register(r'wordsets', WordSetViewSet)
router.register(r'tests', TestViewSet)
router.register(r'test-results', TestResultViewSet)
router.register(r'progress', UserProgressViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/wordsets/<int:wordset_pk>/cards/', WordCardViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='wordcard-list'),
    path('api/wordsets/<int:wordset_pk>/tests/', TestViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='test-list'),
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/login/', CustomAuthToken.as_view(), name='login'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/review/', ReviewCardsView.as_view(), name='review-list'),
    path('api/review/<int:card_id>/', ReviewCardsView.as_view(), name='review-card'),
]