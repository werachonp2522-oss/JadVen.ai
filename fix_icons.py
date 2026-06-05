import os

file_path = r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'เน เธ เน‰เธ›เธฑเธ เธซเธฒเธ เธฐเธ—เธฑเธ™เธซเธฑเธ™': 'แก้ปัญหากะทันหัน',
    'เน เธ เน‰เน„เธ‚เน€เธ‡เธทเนˆเธญเธ™เน„เธ‚': 'แก้ไขเงื่อนไข',
    "icon: 'โ˜€๏ธ '": "icon: '☀️'",
    "icon: '๐ŸŒ…'": "icon: '🌇'",
    "icon: '๐ŸŒ™'": "icon: '🌙'",
    '๐Ÿ“Š สรุปกำลังคน (Smart Validator)': '📊 สรุปกำลังคน (Smart Validator)',
    'โœ… ค่ากำลังคนเพียงพอ!': '✅ ค่ากำลังคนเพียงพอ!',
    'โ Œ กำลังคนไม่พอ! ขาดอีก': '❌ กำลังคนไม่พอ! ขาดอีก',
    '๐Ÿ’ก แนะนำ:': '💡 แนะนำ:',
    ' โ†’ ': ' → ',
    "icon: '๐Ÿ‘ฉโ€ โš•๏ธ '": "icon: '👩‍⚕️'",
    "icon: '๐Ÿ ฅ'": "icon: '💉'",
    "icon: '๐Ÿค '": "icon: '🤝'",
    "icon: '๐Ÿ“‹'": "icon: '📋'",
    "icon: 'โš–๏ธ '": "icon: '⚖️'",
    "icon: '๐Ÿ“Š'": "icon: '📊'"
}

count = 0
for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"Replaced {old} -> {new}")
    else:
        print(f"Could NOT find {old}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Total replacements applied: {count}")
