/**
 * @file js/ai/ComputerLogic.js - CPU大名思考ルーチン・侵攻/内政/外交AI・城代補任
 * 戦国天下統一伝 ES6モジュール
 * @typedef {import('../types.js').Officer} Officer
 * @typedef {import('../types.js').Province} Province
 * @typedef {import('../types.js').PlayableDaimyo} PlayableDaimyo
 * @typedef {import('../types.js').Scenario} Scenario
 */

// モジュール間安全参照ヘルパー
var getClanAbility = (clanId) => (typeof window !== 'undefined' && typeof window.getClanAbility === 'function')
  ? window.getClanAbility(clanId)
  : ((typeof window !== 'undefined' && window.CLAN_ABILITIES?.[clanId]) || { politics: 60, military: 60, stratagem: 55, personality: 'balanced' });
var HISTORICAL_ALLIANCE_BONDS = (typeof window !== 'undefined' && window.HISTORICAL_ALLIANCE_BONDS) || [];
var AI_PERSONALITY_TUNING = (typeof window !== 'undefined' && window.AI_PERSONALITY_TUNING) || {
  aggressive: { attackProb: 0.60, requiredRatio: 0.98, forceRatio: 0.75, minSourceTroops: 1400, coalitionBoost: 0.25, coalitionCap: 0.88, ignoreRice: true,  allianceBonus: -0.08, frontShiftMax: 500 },
  balanced:   { attackProb: 0.25, requiredRatio: 1.25, forceRatio: 0.70, minSourceTroops: 1600, coalitionBoost: 0.25, coalitionCap: 0.75, ignoreRice: false, allianceBonus: 0 },
  domestic:   { attackProb: 0.07, requiredRatio: 1.45, forceRatio: 0.65, minSourceTroops: 1800, coalitionBoost: 0.15, coalitionCap: 0.40, ignoreRice: false, allianceBonus: 0.10 }
};

export class ComputerLogic {
  constructor(game) {
    this.game = game;
  }
}

export const ComputerLogicMethods = {
  processBlankProvinceUprisings() {
    if (!this.provinces || !this.activeOfficers) return 0;

    const blankProvs = this.provinces.filter(p => !p.ownerId || p.ownerId === 'null' || p.ownerId === 'undefined');
    if (blankProvs.length === 0) return 0;

    let totalUprisings = 0;

    for (const prov of blankProvs) {
      // その空白地を本拠・流浪地(defaultProv)としている浪人武将（生存武将）
      const localRonins = this.activeOfficers.filter(o => 
        o.clanId === 'ronin' && 
        !o.isDead && 
        o.defaultProv === prov.id
      );

      // 元大名を優先。いなければ一般浪人も一定確率で旗揚げ
      let candidates = localRonins.filter(o => this.isFormerDaimyo(o));
      if (candidates.length === 0) {
        const chance = window.RONIN_BLANK_UPRISING_CHANCE || 0.28;
        if (Math.random() > chance) continue;
        candidates = [...localRonins];
      }
      if (candidates.length === 0) continue;

      // 複数いる場合は能力値合計の最も高い武将を選出
      candidates.sort((a, b) => {
        const scoreA = (Number(a.military) || 0) + (Number(a.politic) || 0) + (Number(a.intel) || 0);
        const scoreB = (Number(b.military) || 0) + (Number(b.politic) || 0) + (Number(b.intel) || 0);
        return scoreB - scoreA;
      });
      const leader = candidates[0];

      // 元々のクランID（マスターデータ上のクランID）
      const masterOff = (window.OFFICERS_MASTER || []).find(m => m.id === leader.id);
      const origClanId = leader._originalClanId || masterOff?.clanId || null;

      // 現在そのクランがマップ上に大名として現存しているか確認
      const isClanActiveOnMap = origClanId && origClanId !== 'ronin' && this.provinces.some(p => p.ownerId === origClanId);

      let newClanId = origClanId;
      if (!newClanId || newClanId === 'ronin' || isClanActiveOnMap) {
        // すでに同名勢力が現存しているか、元IDがない場合は独立勢力IDを生成
        newClanId = 'clan_' + leader.id.replace(/^off_/, '');
      }

      // 領国データの更新
      prov.ownerId = newClanId;
      prov.governorId = leader.id;
      prov.governance = 'direct';
      const koku = Number(prov.kokudaka) || 50000;
      prov.troops = Math.max(prov.troops || 0, Math.round((koku / 1000) * 10 + 1200));
      prov.rice = Math.max(prov.rice || 0, Math.round(koku / 1000 * 1.5 + 40));
      prov.commerce = Math.max(prov.commerce || 0, Math.round(koku / 2000 * 1.5 + 30));
      prov.defense = Math.max(prov.defense || 0, 50);
      prov.morale = 85;
      prov.order = 85;

      // 当主武将データの更新
      leader.clanId = newClanId;
      leader.isDaimyo = true;
      leader.hasBeenDaimyo = true;
      leader.assignedProvId = prov.id;
      if (this.formerDaimyoIds) this.formerDaimyoIds.add(leader.id);

      // 本拠地と家名登録
      if (!window.CLAN_CAPITAL_PROVINCES) window.CLAN_CAPITAL_PROVINCES = {};
      window.CLAN_CAPITAL_PROVINCES[newClanId] = prov.id;
      if (!this.lastDaimyoNames) this.lastDaimyoNames = {};
      this.lastDaimyoNames[newClanId] = leader.name;
      if (!this.foundingLeaderNames) this.foundingLeaderNames = {};
      this.foundingLeaderNames[newClanId] = leader.name;

      // 旧臣・一門の同伴旗揚げ
      let joinedCount = 0;
      localRonins.forEach(r => {
        if (r.id !== leader.id && origClanId && (r.clanId === 'ronin' || r.clanId === origClanId)) {
          const rMaster = (window.OFFICERS_MASTER || []).find(m => m.id === r.id);
          if (rMaster?.clanId === origClanId || r._originalClanId === origClanId) {
            r.clanId = newClanId;
            r.isDaimyo = false;
            r.assignedProvId = null;
            joinedCount++;
          }
        }
      });

      const joinedNote = joinedCount > 0 ? `（旧臣${joinedCount}名も馳せ集まりました）` : '';
      const clanDisplayName = this.getClanFamilyName(newClanId);
      const castleName = prov.castleName || prov.castle || '城';
      this.log(`🚩【旗揚げ・御家再興】かつて大名であった名将・${leader.name}公が空白地の${prov.name}国（${castleName}）にて旗揚げし、【${clanDisplayName}】として天下に名乗りを上げました！${joinedNote}`, 'important');

      totalUprisings++;
    }

    if (totalUprisings > 0) {
      try { this.audio.playTaiko?.(); } catch(e) {}
      this.updateUI();
    }

    return totalUprisings;
  },

  // 御家滅亡時: ゆかりの地の城主が独立、残りは空白地化,

  resolveClanCollapseIndependence(clanId) {
    const chance = window.CASTELLAN_INDEPENDENCE_CHANCE || 0.32;
    const owned = this.provinces.filter(p => p.ownerId === clanId);
    const independentProvIds = new Set();

    owned.forEach(p => {
      const gov = p.governorId
        ? (this.activeOfficers || []).find(o => o.id === p.governorId && !o.isDead)
        : null;
      const isHomeCastellan = gov && gov.defaultProv === p.id && !gov.isDaimyo;
      if (isHomeCastellan && Math.random() < chance) {
        const newClanId = 'clan_' + gov.id.replace(/^off_/, '');
        p.ownerId = newClanId;
        p.governorId = gov.id;
        p.governance = 'direct';
        p.morale = Math.max(70, p.morale || 70);
        p.order = Math.max(60, p.order || 60);
        gov.clanId = newClanId;
        gov.isDaimyo = true;
        gov.hasBeenDaimyo = true;
        gov.assignedProvId = p.id;
        if (this.formerDaimyoIds) this.formerDaimyoIds.add(gov.id);
        if (!window.CLAN_CAPITAL_PROVINCES) window.CLAN_CAPITAL_PROVINCES = {};
        window.CLAN_CAPITAL_PROVINCES[newClanId] = p.id;
        this.lastDaimyoNames = this.lastDaimyoNames || {};
        this.lastDaimyoNames[newClanId] = gov.name;
        this.foundingLeaderNames = this.foundingLeaderNames || {};
        this.foundingLeaderNames[newClanId] = gov.name;
        independentProvIds.add(p.id);
        this.log(`🚩【城主独立】${gov.name}がゆかりの地・${p.name}にて独立し、新勢力を旗揚げしました！`, 'important');
      }
    });

    owned.forEach(p => {
      if (independentProvIds.has(p.id)) return;
      p.ownerId = null;
      p.governorId = null;
      p.troops = Math.max(500, Math.round((p.troops || 1000) * 0.5));
    });

    (this.activeOfficers || []).forEach(o => {
      if (o.clanId === clanId) {
        if (o.isDaimyo && independentProvIds.has(o.assignedProvId)) return;
        o.clanId = 'ronin';
        o.assignedProvId = null;
        o.isDaimyo = false;
      }
    });
  },

  // ============================================================================
  // 途中雇用・待機武将の本拠城主任命システム
  // 要望2: 各勢力に途中から雇い入れられた武将が待機中となっているケースが多いですが、
  // それらの武将が歴史上本拠地としたところで城主としてきちんと任命されるようにする
  // ============================================================================,

  staffComputerVacancies(clanId, branches, pool, aliveGov, seat) {
    const combat = (o) => (Number(o.military) || 0) * 2 + (Number(o.intel) || 0) + (Number(o.politic) || 0);
    const civil = (o) => (Number(o.politic) || 0) * 2 + (Number(o.intel) || 0) + (Number(o.military) || 0);
    const atHome = (o) => !!(o.assignedProvId && o.defaultProv === o.assignedProvId);
    let moved = 0;

    const availableForFront = () => pool.filter(o => {
      if (atHome(o)) return false;
      if (!o.assignedProvId) return true;
      const seatP = this.provinces.find(x => x.id === o.assignedProvId && x.governorId === o.id && x.ownerId === clanId);
      if (!seatP) return true;
      return !this.isClanFrontline(seatP);
    }).sort((a, b) => combat(b) - combat(a));

    const fronts = branches.filter(p => this.isClanFrontline(p))
      .sort((a, b) => this.frontlineWeight(b) - this.frontlineWeight(a));
    fronts.forEach(p => {
      const cur = aliveGov(p);
      if (cur && cur.defaultProv === p.id) return;
      const best = availableForFront()[0];
      if (!best || best.assignedProvId === p.id) return;
      if (cur && combat(cur) >= combat(best)) return;
      if (seat(p, best)) moved++;
    });

    const rears = branches.filter(p => !aliveGov(p) && !this.isClanFrontline(p))
      .sort((a, b) => (Number(b.kokudaka) || 0) - (Number(a.kokudaka) || 0));
    rears.forEach(p => {
      const next = pool.filter(o => !o.assignedProvId).sort((a, b) => civil(b) - civil(a))[0];
      if (next && seat(p, next)) moved++;
    });
    return moved;
  },

  // コンピューター勢力の支城は、まずゆかりの地の家臣を城主にする。
  // fillVacancies が真のときだけ、進行中の空き城を埋める。強い武将を前線へ、残りを後方の城へ。
  // シナリオ開始時の初期配置では fillVacancies を渡さない。本拠親政は対象外。
  // プレイヤー勢力は、国司在京・天領代官の城に限って同じ規則で任命する。,

  autoAppointComputerCastellans(options) {
    const fillVacancies = !!(options && options.fillVacancies);
    if (!this.provinces || !this.activeOfficers) return 0;

    const scenarioGovIds = new Set(Object.values(
      (window.SCENARIO_HISTORICAL_GOVERNORS && this.currentScenario)
        ? (window.SCENARIO_HISTORICAL_GOVERNORS[String(this.currentScenario.id)] || {})
        : {}
    ));
    const isUnlistedJodai = (o) => String(o.id || '').startsWith('off_jd_') && !scenarioGovIds.has(o.id);
    const pinnedGovs = (window.PINNED_SCENARIO_GOVERNORS && this.currentScenario)
      ? (window.PINNED_SCENARIO_GOVERNORS[String(this.currentScenario.id)] || {})
      : {};
    const score = (o) => (Number(o.politic) || 0) * 2 + (Number(o.intel) || 0) + (Number(o.military) || 0);
    const blocked = (p) => {
      if (!p || !p.ownerId) return true;
      if (this.isCapitalProvince(p.id, p.ownerId)) return true;
      if (p.ownerId === this.playerClanId && !this.getVacantRule(p, p.ownerId)) return true;
      return false;
    };
    const aliveGov = (p) => {
      if (!p || !p.governorId) return null;
      return this.activeOfficers.find(o => o.id === p.governorId && !o.isDead && o.clanId === p.ownerId) || null;
    };
    const seat = (prov, officer) => {
      if (!prov || !officer) return false;
      if (prov.governorId === officer.id && officer.assignedProvId === prov.id) return false;
      if (officer.assignedProvId && officer.assignedProvId !== prov.id) {
        const old = this.provinces.find(x => x.id === officer.assignedProvId);
        if (old && old.governorId === officer.id) old.governorId = null;
      }
      if (prov.governorId && prov.governorId !== officer.id) {
        const prev = this.activeOfficers.find(o => o.id === prov.governorId);
        if (prev && prev.assignedProvId === prov.id) prev.assignedProvId = null;
      }
      prov.governorId = officer.id;
      officer.assignedProvId = prov.id;
      return true;
    };

    const clanIds = [...new Set(this.provinces.map(p => p.ownerId).filter(id => id && id !== 'ronin' && id !== 'null'))];
    let total = 0;

    for (const clanId of clanIds) {
      const branches = this.provinces.filter(p => p.ownerId === clanId && !blocked(p));
      if (branches.length === 0) continue;

      this.activeOfficers.forEach(o => {
        if (o.clanId !== clanId || !o.assignedProvId) return;
        const seated = this.provinces.find(x => x.id === o.assignedProvId);
        if (!seated || seated.ownerId !== clanId || seated.governorId !== o.id) o.assignedProvId = null;
      });

      branches.forEach(p => {
        if (p.governorId && !aliveGov(p)) {
          const stale = this.activeOfficers.find(o => o.id === p.governorId);
          if (stale && stale.assignedProvId === p.id) stale.assignedProvId = null;
          p.governorId = null;
        }
      });

      const pool = this.activeOfficers.filter(o =>
        o.clanId === clanId && !o.isDead && !o.isDaimyo && !this.isCourtFigure(o) && !isUnlistedJodai(o)
      );

      const homes = new Map();
      pool.forEach(o => {
        if (!o.defaultProv) return;
        const home = branches.find(p => p.id === o.defaultProv);
        if (!home) return;
        const cur = aliveGov(home);
        if (cur && cur.defaultProv === home.id) return;
        // data.js の PINNED_SCENARIO_GOVERNORS で固定した史実城代は動かさない
        if (cur && pinnedGovs[home.id] === cur.id) return;
        if (!homes.has(home.id)) homes.set(home.id, []);
        homes.get(home.id).push(o);
      });

      homes.forEach((cands, provId) => {
        const home = branches.find(p => p.id === provId);
        if (clanId === this.playerClanId && aliveGov(home)) return;
        const movable = cands.filter(o => {
          if (clanId === this.playerClanId && o.assignedProvId && o.assignedProvId !== provId) return false;
          if (!o.assignedProvId || o.assignedProvId === provId) return true;
          const seated = this.provinces.find(p => p.id === o.assignedProvId && p.governorId === o.id);
          if (!seated) return true;
          if (this.isCapitalProvince(seated.id, seated.ownerId)) return false;
          if (o.defaultProv === seated.id) return false;
          return true;
        });
        movable.sort((a, b) => score(b) - score(a));
        const best = movable[0];
        if (best && seat(home, best)) total++;
      });

      // シナリオ開始時はここまで。進行中だけ、ゆかり以外の待機を前線から埋める。
      if (fillVacancies) total += this.staffComputerVacancies(clanId, branches, pool, aliveGov, seat);
    }

    const inGame = document.getElementById('startModal')?.classList.contains('hidden');
    if (total > 0 && inGame) {
      this.log(`🏯【城主配置】諸大名はゆかりの地を優先し、前線と空き城へ家臣${total}名を城主に任命しました。`);
    }
    return total;
  },

  // シナリオを切り替えるたびに、史実本拠の初期値へ戻してから「今領有している城」へ合わせる,

  toggleAutoPlay() {
    if (this.isAutoPlay) {
      this.stopAutoPlay('手動停止');
    } else {
      this.startAutoPlay();
    }
  },

  runAutoStep() {
    if (!this.isAutoPlay) return;

    try {
      if (this.inBattle) {
        this.stopAutoPlay('合戦発生のため');
        return;
      }

      const defeatModal = document.getElementById('defeatModal');
      if (defeatModal && !defeatModal.classList.contains('hidden')) {
        this.stopAutoPlay('御家滅亡のため');
        return;
      }

      if (this.autoPlayPausedForEvent || this.isEventChoiceOpen()) {
        this.pauseAutoPlayForEvent();
        return;
      }

      if (this.tryAutoAcknowledgeDialogs()) {
        this.scheduleNextAutoSeason();
        return;
      }

      // 「季節を進める」ボタンに押下パルスアニメーション演出
      const nextBtn = document.getElementById('nextTurnBtn');
      if (nextBtn) {
        nextBtn.classList.add('auto-trigger-pulse');
        setTimeout(() => {
          nextBtn.classList.remove('auto-trigger-pulse');
        }, Math.min(80, Math.round(this.autoPlaySpeed * 1000 / 2)));
      }

      // 季節進行
      this.nextSeason();

      // イベント選択で止まっている間は次の期を進めない
      if (this.isAutoPlay && !this.autoPlayPausedForEvent && !this.isEventChoiceOpen()) {
        this.scheduleNextAutoSeason();
      }
    } catch (err) {
      console.error('オート進行エラー', err);
      this.log('⚠【季節オート進行】進行中に不具合が起きたため、次の期へ続行します。');
      if (this.isAutoPlay && !this.autoPlayPausedForEvent && !this.isEventChoiceOpen()) {
        this.scheduleNextAutoSeason();
      }
    }
  },

  // ============================================================================
  // 季節を進める (ターン終了・委任実行・AI思考・包囲網・自動セーブ)
  // ============================================================================,

  executeAiDiplomacy() {
    if (this.seasonIdx !== 0) return;
    const alive = new Set((this.provinces || []).map(p => p.ownerId).filter(Boolean));
    const bonds = HISTORICAL_ALLIANCE_BONDS.filter(bond =>
      this.year >= bond.from && this.year <= bond.to && alive.has(bond.a) && alive.has(bond.b)
    );
    bonds.sort((a, b) => {
      const aPlayer = (a.a === this.playerClanId || a.b === this.playerClanId) ? 1 : 0;
      const bPlayer = (b.a === this.playerClanId || b.b === this.playerClanId) ? 1 : 0;
      if (aPlayer !== bPlayer) return bPlayer - aPlayer;
      const aFresh = (this.year - a.from) <= 1 ? 1 : 0;
      const bFresh = (this.year - b.from) <= 1 ? 1 : 0;
      if (aFresh !== bFresh) return bFresh - aFresh;
      return Math.random() - 0.5;
    });

    let formed = 0;
    const maxForm = 3;
    const now = this.year * 4 + this.seasonIdx;
    for (const bond of bonds) {
      if (formed >= maxForm) break;
      if (this.isAllied(bond.a, bond.b)) continue;
      if (!bond.remote && !this.clansShareBorder(bond.a, bond.b)) continue;
      const key = [bond.a, bond.b].sort().join('|');
      const cooledAt = this.allianceCooldown ? this.allianceCooldown[key] : null;
      if (cooledAt != null && now - cooledAt < 4) continue;

      const fresh = (this.year - bond.from) <= 1;
      let chance = fresh ? 0.85 : 0.4;
      const abA = getClanAbility(bond.a);
      const abB = getClanAbility(bond.b);
      if (abA.personality === 'domestic' || abB.personality === 'domestic') chance += AI_PERSONALITY_TUNING.domestic.allianceBonus;
      // 攻勢型は手を縛られる同盟を嫌う（特にプレイヤーと国境を接している時は、同盟より切り取りを優先）
      [bond.a, bond.b].forEach(id => {
        if (id === this.playerClanId) return;
        if (getClanAbility(id).personality !== 'aggressive') return;
        chance += AI_PERSONALITY_TUNING.aggressive.allianceBonus;
        if (this.playerClanId && this.clansShareBorder(id, this.playerClanId)) chance -= 0.06;
      });
      if (this.clanFeelsThreatened(bond.a) || this.clanFeelsThreatened(bond.b)) chance += 0.12;
      if (Math.random() > Math.min(0.95, chance)) continue;

      if (!this.alliances) this.alliances = [];
      this.alliances.push({
        members: [bond.a, bond.b],
        formedYear: this.year,
        formedSeason: this.seasonIdx
      });
      formed++;
      const involvesPlayer = bond.a === this.playerClanId || bond.b === this.playerClanId;
      const partnerId = bond.a === this.playerClanId ? bond.b : (bond.b === this.playerClanId ? bond.a : null);
      if (involvesPlayer && partnerId) {
        this.log(`🤝【諸侯同盟】${this.allianceClanLabel(partnerId)}が${bond.label}を申し出て、貴家と二年間の同盟を結びました。`, 'important');
      } else {
        this.log(`🤝【諸侯同盟】${this.allianceClanLabel(bond.a)}と${this.allianceClanLabel(bond.b)}が${bond.label}を結びました。約定は二年です。`);
      }
    }
  },

  aiClanSupplyRatio(clanId) {
    const provs = (this.provinces || []).filter(p => p.ownerId === clanId);
    if (provs.length === 0) return 1;
    let cur = 0, base = 0;
    provs.forEach(p => {
      const init = (window.PROVINCES_DATA || []).find(item => item.id === p.id);
      cur += Number(p.rice) || 0;
      base += Math.max(20, Math.round((Number(init?.kokudaka) || 50000) / 1000));
    });
    return base > 0 ? cur / base : 1;
  },

  async executeAiTurn() {
    this.executeAiDiplomacy();

    // 1. 兵力増加のゲームバランス適正化 (複利爆発を撤廃し、石高に応じた上限と性格別成長)
    const allClanIds = [...new Set(this.provinces.map(p => p.ownerId))].filter(id => id !== this.playerClanId);

    // プレイヤー後方領国も治安良好なら緩やかに自然補充 (40〜80人)
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    myProvs.forEach(p => {
      const maxTroops = p.rice * 12 + 2500;
      if (!this.isProvinceFrontier(p) && (p.order || 80) >= 70 && p.troops < maxTroops) {
        const naturalRecovery = Math.round(40 + Math.random() * 40);
        p.troops = Math.min(maxTroops, p.troops + naturalRecovery);
      }
    });

    // AI諸大名の領国統治と兵備 (非同期ループでUIフリーズを防止)
    for (const clanId of allClanIds) {
      const clanProvs = this.provinces.filter(p => p.ownerId === clanId);
      if (clanProvs.length === 0) continue;

      const ability = getClanAbility(clanId);
      const personality = ability.personality; // aggressive / balanced / domestic
      const milRatio = (ability.military || 70) / 100;
      const polRatio = (ability.politics || 70) / 100;

      clanProvs.forEach(p => {
        // 石高に応じた兵力上限（石高×10 + 2000）でインフレを完全に防止
        const maxTroops = p.rice * 10 + 2000;

        if (personality === 'domestic') {
          // 内政型：城防・治安の維持が最優先、兵力は上限まで堅実に小幅補充（自国をガチガチに固める）
          const isBorder = (p.neighbors || []).some(nId => {
            const n = this.provinces.find(x => x.id === nId);
            return n && n.ownerId && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId);
          });
          p.defense = Math.min(100, p.defense + (isBorder ? 4 : 3));
          p.order = Math.min(100, (p.order || 80) + 4);
          p.morale = Math.min(100, (Number(p.morale) || 70) + 1);
          // 開墾：ときどき石高が伸びる（基準石高の1.5倍まで）
          if (Math.random() < 0.2) {
            const init = (window.PROVINCES_DATA || []).find(item => item.id === p.id);
            const cap = Math.round((Number(init?.kokudaka) || 50000) / 1000 * 1.5);
            if (p.rice < cap) p.rice += 1;
          }
          if (p.troops < maxTroops) {
            p.troops = Math.min(maxTroops, p.troops + Math.round(40 + polRatio * 40));
          }
        } else if (personality === 'balanced') {
          // バランス型：攻守の均衡
          p.defense = Math.min(100, p.defense + 1);
          if (p.troops < maxTroops) {
            p.troops = Math.min(maxTroops, p.troops + Math.round(50 + milRatio * 50));
          }
        } else {
          // 攻勢型：前線に兵員を集中補充
          const isFrontier = (p.neighbors || []).some(nId => {
            const n = this.provinces.find(x => x.id === nId);
            return n && n.ownerId !== clanId;
          });
          const gain = isFrontier ? Math.round(70 + milRatio * 70) : Math.round(40 + milRatio * 30);
          if (p.troops < maxTroops) {
            p.troops = Math.min(maxTroops, p.troops + gain);
          }
          // 攻勢型は治安より軍備：後方の治安は緩む
          if (!isFrontier && (p.order || 80) > 60 && Math.random() < 0.3) p.order = (p.order || 80) - 1;
        }
      });

      // 攻勢型：後方の余剰兵を隣接する自軍前線へ集中（兵站を顧みない前線集中）
      if (personality === 'aggressive') {
        const isFront = (q) => (q.neighbors || []).some(nId => {
          const n = this.provinces.find(x => x.id === nId);
          return n && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId);
        });
        clanProvs.filter(q => !isFront(q) && q.troops > 2200).forEach(q => {
          const front = (q.neighbors || [])
            .map(nId => this.provinces.find(x => x.id === nId))
            .filter(n => n && n.ownerId === clanId && isFront(n))
            .sort((a, b) => b.troops - a.troops)[0];
          if (!front) return;
          const move = Math.min(AI_PERSONALITY_TUNING.aggressive.frontShiftMax, Math.round((q.troops - 2000) * 0.25));
          if (move <= 0) return;
          q.troops -= move;
          front.troops += move;
        });
      }

      // メインスレッドのフリーズを防止するため非同期解放
      await new Promise(resolve => setTimeout(resolve, 0));
    }

    // 2. AI侵攻判断（「適宜バランスよく攻め込む」：1ターン最大3戦線に制御）
    let battleCount = 0;
    const maxBattlesPerTurn = 3;

    // 行動順をシャッフル（大名の攻勢型優先）
    const sortedClanIds = allClanIds.sort((a, b) => {
      const aAb = getClanAbility(a);
      const bAb = getClanAbility(b);
      const aScore = aAb.personality === 'aggressive' ? 2 : aAb.personality === 'balanced' ? 1 : 0;
      const bScore = bAb.personality === 'aggressive' ? 2 : bAb.personality === 'balanced' ? 1 : 0;
      return (bScore - aScore) || (Math.random() - 0.5);
    });

    for (const clanId of sortedClanIds) {
      if (battleCount >= maxBattlesPerTurn) break;
      // 領主のいない空白地（国人・土豪）や、当主不在の勢力は他国へ攻め込まない
      if (!this.clanHasLivingLord(clanId)) continue;

      const clanProvs = this.provinces.filter(p => p.ownerId === clanId);
      if (clanProvs.length === 0) continue;

      const ability = getClanAbility(clanId);
      const personality = ability.personality;

      // 性格に応じた侵攻確率の調整（AI_PERSONALITY_TUNING）
      const tune = AI_PERSONALITY_TUNING[personality] || AI_PERSONALITY_TUNING.balanced;
      const threatened = this.clanFeelsThreatened(clanId);
      let attackProb = tune.attackProb;

      // 包囲網結成時やプレイヤー勢力拡大時は包囲網参加大名が好戦的に（内政型は控えめに）
      const myProvsCount = this.provinces.filter(p => p.ownerId === this.playerClanId).length;
      if (this.coalitionFormed || myProvsCount >= 12) {
        attackProb = Math.min(tune.coalitionCap, attackProb + tune.coalitionBoost);
      }
      // 内政型は多正面作戦をほぼ起こさない：既に他所で戦が起きている季は更に自重
      if (personality === 'domestic' && battleCount > 0 && !threatened) attackProb *= 0.5;

      // 兵糧事情：飢饉で石高が落ちている・冬季は、攻勢型以外は出陣を控える（攻勢型は兵糧を無視して出陣）
      if (!tune.ignoreRice) {
        const supply = this.aiClanSupplyRatio(clanId);
        if (supply < 0.75) attackProb *= personality === 'domestic' ? 0.2 : 0.5;
        if (this.seasonIdx === 3) attackProb *= personality === 'domestic' ? 0.4 : 0.75;
      }

      if (Math.random() > attackProb) continue;

      // 前線国を選定（自勢力以外かつ非同盟国の領国に隣接）
      const frontierProvs = clanProvs.filter(p => {
        return (p.neighbors || []).some(nId => {
          const n = this.provinces.find(x => x.id === nId);
          return n && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId);
        });
      });
      if (frontierProvs.length === 0) continue;

      // 最も兵力が多い前線国から出陣（最低出陣下限: 攻勢型1400 / 均衡1600 / 内政1800人）
      const srcProv = frontierProvs.sort((a, b) => b.troops - a.troops)[0];
      if (srcProv.troops < tune.minSourceTroops) continue;

      // 侵攻可能な隣接敵国（同盟国は除外）
      const targets = (srcProv.neighbors || [])
        .map(nId => this.provinces.find(x => x.id === nId))
        .filter(n => n && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId));
      if (targets.length === 0) continue;

      const playerTargets = targets.filter(n => n.ownerId === this.playerClanId && !n.justConquered);
      const otherTargets = targets.filter(n => n.ownerId !== this.playerClanId);

      let target;
      if ((this.coalitionFormed || personality === 'aggressive') && playerTargets.length > 0) {
        target = playerTargets.sort((a, b) => a.troops - b.troops)[0];
      } else if (personality === 'domestic' && !this.coalitionFormed && !threatened) {
        // 内政型は脅威を感じていなければプレイヤーへは手を出さず、弱い隣国（空白地優先）だけを狙う
        target = otherTargets.sort((a, b) => (a.ownerId ? 1 : 0) - (b.ownerId ? 1 : 0) || a.troops - b.troops)[0];
      } else {
        const allTargets = [...playerTargets, ...otherTargets];
        target = allTargets.sort((a, b) => a.troops - b.troops)[0];
      }

      if (!target) continue;

      // 出陣兵力（攻勢型75% / 均衡70% / 内政65%を出陣、残りは守備に残す）
      const attackForce = Math.round(srcProv.troops * tune.forceRatio);

      // 性格に応じた勝算基準（必要兵力比）
      // 攻勢型: 0.98倍以上、バランス型: 1.25倍以上、内政型: 1.45倍以上で出陣
      const requiredRatio = tune.requiredRatio;
      if (attackForce < target.troops * requiredRatio) continue;

      // ===== 合戦発生！ =====
      battleCount++;
      const isAttackingPlayer = target.ownerId === this.playerClanId;
      const attackerName = this.getClanFamilyName(clanId);
      const defenderName = isAttackingPlayer
        ? `我が${this.playerDaimyo?.clan || '軍'}` : this.getClanFamilyName(target.ownerId);

      // 攻め込んだ時の効果音再生！
      const canPlayBattleSfx = !this.isAutoPlay || this.autoPlaySpeed >= 0.3;
      if (isAttackingPlayer) {
        // プレイヤーへの攻撃時：緊迫した法螺貝と激しい陣太鼓！
        if (canPlayBattleSfx) {
          this.audio.playHoragai(0.95);
          setTimeout(() => {
            this.audio.playTaiko(1.4);
            this.audio.playGachaGacha(1.2);
          }, 280);
        }
      } else {
        // AI同士の合戦時：遠くで響く陣太鼓で臨場感を演出！
        if (canPlayBattleSfx) {
          this.audio.playTaiko(0.75);
        }
      }

      // 戦闘結果の計算 (各大名軍事能力反映 + 陣形三すくみ・地形)
      const targetAbility = getClanAbility(target.ownerId);
      const atkForm = this.pickEnemyFormation(clanId, target, null);
      const defForm = this.pickEnemyFormation(target.ownerId, target, atkForm);
      const rps = this.getRpsMultipliers(atkForm, defForm);
      const atkTerrain = this.getTerrainDealtBonus(atkForm, target);
      const defTerrain = this.getTerrainDealtBonus(defForm, target);
      const attackPower = attackForce * (ability.military / 65) * (0.85 + Math.random() * 0.35) * rps.dealt * atkTerrain;
      const defensePower = target.troops * (target.defense / 80) * (targetAbility.military / 65) * (0.85 + Math.random() * 0.35) * rps.taken * defTerrain;
      const attackerWins = attackPower > defensePower;

      srcProv.troops -= Math.round(attackForce * 0.25);

      if (attackerWins) {
        const remainTroops = Math.max(500, Math.round(attackForce * 0.65));
        const oldOwner = target.ownerId;
        this.handleProvinceLoss(target, oldOwner);
        target.ownerId = clanId;
        target.troops = remainTroops;
        target.defense = Math.max(35, target.defense - 25);
        target.morale = 75;

        if (isAttackingPlayer) {
          this.audio.playHyoshigi();
          this.log(`⚔【敵襲・領地喪失】${attackerName}軍が${target.name}に電撃侵攻！我が守備軍は敗れ城を奪われました！`, 'battle');
          this.showOrderResult('⚔️ 敵軍侵攻！領地喪失', `${target.name} が ${attackerName}に攻略されました！`, '#e74c3c');
          if (this.selectedProvId === target.id) {
            this.selectedProvId = null;
          }
        } else {
          this.log(`⚔【群雄動乱】${attackerName}が${target.name}へ進攻！激闘の末、${defenderName}軍を破り領国を奪回・併合しました。`);
        }
      } else {
        // 撃退
        const defRemain = Math.max(300, Math.round(target.troops * 0.75));
        target.troops = defRemain;
        target.defense = Math.max(20, target.defense - 15);
        srcProv.troops -= Math.round(attackForce * 0.35);

        if (isAttackingPlayer) {
          this.audio.playFanfare();
          this.log(`🛡【防衛成功】${attackerName}軍の${target.name}侵攻を我が軍が頑強に撃退しました！`, 'important');
          this.showOrderResult('🛡️ 敵襲撃退！', `${target.name}にて ${attackerName}軍の撃退に成功しました！`, '#2ecc71');
        } else {
          this.log(`🛡【防戦】${defenderName}軍が${target.name}にて${attackerName}軍の猛攻を退けました。`);
        }
      }
    }
  },

  executeGovernanceTurn() {
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    let domesticCount = 0;
    let militaryCount = 0;
    let logisticsCount = 0;
    let totalMovedTroops = 0;
    const conqueredProvinces = [];

    // 1. 各方針に基づく領国発展・徴募・兵站
    myProvs.forEach(p => {
      const effStats = this.getEffectiveStats(p.id);
      const mult = effStats.isDirectRule ? 0.5 : 1.0;
      const polBonus = (effStats.politics || 50) / 70;
      const milBonus = (effStats.military || 50) / 70;

      if (p.governance === 'domestic') {
        const dRice = Math.round(20 * mult * polBonus);
        const dComm = Math.round(20 * mult * polBonus);
        p.rice += dRice;
        p.commerce += dComm;
        this.gold += Math.round(30 * mult * polBonus);
        this.rice += Math.round(40 * mult * polBonus);
        domesticCount++;
      } else if (p.governance === 'military') {
        p.troops += Math.round(300 * mult * milBonus);
        p.defense = Math.min(100, p.defense + Math.round(6 * mult));
        p.morale = Math.min(100, p.morale + Math.round(4 * mult));
        militaryCount++;
      } else if (p.governance === 'balanced') {
        p.troops += Math.round(150 * mult * milBonus);
        p.rice += Math.round(8 * mult * polBonus);
        p.commerce += Math.round(8 * mult * polBonus);
        p.defense = Math.min(100, p.defense + Math.round(3 * mult));
      } else if (p.governance === 'logistics') {
        if (p.troops > 2000) {
          const surplus = Math.min(1500, p.troops - 2000);
          const frontierTarget = (p.neighbors || [])
            .map(nId => this.provinces.find(x => x.id === nId))
            .find(x => x && x.ownerId === this.playerClanId && this.isProvinceFrontier(x));

          if (frontierTarget) {
            p.troops -= surplus;
            frontierTarget.troops += surplus;
            totalMovedTroops += surplus;
            logisticsCount++;
          }
        }
      }
    });

    // 2. 軍事委任領国による自律進攻（勝手に攻め込んで領土拡大！）
    const militaryFrontiers = myProvs.filter(p => p.governance === 'military' && this.isProvinceFrontier(p))
      .sort((a, b) => b.troops - a.troops);

    const attackedProvIds = new Set();
    let attackActions = 0;
    const maxAutonomousAttacks = 3; // 1ターン最大3戦線で自律進攻

    for (const srcProv of militaryFrontiers) {
      if (attackActions >= maxAutonomousAttacks) break;
      if (srcProv.troops < 1500) continue; // 最低1500人以上の軍勢が必要
      if (this.rice < 60) break; // 兵糧枯渇時は自重

      // 隣接する敵国（今ターン未攻撃の国）
      const enemyNeighbors = (srcProv.neighbors || [])
        .map(nId => this.provinces.find(x => x.id === nId))
        .filter(n => n && n.ownerId !== this.playerClanId && !this.isAllied(this.playerClanId, n.ownerId) && !attackedProvIds.has(n.id));

      if (enemyNeighbors.length === 0) continue;

      // 出陣兵力：70%（守備30%は本拠に残す）
      const attackForce = Math.round(srcProv.troops * 0.7);

      // 勝算のある敵国を選定（出陣兵力が敵の0.8倍以上、または自軍兵力が敵を上回る）
      const viableTargets = enemyNeighbors
        .filter(target => attackForce >= target.troops * 0.8 || srcProv.troops > target.troops)
        .sort((a, b) => (a.troops * a.defense) - (b.troops * b.defense));

      if (viableTargets.length === 0) continue;

      const target = viableTargets[0];
      attackedProvIds.add(target.id);
      attackActions++;

      // 兵糧消費（出陣兵力の10%程度、最低50）
      const riceCost = Math.min(this.rice, Math.max(50, Math.round(attackForce * 0.1)));
      this.rice = Math.max(0, this.rice - riceCost);

      // 戦闘力判定（城主能力・直轄ペナルティを反映）
      const srcEff = this.getEffectiveStats(srcProv.id);
      const targetEff = this.getEffectiveStats(target.id);
      const attackPower = attackForce * (srcEff.military / 60) * (0.9 + Math.random() * 0.35);
      const defensePower = target.troops * (target.defense / 80) * (targetEff.military / 60) * (0.8 + Math.random() * 0.4);
      const won = attackPower > defensePower;

      const enemyClanId = target.ownerId;
      const enemyClanName = this.getClanFamilyName(enemyClanId);

      if (won) {
        // 攻略成功！
        const remainTroops = Math.max(1200, Math.round(attackForce * 0.75));
        srcProv.troops = Math.max(600, srcProv.troops - attackForce);

        this.handleProvinceLoss(target, enemyClanId);
        target.ownerId = this.playerClanId;
        target.troops = remainTroops;
        target.defense = Math.max(50, target.defense);
        target.morale = 80;
        target.governance = 'military'; // 新規攻略地も軍事進攻型を付与して前線基地化
        target.justConquered = true; // 今ターンの攻略直後保護フラグ（敵AI即時奪還防止）

        conqueredProvinces.push({
          srcName: srcProv.name,
          targetName: target.name,
          enemyClanName: enemyClanName
        });

        this.log(`🎌【委任軍快進撃！】${srcProv.name}の委任軍が敵領【${target.name}】（${enemyClanName}領）へ電撃進攻！見事攻略し我が領土に組み入れました！`, 'important');

        // 敵大名滅亡チェック
        const remainingEnemyProvs = this.provinces.filter(p => p.ownerId === enemyClanId);
        if (remainingEnemyProvs.length === 0) {
          this.log(`💀【御家滅亡】${enemyClanName}は全領国を失い、完全に滅亡しました！`, 'battle');
        }
      } else {
        // 攻略失敗（撤退）
        srcProv.troops = Math.max(500, srcProv.troops - Math.round(attackForce * 0.35));
        target.troops = Math.max(300, Math.round(target.troops * 0.75));
        this.log(`⚔【委任軍合戦】${srcProv.name}の委任軍が【${target.name}】（${enemyClanName}領）へ進攻するも、敵の堅い守りに阻まれ撤退しました。`);
      }
    }

    // 委任進攻結果の演出
    if (conqueredProvinces.length > 0) {
      this.audio.playFanfare();
      const conqueredNames = conqueredProvinces.map(c => `${c.targetName} (${c.enemyClanName}領)`).join('・');
      this.showOrderResult('🎌 委任軍 領土攻略！', `${conqueredNames} を電撃攻略！`, '#2ecc71');
    }

    if (domesticCount > 0 || militaryCount > 0 || logisticsCount > 0 || conqueredProvinces.length > 0) {
      const conqueredMsg = conqueredProvinces.length > 0 ? `、前線委任軍が【${conqueredProvinces.length}カ国】を攻略領有` : '';
      this.log(`【委任統治報告】内政型${domesticCount}国で開発、軍事進攻型${militaryCount}国で増強${conqueredMsg}、兵站型から前線へ兵${totalMovedTroops.toLocaleString()}人を輸送完了。`);
    }
  },

  // 自動セーブ,

};
