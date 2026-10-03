with open('full_event_audit_report.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

print(f"Total lines: {len(lines)}")
# Group by event ID
by_event = {}
for line in lines:
    eid = line.split(']')[0].replace('[', '')
    by_event.setdefault(eid, []).append(line)

for eid, issues in by_event.items():
    print(f"\n=== EVENT: {eid} ({len(issues)} notices) ===")
    for iss in issues[:10]:
        print("  ", iss)
