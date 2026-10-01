from rest_framework import viewsets
from .models import Province, District, Subdistrict
from .serializers import ProvinceSerializer, DistrictSerializer, SubdistrictSerializer

class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

class SubdistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subdistrict.objects.all()
    serializer_class = SubdistrictSerializer