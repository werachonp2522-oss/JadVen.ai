"""
fix_all_thai.py - แก้ภาษาไทยใน page.tsx โดยใช้ English anchor text
รัน: python fix_all_thai.py (ใน terminal ของ VS Code)
"""
import re, pathlib, shutil

FILE = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")
bak = FILE.with_name("page.tsx.bak_v3")
shutil.copy2(FILE, bak)
print(f"Backup: {bak.name}")

text = FILE.read_text(encoding='utf-8')
original_len = len(text)

def fix(pattern, replacement, flags=0):
    global text
    new, n = re.subn(pattern, replacement, text, flags=flags)
    if n > 0:
        text = new
        print(f"  ✅ {n}x: {replacement[:60]}")
    return n

print("\n=== แก้ NavItem labels ===")
fix(r'label="[^"]+"(?=\s+isActive=\{activeTab === \'schedule\')', 'label="ตารางเวร (Schedule)"')
# simpler: จับจาก content ที่มี (X) ใน string
fix(r'label="[^"]*\(Schedule\)"', 'label="ตารางเวร (Schedule)"')
fix(r'label="[^"]*\(Staff\)"', 'label="บุคลากร (Staff)"')
fix(r'label="[^"]*\(Rule Builder\)"', 'label="ตั้งกฎ (Rule Builder)"')
fix(r'label="[^"]*\(Ward Config\)"', 'label="ตั้งค่าวอร์ด (Ward Config)"')
fix(r'label="[^"]*\(Leave\)"', 'label="วันลา (Leave)"')
fix(r'label="[^"]*\(Dashboard\)"', 'label="แดชบอร์ด (Dashboard)"')
fix(r'label="[^"]*\(Admin\)"', 'label="จัดการผู้ใช้ (Admin)"')
fix(r'label="[^"]*\(Calendar\)"', 'label="ปฏิทินเวร (Calendar)"')

print("\n=== แก้ Header titles ===")
fix(r'"[^"]*\(Smart Roster\)"', '"จัดการตารางเวรอัจฉริยะ (Smart Roster)"')
fix(r'"[^"]*\(AI-Conflict Solver\)"', '"ระบบจัดการความขัดแย้ง (AI-Conflict Solver)"')
fix(r'"[^"]*\(Universal Rule Builder\)"', '"ตัวสร้างกฎครอบจักรวาล (Universal Rule Builder)"')
fix(r'"[^"]*\(Calendar\)"', '"ปฏิทินตารางเวร (Calendar)"')
# Header for staff - match by activeTab condition
fix(r"(activeTab === 'staff' && \")[^\"]+\"", r'\1รายชื่อบุคลากรพยาบาล"')
fix(r"(activeTab === 'wardconfig' && \")[^\"]+\"", r'\1ตั้งค่าความต้องการบุคลากรประจำวอร์ด"')
fix(r"(activeTab === 'leave' && \")[^\"]+\"", r'\1จัดการวันลาบุคลากร"')
fix(r"(activeTab === 'dashboard' && \")[^\"]+\"", r'\1แดชบอร์ดสถิติ"')
fix(r"(activeTab === 'users' && \")[^\"]+\"", r'\1จัดการผู้ใช้งานระบบ (Admin)"')

print("\n=== แก้ Sidebar role/ward ===")
fix(r"'[^']*Admin[^']*'\s*:\s*currentUser\?\.role === 'head_nurse'", "'🔴 Admin' : currentUser?.role === 'head_nurse'")
fix(r"=== 'head_nurse' \? '[^']+' : '[^']+'", "=== 'head_nurse' ? '🟢 Head Nurse' : '🔵 Nurse'")
fix(r"title=\"[^\"]+\"(?=\s+className=\"p-1\.5 rounded-lg text-slate-400 hover:text-red-400)", 'title="ออกจากระบบ"')
fix(r"\.replace\('[^']*',\s*''\)(?=\s*\|\|\s*'ER')", ".replace('แผนก ', '')")

print("\n=== แก้ Ward options ===")
fix(r"'[^']*(?:ER\s*\([^)]+\))[^']*'(?!\s*\))", "'แผนก ER (ฉุกเฉิน)'")
fix(r'"[^"]*(?:ER\s*\([^)]+\))[^"]*"(?=\s*>)', '"แผนก ER (ฉุกเฉิน)"')
fix(r"value=\"[^\"]*ER[^\"]*\"", 'value="แผนก ER (ฉุกเฉิน)"')
fix(r"value=\"[^\"]*ICU[^\"]*\"", 'value="แผนก ICU"')
fix(r"value=\"[^\"]*OPD[^\"]*\"", 'value="แผนก OPD"')
fix(r"value=\"[^\"]*IPD[^\"]*\"", 'value="แผนก IPD"')
fix(r"(?<=<option>)[^<]*ER[^<]*(?=</option>)", "แผนก ER (ฉุกเฉิน)")
fix(r"(?<=<option>)[^<]*ICU[^<]*(?=</option>)", "แผนก ICU")
fix(r"(?<=<option>)[^<]*OPD[^<]*(?=</option>)", "แผนก OPD")
fix(r"(?<=<option>)[^<]*IPD[^<]*(?=</option>)", "แผนก IPD")
fix(r"ward:\s*'[^']*ER[^']*'", "ward: 'แผนก ER (ฉุกเฉิน)'")

print("\n=== แก้ Toast messages ===")
fix(r"showToast\('[^']*✅',\s*'success'\)", "showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success')")
fix(r"showToast\('[^']*✅',\s*'success'\);\s*setPwForm", "showToast('เปลี่ยนรหัสผ่านสำเร็จ ✅', 'success'); setPwForm")
fix(r"showToast\(data\.detail \|\| '[^']+',\s*'error'\)", "showToast(data.detail || 'เกิดข้อผิดพลาด', 'error')")
fix(r"showToast\('[^']*Server',\s*'error'\)", "showToast('ไม่สามารถเชื่อมต่อ Server', 'error')")
fix(r"showToast\('[^']+',\s*'error'\);\s*return;", "showToast('รหัสผ่านใหม่ไม่ตรงกัน', 'error'); return;")
fix(r"setAiMessages\(prev => \[\.\.\.prev,\s*\{\s*role:\s*'ai',\s*text:\s*'[^']*AI[^']*'\s*\}\]\)", "setAiMessages(prev => [...prev, { role: 'ai', text: 'ไม่สามารถเชื่อมต่อ AI ได้' }])")

print("\n=== แก้ Profile Modal ===")
fix(r"User className=\"h-5 w-5 text-brand-400\" /> [^<]+</h3>", 'User className="h-5 w-5 text-brand-400" /> โปรไฟล์ของฉัน</h3>')
fix(r"(<label[^>]+>)[^<]{3,}(-[^<]+</label>)", r'\1ชื่อ-นามสกุล</label>')
fix(r"(<label[^>]{0,100}>)[^<]{3,}(?=</label>.*บันทึก)", r'\1ชื่อ-นามสกุล')
fix(r"profileSaving \? '\.\.\.' : '[^']+'", "profileSaving ? '...' : 'บันทึก'")
fix(r'Key className="h-4 w-4" /> [^<]+</p>(?=.*input.*password)', 'Key className="h-4 w-4" /> เปลี่ยนรหัสผ่าน</p>')
fix(r'placeholder="[^"]*(?="\s+value=\{pwForm\.current\})', 'placeholder="รหัสผ่านปัจจุบัน')
fix(r'placeholder="[^"]*(?="\s+value=\{pwForm\.newPw\})', 'placeholder="รหัสผ่านใหม่ (อย่างน้อย 6 ตัว)')
fix(r'placeholder="[^"]*(?="\s+value=\{pwForm\.confirm\})', 'placeholder="ยืนยันรหัสผ่านใหม่')
fix(r"profileSaving \? '[^']*\.\.\.' : '[^']*(?=เปลี่ยน|change|pass)", "profileSaving ? 'กำลังบันทึก...' : 'เปลี่ยนรหัสผ่าน'")
fix(r"currentUser\?\.role === 'admin' \? '[^']+' : currentUser\?\.role === 'head_nurse' \? '[^']+' : '[^']+'(?=\}</p>)",
    "currentUser?.role === 'admin' ? '🔴 Admin' : currentUser?.role === 'head_nurse' ? '🟢 Head Nurse' : '🔵 Nurse'")

print("\n=== แก้ ScheduleView ===")
fix(r"const days = \[[^\]]+\](?=;.*join.*','.*\\n)", "const days = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์']")
fix(r"let csv = '[^']+,' \+ days", "let csv = 'พยาบาล,' + days")
fix(r"'[^']*\(OR-Tools AI\)[^']*'(?=.*setLoading\(false\))", "'AI กำลังคำนวณ 1,000+ ความเป็นไปได้...'")
fix(r"'[^']*OR-Tools AI'(?=\})", "'สร้างตารางด้วย OR-Tools AI'")
fix(r'"[^"]*OR-Tools AI[^"]*"(?=\s+เพื่อ)', '"กดปุ่ม "สร้างตารางด้วย OR-Tools AI" เพื่อเริ่มคำนวณเวร"')
fix(r'(<th[^>]{0,80}>)[^<]{2,10}(?=</th>.*<th.*Day|วัน)', r'\1บุคลากร')
fix(r"วัน\{?\['[^']+',", "วัน{['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.'][i]}")
fix(r"'[^']*\(Core Rules\)[^']*'", "'กฎพื้นฐาน (Core Rules)'")
fix(r"'[^']*\(Staffing Mix\)[^']*'", "'พยาบาลเวร (Staffing Mix)'")

print("\n=== แก้ ConflictSolverView ===")
fix(r"\(Gemini 1\.5 Pro\)", "(Gemini 1.5 Pro)")
fix(r'"[^"]*\(Gemini 1\.5 Pro\)"', '"จัดการเหตุขัดแย้งกะทับหัด (Gemini 1.5 Pro)"')
fix(r'"[^"]*\(Natural Language Input\)"', '"ระบุปัญหา (Natural Language Input)"')
fix(r'"[^"]*\(Conflict Resolution Options\)"', '"AI เสนอทางเลือก (Conflict Resolution Options)"')
fix(r'useState\("[^"]*RN-A[^"]*"\)', 'useState("พยาบาลสมศรีกอภาระทับหัดครั้งนี้ ช่วยกรับตารางให้หน้อย")')

print("\n=== แก้ StaffView ===")
fix(r"(RN):\s*(?:person\.role_type === 'RN' \? )'[^']+'", r"person.role_type === 'RN' ? 'พยาบาลวิชาชีพ (RN)'")
fix(r"'[^']*\(RN\)'\s*:", "'พยาบาลวิชาชีพ (RN)' :")
fix(r"'[^']*\(TN\)'\s*:", "'พยาบาลเทคนิค (TN)' :")
fix(r"'[^']*\(PN\)'\s*:", "'ผู้ช่วยพยาบาล (PN)' :")
fix(r"option value=\"RN\">RN \([^)]+\)", 'option value="RN">RN (พยาบาลวิชาชีพ)')
fix(r"option value=\"TN\">TN \([^)]+\)", 'option value="TN">TN (พยาบาลเทคนิค)')
fix(r"option value=\"PN\">PN \([^)]+\)", 'option value="PN">PN (ผู้ช่วยพยาบาล)')
fix(r"option value=\"NA\">NA \([^)]+\)", 'option value="NA">NA (ผู้ช่วยเหลือ)')
fix(r"placeholder=\"[^\"]*Database\.\.\."  , 'placeholder=""')

print("\n=== แก้ WardConfigView ===")
fix(r'"[^"]*\(Smart Validator\)"', '"🧮 สรุปกำลังคน (Smart Validator)"')
fix(r"✓ เหลืออีก \{surplus\}", "✓ เหลืออีก {surplus}")

print("\n=== แก้ LeaveView ===")
fix(r"pending:\s*'[^']+'(?=.*approved)", "pending: 'รอพิจารณา'")
fix(r"approved:\s*'[^']+'(?=.*rejected)", "approved: 'อนุมัติ'")
fix(r"rejected:\s*'[^']+'(?=.*return)", "rejected: 'ไม่อนุมัติ'")
fix(r"leave_type:\s*'[^']+'(?=.*reason)", "leave_type: 'ลาป่วย'")
fix(r"<option>[^<]*ลา[^<]*ป่[^<]*วย[^<]*</option>", "<option>ลาป่วย</option>")
# Match leave types by position in select
fix(r"<option>[^<]{5,20}</option><option>[^<]{5,20}</option><option>[^<]{5,20}</option><option>[^<]{5,20}</option>",
    "<option>ลาป่วย</option><option>ลากิจ</option><option>ลาพักร้อน</option><option>ลาคลอด</option>")

print("\n=== แก้ DashboardView ===")
fix(r"label:\s*'[^']*Active'", "label: 'บุคลากร Active'")
fix(r"label:\s*'[^']*\(RN\)'", "label: 'พยาบาลวิชาชีพ (RN)'")
fix(r"label:\s*'[^']*\(NA/PN\)'", "label: 'ผู้ช่วย (NA/PN)'")
fix(r"label:\s*'[^']*Score[^']*'", "label: 'Fairness Score ล่าสุด'")

print("\n=== แก้ CalendarView ===")
fix(r"M:\s*'[^']{2,10}'(?=,\s*E:)", "M: 'เช้า'")
fix(r"E:\s*'[^']{2,10}'(?=,\s*N:)", "E: 'บ่าย'")
fix(r"N:\s*'[^']{2,10}'(?=,\s*OFF:)", "N: 'ดึก'")
fix(r"OFF:\s*'[^']{2,10}'(?=\s*})", "OFF: 'หยุด'")
fix(r"const daysOfWeek = \[[^\]]+\]", "const daysOfWeek = ['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.']")

print("\n=== แก้ UserManagementView ===")
fix(r"option value=\"admin\">Admin \([^)]+\)", 'option value="admin">Admin (ผู้ดูแลระบบ)')
fix(r"option value=\"head_nurse\">Head Nurse \([^)]+\)", 'option value="head_nurse">Head Nurse (หัวหน้าพยาบาล)')
fix(r"option value=\"nurse\">Nurse \([^)]+\)", 'option value="nurse">Nurse (พยาบาล)')

print("\n=== แก้ AI Chat ===")
fix(r"(aiMessages\.length === 0 && <p[^>]{0,100}>)[^<]{10,}(?=</p>)",
    r'\1ถามอะไรก็ได้เกี่ยวกับตารางเวร เช่น "พยาบาลที่ว่างเวรดึกเยอะสุด?"')
fix(r"text-slate-400'>([^<]{5,30})\.\.\.</div>(?=\s*\})", "text-slate-400'>กำลังคิด...</div>")
fix(r'placeholder="[^"]*คำถาม[^"]*"', 'placeholder="พิมพ์คำถาม..."')
fix(r'placeholder="[^"]{3,30}\.\.\."(?=.*aiInput)', 'placeholder="พิมพ์คำถาม..."')

print(f"\n=== สรุป ===")
print(f"ขนาดไฟล์ก่อน: {original_len:,}")
print(f"ขนาดไฟล์หลัง: {len(text):,}")

FILE.write_text(text, encoding='utf-8')
print(f"✅ บันทึกเสร็จ! → {FILE.name}")
print("🔄 รีเฟรช browser ได้เลย (Next.js hot-reload อัตโนมัติ)")
input("\nกด Enter เพื่อปิด...")
