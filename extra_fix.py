import pathlib
import re

file_path = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")

with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

lines = text.split("\n")
changes = 0

for i, line in enumerate(lines):
    orig = line
    
    # RuleBuilderView
    if "(Universal Rules)" in line:
        lines[i] = re.sub(r'>.*?\(Universal Rules\)<', '>ตั้งค่ากฎครอบจักรวาล (Universal Rules)<', line)
    elif "AI (OR-Tools)" in line and "text-slate-400" in line:
        lines[i] = re.sub(r'>.*?</p>', '>กำหนดเงื่อนไขและข้อจำกัดต่างๆ เพื่อให้ AI (OR-Tools) คำนวณตารางเวรได้แม่นยำ</p>', line)
    elif "<Plus" in lines[i-1] and "<span>" in line and "button" in lines[i-2]:
        lines[i] = re.sub(r'<span>.*?</span>', '<span>สร้างกฎใหม่</span>', line)
    elif "<Settings" in line and "</button>" in lines[i+1]:
        lines[i] = re.sub(r'/>.*', '/> แก้ไขเงื่อนไข', line)
    elif "group-hover:text-white" in line and "h3" in line and "border-dashed" in lines[i-4]:
        lines[i] = re.sub(r'>.*?</h3>', '>สร้างกฎเฉพาะถิ่น</h3>', line)
    elif "text-slate-500 mt-1" in line and "p" in line and "border-dashed" in lines[i-5]:
         lines[i] = re.sub(r'>.*?</p>', '>เพิ่มข้อจำกัดใหม่สำหรับแผนกของคุณ</p>', line)
         
    # WardConfigView
    elif "<Settings" in lines[i-1] and "h3" in lines[i-2] and "glass-card" in lines[i-3]:
        lines[i] = "          ตั้งค่าทั่วไป"
    elif 'label className="text-sm text-slate-400 block mb-2"' in line:
        if "max_shifts_per_week" in lines[i+3]:
            lines[i] = re.sub(r'>.*?</label>', '>เวรสูงสุดที่ทำได้ (ต่อสัปดาห์)</label>', line)
        elif "min_shifts_per_week" in lines[i+3]:
            lines[i] = re.sub(r'>.*?</label>', '>เวรขั้นต่ำที่ต้องทำ (ต่อสัปดาห์)</label>', line)
        elif "min_rn_per_shift" in lines[i+3]:
            lines[i] = re.sub(r'>.*?</label>', '>จำนวน RN ขั้นต่ำ (ต่อเวร)</label>', line)
        elif "min_pn_per_shift" in lines[i+3]:
             lines[i] = re.sub(r'>.*?</label>', '>จำนวน PN ขั้นต่ำ (ต่อเวร)</label>', line)
    elif "label className=" in line and "text-center block mb-4" in line:
        if "M" in line: lines[i] = re.sub(r'>.*?</label>', '>เวรเช้า (Morning)</label>', line)
        if "E" in line: lines[i] = re.sub(r'>.*?</label>', '>เวรบ่าย (Evening)</label>', line)
        if "N" in line: lines[i] = re.sub(r'>.*?</label>', '>เวรดึก (Night)</label>', line)
    elif 'className="text-xs text-slate-400 block mb-1"' in line:
        if "min_rn" in lines[i+3]: lines[i] = re.sub(r'>.*?</label>', '>พยาบาลวิชาชีพ (RN)</label>', line)
        if "min_pn" in lines[i+3]: lines[i] = re.sub(r'>.*?</label>', '>พยาบาลเทคนิค (PN)</label>', line)
        if "min_na" in lines[i+3]: lines[i] = re.sub(r'>.*?</label>', '>ผู้ช่วยพยาบาล (NA)</label>', line)
    elif 'className="flex justify-center"' in lines[i-1] and "button" in line:
        pass # Wait, button text is usually dynamic
    elif "!isFeasible ?" in line and "saving ?" in line:
        # lines[i] is the button text for saving
        pass # Better to not regex this one if complex, let's specify it
        
    if orig != lines[i]:
        changes += 1

# Manually fix the save button
text = "\n".join(lines)
text = text.replace("เธ เธณเธฅเธฑเธ‡เธ„เธ™เน„เธกเนˆเธžเธญ โ€” เธ เธฃเธธเธ“เธฒเธ›เธฃเธฑเธšเธ„เนˆเธฒ", "กำลังคนไม่พอ — กรุณาปรับค่า")
text = text.replace("เธ เธณเธฅเธฑเธ‡เธšเธฑเธ™เธ—เธถเธ ...", "กำลังบันทึก...")
text = text.replace("เธšเธฑเธ™เธ—เธถเธ เธชเธณเน€เธฃเน‡เธˆ โœ“", "บันทึกสำเร็จ ✓")
text = text.replace("เธšเธฑเธ™เธ—เธถเธ เธ„เนˆเธฒเธ•เธฑเน‰เธ‡เธ„เนˆเธฒเธงเธญเธฃเนŒเธ”", "บันทึกค่าตั้งค่าวอร์ด")
text = text.replace("เธ•เธฑเน‰เธ‡เธ„เนˆเธฒเธ—เธฑเนˆเธงเน„เธ›", "ตั้งค่าทั่วไป")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"✅ Replaced extra {changes} elements successfully!")
