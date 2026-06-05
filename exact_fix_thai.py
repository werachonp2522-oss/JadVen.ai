import pathlib

file_path = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")

with open(file_path, "rb") as f:
    raw_bytes = f.read()

try:
    # Try decoding assuming the bytes were valid windows-874 but interpreted as utf-8
    # Wait, if they were SAVED as utf-8 (so a single windows-874 byte became a 2-byte utf-8 sequence),
    # meaning the original bytes are now lost in utf-8 translation?
    # Let's check how "เธญเธฑเธ›" is encoded.
    
    # If the file was saved as UTF-8 from an editor that read Windows-874 bytes as Latin-1 or similar:
    text_utf8 = raw_bytes.decode('utf-8')
    # Can we fix it?
    # Actually, the string "เธญเธฑเธ›" is composed of Thai characters in UTF-8.
    # It seems the editor read the original TIS-620 bytes as MacThai or Latin-1, and saved them as UTF-8 representations of those Latin-1 chars.
    
    # Let's inspect the first replacement simply
    pass
except Exception as e:
    print(e)

# But wait, looking at the string: "เธญเธฑเธ›เน€เธ”เธ•"
print("Length of test string:", len("เธญเธฑเธ›เน€เธ”เธ•"))
# If we encode this to latin1, do we get the original tis-620 bytes?
try:
    test_str = "เธญเธฑเธ›เน€เธ”เธ•"
    # This might mean it was decoded as window-1252 instead of tis-620
    b = test_str.encode('windows-1252')
    print("Decoded as tis-620:", b.decode('tis-620'))
except Exception as e:
    print("Cannot reverse via windows-1252:", e)

try:
    test_str = "เธญเธฑเธ›เน€เธ”เธ•"
    b = test_str.encode('latin1')
    print("Decoded as tis-620 from latin1:", b.decode('tis-620'))
except Exception as e:
    print("Cannot reverse via latin1:", e)

# What if it's CP874 -> UTF-8 without conversion? No, "เธ" is a valid Thai character.
# This happens when TIS-620 bytes are interpreted as Windows-1252, and then saved as UTF-8.
# But "เธ" is Thai... wait.
# TIS-620 'อ' is 0xCD.
# In MacThai, 0xCD is 'เ'.
# Wait, let's just make a targeted script that replaces these EXACT mangled strings with the correct ones. That is the safest bet!

replaces = [
    ("showToast('เธญเธฑเธ›เน€เธ”เธ•เน‚เธ›เธฃเน„เธŸเธฅเนŒเธชเธณเน€เธฃเน‡เธˆ โœ…', 'success')", "showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success')"),
    ("showToast(data.detail || 'เน€เธ เธดเธ”เธ‚เน‰เธญเธœเธดเธ”เธžเธฅเธฒเธ”', 'error')", "showToast(data.detail || 'เกิดข้อผิดพลาด', 'error')"),
    ("showToast('เน„เธกเนˆเธชเธฒเธกเธฒเธฃเธ–เน€เธŠเธทเนˆเธญเธกเธ•เนˆเธญ Server', 'error')", "showToast('ไม่สามารถเชื่อมต่อ Server', 'error')"),
    ("showToast('เธฃเธซเธฑเธชเธœเนˆเธฒเธ™เนƒเธซเธกเนˆเน„เธกเนˆเธ•เธฃเธ‡เธ เธฑเธ™', 'error')", "showToast('รหัสผ่านใหม่ไม่ตรงกัน', 'error')"),
    ("showToast('เน€เธ›เธฅเธตเนˆเธขเธ™เธฃเธซเธฑเธชเธœเนˆเธฒเธ™เธชเธณเน€เธฃเน‡เธˆ โœ…', 'success')", "showToast('เปลี่ยนรหัสผ่านสำเร็จ ✅', 'success')"),
    ("text: 'เน„เธกเนˆเธชเธฒเธกเธฒเธฃเธ–เน€เธŠเธทเนˆเธญเธกเธ•เนˆเธญ AI เน„เธ”เน‰'", "text: 'ไม่สามารถเชื่อมต่อ AI ได้'"),
    ('label="เธ•เธฒเธฃเธฒเธ‡เน€เธงเธฃ (Schedule)"', 'label="ตารางเวร (Schedule)"'),
    ('label="เน เธ เน‰เธ›เธฑเธ เธซเธฒเธ เธฐเธ—เธฑเธ™เธซเธฑเธ™"', 'label="จัดการความขัดแย้ง (Conflict)"'),
    ('label="เธšเธธเธ„เธฅเธฒเธ เธฃ (Staff)"', 'label="บุคลากร (Staff)"'),
    ('label="เธ•เธฑเน‰เธ‡เธ„เนˆเธฒเธ เธŽ (Rule Builder)"', 'label="ตั้งค่ากฎ (Rule Builder)"'),
    ('label="เธ•เธฑเน‰เธ‡เธ„เนˆเธฒเธงเธญเธฃเนŒเธ” (Ward Config)"', 'label="ตั้งค่าวอร์ด (Ward Config)"'),
    ('label="เธงเธฑเธ™เธฅเธฒ (Leave)"', 'label="วันลา (Leave)"'),
    ('label="เน เธ”เธŠเธšเธญเธฃเนŒเธ” (Dashboard)"', 'label="แดชบอร์ด (Dashboard)"'),
    ('label="เธˆเธฑเธ”เธ เธฒเธฃเธœเธนเน‰เนƒเธŠเน‰ (Admin)"', 'label="จัดการผู้ใช้ (Admin)"'),
    ('label="เธ›เธ เธดเธ—เธดเธ™เน€เธงเธฃ (Calendar)"', 'label="ปฏิทินเวร (Calendar)"'),
    ('เธˆเธฑเธ”เธ เธฒเธฃเธ•เธฒเธฃเธฒเธ‡เน€เธงเธฃเธญเธฑเธˆเธ‰เธฃเธดเธขเธฐ (Smart Roster)', 'จัดการตารางเวรอัจฉริยะ (Smart Roster)'),
    ('เธฃเธฐเธšเธšเธˆเธฑเธ”เธ เธฒเธฃเธ„เธงเธฒเธกเธ‚เธฑเธ”เน เธขเน‰เธ‡ (AI-Conflict Solver)', 'ระบบจัดการความขัดแย้ง (AI-Conflict Solver)'),
    ('เธฃเธฒเธขเธŠเธทเนˆเธญเธšเธธเธ„เธฅเธฒเธ เธฃเธžเธขเธฒเธšเธฒเธฅ', 'รายชื่อบุคลากร (Staff)'),
    ('เธ•เธฑเธงเธชเธฃเน‰เธฒเธ‡เธ เธŽเธ„เธฃเธญเธšเธˆเธฑเธ เธฃเธงเธฒเธฅ (Universal Rule Builder)', 'ตั้งค่ากฎ (Universal Rule Builder)'),
    ('เธ•เธฑเน‰เธ‡เธ„เนˆเธฒเธ„เธงเธฒเธกเธ•เน‰เธญเธ‡เธ เธฒเธฃเธšเธธเธ„เธฅเธฒเธ เธฃเธ›เธฃเธฐเธˆเธณเธงเธญเธฃเนŒเธ”', 'ตั้งค่าวอร์ด (Ward Config)'),
    ('เธˆเธฑเธ”เธ เธฒเธฃเธงเธฑเธ™เธฅเธฒเธšเธธเธ„เธฅเธฒเธ เธฃ', 'จัดการวันลา (Leave)'),
    ('เน เธ”เธŠเธšเธญเธฃเนŒเธ”เธชเธ–เธดเธ•เธด', 'แดชบอร์ด (Dashboard)'),
    ('เธˆเธฑเธ”เธ เธฒเธฃเธœเธนเน‰เนƒเธŠเน‰เธ‡เธฒเธ™เธฃเธฐเธšเธš (Admin)', 'จัดการผู้ใช้ (Admin)'),
    ('เธ›เธ เธดเธ—เธดเธ™เธ•เธฒเธฃเธฒเธ‡เน€เธงเธฃ (Calendar)', 'ปฏิทินเวร (Calendar)')
]

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

changes = 0
for old, new in replaces:
    if old in text:
        text = text.replace(old, new)
        changes += 1
        
with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"✅ Replaced {changes} mangled strings successfully!")
