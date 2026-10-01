import json
import os
from django.core.management.base import BaseCommand
from addressapp.models import Province, District, Subdistrict

class Command(BaseCommand):
    help = 'Import Thailand geography data from JSON files into SQLite database'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join('addressapp', 'data')

        # 1. นำเข้าข้อมูลจังหวัด (Provinces)
        province_file = os.path.join(data_dir, 'provinces.json')
        if os.path.exists(province_file):
            with open(province_file, 'r', encoding='utf-8') as f:
                provinces_data = json.load(f)
                for p in provinces_data:
                    Province.objects.update_or_create(
                        id=p.get('id'),
                        defaults={
                            'code': p.get('provinceCode'),
                            'name_th': p.get('provinceNameTh'),
                            'name_en': p.get('provinceNameEn')
                        }
                    )
            self.stdout.write(self.style.SUCCESS('✅ นำเข้าข้อมูลจังหวัด (Provinces) สำเร็จ!'))

        # 2. นำเข้าข้อมูลอำเภอ/เขต (Districts)
        district_file = os.path.join(data_dir, 'districts.json')
        if os.path.exists(district_file):
            with open(district_file, 'r', encoding='utf-8') as f:
                districts_data = json.load(f)
                for d in districts_data:
                    District.objects.update_or_create(
                        id=d.get('id'),
                        defaults={
                            'province_id': d.get('provinceCode'),
                            'code': d.get('districtCode'),
                            'name_th': d.get('districtNameTh'),
                            'name_en': d.get('districtNameEn')
                        }
                    )
            self.stdout.write(self.style.SUCCESS('✅ นำเข้าข้อมูลอำเภอ (Districts) สำเร็จ!'))

        # 3. นำเข้าข้อมูลตำบล/แขวง (Subdistricts)
        subdistrict_file = os.path.join(data_dir, 'subdistricts.json')
        if os.path.exists(subdistrict_file):
            with open(subdistrict_file, 'r', encoding='utf-8') as f:
                subdistricts_data = json.load(f)
                for s in subdistricts_data:
                    Subdistrict.objects.update_or_create(
                        id=s.get('id'),
                        defaults={
                            'district_id': s.get('districtCode'),
                            'code': s.get('subdistrictCode'),
                            'name_th': s.get('subdistrictNameTh'),
                            'name_en': s.get('subdistrictNameEn'),
                            'zip_code': str(s.get('postalCode', ''))
                        }
                    )
            self.stdout.write(self.style.SUCCESS('✅ นำเข้าข้อมูลตำบลและรหัสไปรษณีย์ (Subdistricts) สำเร็จ!'))

        self.stdout.write(self.style.SUCCESS('🎉 ข้อมูลที่อยู่ทั้งหมดถูกบันทึกลงฐานข้อมูลเรียบร้อยแล้ว!'))