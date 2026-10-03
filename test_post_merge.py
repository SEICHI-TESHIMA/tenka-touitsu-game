import sys
import json
import re
from collections import defaultdict
from simulate_merge import merged_officers_dict, merges_extended, merge_id_map

# Rename dummy successors to unique historical/appropriate names
rename_map = {
    'off_tsunemoto_succ_3': ('源為義', '河内源氏の棟梁。頼朝・義経の祖父。保元の乱で敗れるまで源氏一門を率いた。'),
    'off_kiyohara_succ_3': ('清原頼衡', '出羽の豪族清原氏の後裔として血脈を繋いだ。'),
    'off_iehira_succ_2': ('清原兼衡', '出羽山中に隠棲し、清原氏の命脈を保った。'),
    'off_hidesato_succ_3': ('藤原公清', '秀郷流藤原氏の正統として武蔵・下野の基盤を支えた。'),
    'off_kiyohara_succ_4': ('清原長衡', '鎌倉幕府のもとで出羽の在地領主として家名を保った。'),
    'off_succ_satake_1325_141': ('佐竹義春', '南北朝期に常陸守護佐竹氏の一門として家を支えた。'),
}

for oid, (new_name, new_lore) in rename_map.items():
    if oid in merged_officers_dict:
        merged_officers_dict[oid]['name'] = new_name
        merged_officers_dict[oid]['lore'] = new_lore

# Check duplicate names now
name_map = defaultdict(list)
for o in merged_officers_dict.values():
    name_map[o['name']].append(o)

dup_names = {k: v for k, v in name_map.items() if len(v) > 1}
print(f"Remaining duplicate names count: {len(dup_names)}")
for k, v in dup_names.items():
    print(f"\n{k} ({len(v)} entries):")
    for o in v:
        print(f"  {o['id']}: {o['birthYear']}-{o['deathYear']}, prov:{o.get('defaultProv')}")
