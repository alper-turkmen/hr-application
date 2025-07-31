from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityTypeViewSet, StatusViewSet, CandidateFlowViewSet, ActivityViewSet

router = DefaultRouter()
router.register(r'activity-types', ActivityTypeViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'candidate-flows', CandidateFlowViewSet)
router.register(r'activities', ActivityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]