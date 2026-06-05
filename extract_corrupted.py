import re
import pathlib

file_path = pathlib.Path(r"d:\project_dev\JadVen.ai\frontend\src\app\page.tsx")

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Extract all string literals containing 'เธ'
# We will match strings in single quotes, double quotes, and backticks.
matches = set()
for m in re.findall(r'[\'"`]([^<>\'"`]*เธ[^<>\'"`]*)[\'"`]', text):
    matches.add(m)

# also extract text inside JSX tags
for m in re.findall(r'>([^<>]*เธ[^<>]*)<', text):
    matches.add(m.strip())

with open("d:\project_dev\JadVen.ai\corrupted_strings.txt", "w", encoding="utf-8") as f:
    for m in sorted(list(matches)):
        f.write(m + "\n")

print(f"Extracted {len(matches)} corrupted strings to corrupted_strings.txt")
