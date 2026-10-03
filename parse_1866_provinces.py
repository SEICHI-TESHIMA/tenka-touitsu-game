import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Officers
idx_off = text.find('window.OFFICERS_MASTER = [')
end_off = text.find('];', idx_off)
officers = json.loads(text[idx_off + len('window.OFFICERS_MASTER = '): end_off + 1])

# Scenarios
idx_scen = text.find('window.SCENARIOS_DATA = [')
end_scen = text.find('];\n\nwindow.CLAN_MASTER_DATA', idx_scen)
if end_scen == -1:
    end_scen = text.find('];', idx_scen)

scenarios = json.loads(text[idx_scen + len('window.SCENARIOS_DATA = '): end_scen + 1])

scen_1866 = next(s for s in scenarios if str(s['id']) == '1866')
print("Scenario 1866 title:", scen_1866.get('title'))
prov_owners = scen_1866.get('owners', {})
print("Total provinces in 1866:", len(prov_owners))
owners_1866 = set(prov_owners.values())
print("Unique owners in 1866:", sorted(list(owners_1866)))

print("north_shinano owner:", prov_owners.get('north_shinano'))
print("south_shinano owner:", prov_owners.get('south_shinano'))
print("musashi owner:", prov_owners.get('musashi'))
print("satsuma owner:", prov_owners.get('satsuma'))
print("nagato owner:", prov_owners.get('nagato'))
print("suo owner:", prov_owners.get('suo'))

# Check alive officers in 1866
alive_1866 = [o for o in officers if (o.get('birthYear', 9999) <= 1866 <= o.get('deathYear', -9999))]
print(f"\nTotal alive in 1866: {len(alive_1866)}")

# Check their clanId and whether their clan is in owners_1866
unlanded = []
for o in alive_1866:
    clan = o.get('clanId')
    if clan not in owners_1866:
        unlanded.append(o)

print(f"Alive with unlanded clan: {len(unlanded)}")
for o in unlanded:
    print(f"  {o['id']:<30} {o['name']:<15} clan:{o.get('clanId',''):<15} {o.get('birthYear')}-{o.get('deathYear')} prov:{o.get('defaultProv')}")
