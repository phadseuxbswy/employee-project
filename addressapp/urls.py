from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvinceViewSet, DistrictViewSet, SubdistrictViewSet

router = DefaultRouter()
router.register(r'provinces', ProvinceViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'subdistricts', SubdistrictViewSet)

urlpatterns = [
    path('', include(router.urls)),
]