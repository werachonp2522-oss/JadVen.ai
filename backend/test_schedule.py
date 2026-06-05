import requests
import json

# Test schedule generation
staff_res = requests.get('http://127.0.0.1:8000/api/staff/')
staff = staff_res.json()
nurses = [
    {'id': str(s['id']), 'name': s['employee_id'], 'type': s['role_type'], 'seniority': s['seniority']}
    for s in staff if s['is_active']
]
print(f"Active nurses: {len(nurses)}")
print([f"{n['name']}({n['type']})" for n in nurses])

# Get ward config
cfg_res = requests.get('http://127.0.0.1:8000/api/ward-config/')
cfg = cfg_res.json()
if cfg:
    print(f"WardConfig: {json.dumps(cfg[0]['config'], ensure_ascii=False, indent=2)}")

# Generate schedule
r = requests.post('http://127.0.0.1:8000/api/schedule/generate', json={'num_days': 7, 'nurses': nurses})
data = r.json()
print(f"\nStatus: {data.get('status')}")
print(f"Message: {data.get('message','')}")
if data.get('fairness_score'):
    print(f"Fairness Score: {data.get('fairness_score')}")
for s in data.get('schedule', []):
    print(f"  {s['nurse']}: {s['shifts']}")
