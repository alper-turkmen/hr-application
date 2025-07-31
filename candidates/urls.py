from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidateViewSet, EducationViewSet, WorkExperienceViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet)
router.register(r'educations', EducationViewSet)
router.register(r'work-experiences', WorkExperienceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]