from rest_framework import serializers
from .models import Province, District, Subdistrict

class SubdistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subdistrict
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    subdistricts = SubdistrictSerializer(many=True, read_only=True)
    
    class Meta:
        model = District
        fields = '__all__'

class ProvinceSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = Province
        fields = '__all__'