"""
fix_encoding.py - แก้ภาษาไทยเพี้ยนในไฟล์ page.tsx
วิธีใช้: ดับเบิลคลิกที่ไฟล์นี้ หรือรัน: python fix_encoding.py
"""

import pathlib, shutil

TARGET_FILES = [
    r"frontend\src\app\page.tsx",
    r"frontend\src\app\login\page.tsx",
]

BASE = pathlib.Path(__file__).parent

def fix_file(filepath):
    f = BASE / filepath
    if not f.exists():
        print(f"  ⚠️  ไม่พบไฟล์: {filepath}")
        return False

    # Backup
    bak = f.with_suffix(".tsx.bak")
    shutil.copy2(f, bak)

    raw = f.read_bytes()
    # ลบ UTF-8 BOM ถ้ามี
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    # Decode ของที่ corrupt แล้ว (UTF-8 ของ cp1252 ที่อ่านผิด)
    text = raw.decode('utf-8', errors='replace')

    # -------- Reverse encoding --------
    # แต่ละตัวอักษร: ถ้า <= U+00FF → map กลับเป็น byte ตรงๆ (latin-1)
    # ถ้า > U+00FF → encode เป็น cp1252 (สำหรับ €, Ÿ, œ, ...)
    # ถ้า encode ไม่ได้ → แทนด้วย ? (ตัวอักษรที่ .NET ทำลายไปแล้ว)
    result_bytes = bytearray()
    for ch in text:
        cp = ord(ch)
        if cp <= 0xFF:
            result_bytes.append(cp)          # latin-1 direct map
        else:
            try:
                b = ch.encode('cp1252')
                result_bytes.extend(b)       # cp1252 special range
            except (UnicodeEncodeError, LookupError):
                result_bytes.append(0x3F)    # '?' fallback

    # Decode กลับเป็น UTF-8 = ภาษาไทยที่ถูกต้อง
    try:
        fixed = result_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  ❌ Decode ล้มเหลว: {e}")
        shutil.copy2(bak, f)
        return False

    f.write_text(fixed, encoding='utf-8', newline='\n')
    print(f"  ✅ แก้สำเร็จ: {filepath}")
    return True


print("")
print("=== แก้ encoding ภาษาไทย ===")
print("")
ok = 0
for rel in TARGET_FILES:
    if fix_file(rel):
        ok += 1

print("")
if ok == len(TARGET_FILES):
    print("✅ เสร็จสิ้น! รีเฟรช browser ได้เลยครับ")
else:
    print(f"แก้สำเร็จ {ok}/{len(TARGET_FILES)} ไฟล์")
    print("ไฟล์ backup (.bak) ถูกเก็บไว้")

input("\nกด Enter เพื่อปิด...")
