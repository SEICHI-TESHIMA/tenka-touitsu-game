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
        o.clanId === clanId && !o.isDead && !o.isDaimyo && !this.isCourtFigure(o) && !isUnlistedJodai(o) && !o.isStandby
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
          if (pinnedGovs[seated.id] === o.id) return false;
          const scenGovMap = (window.SCENARIO_HISTORICAL_GOVERNORS && this.currentScenario)
            ? (window.SCENARIO_HISTORICAL_GOVERNORS[String(this.currentScenario.id)] || {})
            : {};
          if (scenGovMap[seated.id] === o.id) return false;
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

  /**
   * オート進行時の大名・軍師自動政務
   * オート進行中、プレイヤーのAPが残っている場合に大名と軍師が本拠・直轄地を自動統治
   */
  executeAutoDaimyoGovernance() {
    if (this.ap <= 0) return;
    const myProvs = (this.provinces || []).filter(p => p.ownerId === this.playerClanId);
    if (myProvs.length === 0) return;

    const capitalId = (window.CLAN_CAPITAL_PROVINCES && window.CLAN_CAPITAL_PROVINCES[this.playerClanId]) || myProvs[0].id;
    const capital = this.provinces.find(p => p.id === capitalId) || myProvs[0];

    while (this.ap > 0) {
      // 1. 治安危機領国（治安65以下）があれば治安向上を最優先
      const endangeredOrder = myProvs.find(p => (Number(p.order) || 80) <= 65 && this.gold >= 30);
      if (endangeredOrder) {
        this.ap -= 1;
        this.gold -= 30;
        endangeredOrder.order = Math.min(100, (Number(endangeredOrder.order) || 80) + 15);
        this.log(`📜【オート政務・徳政施策】軍師の進言により、治安の低下した${endangeredOrder.name}へ施策を行い治安を回復しました。(治安+15)`);
        continue;
      }

      // 2. 本拠地兵力が少なければ募兵（兵糧・金に余裕がある場合）
      const maxCapitalTroops = (Number(capital.rice) || 100) * 10 + 2000;
      if ((capital.troops || 0) < maxCapitalTroops * 0.75 && this.gold >= 50 && this.rice >= 50) {
        this.ap -= 1;
        this.gold -= 50;
        this.rice -= 50;
        const recruitCount = Math.round(350 + Math.random() * 200);
        capital.troops = (capital.troops || 0) + recruitCount;
        this.log(`🚩【オート政務・兵員徴募】本拠・${capital.name}にて兵員${recruitCount}人を徴募・訓練しました。`);
        continue;
      }

      // 3. 資金に余裕があれば本拠地を開墾・商業開発
      if (this.gold >= 60) {
        this.ap -= 1;
        this.gold -= 40;
        capital.rice = (Number(capital.rice) || 50) + 2;
        capital.commerce = (Number(capital.commerce) || 50) + 2;
        capital.defense = Math.min(100, (Number(capital.defense) || 50) + 2);
        this.log(`🌾【オート政務・本拠開発】本拠・${capital.name}にて開墾・治水と城壁修築を実施しました。(石高+2, 城防+2)`);
        continue;
      }

      break;
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

      // オート進行時の大名・軍師による自動政務（APを無駄にせず有効活用）
      this.executeAutoDaimyoGovernance();

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

  /**
   * AI思考改善第4弾: 謀略AI（AI大名による調略・流言・扇動・防諜戦）
   */
  async executeAiStratagems() {
    if (!this.provinces || this.provinces.length === 0) return;
    const allClanIds = [...new Set(this.provinces.map(p => p.ownerId))].filter(id => id && id !== 'null' && id !== 'ronin');
    const aiClanIds = allClanIds.filter(id => id !== this.playerClanId);
    if (aiClanIds.length === 0) return;

    // 1季あたりの最大工作件数（過度な頻発を防ぐ: 最大2件、プレイヤー向けは最大1件）
    let stratagemCount = 0;
    const maxStratagemsPerSeason = 2;
    let targetPlayerCount = 0;

    // 各大名の知謀スコアでソート（知将・策士タイプを優先）
    const sortedClans = aiClanIds.map(clanId => {
      const power = this.getClanStratagemPower ? this.getClanStratagemPower(clanId) : 55;
      const ab = getClanAbility(clanId);
      return { clanId, power, ability: ab };
    }).filter(c => c.power >= 60) // 知謀60以上の勢力のみ工作を検討
      .sort((a, b) => b.power - a.power || (Math.random() - 0.5));

    for (const { clanId, power } of sortedClans) {
      if (stratagemCount >= maxStratagemsPerSeason) break;
      if (!this.clanHasLivingLord(clanId)) continue;

      // 発令確率の判定（知謀が高いほど高確率、最大35%程度）
      const baseProb = Math.max(0.05, (power - 55) * 0.008);
      const threatened = this.clanFeelsThreatened(clanId);
      const prob = threatened ? baseProb * 1.3 : baseProb;
      if (Math.random() > prob) continue;

      // 前線城の探索
      const myProvs = this.provinces.filter(p => p.ownerId === clanId);
      const frontierProvs = myProvs.filter(p => {
        return (p.neighbors || []).some(nId => {
          const n = this.provinces.find(x => x.id === nId);
          return n && n.ownerId && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId);
        });
      });
      if (frontierProvs.length === 0) continue;

      // 隣接する敵領国の候補を抽出
      const potentialTargets = [];
      frontierProvs.forEach(src => {
        (src.neighbors || []).forEach(nId => {
          const tgt = this.provinces.find(x => x.id === nId);
          if (tgt && tgt.ownerId && tgt.ownerId !== clanId && !this.isAllied(clanId, tgt.ownerId)) {
            potentialTargets.push({ src, target: tgt });
          }
        });
      });
      if (potentialTargets.length === 0) continue;

      // ターゲット評価:
      // 1) プレイヤー城で直轄地（城主不在＝防諜手薄！）は格好の標的
      // 2) 治安が乱れている城
      // 3) 次の侵攻目標候補
      potentialTargets.sort((a, b) => {
        const aTgt = a.target;
        const bTgt = b.target;
        const aIsPlayer = aTgt.ownerId === this.playerClanId ? 1 : 0;
        const bIsPlayer = bTgt.ownerId === this.playerClanId ? 1 : 0;
        const aEff = this.getEffectiveStats(aTgt.id);
        const bEff = this.getEffectiveStats(bTgt.id);
        const aDirect = aEff.isDirectRule ? 1 : 0;
        const bDirect = bEff.isDirectRule ? 1 : 0;
        const aScore = aIsPlayer * 20 + aDirect * 25 + (100 - (aTgt.order || 80)) * 0.5;
        const bScore = bIsPlayer * 20 + bDirect * 25 + (100 - (bTgt.order || 80)) * 0.5;
        return bScore - aScore + (Math.random() * 10 - 5);
      });

      const chosen = potentialTargets[0];
      const targetProv = chosen.target;
      const isTargetPlayer = targetProv.ownerId === this.playerClanId;

      if (isTargetPlayer && targetPlayerCount >= 1) continue;

      const attackerName = this.getClanFamilyName(clanId);
      const targetName = targetProv.name;
      const targetEff = this.getEffectiveStats(targetProv.id);
      const targetStrat = Number(targetEff.stratagem) || 50;
      const targetOrder = Number(targetProv.order) || 80;

      // 防諜成功判定 (Counter-Intelligence)
      // 防衛側城主の知謀 + 治安補正 vs 攻撃側の知謀
      const diff = targetStrat - power;
      const orderBonus = (targetOrder - 70) * 0.003;
      const counterSuccessRate = Math.max(0.20, Math.min(0.85, 0.45 + diff * 0.007 + orderBonus));
      const counterSuccess = Math.random() < counterSuccessRate;

      stratagemCount++;
      if (isTargetPlayer) targetPlayerCount++;

      // 工作の種別（知謀に応じて決定）
      // 1: 放火・城割（defense低下）
      // 2: 流言・扇動（morale & order低下）
      // 3: 内応・調略（troops引き抜き脱走：知謀75以上限定）
      const typeRoll = Math.random();
      let stratType = 'fire';
      if (power >= 75 && typeRoll < 0.35) {
        stratType = 'treason';
      } else if (typeRoll < 0.65) {
        stratType = 'rumor';
      } else {
        stratType = 'fire';
      }

      if (counterSuccess) {
        // ===== 防諜成功（撃退） =====
        if (isTargetPlayer) {
          try { this.audio.playSword?.(); } catch(e) {}
          const govLabel = targetEff.isDirectRule
            ? `我が城代守備隊`
            : `我が城主・${targetEff.name}`;

          let extraReward = '';
          // 城主知謀が極めて高い（85以上）場合、敵の忍びを捕縛して工作資金を押収
          if (targetStrat >= 85 && Math.random() < 0.5) {
            const seizedGold = Math.round(20 + Math.random() * 25);
            this.gold += seizedGold;
            extraReward = ` さらに潜入した敵忍びを捕縛し、工作資金【金${seizedGold}貫】を押収しました！`;
          }

          this.log(`🛡️【防諜成功】${govLabel}の鋭い警戒網により、${attackerName}が${targetName}に放った忍び衆を捕捉・撃退！工作を未然に防ぎました！(防諜知謀:${targetStrat} vs 敵知謀:${power})${extraReward}`, 'important');
          this.showOrderResult('🛡️ 防諜成功！忍びを撃退', `${targetName}にて ${attackerName}の謀略工作を阻止しました！`, '#2ecc71');
        } else {
          // AI同士
          this.log(`🛡️【防諜】${this.getClanFamilyName(targetProv.ownerId)}は${targetName}にて${attackerName}の忍びを警戒網で撃退しました。`);
        }
      } else {
        // ===== 工作成功（被災） =====
        if (stratType === 'fire') {
          // 放火・城割
          const defDmg = Math.round(10 + (power / 100) * 12);
          targetProv.defense = Math.max(15, (targetProv.defense || 50) - defDmg);
          if (isTargetPlayer) {
            try { this.audio.playSlash?.(); } catch(e) {}
            this.log(`🔥【敵国謀略・放火城割】${attackerName}の放った忍び衆が${targetName}の城下に潜入放火！堀と城壁が破壊されました！(城防 -${defDmg} / 防諜知謀:${targetStrat} vs 敵知謀:${power})`, 'battle');
            this.showOrderResult('🔥 敵の謀略！城郭破壊', `${targetName}にて ${attackerName}の放火工作！城防 -${defDmg}`, '#e74c3c');
          } else {
            this.log(`🔥【群雄謀略】${attackerName}が${targetName}に忍びを放ち放火！城防を削ぎました。`);
          }
        } else if (stratType === 'rumor') {
          // 流言・扇動
          const morDmg = Math.round(14 + (power / 100) * 14);
          const ordDmg = Math.round(10 + (power / 100) * 10);
          targetProv.morale = Math.max(20, (targetProv.morale || 70) - morDmg);
          targetProv.order = Math.max(20, (targetProv.order || 80) - ordDmg);
          if (isTargetPlayer) {
            try { this.audio.playHyoshigi?.(); } catch(e) {}
            this.log(`🗣️【敵国謀略・流言扇動】${attackerName}が放った密偵の流言飛語により、${targetName}の領民と将兵が動揺！(士気 -${morDmg}, 治安 -${ordDmg} / 防諜知謀:${targetStrat} vs 敵知謀:${power})`, 'battle');
            this.showOrderResult('🗣️ 敵の謀略！流言飛語', `${targetName}にて人心動揺！士気 -${morDmg} ｜ 治安 -${ordDmg}`, '#e67e22');
          } else {
            this.log(`🗣️【群雄謀略】${attackerName}が${targetName}に流言を放ち、将兵と領民を動揺させました。`);
          }
        } else {
          // 内応・調略（兵員離反）
          const betray = Math.min(Math.round((targetProv.troops || 1000) * 0.12), 650);
          targetProv.troops = Math.max(400, (targetProv.troops || 1000) - betray);
          targetProv.morale = Math.max(25, (targetProv.morale || 70) - 12);
          if (isTargetPlayer) {
            try { this.audio.playSlash?.(); } catch(e) {}
            this.log(`🤝【敵国謀略・兵員内応】${attackerName}の調略により、${targetName}の守備隊から${betray.toLocaleString()}人が寝返り・脱走しました！(守備兵 -${betray}人, 士気 -12)`, 'battle');
            this.showOrderResult('🤝 敵の調略！兵員離反', `${targetName}にて将兵が調略され ${betray.toLocaleString()}人が脱走！`, '#9b59b6');
          } else {
            this.log(`🤝【群雄謀略】${attackerName}が${targetName}の武士団を調略し、守備隊の一部を離反させました。`);
          }
        }
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

  /**
   * 敵AI思考改善: 前線危機の検知と「後詰め（防衛救援）」システム
   * プレイヤーや強敵に隣接する前線城が劣勢な場合、後方城から救援兵力を前線へ急行させる
   */
  executeAiDefenseReinforcements() {
    if (!this.provinces || this.provinces.length === 0) return;
    const allClanIds = [...new Set(this.provinces.map(p => p.ownerId))].filter(id => id && id !== this.playerClanId && id !== 'null' && id !== 'ronin');
    
    for (const clanId of allClanIds) {
      const clanProvs = this.provinces.filter(p => p.ownerId === clanId);
      if (clanProvs.length <= 1) continue;

      const isFront = (q) => (q.neighbors || []).some(nId => {
        const n = this.provinces.find(x => x.id === nId);
        return n && n.ownerId && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId);
      });

      // 危機にある前線城を特定（敵兵力に対して劣勢、または兵力1500未満）
      const endangeredFronts = clanProvs.filter(p => isFront(p)).map(p => {
        const enemyNeighbors = (p.neighbors || [])
          .map(nId => this.provinces.find(x => x.id === nId))
          .filter(n => n && n.ownerId && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId));
        const maxEnemyTroop = Math.max(0, ...enemyNeighbors.map(n => n.troops || 0));
        const deficit = maxEnemyTroop - (p.troops || 0);
        const isPlayerBorder = enemyNeighbors.some(n => n.ownerId === this.playerClanId);
        return { prov: p, deficit, isPlayerBorder, currentTroops: p.troops || 0 };
      }).filter(f => f.deficit > 200 || f.currentTroops < 1500)
        .sort((a, b) => (b.isPlayerBorder ? 5000 : 0) + b.deficit - ((a.isPlayerBorder ? 5000 : 0) + a.deficit));

      for (const { prov: frontProv, isPlayerBorder } of endangeredFronts) {
        // 隣接する後方城（安全な城、または兵力1800以上の城）から増援を探索
        const rearSupporters = (frontProv.neighbors || [])
          .map(nId => this.provinces.find(x => x.id === nId))
          .filter(n => n && n.ownerId === clanId && (n.troops || 0) > 1800)
          .sort((a, b) => (b.troops || 0) - (a.troops || 0));

        if (rearSupporters.length > 0) {
          const rear = rearSupporters[0];
          const shiftAmount = Math.min(800, Math.round(((rear.troops || 0) - 1400) * 0.45));
          if (shiftAmount >= 150) {
            rear.troops -= shiftAmount;
            frontProv.troops = (frontProv.troops || 0) + shiftAmount;
            if (isPlayerBorder && (!this.isAutoPlay || this.autoPlaySpeed >= 0.3)) {
              this.log(`🏯【後詰め迎撃】${this.getClanFamilyName(clanId)}は我が軍の脅威に備え、後方・${rear.name}より前線【${frontProv.name}】へ援軍${shiftAmount.toLocaleString()}人を急行させました！`);
            }
            break; // 1勢力1季あたり最も危険な前線1箇所に重点配分
          }
        }
      }
    }
  },

  /**
   * AI思考改善第1弾: 大局観・戦略目標・背後急襲（隙突き）・要衝評価に基づく最適侵攻計画の策定
   * @param {string} clanId 
   * @param {object} tune 
   * @param {object} ability 
   * @returns {object|null} 最適な侵攻計画 { srcProv, target, attackForce, motive, score, powerRatio }
   */
  findBestInvasionPlan(clanId, tune, ability) {
    const clanProvs = (this.provinces || []).filter(p => p.ownerId === clanId);
    if (clanProvs.length === 0) return null;

    const personality = ability.personality || 'balanced';
    const threatened = this.clanFeelsThreatened(clanId);
    const myProvsCount = (this.provinces || []).filter(p => p.ownerId === this.playerClanId).length;

    // 最低出陣兵力を満たし、非同盟かつ自領以外の領国に隣接する前線城をすべて抽出
    const candidateFrontiers = clanProvs.filter(p => {
      if ((p.troops || 0) < tune.minSourceTroops) return false;
      return (p.neighbors || []).some(nId => {
        const n = this.provinces.find(x => x.id === nId);
        return n && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId);
      });
    });
    if (candidateFrontiers.length === 0) return null;

    // 本拠地・地域情報
    const capitalId = (window.CLAN_CAPITAL_PROVINCES && window.CLAN_CAPITAL_PROVINCES[clanId]) || clanProvs[0]?.id;
    const capitalProv = this.provinces.find(p => p.id === capitalId) || clanProvs[0];
    const capitalRegion = capitalProv?.region || null;

    // 上洛・畿内志向（天下を睨む大名）
    const KINAI_PROV_IDS = new Set(['yamashiro', 'south_omi', 'north_omi', 'settsu', 'kawachi', 'yamato', 'tamba', 'izumi', 'harima', 'iga', 'ise']);
    const isKyotoAmbitionClan = [
      'oda', 'takeda', 'uesugi', 'mori', 'hojo', 'tokugawa', 'imagawa',
      'miyoshi', 'ashikaga', 'hosokawa', 'asai', 'asakura', 'rokukaku'
    ].includes(clanId) || personality === 'aggressive' || this.coalitionFormed;

    const candidates = [];

    // 全前線城 × 隣接敵国の組み合わせを総当たりで戦略評価
    for (const srcProv of candidateFrontiers) {
      const attackForce = Math.round(srcProv.troops * tune.forceRatio);
      const neighborTargets = (srcProv.neighbors || [])
        .map(nId => this.provinces.find(x => x.id === nId))
        .filter(n => n && n.ownerId !== clanId && !this.isAllied(clanId, n.ownerId));

      for (const target of neighborTargets) {
        const isTargetPlayer = target.ownerId === this.playerClanId;
        const isBlank = !target.ownerId || target.ownerId === 'null' || target.ownerId === 'undefined';

        // プレイヤー直前征服保護フラグ
        if (isTargetPlayer && target.justConquered) continue;

        // 1. 戦力比（Combat Power Ratio）の精密計算
        const targetAbility = isBlank
          ? { military: 45, politics: 45 }
          : getClanAbility(target.ownerId);

        const atkPowerEst = attackForce * ((ability.military || 65) / 65);
        const defDefenseFactor = Math.max(30, Number(target.defense) || 50) / 80;
        const defMoraleFactor = Math.max(30, Number(target.morale) || 70) / 80;
        const defMilFactor = (Number(targetAbility.military) || 60) / 65;
        const defPowerEst = Math.max(100, (Number(target.troops) || 500) * defDefenseFactor * defMoraleFactor * defMilFactor);

        const powerRatio = atkPowerEst / defPowerEst;
        const rawTroopRatio = attackForce / Math.max(1, Number(target.troops) || 1);

        // 勝算判定（必要比率を満たさない場合は無謀な突撃を自重）
        if (powerRatio < tune.requiredRatio && rawTroopRatio < tune.requiredRatio) continue;

        // 2. 戦略スコア算出 (初期値: 100)
        let score = 100;
        const motiveFactors = [];

        // --- A. 隙突き・背後急襲（脆弱度評価） ---
        let backstabScore = 0;
        if (target.troops <= 800) {
          backstabScore += 45;
        } else if (target.troops <= 1300) {
          backstabScore += 25;
        }
        if ((Number(target.defense) || 50) <= 40) {
          backstabScore += 30;
        } else if ((Number(target.defense) || 50) <= 55) {
          backstabScore += 15;
        }
        if ((Number(target.morale) || 70) <= 55) {
          backstabScore += 35;
        } else if ((Number(target.morale) || 70) <= 65) {
          backstabScore += 18;
        }
        if ((Number(target.order) || 80) <= 50) {
          backstabScore += 20;
        }
        if (!isBlank) {
          const friendlyNeighborsOfTarget = (target.neighbors || []).filter(nId => {
            const nb = this.provinces.find(x => x.id === nId);
            return nb && nb.ownerId === target.ownerId;
          }).length;
          if (friendlyNeighborsOfTarget === 0) {
            backstabScore += 30; // 完全孤立城
          } else if (friendlyNeighborsOfTarget === 1) {
            backstabScore += 15; // 突出部
          }
        }

        if (backstabScore > 0) {
          score += backstabScore;
          motiveFactors.push({
            type: 'backstab',
            title: '背後急襲・虚を突く電撃戦',
            desc: `${target.name}の手薄な防備と動揺を見抜き、電撃奇襲`,
            weight: backstabScore
          });
        }

        // --- B. 空白地併合（内政型・小大名の手堅い領土拡張） ---
        if (isBlank) {
          let blankScore = 0;
          if (personality === 'domestic') {
            blankScore = 75;
          } else if (personality === 'balanced') {
            blankScore = 40;
          } else {
            blankScore = 20;
          }
          score += blankScore;
          motiveFactors.push({
            type: 'annex_blank',
            title: '無主の地を併合',
            desc: `空白地盤の${target.name}を併合し領国基盤を強化`,
            weight: blankScore
          });
        }

        // --- C. 大局観・戦略目標 ---
        // 1) 上洛・畿内回廊の掌握
        const isKinai = target.region === '近畿' || KINAI_PROV_IDS.has(target.id);
        if (isKinai && isKyotoAmbitionClan) {
          const kyotoScore = (target.id === 'yamashiro') ? 60 : 40;
          score += kyotoScore;
          motiveFactors.push({
            type: 'capital_push',
            title: '天下への道・上洛回廊',
            desc: `帝都・畿内へ向かう回廊を開かんと${target.name}へ進軍`,
            weight: kyotoScore
          });
        }

        // 2) 地方統一（同地域平定）
        if (capitalRegion && target.region === capitalRegion) {
          const unifyScore = 35;
          score += unifyScore;
          motiveFactors.push({
            type: 'unify_region',
            title: `${capitalRegion}地方の覇権確立`,
            desc: `${capitalRegion}地方一統を目指し同州の${target.name}へ出陣`,
            weight: unifyScore
          });
        }

        // 3) 経済・軍事要衝の争奪
        let resourceScore = 0;
        if (target.goldMine || target.silverMine) {
          resourceScore += 40;
        }
        if (target.specialty && /港|湊|海|貿易|鉄|刀|鉄砲/.test(target.specialty)) {
          resourceScore += 25;
        }
        if ((target.neighbors || []).length >= 5) {
          resourceScore += 20;
        }
        if (resourceScore > 0) {
          score += resourceScore;
          motiveFactors.push({
            type: 'resource_seize',
            title: '富国強兵・戦略要衝争奪',
            desc: `金山・湊など重要物資と交通の要衝たる${target.name}を攻略`,
            weight: resourceScore
          });
        }

        // --- D. プレイヤーに対する敵対心・包囲網 ---
        if (isTargetPlayer) {
          if (this.coalitionFormed) {
            const coalScore = 65;
            score += coalScore;
            motiveFactors.push({
              type: 'coalition_strike',
              title: '反覇権・包囲網一斉蜂起',
              desc: `諸侯包囲網の盟約に基づき、貴家領国・${target.name}へ総攻撃`,
              weight: coalScore
            });
          } else if (myProvsCount >= 12) {
            const containScore = 35;
            score += containScore;
            motiveFactors.push({
              type: 'contain_player',
              title: '強大勢力への牽制',
              desc: `勢力を伸ばす貴家を抑止すべく${target.name}へ侵攻`,
              weight: containScore
            });
          } else if (personality === 'aggressive') {
            const rivalScore = 25;
            score += rivalScore;
            motiveFactors.push({
              type: 'aggressive_rival',
              title: '好敵手との雌雄決戦',
              desc: `気鋭の武威を示さんと貴家領国・${target.name}へ出陣`,
              weight: rivalScore
            });
          } else if (personality === 'domestic' && !threatened) {
            score -= 40;
          }
        }

        // --- E. 勝算ボーナスと揺らぎ ---
        score += Math.min(30, Math.max(0, (powerRatio - tune.requiredRatio) * 20));
        score += (Math.random() * 16 - 8);

        motiveFactors.sort((a, b) => b.weight - a.weight);
        const topMotive = motiveFactors[0] || {
          type: 'standard',
          title: '領国拡張の進軍',
          desc: `領土拡大と武威宣揚のため${target.name}へ進軍`,
          weight: 10
        };

        candidates.push({
          srcProv,
          target,
          attackForce,
          score,
          powerRatio,
          motive: topMotive
        });
      }
    }

    if (candidates.length === 0) return null;

    candidates.sort((a, b) => b.score - a.score);
    return candidates[0];
  },

  async executeAiTurn() {
    this.executeAiDiplomacy();
    await this.executeAiStratagems();

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

    // 2. 敵AI防衛後詰め（劣勢・危機前線への救援増援）
    this.executeAiDefenseReinforcements();

    // 3. AI侵攻判断（「適宜バランスよく攻め込む」：1ターン最大3戦線に制御）
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

      // AI思考改善第1弾: 大局観・戦略目標・背後急襲（隙突き）に基づく最適侵攻計画の策定
      const plan = this.findBestInvasionPlan(clanId, tune, ability);
      if (!plan) continue;

      const { srcProv, target, attackForce, motive } = plan;

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
      const isBlankTarget = !target.ownerId || target.ownerId === 'null';
      const targetAbility = isBlankTarget
        ? { military: 45, politics: 45 }
        : getClanAbility(target.ownerId);

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
          let battleTitle = '⚔️ 敵軍侵攻！領地喪失';
          let battleLogIcon = '⚔';
          if (motive.type === 'backstab') {
            battleTitle = '⚡ 敵襲！手薄を衝かる';
            battleLogIcon = '⚡';
          } else if (motive.type === 'capital_push') {
            battleTitle = '👑 敵襲！上洛の要衝奪取';
            battleLogIcon = '👑';
          } else if (motive.type === 'coalition_strike') {
            battleTitle = '🔥 包囲網蜂起！領地喪失';
            battleLogIcon = '🔥';
          } else if (motive.type === 'resource_seize') {
            battleTitle = '💎 要衝争奪！領地喪失';
            battleLogIcon = '💎';
          }

          this.log(`${battleLogIcon}【敵襲・${motive.title}】${attackerName}軍が${motive.desc}として${target.name}に侵攻！我が守備軍は敗れ城を奪われました！`, 'battle');
          this.showOrderResult(battleTitle, `${target.name} が ${attackerName}に攻略されました！ (${motive.title})`, '#e74c3c');
          if (this.selectedProvId === target.id) {
            this.selectedProvId = null;
          }
        } else {
          this.log(`⚔【群雄動乱・${motive.title}】${attackerName}が${motive.desc}として${target.name}へ進攻！激闘の末、${defenderName}軍を破り領国を奪回・併合しました。`);
        }
      } else {
        // 撃退
        const defRemain = Math.max(300, Math.round(target.troops * 0.75));
        target.troops = defRemain;
        target.defense = Math.max(20, target.defense - 15);
        srcProv.troops -= Math.round(attackForce * 0.35);

        if (isAttackingPlayer) {
          this.audio.playFanfare();
          this.log(`🛡【防衛成功】${attackerName}軍による${target.name}侵攻（${motive.title}）を、我が守備隊が頑強に撃退しました！`, 'important');
          this.showOrderResult('🛡️ 敵襲撃退！', `${target.name}にて ${attackerName}軍の撃退に成功しました！`, '#2ecc71');
        } else {
          this.log(`🛡【防戦】${defenderName}軍が${target.name}にて${attackerName}軍の猛攻（${motive.title}）を退けました。`);
        }
      }
    }
  },

  executeGovernanceTurn() {
    const myProvs = (this.provinces || []).filter(p => p.ownerId === this.playerClanId);
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
        // 内政委任の知能化: 治安が危険（65以下）な場合は、一揆防止のため治安回復・徳政を最優先！
        if ((Number(p.order) || 80) <= 65) {
          p.order = Math.min(100, (Number(p.order) || 80) + Math.round(14 * mult * polBonus));
          p.defense = Math.min(100, (Number(p.defense) || 50) + Math.round(3 * mult));
        } else {
          const dRice = Math.round(20 * mult * polBonus);
          const dComm = Math.round(20 * mult * polBonus);
          p.rice = (Number(p.rice) || 50) + dRice;
          p.commerce = (Number(p.commerce) || 50) + dComm;
          this.gold += Math.round(30 * mult * polBonus);
          this.rice += Math.round(40 * mult * polBonus);
        }
        domesticCount++;
      } else if (p.governance === 'military') {
        p.troops = (Number(p.troops) || 0) + Math.round(300 * mult * milBonus);
        p.defense = Math.min(100, (Number(p.defense) || 50) + Math.round(6 * mult));
        p.morale = Math.min(100, (Number(p.morale) || 70) + Math.round(4 * mult));
        militaryCount++;
      } else if (p.governance === 'balanced') {
        if ((Number(p.order) || 80) <= 60) {
          p.order = Math.min(100, (Number(p.order) || 80) + Math.round(10 * mult));
        }
        p.troops = (Number(p.troops) || 0) + Math.round(150 * mult * milBonus);
        p.rice = (Number(p.rice) || 50) + Math.round(8 * mult * polBonus);
        p.commerce = (Number(p.commerce) || 50) + Math.round(8 * mult * polBonus);
        p.defense = Math.min(100, (Number(p.defense) || 50) + Math.round(3 * mult));
      } else if (p.governance === 'logistics') {
        // 兵站委任の知能化: 最も支援を必要としている危機前線へ重点ピストン輸送！
        if ((p.troops || 0) > 1800) {
          const surplus = Math.min(1500, (p.troops || 0) - 1500);
          const frontierCandidates = (p.neighbors || [])
            .map(nId => this.provinces.find(x => x.id === nId))
            .filter(x => x && x.ownerId === this.playerClanId && this.isProvinceFrontier(x));

          if (frontierCandidates.length > 0) {
            frontierCandidates.sort((a, b) => {
              const aEnemyTroops = (a.neighbors || [])
                .map(nId => this.provinces.find(x => x.id === nId))
                .filter(x => x && x.ownerId !== this.playerClanId)
                .reduce((sum, x) => sum + (x.troops || 0), 0);
              const bEnemyTroops = (b.neighbors || [])
                .map(nId => this.provinces.find(x => x.id === nId))
                .filter(x => x && x.ownerId !== this.playerClanId)
                .reduce((sum, x) => sum + (x.troops || 0), 0);
              const aNeed = aEnemyTroops * 0.6 - (a.troops || 0);
              const bNeed = bEnemyTroops * 0.6 - (b.troops || 0);
              return bNeed - aNeed;
            });

            const bestFrontier = frontierCandidates[0];
            p.troops -= surplus;
            bestFrontier.troops = (bestFrontier.troops || 0) + surplus;
            totalMovedTroops += surplus;
            logisticsCount++;
          }
        }
      }
    });

    // 2. 軍事委任領国による「戦略的自律進攻」（勝算と大局観に基づき確実に領土拡大）
    const militaryFrontiers = myProvs.filter(p => p.governance === 'military' && this.isProvinceFrontier(p));
    const attackedProvIds = new Set();
    let attackActions = 0;
    const maxAutonomousAttacks = 3;

    // 全ての軍事委任前線城 × 隣接敵国の組み合わせを戦略スコアリング評価
    const autonomousCandidates = [];
    for (const srcProv of militaryFrontiers) {
      if ((srcProv.troops || 0) < 1500) continue;
      const attackForce = Math.round((srcProv.troops || 0) * 0.72);
      const enemyNeighbors = (srcProv.neighbors || [])
        .map(nId => this.provinces.find(x => x.id === nId))
        .filter(n => n && n.ownerId !== this.playerClanId && !this.isAllied(this.playerClanId, n.ownerId));

      for (const target of enemyNeighbors) {
        const isBlank = !target.ownerId || target.ownerId === 'null';
        const srcEff = this.getEffectiveStats(srcProv.id);
        const targetEff = isBlank ? { military: 40 } : this.getEffectiveStats(target.id);

        const atkPowerEst = attackForce * ((Number(srcEff.military) || 60) / 60);
        const defDefenseFactor = Math.max(30, Number(target.defense) || 50) / 80;
        const defMoraleFactor = Math.max(30, Number(target.morale) || 70) / 80;
        const defMilFactor = (Number(targetEff.military) || 60) / 60;
        const defPowerEst = Math.max(100, (Number(target.troops) || 500) * defDefenseFactor * defMoraleFactor * defMilFactor);

        const powerRatio = atkPowerEst / defPowerEst;
        const troopRatio = attackForce / Math.max(1, Number(target.troops) || 1);

        // 勝算判定: 勝算が足りない場合は無謀な自爆特攻を自重！
        if (powerRatio < 1.05 && troopRatio < 1.15) continue;

        let score = 100;
        let motiveTitle = '領土拡大';

        if (isBlank) {
          score += 70; // 空白地は無血開城できる最優先目標！
          motiveTitle = '空白地の無血併合';
        } else {
          if ((target.troops || 0) <= 1000) { score += 35; motiveTitle = '手薄な守備への急襲'; }
          if ((Number(target.defense) || 50) <= 45) { score += 25; motiveTitle = '城防脆弱地の強襲'; }
          if ((Number(target.morale) || 70) <= 60) { score += 25; motiveTitle = '敵士気動揺への急襲'; }
          if (target.goldMine || target.silverMine) { score += 30; motiveTitle = '金山要衝の奪取'; }
        }
        score += Math.min(30, (powerRatio - 1.0) * 20);

        autonomousCandidates.push({
          srcProv,
          target,
          attackForce,
          score,
          powerRatio,
          motiveTitle,
          srcEff,
          targetEff
        });
      }
    }

    autonomousCandidates.sort((a, b) => b.score - a.score);

    for (const plan of autonomousCandidates) {
      if (attackActions >= maxAutonomousAttacks) break;
      if (this.rice < 60) break;
      if (attackedProvIds.has(plan.target.id)) continue;
      if ((plan.srcProv.troops || 0) < plan.attackForce + 500) continue;

      const { srcProv, target, attackForce, motiveTitle, srcEff, targetEff } = plan;
      attackedProvIds.add(target.id);
      attackActions++;

      const isBlank = !target.ownerId || target.ownerId === 'null';
      const riceCost = Math.min(this.rice, Math.max(50, Math.round(attackForce * 0.1)));
      this.rice = Math.max(0, this.rice - riceCost);

      const attackPower = attackForce * ((Number(srcEff.military) || 60) / 60) * (0.9 + Math.random() * 0.35);
      const defensePower = (Number(target.troops) || 500) * ((Number(target.defense) || 50) / 80) * ((Number(targetEff.military) || 60) / 60) * (0.8 + Math.random() * 0.4);
      const won = attackPower > defensePower;

      const enemyClanId = target.ownerId;
      const enemyClanName = isBlank ? '無主' : this.getClanFamilyName(enemyClanId);

      if (won) {
        const remainTroops = Math.max(1200, Math.round(attackForce * 0.75));
        srcProv.troops = Math.max(600, (srcProv.troops || 0) - attackForce);

        this.handleProvinceLoss(target, enemyClanId);
        target.ownerId = this.playerClanId;
        target.troops = remainTroops;
        target.defense = Math.max(50, target.defense || 50);
        target.morale = 80;
        target.governance = 'military';
        target.justConquered = true;

        conqueredProvinces.push({
          srcName: srcProv.name,
          targetName: target.name,
          enemyClanName: enemyClanName,
          motiveTitle
        });

        this.log(`🎌【委任軍快進撃・${motiveTitle}】${srcProv.name}の委任軍（城主:${srcEff.name}）が敵領【${target.name}】（${enemyClanName}）へ電撃進攻！見事攻略し我が領土に組み入れました！`, 'important');

        if (enemyClanId && enemyClanId !== 'null') {
          const remainingEnemyProvs = this.provinces.filter(p => p.ownerId === enemyClanId);
          if (remainingEnemyProvs.length === 0) {
            this.log(`💀【御家滅亡】${enemyClanName}は全領国を失い、完全に滅亡しました！`, 'battle');
          }
        }
      } else {
        srcProv.troops = Math.max(500, (srcProv.troops || 0) - Math.round(attackForce * 0.35));
        target.troops = Math.max(300, Math.round((target.troops || 500) * 0.75));
        this.log(`⚔【委任軍合戦】${srcProv.name}の委任軍が【${target.name}】（${enemyClanName}）へ進攻するも、敵の堅い守りに阻まれ撤退しました。`);
      }
    }

    // 委任進攻結果の演出
    if (conqueredProvinces.length > 0) {
      try { this.audio.playFanfare?.(); } catch(e) {}
      const conqueredNames = conqueredProvinces.map(c => `${c.targetName} (${c.enemyClanName})`).join('・');
      this.showOrderResult('🎌 委任軍 領土攻略！', `${conqueredNames} を電撃攻略！`, '#2ecc71');
    }

    if (domesticCount > 0 || militaryCount > 0 || logisticsCount > 0 || conqueredProvinces.length > 0) {
      const conqueredMsg = conqueredProvinces.length > 0 ? `、前線委任軍が【${conqueredProvinces.length}カ国】を攻略領有` : '';
      this.log(`【委任統治報告】内政型${domesticCount}国で開発・治安維持、軍事進攻型${militaryCount}国で増強${conqueredMsg}、兵站型から前線へ兵${totalMovedTroops.toLocaleString()}人を輸送完了。`);
    }
  },

  // 自動セーブ,

};
