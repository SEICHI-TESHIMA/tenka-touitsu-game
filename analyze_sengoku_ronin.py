import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('detailed_ronin_report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

scens = text.split('=======================================================')
for s in scens[1:]:
    lines = s.strip().split('\n')
    header = lines[0]
    sid = header.split(']')[0].replace('Scenario [', '')
    if any(yr in header for yr in ['1546', '1560', '1570', '1582', '1584', '1587', '1590', '1592', '1600', '1614']):
        print(f"\n*** {header} ***")
        for l in lines[3:]:
            parts = [p.strip() for p in l.split('|')]
            if len(parts) >= 4:
                oid, name, clan, defp = parts[0], parts[1], parts[2], parts[3]
                # Filter out generic generated officers if needed, or inspect notable
                if not oid.startswith('off_succ_') and not oid.startswith('off_succ2_'):
                    print(f"  {oid:26s} | {name:12s} | {clan:15s} | {defp}")

