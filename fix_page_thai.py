"""
fix_page_thai.py - แก้ภาษาไทยทั้งหมดใน page.tsx
รัน: python fix_page_thai.py (จาก folder d:\project_dev\JadVen.ai)
"""
import pathlib, shutil

f = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")
bak = f.with_suffix(".tsx.bak2")
shutil.copy2(f, bak)
print(f"Backup saved: {bak}")

text = f.read_text(encoding='utf-8')

# === รายการ corrections ทั้งหมด (wrong → correct) ===
FIXES = [
    # NavItem labels
    ('label="??•??²??£??²??เน€??§??£ (Schedule)"',       'label="ตารางเวร (Schedule)"'),
    ('label="??แ??ก??ัน??หา??กระ??ทั??หัด"',            'label="แก้ปัญหาขัดแย้ง"'),
    ('label="บุ??กลา??กร (Staff)"',                      'label="บุคลากร (Staff)"'),
    ('label="ตั??งกฎ (Rule Builder)"',                  'label="ตั้งกฎ (Rule Builder)"'),
    ('label="ตั??งค่าวอร์ด (Ward Config)"',             'label="ตั้งค่าวอร์ด (Ward Config)"'),
    ('label="วัน??ลา (Leave)"',                         'label="วันลา (Leave)"'),
    ('label="แดช??บอร์ด (Dashboard)"',                  'label="แดชบอร์ด (Dashboard)"'),
    ('label="จัด??การ??ผู้??ใช้ (Admin)"',              'label="จัดการผู้ใช้ (Admin)"'),
    ('label="ปฏิ??ทิน??เวร (Calendar)"',                'label="ปฏิทินเวร (Calendar)"'),

    # Sidebar role display
    ("? '🔴 Admin' : currentUser?.role === 'head_nurse' ? '🟢 Head Nurse' : '🔵 Nurse'",
     "? '🔴 Admin' : currentUser?.role === 'head_nurse' ? '🟢 Head Nurse' : '🔵 Nurse'"),
    ("' ?? '}{currentUser?.ward?.replace('??  ??  ??  ??   ', '') || 'ER'}",
     "' · '}{currentUser?.ward?.replace('แผนก ', '') || 'ER'}"),

    # Header titles
    ('"??จัดการตาราง??เวรอัจฉริยะ (Smart Roster)"',   '"จัดการตารางเวรอัจฉริยะ (Smart Roster)"'),
    ('"??ระบบจัดการ??ความขัดแย้ง (AI-Conflict Solver)"', '"ระบบจัดการความขัดแย้ง (AI-Conflict Solver)"'),
    ('"??รายชื่อบุคลากร??พยาบาล"',                     '"รายชื่อบุคลากรพยาบาล"'),
    ('"??ตัวสร้างกฎ??ครอบจักรวาล (Universal Rule Builder)"', '"ตัวสร้างกฎครอบจักรวาล (Universal Rule Builder)"'),
    ('"??ตั้งค่าความ??ต้องการ??บุคลากรประจำวอร์ด"',   '"ตั้งค่าความต้องการบุคลากรประจำวอร์ด"'),
    ('"??จัดการวันลา??บุคลากร"',                       '"จัดการวันลาบุคลากร"'),
    ('"??แดชบอร์ด??สถิติ"',                            '"แดชบอร์ดสถิติ"'),
    ('"??จัดการ??ผู้ใช้งาน??ระบบ (Admin)"',            '"จัดการผู้ใช้งานระบบ (Admin)"'),
    ('"??ปฏิทิน??ตาราง??เวร (Calendar)"',              '"ปฏิทินตารางเวร (Calendar)"'),

    # Profile modal
    ('showToast(\'????????\\u0000??\\u0000??\\u0000??\\u0000??\\u0000?????\\u0000??\\u0000?????\\u0000????????\\u0000?????\\u0000??\\u0000 ?\\u0000\\u0000\', \'success\')',
     "showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success')"),

    # Toast messages
    ("showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success')",  "showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success')"),
    ("showToast(data.detail || 'เกิดข้อผิดพลาด', 'error')",  "showToast(data.detail || 'เกิดข้อผิดพลาด', 'error')"),
    ("showToast('ไม่สามารถเชื่อมต่อ Server', 'error')",  "showToast('ไม่สามารถเชื่อมต่อ Server', 'error')"),
    ("showToast('เปลี่ยนรหัสผ่านสำเร็จ ✅', 'success')",  "showToast('เปลี่ยนรหัสผ่านสำเร็จ ✅', 'success')"),
    ("showToast('รหัสผ่านใหม่ไม่ตรงกัน', 'error')",  "showToast('รหัสผ่านใหม่ไม่ตรงกัน', 'error')"),
]

# ===== Simple ??-text replacements via exact string match =====
EXACT = {
    # === COMMON PATTERNS ===
    "????????????????????": "เข้าสู่ระบบไม่สำเร็จ",
    "????????????????????? Server ???": "ไม่สามารถเชื่อมต่อกับ Server ได้",
    "?????????????????????????????": "ระบบจัดตารางเวรพยาบาลอัจฉริยะ",
    "???????????": "เข้าสู่ระบบ",
    "??????????": "ชื่อผู้ใช้",
    "????????": "รหัสผ่าน",
    "????????????????...": "กำลังเข้าสู่ระบบ...",
    "??????????? ?": "เข้าสู่ระบบ →",
    "? ??????????": "🔑 บัญชีทดสอบ",
}

count = 0
for wrong, right in EXACT.items():
    if wrong in text:
        text = text.replace(wrong, right)
        count += 1
        print(f"✅ แก้: {wrong[:40]!r} → {right[:30]!r}")

print(f"\nแก้ไขได้ {count} รายการ")
print("กำลังบันทึก...")

f.write_text(text, encoding='utf-8')
print("✅ บันทึกเสร็จ!")
input("\nกด Enter เพื่อปิด...")
