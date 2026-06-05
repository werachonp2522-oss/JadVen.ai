import pathlib
import re

file_path = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")

with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

# Safe regex pattern replacements.
# We will match the entire line and only replace the string literal if it matches.
# This avoids the catastrophic backtracking/looping issue from earlier.

lines = text.split("\n")
new_lines = []
changes = 0

for line in lines:
    orig = line
    
    # Toast profile success
    if "showToast(" in line and "'success'" in line and "updated" in line and "currentUser" in line:
        line = re.sub(r"showToast\('.*?', 'success'\)", "showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success')", line)
    
    # Toast error general
    elif "showToast(data.detail" in line and "'error'" in line:
         line = re.sub(r"showToast\(data\.detail.*?, 'error'\)", "showToast(data.detail || 'เกิดข้อผิดพลาด', 'error')", line)
         
    # Toast error server
    elif "catch" in orig.lower() and "showToast(" in line and "'error'" in line and "Server" in orig:
         line = re.sub(r"showToast\('.*?', 'error'\)", "showToast('ไม่สามารถเชื่อมต่อ Server', 'error')", line)

    # Toast new pw mismatch
    elif "pwForm.newPw" in line and "pwForm.confirm" in line and "showToast" in line:
         line = re.sub(r"showToast\('.*?', 'error'\)", "showToast('รหัสผ่านใหม่ไม่ตรงกัน', 'error')", line)

    # Toast pw success
    elif "pwForm.current" not in line and "pwForm.newPw" not in line and "showToast(" in line and "'success'" in line and "setPwForm" in line:
         line = re.sub(r"showToast\('.*?', 'success'\)", "showToast('เปลี่ยนรหัสผ่านสำเร็จ ✅', 'success')", line)

    # AI connection error
    elif "catch {" in line and "setAiMessages(" in line and "role: 'ai'" in line:
         line = re.sub(r"text: '.*?'", "text: 'ไม่สามารถเชื่อมต่อ AI ได้'", line)

    # Sidebar / Headings with anchors - using double quotes for labels
    elif 'label="' in line:
        if '(Schedule)' in line: line = re.sub(r'label=".*?"', 'label="ตารางเวร (Schedule)"', line)
        elif 'Conflict' in line or 'เธซเธฑเธ™' in line: line = re.sub(r'label=".*?"', 'label="จัดการความขัดแย้ง (Conflict)"', line)
        elif '(Staff)' in line: line = re.sub(r'label=".*?"', 'label="บุคลากร (Staff)"', line)
        elif '(Rule Builder)' in line: line = re.sub(r'label=".*?"', 'label="ตั้งค่ากฎ (Rule Builder)"', line)
        elif '(Ward Config)' in line: line = re.sub(r'label=".*?"', 'label="ตั้งค่าวอร์ด (Ward Config)"', line)
        elif '(Leave)' in line: line = re.sub(r'label=".*?"', 'label="วันลา (Leave)"', line)
        elif '(Dashboard)' in line: line = re.sub(r'label=".*?"', 'label="แดชบอร์ด (Dashboard)"', line)
        elif '(Admin)' in line: line = re.sub(r'label=".*?"', 'label="จัดการผู้ใช้ (Admin)"', line)
        elif '(Calendar)' in line: line = re.sub(r'label=".*?"', 'label="ปฏิทินเวร (Calendar)"', line)

    # Titles and other UI strings
    elif "(Smart Roster)" in line: line = re.sub(r'".*?\(Smart Roster\)"', '"จัดการตารางเวรอัจฉริยะ (Smart Roster)"', line)
    elif "(AI-Conflict Solver)" in line: line = re.sub(r'".*?\(AI-Conflict Solver\)"', '"ระบบจัดการความขัดแย้ง (AI-Conflict Solver)"', line)
    elif "activeTab === 'staff'" in line: line = re.sub(r'".*?"', '"รายชื่อบุคลากร (Staff)"', line)
    elif "(Universal Rule Builder)" in line: line = re.sub(r'".*?\(Universal Rule Builder\)"', '"ตั้งค่ากฎ (Universal Rule Builder)"', line)
    elif "activeTab === 'wardconfig'" in line: line = re.sub(r'".*?"', '"ตั้งค่าวอร์ด (Ward Config)"', line)
    elif "activeTab === 'leave'" in line: line = re.sub(r'".*?"', '"จัดการวันลา (Leave)"', line)
    elif "activeTab === 'dashboard'" in line: line = re.sub(r'".*?"', '"แดชบอร์ด (Dashboard)"', line)
    elif "(Admin)" in line and "h1" not in line and "nav" not in line: line = re.sub(r'".*?\(Admin\)"', '"จัดการผู้ใช้ (Admin)"', line)
    elif "activeTab === 'users'" in line: line = re.sub(r'"[\w\W]*?"', '"จัดการผู้ใช้งานระบบ (Admin)"', line)
    
    # Profile
    elif "User className=" in line:
        line = re.sub(r'</h3>', ' โปรไฟล์ของฉัน</h3>', re.sub(r'<User.*?/>.*?</h3', '<User className="h-5 w-5 text-brand-400" /></h3', line))
    elif "label className=" in line and "-" in line:
        line = re.sub(r'>.*?</label>', '>ชื่อ-นามสกุล</label>', line)
    elif "handleSaveProfile" in line and "disabled" in line:
        line = re.sub(r">.*?</button>", ">{profileSaving ? 'กำลังบันทึก...' : 'บันทึก'}</button>", line)
    
    # Passwords
    elif "<Key" in line:
        line = re.sub(r'</p>', ' เปลี่ยนรหัสผ่าน</p>', re.sub(r'<Key.*?/>.*?</p', '<Key className="h-4 w-4" /></p', line))
    elif "placeholder=" in line and "current" in line:
        line = re.sub(r'placeholder=".*?"', 'placeholder="รหัสผ่านปัจจุบัน"', line)
    elif "placeholder=" in line and "newPw" in line:
        line = re.sub(r'placeholder=".*?"', 'placeholder="รหัสผ่านใหม่ (อย่างน้อย 6 ตัว)"', line)
    elif "placeholder=" in line and "confirm" in line:
        line = re.sub(r'placeholder=".*?"', 'placeholder="ยืนยันรหัสผ่านใหม่"', line)
    elif "handleChangePassword" in line:
        line = re.sub(r">.*?</button>", ">{profileSaving ? 'กำลังบันทึก...' : 'เปลี่ยนรหัสผ่าน'}</button>", line)
        
    # AI Empty State
    elif "aiMessages.length === 0" in line:
        line = re.sub(r'>.*?</p>', '>ถามอะไรก็ได้เกี่ยวกับตารางเวร เช่น "ใครลงเวรดึกเยอะสุด?"</p>', line)
    elif "aiLoading &&" in line:
        line = re.sub(r'>.*?</div', '>กำลังคิด...</div', line)
    elif "aiInput" in line and "placeholder=" in line:
        line = re.sub(r'placeholder=".*?"', 'placeholder="พิมพ์คำถาม..."', line)

    if orig != line:
        changes += 1
    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

print(f"✅ Replaced {changes} lines successfully using safe context matching!")
