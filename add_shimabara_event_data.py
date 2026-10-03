import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

s_idx = text.find('window.HISTORICAL_EVENTS_DATA =') + len('window.HISTORICAL_EVENTS_DATA =')
e_idx = text.find('window.HISTORICAL_CASTLE_CHANGES =')
events_str = text[s_idx:e_idx].strip().rstrip(';')
events = json.loads(events_str)

# 1. Add/Update evt_1637_shimabara_outbreak
evt_1637 = {
    "id": "evt_1637_shimabara_outbreak",
    "scenarioId": "*",
    "year": 1637,
    "season": "冬",
    "title": "島原の乱勃発・天草四郎の蜂起と原城籠城",
    "desc": "肥前島原藩主・松倉勝家と肥後唐津藩主・寺沢堅高の苛酷を極める年貢取り立てとキリシタン弾圧に対し、島原・天草の領民・旧小西有馬遺臣ら三万七千が蜂起！16歳のカリスマ・天草四郎時貞を総大将に戴き、廃城となっていた原城に立て籠もって幕府へ反旗を翻した！九州全土が騒乱の渦に巻き込まれる！",
    "changes": {
        "territory": {
            "hizen": "amakusa"
        },
        "message": "肥前島原にて三万七千の民衆・キリシタンが蜂起！天草四郎時貞率いる一揆軍が肥前（原城）を掌握しました！"
    }
}

# 2. Update evt_1638_shimabara_fall
evt_1638 = {
    "id": "evt_1638_shimabara_fall",
    "scenarioId": "*",
    "year": 1638,
    "season": "春",
    "title": "原城総攻撃・島原の乱終結と天領化",
    "desc": "幕府追討総大将・知恵伊豆松平信綱の指揮のもと、細川忠利・立花宗茂・黒田忠之・水野勝成ら九州・西国諸大名十二万五千の大軍が原城へ総攻撃！天草四郎以下三万七千の一揆軍は壮絶に玉砕した。苛政の責任を問われ島原藩主・松倉勝家は斬首、肥前島原は幕府直轄天領となった！",
    "changes": {
        "territory": {
            "hizen": "tokugawa"
        },
        "message": "島原の乱が鎮圧され、反乱領地（肥前島原）が幕府直轄天領として厳重に管理されました！"
    }
}

# Update in events list
existing_idx_1637 = next((i for i, e in enumerate(events) if e['id'] == 'evt_1637_shimabara_outbreak'), None)
if existing_idx_1637 is not None:
    events[existing_idx_1637] = evt_1637
else:
    # Insert before evt_1638
    idx_1638 = next((i for i, e in enumerate(events) if e['id'] == 'evt_1638_shimabara_fall'), len(events))
    events.insert(idx_1638, evt_1637)

existing_idx_1638 = next((i for i, e in enumerate(events) if e['id'] == 'evt_1638_shimabara_fall'), None)
if existing_idx_1638 is not None:
    events[existing_idx_1638] = evt_1638

new_events_json = json.dumps(events, ensure_ascii=False, indent=2)
new_text = text[:s_idx] + " " + new_events_json + ";\n\n" + text[e_idx:]

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print(f"Successfully added Shimabara events to data.js! Total events: {len(events)}")
