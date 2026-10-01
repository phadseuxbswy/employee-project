let addressData = []; // เก็บข้อมูลทั้งหมดที่ดึงมาจาก API

const provinceSelect = document.getElementById('province');
const districtSelect = document.getElementById('district');
const subdistrictSelect = document.getElementById('subdistrict');
const zipcodeInput = document.getElementById('zipcode');

// 1. ดึงข้อมูลทันทีที่เปิดหน้าเว็บ
document.addEventListener('DOMContentLoaded', () => {
    // เรียก API ไปที่ Django ของเรา
    fetch('http://127.0.0.1:8000/api/address/provinces/')
        .then(response => response.json())
        .then(data => {
            addressData = data;
            // นำชื่อจังหวัดมาใส่ Dropdown
            addressData.forEach(province => {
                const option = document.createElement('option');
                option.value = province.id;
                option.textContent = province.name_th;
                provinceSelect.appendChild(option);
            });
        })
        .catch(error => console.error('ดึงข้อมูลไม่ได้:', error));
});

// 2. เมื่อเลือก "จังหวัด" -> ให้แสดง "อำเภอ"
provinceSelect.addEventListener('change', (e) => {
    const provinceId = parseInt(e.target.value);
    
    // เคลียร์ค่าอำเภอ, ตำบล, รหัสไปรษณีย์
    districtSelect.innerHTML = '<option value="">-- เลือกอำเภอ --</option>';
    subdistrictSelect.innerHTML = '<option value="">-- เลือกตำบล --</option>';
    zipcodeInput.value = '';
    districtSelect.disabled = true;
    subdistrictSelect.disabled = true;
    
    if (provinceId) {
        // ค้นหาข้อมูลจังหวัดที่เลือก
        const selectedProvince = addressData.find(p => p.id === provinceId);
        
        // นำข้อมูลอำเภอมาใส่
        selectedProvince.districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district.id;
            option.textContent = district.name_th;
            districtSelect.appendChild(option);
        });
        districtSelect.disabled = false; // ปลดล็อกช่องอำเภอ
    }
});

// 3. เมื่อเลือก "อำเภอ" -> ให้แสดง "ตำบล"
districtSelect.addEventListener('change', (e) => {
    const provinceId = parseInt(provinceSelect.value);
    const districtId = parseInt(e.target.value);
    
    subdistrictSelect.innerHTML = '<option value="">-- เลือกตำบล --</option>';
    zipcodeInput.value = '';
    subdistrictSelect.disabled = true;

    if (districtId) {
        const selectedProvince = addressData.find(p => p.id === provinceId);
        const selectedDistrict = selectedProvince.districts.find(d => d.id === districtId);
        
        selectedDistrict.subdistricts.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.id;
            option.textContent = sub.name_th;
            option.setAttribute('data-zip', sub.zip_code); // ซ่อนรหัสไปรษณีย์ไว้
            subdistrictSelect.appendChild(option);
        });
        subdistrictSelect.disabled = false; // ปลดล็อกช่องตำบล
    }
});

// 4. เมื่อเลือก "ตำบล" -> ให้แสดง "รหัสไปรษณีย์"
subdistrictSelect.addEventListener('change', (e) => {
    const selectedOption = e.target.options[e.target.selectedIndex];
    if (selectedOption.value) {
        zipcodeInput.value = selectedOption.getAttribute('data-zip');
    } else {
        zipcodeInput.value = '';
    }
});