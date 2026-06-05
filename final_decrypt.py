import pathlib
import re

def fix_mojibake(mangled_str):
    try:
        raw_bytes = mangled_str.encode('windows-1252', errors='ignore')
        fixed = raw_bytes.decode('windows-874', errors='ignore')
        
        # Only return the fixed string if it actually contains valid Thai text and changed
        if fixed != mangled_str and any('\u0e00' <= c <= '\u0e7f' for c in fixed):
            return fixed
        return mangled_str
    except Exception:
        return mangled_str

file_path = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

def replace_match(match):
    original = match.group(0)
    fixed = fix_mojibake(original)
    return fixed

# Find all blocks of text containing the telltale signature 'เธ' and fix them.
# The regex looks for sequences of characters that contain 'เธ' and are mostly Thai mojibake.
# We'll use a precise substitution logic.

lines = text.split("\n")
changes = 0

for i, line in enumerate(lines):
    # Find all sequences that look like our mangled text (containing 'เธ' or similar TIS-620 characters mapped to cp1252)
    new_line = line
    
    # We can just look for substring matches of the corrupted strings we extracted earlier.
    # A cleaner way is to apply the fix_mojibake function to sequences of words.
    
    # Let's extract all text between quotes, tags, or curly braces that contain 'เธ' or 'เน'
    pattern = re.compile(r'([^<>"\'`{}]+)')
    
    parts = pattern.split(new_line)
    for j, part in enumerate(parts):
        if 'เธ' in part or 'เน' in part or 'โ' in part or '๐' in part:
            fixed_part = fix_mojibake(part)
            if fixed_part != part:
                parts[j] = fixed_part
                
    new_line = "".join(parts)
    
    if new_line != line:
        changes += 1
        lines[i] = new_line

with open(file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Successfully decrypted and fixed {changes} lines in page.tsx!")
