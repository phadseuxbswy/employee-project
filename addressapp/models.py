from django.db import models

class Province(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.IntegerField(unique=True)
    name_th = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name_th

class District(models.Model):
    id = models.IntegerField(primary_key=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts', to_field='code', db_column='province_code')
    code = models.IntegerField(unique=True)
    name_th = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name_th

class Subdistrict(models.Model):
    id = models.IntegerField(primary_key=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='subdistricts', to_field='code', db_column='district_code')
    code = models.IntegerField(unique=True)
    name_th = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150, null=True, blank=True)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name_th} ({self.zip_code})"