"""
fix_mangled_thai.py - แก้ไขภาษาไทยที่ถูกแทนที่ผิดพลาด (เช่น เข้าสู่ระบบ, รหัสผ่านปนกัน)
รัน: python fix_mangled_thai.py
"""
import re
import pathlib
import shutil

FILE = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")
bak = FILE.with_name("page.tsx.bak_mangled")
shutil.copy2(FILE, bak)

text = FILE.read_text(encoding='utf-8')

# เราจะใช้ Regex ที่ match ทั้งข้อความแปลกๆ และแทนที่ด้วยข้อความที่ถูกต้อง
# เนื่องจากข้อความมันยาวและมี \ufffd (แสดงเป็น ) เราจะใช้ (?:.*?) หรือ pattern กว้างๆ
# โดยมี context กั้นหน้าและหลัง

REPLACEMENTS = [
    # Sidebar Navigation
    (r'label="[^"]*\(Schedule\)"', 'label="ตารางเวร (Schedule)"'),
    (r'label="[^"]*\(conflict\)"', 'label="จัดการความขัดแย้ง"'),
    (r'label="[^"]*\(Staff\)"', 'label="บุคลากร (Staff)"'),
    (r'label="[^"]*\(Ward Config\)"', 'label="ตั้งค่าวอร์ด (Ward Config)"'),
    (r'label="[^"]*\(Leave\)"', 'label="วันลา (Leave)"'),
    (r'label="[^"]*\(Dashboard\)"', 'label="แดชบอร์ด (Dashboard)"'),
    (r'label="[^"]*\(Admin\)"', 'label="จัดการผู้ใช้ (Admin)"'),
    (r'label="[^"]*\(Calendar\)"', 'label="ปฏิทินเวร (Calendar)"'),
    
    # Active Tab match fallback
    (r'label="[^"]+"(?=\s+isActive=\{activeTab === \'conflict\'\})', 'label="จัดการความขัดแย้ง"'),

    # Headers
    (r'activeTab === \'schedule\' && "[^"]*\(Smart Roster\)"', 'activeTab === \'schedule\' && "จัดการตารางเวรอัจฉริยะ (Smart Roster)"'),
    (r'activeTab === \'conflict\' && "[^"]*\(AI-Conflict Solver\)"', 'activeTab === \'conflict\' && "ระบบจัดการความขัดแย้ง (AI-Conflict Solver)"'),
    (r'activeTab === \'staff\' && "[^"]+"', 'activeTab === \'staff\' && "รายชื่อบุคลากรพยาบาล"'),
    (r'activeTab === \'rules\' && "[^"]*\(Universal Rule Builder\)"', 'activeTab === \'rules\' && "ตัวสร้างกฎครอบจักรวาล (Universal Rule Builder)"'),
    (r'activeTab === \'wardconfig\' && "[^"]+"', 'activeTab === \'wardconfig\' && "ตั้งค่าความต้องการบุคลากรประจำวอร์ด"'),
    (r'activeTab === \'leave\' && "[^"]+"', 'activeTab === \'leave\' && "จัดการวันลาบุคลากร"'),
    (r'activeTab === \'dashboard\' && "[^"]+"', 'activeTab === \'dashboard\' && "แดชบอร์ดสถิติ"'),
    (r'activeTab === \'users\' && "[^"]*\(Admin\)"', 'activeTab === \'users\' && "จัดการผู้ใช้งานระบบ (Admin)"'),
    (r'activeTab === \'calendar\' && "[^"]*\(Calendar\)"', 'activeTab === \'calendar\' && "ปฏิทินเวร (Calendar)"'),

    # Profile Modal & Toasts
    (r"showToast\([^,]+,\s*'success'\)", "showToast('สำเร็จ ✅', 'success')"),
    (r"showToast\(data\.detail || '[^']+',\s*'error'\)", "showToast(data.detail || 'เกิดข้อผิดพลาด', 'error')"),
    (r"showToast\('[^']+',\s*'error'\)", "showToast('มีข้อผิดพลาด โปรดลองใหม่', 'error')"),
    (r"<label[^>]*>.*?/label>(?=\s*<div className=\"flex gap-2\">)", "<label className=\"block text-sm font-medium text-slate-300\">ชื่อ-นามสกุล</label>"),
    (r"profileSaving \? '[^']+' : '[^']+'(?=\s*</button>\s*</div>\s*<div className=\"border-t)", "profileSaving ? 'กำลังบันทึก...' : 'บันทึก'"),
    (r"<p className=\"text-sm font-medium text-slate-300 flex items-center gap-2\"><Key className=\"h-4 w-4\" /> [^<]+</p>", "<p className=\"text-sm font-medium text-slate-300 flex items-center gap-2\"><Key className=\"h-4 w-4\" /> เปลี่ยนรหัสผ่าน</p>"),
    (r'placeholder="[^"]+"(?=\s+value=\{pwForm\.current\})', 'placeholder="รหัสผ่านปัจจุบัน"'),
    (r'placeholder="[^"]+"(?=\s+value=\{pwForm\.newPw\})', 'placeholder="รหัสผ่านใหม่"'),
    (r'placeholder="[^"]+"(?=\s+value=\{pwForm\.confirm\})', 'placeholder="ยืนยันรหัสผ่านใหม่"'),
    (r"profileSaving \? '[^']+' : '[^']+'(?=\s*</button>\s*</div>\s*</div>)", "profileSaving ? 'กำลังเปลี่ยน...' : 'เปลี่ยนรหัสผ่าน'"),

    # AI Chat
    (r"text: '[^']+' \}\]\)", "text: 'เกิดข้อผิดพลาดในการเชื่อมต่อ AI' }])"),
    (r"aiMessages\.length === 0 && <p className=\"[^\"]+\">[^<]+</p>", "aiMessages.length === 0 && <p className=\"text-slate-500 text-center py-10\">พิมพ์คำถามเกี่ยวกับตารางเวร เช่น \"ใครว่างเวรดึกวันศุกร์นี้บ้าง?\"</p>"),
    (r"aiLoading && <div[^>]+><div[^>]+>[^<]+</div></div>", "aiLoading && <div className=\"flex justify-start\"><div className=\"bg-slate-700 px-4 py-2 rounded-2xl text-sm text-slate-400\">กำลังวิเคราะห์...</div></div>"),
    (r'placeholder="[^"]+"(?=\s+className="flex-1 bg-slate-900)', 'placeholder="พิมพ์คำถามของคุณที่นี่..."'),

    # Wards / Roles Options
    (r"<option>[^<]+ER[^<]*</option>", "<option>แผนก ER (ฉุกเฉิน)</option>"),
    (r"<option>[^<]+ICU[^<]*</option>", "<option>แผนก ICU</option>"),
    (r"<option>[^<]*IPD[^<]*</option>", "<option>แผนก IPD</option>"),
    (r"<option>แผนก OPD</option>", "<option>แผนก OPD</option>"), # safety
    (r"'[^']*ER\s*\([^)]+\)'", "'แผนก ER (ฉุกเฉิน)'"),
    
    # Schedule View
    (r"const days = \[[^\]]+\];", "const days = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์'];"),
    (r"let csv = '[^']+' \+ days\.join", "let csv = 'รายชื่อ,' + days.join"),
    (r"'AI [^']+' : '[^']*OR-Tools AI'", "'AI กำลังคำนวณ 1,000+ ความเป็นไปได้...' : 'สร้างตารางด้วย OR-Tools AI'"),
    (r"<p>[^<]*OR-Tools AI[^<]*</p>", "<p>กดปุ่ม \"สร้างตารางด้วย OR-Tools AI\" เพื่อเริ่ม</p>"),
    (r"<th className=\"px-6 py-4 font-semibold text-slate-300\">[^<]+</th>(?=\s*\{\[\.\.\.Array\(7\)\])", "<th className=\"px-6 py-4 font-semibold text-slate-300\">บุคลากร</th>"),
    (r"<div className=\"text-xs text-slate-500 mb-1\">[^<]+\{\['[^']+',\s*'[^']+',\s*'[^']+',\s*'[^']+',\s*'[^']+',\s*'[^']+',\s*'[^']+'\]\[i\]\}</div>", "<div className=\"text-xs text-slate-500 mb-1\">{['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.'][i]}</div>"),
    (r"<th className=\"px-6 py-4 font-semibold text-center text-slate-300 border-l border-slate-700/50\">[^<]+</th>", "<th className=\"px-6 py-4 font-semibold text-center text-slate-300 border-l border-slate-700/50\">ภาพรวม</th>"),
    (r"<span>[^<]+\(Core Rules\)</span>", "<span>กฎพื้นฐาน (Core Rules)</span>"),
    (r"<span>[^<]+\(Staffing Mix\)</span>", "<span>ความต้องการพยาบาล (Staffing Mix)</span>"),

    # AI Conflict
    (r"useState\(\"[^\"]+\"(?=\);.*loading.*response)", "useState(\"พยาบาลสมศรีขอลาป่วยกะทันหันพรุ่งนี้ ช่วยหาคนแทนให้หน่อย\");"),
    (r"<h2 className=\"[^\"]+\">[^<]+\(Gemini 1\.5 Pro\)</h2>", "<h2 className=\"2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">ผู้ช่วยแก้ไขปัญหา (Gemini 1.5 Pro)</h2>"),
    (r"<p className=\"text-slate-400\">[^<]+Real-time</p>", "<p className=\"text-slate-400\">ให้ AI ช่วยแก้ปัญหาตารางเวรกะทันหันแบบ Real-time</p>"),
    (r"<label className=\"text-sm font-medium text-slate-300\">[^<]+\(Natural Language Input\)</label>", "<label className=\"text-sm font-medium text-slate-300\">อธิบายปัญหา (Natural Language Input)</label>"),
    (r"<span>[^<]+</span>(?=\s*</button>\s*</div>\s*</div>\s*\{response &&)", "<span>ขอคำแนะนำจาก AI</span>"),
    (r"<h3 className=\"font-bold text-lg mb-4 flex items-center gap-2 text-emerald-400\">\s*<Activity className=\"h-5 w-5\" />\s*[^<]+\(Conflict Resolution Options\)\s*</h3>", "<h3 className=\"font-bold text-lg mb-4 flex items-center gap-2 text-emerald-400\"><Activity className=\"h-5 w-5\" /> ทางเลือกแก้ไขปัญหา (Conflict Resolution Options)</h3>"),
    (r"Option A: [^<]+", "Option A: แนะนำให้ปรับเวลา"),
    (r"Option B: [^<]+", "Option B: แนะนำให้หาคนแทน"),
    (r"Option C: [^<]+", "Option C: แนะนำให้ควบเวร"),

    # Staff View
    (r"confirm\([^)]+\)", "confirm('ยืนยันลบข้อมูลหรือไม่?')"),
    (r"alert\([^)]+\)", "alert('เกิดข้อผิดพลาด!')"),
    (r'placeholder="[^"]+"(?=\s+className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4)', 'placeholder="ค้นหาชื่อพยาบาล..."'),
    (r"}[^<]+\(Filter\)", "} กรองแผนก (Filter)"),
    (r"<span>[^<]+</span>(?=\s*</button>\s*</div>\s*<div className=\"bg-slate-800/50 rounded-2xl)", "<span>เพิ่มบุคลากรใหม่</span>"),

    # Staff Table
    (r"<th className=\"px-6 py-4 font-semibold text-slate-300\">[^<]+</th>(?=\s*<th className=\"px-6 py-4 font-semibold text-slate-300\">[^<]+\(Type\))", "<th className=\"px-6 py-4 font-semibold text-slate-300\">รหัส / ชื่อ-นามสกุล</th>"),
    (r"<th className=\"px-6 py-4 font-semibold text-slate-300\">[^<]+\(Type\)</th>", "<th className=\"px-6 py-4 font-semibold text-slate-300\">ตำแหน่ง (Type)</th>"),
    (r"<th className=\"px-6 py-4 font-semibold text-slate-300\">[^<]+\(Seniority\)</th>", "<th className=\"px-6 py-4 font-semibold text-slate-300\">ความอาวุโส (Seniority)</th>"),
    (r"<th className=\"px-6 py-4 font-semibold text-slate-300\">[^<]+</th>(?=\s*<th className=\"px-6 py-4 font-semibold text-right text-slate-300\")", "<th className=\"px-6 py-4 font-semibold text-slate-300\">สถานะ</th>"),
    (r"<th className=\"px-6 py-4 font-semibold text-right text-slate-300\">[^<]+</th>", "<th className=\"px-6 py-4 font-semibold text-right text-slate-300\">จัดการ</th>"),
    (r"<td colSpan=\{5\} className=\"text-center py-8 text-slate-400\">[^<]+</td>", "<td colSpan={5} className=\"text-center py-8 text-slate-400\">กำลังโหลด...</td>"),

    (r"person\.role_type === 'RN' \? '[^']+' :", "person.role_type === 'RN' ? 'พยาบาลวิชาชีพ (RN)' :"),
    (r"person\.role_type === 'PN' \? '[^']+' :", "person.role_type === 'PN' ? 'ผู้ช่วยพยาบาล (PN)' :"),
    (r"'[^']+\(TN\)'", "'พยาบาลเทคนิค (TN)'"),
    (r"<span className=\"w-1\.5 h-1\.5 rounded-full bg-emerald-400\"></span>\s*[^<]+</span>", "<span className=\"w-1.5 h-1.5 rounded-full bg-emerald-400\"></span> ทำงานปกติ</span>"),

    # Staff Modal
    (r"<h3 className=\"text-lg font-bold text-white\">\{\s*editingStaff \? '[^']+' : '[^']+'\s*\}</h3>", "<h3 className=\"text-lg font-bold text-white\">{editingStaff ? 'แก้ไขข้อมูลบุคลากร' : 'เพิ่มบุคลากรใหม่'}</h3>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+\(ID\)</label>", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">รหัสพนักงาน (ID)</label>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<input required type=\"text\" value=\{formData\.name)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">ชื่อ - นามสกุล</label>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<select value=\{formData\.role_type)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">ตำแหน่ง</label>"),
    (r"<option value=\"RN\">RN \([^)]+\)</option>", "<option value=\"RN\">RN (พยาบาลวิชาชีพ)</option>"),
    (r"<option value=\"TN\">TN \([^)]+\)</option>", "<option value=\"TN\">TN (พยาบาลเทคนิค)</option>"),
    (r"<option value=\"PN\">PN \([^)]+\)</option>", "<option value=\"PN\">PN (ผู้ช่วยพยาบาล)</option>"),
    (r"<option value=\"NA\">NA \([^)]+\)</option>", "<option value=\"NA\">NA (ผู้ช่วยเหลือคนไข้)</option>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<select value=\{formData\.seniority)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">ความอาวุโส</label>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<select value=\{formData\.ward)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">ประจำวอร์ด</label>"),
    (r"<label htmlFor=\"isActive\" className=\"text-sm font-medium text-slate-300\">[^<]+\(Active\)</label>", "<label htmlFor=\"isActive\" className=\"text-sm font-medium text-slate-300\">สถานะปฏิบัติงาน (Active)</label>"),

    # Buttons
    (r"onClick=\{\(\) => setModalOpen\(false\)\}[^>]+>[^<]+</button>", "onClick={() => setModalOpen(false)} className=\"px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-medium transition-colors border border-slate-700\">ยกเลิก</button>"),
    (r"type=\"submit\" className=\"px-4 py-2 bg-blue-600[^>]+>[^<]+</button>", "type=\"submit\" className=\"px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-600/20\">บันทึกข้อมูล</button>"),
    (r"type=\"submit\" className=\"px-4 py-2 bg-brand-600[^>]+>[^<]+</button>", "type=\"submit\" className=\"px-4 py-2 bg-brand-600 hover:bg-brand-500 rounded-lg text-sm text-white font-medium\">ยืนยันบันทึก</button>"),
    (r"type=\"button\" onClick=\{\(\) => setModalOpen\(false\)\}[^>]+>[^<]+</button>", "type=\"button\" onClick={() => setModalOpen(false)} className=\"px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white\">ยกเลิก</button>"),

    # Rules View
    (r"<h2 className=\"text-xl font-bold text-white mb-1\">[^<]+\(Universal Rules\)</h2>", "<h2 className=\"text-xl font-bold text-white mb-1\">กฎเกณฑ์ทั้งหมด (Universal Rules)</h2>"),
    (r"<p className=\"text-sm text-slate-400\">[^<]+\(OR-Tools\)[^<]+</p>", "<p className=\"text-sm text-slate-400\">ปรับแต่งกฎที่ใช้สำหรับการกำหนดตารางเวลาด้วย AI (OR-Tools)</p>"),
    (r"<span>[^<]+</span>(?=\s*</button>\s*</div>\s*<div className=\"grid)", "<span>สร้างกฎใหม่</span>"),
    (r"<h3 className=\"font-medium text-slate-300 group-hover:text-white transition-colors\">[^<]+</h3>(?=\s*<p className=\"text-xs text-slate-500 mt-1\">[^<]+</p>\s*</div>\s*</div>)", "<h3 className=\"font-medium text-slate-300 group-hover:text-white transition-colors\">เพิ่มกฎเกณฑ์เฉพาะที่กำหนดเอง</h3>\n          <p className=\"text-xs text-slate-500 mt-1\">สร้างกฎที่เฉพาะเจาะจงสำหรับแผนกของคุณ</p>"),

    # Ward Config View
    (r"<h2 className=\"text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">[^<]+</h2>(?=\s*<p className=\"text-slate-400\">[^<]+AI[^<]+</p>)", "<h2 className=\"2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">ตั้งค่าความต้องการกำลังคน (Ward Config)</h2>"),
    (r"<p className=\"text-slate-400\">[^<]+AI[^<]+</p>", "<p className=\"text-slate-400\">กำหนดความต้องการพยาบาลในแต่ละกะเพื่อให้ AI จัดสรรได้อย่างแม่นยำ</p>"),
    (r"<h3 className=\"font-bold text-white mb-4 flex items-center gap-2\">\s*<Activity className=\"h-5 w-5 text-brand-400\" />\s*[^<]+\(Smart Validator\)\s*</h3>", "<h3 className=\"font-bold text-white mb-4 flex items-center gap-2\">\n          <Activity className=\"h-5 w-5 text-brand-400\" />\n          ตัวช่วยวิเคราะห์ (Smart Validator)\n        </h3>"),
    
    (r"<div className=\"text-xs text-slate-400\">[^<]+/?[^<]*</div>(?=\s*<div className=\"text-2xl font-bold text-white\">\{maxShifts\})", "<div className=\"text-xs text-slate-400\">กะทำงาน/คน</div>"),
    (r"<div className=\"text-xs text-slate-500\">[^<]+</div>(?=\s*</div>\s*<div className=\"bg-slate-900/50 rounded-xl p-3 text-center\">)", "<div className=\"text-xs text-slate-500\">สูงสุด/สัปดาห์</div>"),
    
    (r"<div className=\"text-xs text-slate-400\">[^<]+</div>(?=\s*<div className=\"text-2xl font-bold text-brand-400\">\{capacityPerWeek\})", "<div className=\"text-xs text-slate-400\">กำลังคนที่มี</div>"),
    (r"<div className=\"text-xs text-slate-400\">[^<]+</div>(?=\s*<div className=\"text-2xl font-bold.*>\{demandPerWeek\})", "<div className=\"text-xs text-slate-400\">ความต้องการ</div>"),
    
    (r"<span className=\"font-bold\">\? [^!]+!</span>", "<span className=\"font-bold\">✨ เพียงพอต่อการจัดตาราง!</span>"),
    (r"<span className=\"text-emerald-400/70 ml-1\">[^<]*\{surplus\}[^<]+</span>", "<span className=\"text-emerald-400/70 ml-1\">เกิน {surplus} กะ/สัปดาห์</span>"),
    (r"<div className=\"font-bold\">\? [^!]+! [^<]*\{Math", "<div className=\"font-bold\">⚠️ ขาดกำลังคน! ขาด {Math"),
    (r"<div className=\"text-red-400/70 mt-1\">\s*\?\? [^:]+: [^<]+\{maxShifts\} \? \{maxShifts \+ 1\} [^<]+\s*</div>", "<div className=\"text-red-400/70 mt-1\">คำแนะนำ: เพิ่ม OT หรืออนุญาตให้ขึ้นเวรสูงสุดเป็น {maxShifts} - {maxShifts + 1} กะ</div>"),

    (r"<label className=\"text-xs text-slate-400 block mb-1\">[^<]+\(RN[^<]+\)</label>", "<label className=\"text-xs text-slate-400 block mb-1\">ขั้นต่ำ RN</label>"),
    (r"<label className=\"text-xs text-slate-400 block mb-1\">[^<]+\(NA[^<]+\)</label>", "<label className=\"text-xs text-slate-400 block mb-1\">ขั้นต่ำ NA/PN</label>"),
    (r"<label className=\"text-xs text-slate-400 block mb-1\">[^<]+\([^<]+\)</label>", "<label className=\"text-xs text-slate-400 block mb-1\">ขั้นต่ำรวม</label>"),
    (r"<label className=\"text-sm text-slate-400 block mb-2\">[^<]+\([^<]*\)</label>", "<label className=\"text-sm text-slate-400 block mb-2\">ค่าสูงสุด/ต่ำสุด</label>"),

    # Leave View
    (r"statusLabels\[[a-zA-Z\.]+\] \|\| '[^']+'", "statusLabels[leave.status] || 'รออนุมัติ'"),
    (r"class.*\{statusColors.*>.*?\{\s*[^<]*\s*\}</span>", "className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[leave.status]}`}>{statusLabels[leave.status] || 'สถานะ'}</span>"),
    (r"<h2 className=\"text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">[^<]+</h2>(?=\s*<p className=\"text-slate-400\">[^<]+AI[^<]+</p>\s*</div>)", "<h2 className=\"2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">อนุมัติวันลาพนักงาน</h2>"),
    (r"<p className=\"text-slate-400\">[^<]+AI[^<]+</p>", "<p className=\"text-slate-400\">ระบบจะปรับโครงสร้างการจัดตารางด้วย AI อัตโนมัติเมื่ออนุมัติวันลา</p>"),
    (r"<span>[^<]+</span>(?=\s*</button>\s*</div>\s*</div>\s*\{!leaveModalOpen)", "<span>เพิ่มวันลา</span>"),
    (r"<p className=\"text-slate-500 text-center py-10\">[^<]+</p>(?=\s*\}\s*\{leaves\.map)", "<p className=\"text-slate-500 text-center py-10\">ไม่พบข้อมูลการลา</p>"),
    (r"<h3 className=\"text-lg font-bold text-white\">[^<]+</h3>(?=\s*</div>\s*<form onSubmit=\{handleSubmit\})", "<h3 className=\"text-lg font-bold text-white\">เพิ่มรายการลา</h3>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<select value=\{formData\.staff_id)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">เจ้าหน้าที่</label>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<input required type=\"date\")", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">วันที่ลา</label>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<select value=\{formData\.leave_type)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">ประเภท</label>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">[^<]+</label>(?=\s*<input type=\"text\" value=\{formData\.reason)", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">เหตุผล (ตัวเลือก)</label>"),

    # Dashboard View
    (r"<h2 className=\"text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">[^<]+</h2>(?=\s*<p className=\"text-slate-400\">)", "<h2 className=\"2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">ภาพรวมระบบจัดตารางเวร</h2>"),
    (r"<h3 className=\"font-bold text-white mb-4 flex items-center gap-2\"><Users className=\"h-5 w-5 text-brand-400\" /> [^<]+\(Active\)</h3>", "<h3 className=\"font-bold text-white mb-4 flex items-center gap-2\"><Users className=\"h-5 w-5 text-brand-400\" /> สัดส่วนบุคลากร (Active)</h3>"),
    (r"<h3 className=\"font-bold text-white mb-4 flex items-center gap-2\"><Clock className=\"h-5 w-5 text-brand-400\" /> [^<]+</h3>", "<h3 className=\"font-bold text-white mb-4 flex items-center gap-2\"><Clock className=\"h-5 w-5 text-brand-400\" /> ประวัติการจัดตาราง</h3>"),
    (r"<p className=\"text-slate-500 text-center py-6\">[^<]+</p>", "<p className=\"text-slate-500 text-center py-6\">ไม่มีประวัติการจัดตาราง</p>"),

    # Admin View
    (r"<h2 className=\"text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">[^<]+</h2>(?=\s*<p className=\"text-slate-400\">[^<]+</p>\s*</div>\s*<div className=\"flex justify-end\">)", "<h2 className=\"2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">ตั้งค่าผู้ใช้งานระบบ</h2>"),
    (r"<p className=\"text-slate-400\">[^<]+</p>(?=\s*</div>\s*<div className=\"flex justify-end\">)", "<p className=\"text-slate-400\">เพิ่ม/แก้ไขผู้ใช้งานระบบ กำหนดสิทธิ์ต่างๆ</p>"),
    (r"<Plus className=\"h-4 w-4\" /> [^\n<]+", "<Plus className=\"h-4 w-4\" /> เพิ่มผู้ใช้งานใหม่"),
    (r"<th className=\"px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider\">[^<]+</th>(?=\s*<th className=\"px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider\">Role</th>)", "<th className=\"px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider\">ชื่อ</th>"),
    (r"<h3 className=\"text-lg font-bold text-white\">\{\s*editUser \? '[^']+' : '[^']+'\s*\}</h3>", "<h3 className=\"text-lg font-bold text-white\">{editUser ? 'แก้ไขผู้ใช้งาน' : 'เพิ่มผู้ใช้งานใหม่'}</h3>"),
    (r"<label className=\"block text-sm font-medium text-slate-300 mb-1\">\{editUser \? '[^']+' : '[^']+'\}</label>", "<label className=\"block text-sm font-medium text-slate-300 mb-1\">{editUser ? 'รหัสผ่านใหม่ (ปล่อยว่างถ้าไม่เปลี่ยน)' : 'รหัสผ่าน'}</label>"),

    # Global variables replacement (hard match for shift types)
    (r"const shiftLabels: any = \{ M: '[^']+', E: '[^']+', N: '[^']+', OFF: '[^']+' \};", "const shiftLabels: any = { M: 'เช้า', E: 'บ่าย', N: 'ดึก', OFF: 'หยุด' };"),

    # Calendar View title
    (r"<h2 className=\"text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">[^<]+</h2>(?=\s*<p className=\"text-slate-400 text-sm\">[^<]+</p>)", "<h2 className=\"2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400\">ปฏิทินตารางเวร</h2>"),
    (r"<p className=\"text-slate-400 text-sm\">[^<]+</p>", "<p className=\"text-slate-400 text-sm\">ดูตารางเวรแบบปฏิทิน</p>"),
    (r"<span className=\"text-xs text-slate-400\">[^<]+</span>(?=\s*</div>\s*</div>\s*\{loading && <p className)", "<span className=\"text-xs text-slate-400\">วันของคุณ</span>")
]


for pattern, replacement in REPLACEMENTS:
    try:
        text = re.sub(pattern, replacement, text)
    except Exception as e:
        print(f"Error {pattern}: {e}")

# Save
FILE.write_text(text, encoding='utf-8')
print("✅ ทำการแทนที่ข้อความแปลกๆ ด้วยภาษาไทยที่ถูกต้องเรียบร้อยแล้ว!")
