/**
 * @file js/core/GameState.js - データ状態管理・ターン進行・武将人事・合戦・歴史イベント
 * 戦国天下統一伝 ES6モジュール
 * @typedef {import('../types.js').Officer} Officer
 * @typedef {import('../types.js').Province} Province
 * @typedef {import('../types.js').PlayableDaimyo} PlayableDaimyo
 * @typedef {import('../types.js').Scenario} Scenario
 * @typedef {import('../types.js').HistoricalEvent} HistoricalEvent
 * @typedef {import('../types.js').AllianceBond} AllianceBond
 * @typedef {import('../types.js').GameSaveData} GameSaveData
 */

// モジュール間安全参照ヘルパー
var getClanAbility = (clanId) => (typeof window !== 'undefined' && typeof window.getClanAbility === 'function')
  ? window.getClanAbility(clanId)
  : ((typeof window !== 'undefined' && window.CLAN_ABILITIES?.[clanId]) || { politics: 60, military: 60, stratagem: 55, personality: 'balanced' });

function _createArrayProxy(getter) {
  return new Proxy([], {
    get(target, prop, receiver) {
      const arr = getter();
      if (prop === 'length') return arr.length;
      if (prop === Symbol.iterator) return arr[Symbol.iterator].bind(arr);
      const val = Reflect.get(arr, prop, receiver);
      return typeof val === 'function' ? val.bind(arr) : val;
    },
    has(target, prop) { return Reflect.has(getter(), prop); },
    ownKeys(target) { return Reflect.ownKeys(getter()); },
    getOwnPropertyDescriptor(target, prop) { return Object.getOwnPropertyDescriptor(getter(), prop); }
  });
}
function _createObjectProxy(getter) {
  return new Proxy({}, {
    get(target, prop, receiver) {
      const obj = getter();
      const val = Reflect.get(obj, prop, receiver);
      return typeof val === 'function' ? val.bind(obj) : val;
    },
    has(target, prop) { return Reflect.has(getter(), prop); },
    ownKeys(target) { return Reflect.ownKeys(getter()); },
    getOwnPropertyDescriptor(target, prop) { return Object.getOwnPropertyDescriptor(getter(), prop); }
  });
}

var SCENARIOS = _createArrayProxy(() => (typeof window !== 'undefined' && ((window.SCENARIOS_DATA?.length ? window.SCENARIOS_DATA : window.SCENARIOS) || [])) || []);
var INITIAL_PROVINCES = _createArrayProxy(() => (typeof window !== 'undefined' && ((window.PROVINCES_DATA?.length ? window.PROVINCES_DATA : window.INITIAL_PROVINCES) || [])) || []);
var CLAN_MASTER = _createObjectProxy(() => (typeof window !== 'undefined' && (window.CLAN_MASTER_DATA || window.CLAN_MASTER || {})) || {});
var INITIAL_ALLIANCE_DURATION_SEASONS = (typeof window !== 'undefined' && window.INITIAL_ALLIANCE_DURATION_SEASONS) || 20;
var ALLIANCE_DURATION_SEASONS = (typeof window !== 'undefined' && window.ALLIANCE_DURATION_SEASONS) || 8;
var DAIMYOS = (typeof window !== 'undefined' && window.DAIMYOS) || [];
var FORMATIONS_DATA = (typeof window !== 'undefined' && window.FORMATIONS_DATA) || {};
var DAIMYO_EPILOGUES = (typeof window !== 'undefined' && window.DAIMYO_EPILOGUES) || {};
var EVENT_CLAN_LINEAGE = (typeof window !== 'undefined' && window.EVENT_CLAN_LINEAGE) || [
  ['genji_yoritomo', 'minamoto_yoritomo', 'genji', 'minamoto_yoshitomo'],
  ['kiso', 'kiso_genji']
];
var HISTORICAL_ALLIANCE_BONDS = (typeof window !== 'undefined' && window.HISTORICAL_ALLIANCE_BONDS) || [];

export class GameState {
  /**
   * @param {Object} [game] - SengokuGame インスタンス
   */
  constructor(game) {
    this.game = game;
    // ゲーム進行・単一情報源 (SSOT) 状態プロパティ
    this.currentScenarioId = '1560';
    this.year = 1560;
    this.seasonIdx = 0;
    this.season = '春';
    this.playerClanId = 'oda';
    this.gold = 3000;
    this.rice = 5000;
    this.ap = 3;
    this.provinces = [];
    this.activeOfficers = [];
    this.alliances = [];
    this.formerDaimyoIds = new Set();
    this.triggeredHistoricalEvents = new Set();
    this.happenedEvents = new Set();
    this.selectedProvId = null;
    this.mapHeatMode = 'none';
    this._eventDecidedId = null;
  }

  /**
   * 単方向データフロー: 状態変更をコミットし、画面再描画を一元管理
   * @param {Object|Function} mutation - 状態変更データまたはミューテーション関数
   * @param {Object} [uiOpts] - 描画オプション
   */
  commit(mutation, uiOpts = {}) {
    if (typeof mutation === 'function') {
      mutation(this, this.game);
    } else if (mutation && typeof mutation === 'object') {
      Object.assign(this, mutation);
      if (this.game) Object.assign(this.game, mutation);
    }
    if (this.game && typeof this.game.updateUI === 'function') {
      this.game.updateUI(uiOpts);
    }
  }
}

export const GameStateMethods = {
  isFormerDaimyo(off) {
    if (!off) return false;
    if (off.hasBeenDaimyo || off.isDaimyo) return true;
    if (this.formerDaimyoIds && this.formerDaimyoIds.has(off.id)) return true;
    if (String(off.id).startsWith('off_daimyo_')) return true;
    const master = (window.OFFICERS_MASTER || []).find(m => m.id === off.id);
    if (master && master.isDaimyo) return true;
    return false;
  },

  initData() {
    const rawProvs = (window.PROVINCES_DATA && window.PROVINCES_DATA.length > 0) ? window.PROVINCES_DATA : (INITIAL_PROVINCES || []);
    this.provinces = JSON.parse(JSON.stringify(rawProvs));
    this.provinces.forEach(p => {
      p.governance = 'direct';
    });
  },

  normalizeProvince(p) {
    if (p && p.id) {
      const jp = this.getProvinceJapaneseName(p.id);
      if (jp && jp !== '諸国' && (!p.name || /^[a-z0-9_]+$/i.test(String(p.name)))) p.name = jp;
    }
    const isBad = v => v == null || !Number.isFinite(Number(v));
    const kokudaka = Number(p.kokudaka) || 0;
    // 駐留兵力: 石高に比例 (石高÷1000×8 + 400、最低500人)
    if (isBad(p.troops)) p.troops = Math.max(500, Math.round((kokudaka / 1000) * 8 + 400));
    // 兵糧 (石): 石高÷1000 (20〜80石)
    if (isBad(p.rice)) p.rice = Math.max(20, Math.round(kokudaka / 1000));
    // 商業 (貫): 石高÷2000 (10〜90貫)
    if (isBad(p.commerce)) p.commerce = Math.max(10, Math.round(kokudaka / 2000));
    // 軍勢士気: マスターデータの忠誠度 (loyalty) を流用
    if (isBad(p.morale)) p.morale = Number(p.loyalty) || 80;
    // 城郭防御・治安度の補正
    if (isBad(p.defense)) p.defense = 50;
    if (isBad(p.order)) p.order = 85;
  },

  getSeasonTrackKey() {
    // 大名家専用BGMが有効な場合、プレイヤー大名家のテーマを優先再生
    if (this.music && this.music.daimyoBgmEnabled && this.playerClanId) {
      const clanId = this.playerClanId;
      if (clanId === 'oda') return 'oda';
      if (clanId === 'takeda') return 'takeda';
      if (clanId === 'uesugi') return 'uesugi';
      if (clanId === 'date') return 'date';
      if (clanId === 'mori' || clanId === 'chosokabe') return 'mori_choso';
      if (clanId === 'shimazu') return 'shimazu';
      if (clanId === 'hojo') return 'hojo';
    }
    return this.seasonBgmTracks[this.seasonIdx] || 'spring';
  },

  looksLikeClanId(value) {
    return !value || /^[a-z0-9_]+$/i.test(String(value));
  },

  // 再開案内用。セーブ時点の当主名を日本語で返す（英語IDには落とさない）,

  switchScenario(scenarioId) {
    this.activeOfficers = null;
    this.currentScenarioId = scenarioId;
    const scens = (window.SCENARIOS_DATA && window.SCENARIOS_DATA.length > 0) ? window.SCENARIOS_DATA : (SCENARIOS || []);
    const scen = scens.find(s => String(s.id) === String(scenarioId)) || scens[0];
    if (!scen) return;
    this.currentScenario = scen;

    this.year = scen.year;
    this.honnojiSplit = false;
    this.honnoujiAverted = false;
    this.okehazamaOccurred = false;
    this.kanazawaOccurred = false;
    this.triggeredHistoricalEvents = new Set();
    this.happenedEvents = new Set();
    this.resetHistoricalEventRuntime();
    this.kiyohiraFujiwaraAccepted = false;
    this.kiyohiraSurnameDeclined = false;
    this._kiyohiraAnnounced = false;
    const seasonMap = {'春': 0, '夏': 1, '秋': 2, '冬': 3};
    this.seasonIdx = scen.seasonIdx !== undefined ? scen.seasonIdx : (seasonMap[scen.season] ?? 0);
    this.alliances = this.normalizeAlliances(scen.alliances || [], this.year, this.seasonIdx, INITIAL_ALLIANCE_DURATION_SEASONS);
    this.allianceCooldown = {};
    this.currentWeather = '晴天';

    const descBox = document.getElementById('scenarioDescBox');
    if (descBox) {
      descBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #775533; padding-bottom:3px; margin-bottom:5px;">
          <strong style="color:var(--gold-bright); font-size: 12pt;">【${scen.year}年 ${scen.title} 〜${scen.subtitle || ''}〜】</strong>
          <span style="font-size: 12pt; color:#ffd700;">年号: ${scen.gengo || ''}</span>
        </div>
        <div style="margin-bottom:5px; color:#f5eedc; font-size: 12pt; line-height:1.5;">
          <strong style="color:#ffd700;">【時代背景】</strong>${scen.lore_background || scen.desc}
        </div>
        ${scen.lore_factions ? `
          <div style="margin-bottom:5px; font-size: 12pt; color:#e0d0b0; background:rgba(0,0,0,0.35); padding:5px 8px; border-radius:3px; border-left:3px solid var(--gold);">
            <strong style="color:#ffcc66;">【主要勢力図】</strong><br>${scen.lore_factions.replace(/\n/g, '<br>')}
          </div>
        ` : ''}
        ${scen.lore_focus ? `
          <div style="font-size: 12pt; color:#ffdd88; background:rgba(212,175,55,0.08); padding:3px 6px; border-radius:3px;">
            <strong style="color:#ffd700;">【覇道の焦点】</strong>${scen.lore_focus}
          </div>
        ` : ''}
      `;
    }

    document.querySelectorAll('.scenario-btn').forEach(btn => {
      const isSel = btn.dataset.scenId === scenarioId;
      btn.classList.toggle('selected', isSel);
      if (isSel) {
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
      }
    });

    this.provinces = JSON.parse(JSON.stringify(INITIAL_PROVINCES));
    this.provinces.forEach(p => {
      p.governance = 'direct';
      this.normalizeProvince(p);
      p.order = p.order !== undefined ? p.order : 85;
      if (scen.owners && scen.owners[p.id]) {
        p.ownerId = scen.owners[p.id];
      }
      if (scen.castles && scen.castles[p.id]) {
        p.castle = scen.castles[p.id];
        p.castleName = scen.castles[p.id];
      }
      if (scen.troopScale) {
        p.troops = Math.round(p.troops * scen.troopScale);
        p.rice = Math.round(p.rice * (1 + (scen.troopScale - 1) * 0.3));
        p.commerce = Math.round(p.commerce * (1 + (scen.troopScale - 1) * 0.3));
      }
    });

    // 武将ライフサイクル更新（要件2: switchScenario実行時の呼び出し）
    this.updateActiveOfficers();

    // マスターデータの初期値 (isDaimyo: true) への依存を断ち切り、シナリオ初期化時にフラグを一度すべて損切り（リセット）
    if (this.activeOfficers) {
      this.activeOfficers.forEach(o => { o.isDaimyo = false; });
    }

    // 所属先大名不在武将の史実振り替え・浪人化
    this.resolveOfficerAffiliations(scen);

    // 豊臣姓・羽柴姓の年代連動（1583年以降は豊臣、それ以前は羽柴）
    this.updateToyotomiSurname(false);

    // 1. 大名の自動生成 & 当主の確定 (要件3-1)
    // 地図上の ownerId（存在している全勢力）を走査し、各勢力の当主を決定
    const activeOwners = [...new Set(this.provinces.map(p => p.ownerId).filter(Boolean))];
    activeOwners.forEach(ownerId => {
      const ability = getClanAbility(ownerId);
      const playableD = scen.playables?.find(d => d.id === ownerId);
      const leaderName = playableD?.name || playableD?.leaderName || (playableD?.officerId && window.OFFICERS_MASTER?.find(o => o.id === playableD.officerId)?.name) || this.getDaimyoLeaderName(ownerId);

      // 自勢力に所属する生存武将
      const clanOfficers = this.activeOfficers.filter(o => o.clanId === ownerId && !o.isDead);
      let leaderOfficer = this.seatNamedLord(ownerId);

      if (!leaderOfficer && clanOfficers.length > 0) {
        const masterDm = new Set((window.OFFICERS_MASTER || []).filter(m => m.isDaimyo && m.clanId === ownerId).map(m => m.id));
        const flaggedPool = clanOfficers.filter(o => masterDm.has(o.id));
        leaderOfficer = this.pickClanLeader(ownerId, flaggedPool.length ? flaggedPool : clanOfficers);
        leaderOfficer.isDaimyo = true;
        leaderOfficer.hasBeenDaimyo = true;
        if (this.formerDaimyoIds) this.formerDaimyoIds.add(leaderOfficer.id);
        this.activeOfficers.filter(o => o.clanId === ownerId && o.id !== leaderOfficer.id).forEach(o => {
          o.isDaimyo = false;
        });
      }

      if (!leaderOfficer) {
        const explicit = scen.owners && Object.values(scen.owners).includes(ownerId);
        if (!explicit) {
          this.provinces.filter(p => p.ownerId === ownerId).forEach(p => {
            p.ownerId = null;
            p.governorId = null;
          });
        }
      }
    });

    // 【同姓同名・重複武将の完全排除】
    // ユーザー要件: 「羽柴秀吉と豊臣秀吉が重複して存在するので統一」「年齢の差が100歳以内で同姓同名の武将が複数散在する。史実で正しいほうの武将を残して重複は削除して」
    const getCanonicalName = (name) => {
      if (!name) return '';
      let clean = name.replace(/[（(][^）)]+[）)]/g, '').trim();
      if (clean === '羽柴秀吉' || clean === '豊臣秀吉') return '秀吉';
      if (clean === '羽柴秀長' || clean === '豊臣秀長') return '秀長';
      if (clean === '羽柴秀次' || clean === '豊臣秀次') return '秀次';
      if (clean === '松平元康' || clean === '徳川家康') return '家康';
      if (clean === '黒田官兵衛' || clean === '黒田孝高' || clean === '黒田如水') return '黒田官兵衛';
      if (clean === '細川藤孝' || clean === '細川幽斎') return '細川藤孝';
      if (clean === '片倉景綱' || clean === '片倉小十郎') return '片倉景綱';
      if (clean === '穴山信君' || clean === '穴山梅雪') return '穴山信君';
      if (clean === '佐々木広綱' || clean === '佐佐木広綱') return '佐々木広綱';
      if (clean === '後白河天皇' || clean === '後白河院') return '後白河天皇';
      if (clean === '後鳥羽上皇' || clean === '後鳥羽天皇') return '後鳥羽上皇';
      if (clean === '後嵯峨上皇' || clean === '後嵯峨天皇') return '後嵯峨上皇';
      if (clean === '松平秀忠' || clean === '徳川秀忠') return '徳川秀忠';
      if (clean === '松平家光' || clean === '徳川家光') return '徳川家光';
      if (clean === '松平家綱' || clean === '徳川家綱') return '徳川家綱';
      if (clean === '松平綱吉' || clean === '徳川綱吉') return '徳川綱吉';
      if (clean === '松平家宣' || clean === '徳川家宣') return '徳川家宣';
      if (clean === '松平治郷' || clean === '松平不昧') return '松平治郷';
      return clean;
    };

    const nameGroups = new Map();
    this.activeOfficers.forEach(o => {
      const canonKey = getCanonicalName(o.name);
      if (!nameGroups.has(canonKey)) {
        nameGroups.set(canonKey, []);
      }
      nameGroups.get(canonKey).push(o);
    });

    const deduplicatedOfficers = [];
    nameGroups.forEach((group) => {
      if (group.length === 1) {
        deduplicatedOfficers.push(group[0]);
        return;
      }

      const getPriority = (off) => {
        let score = 0;
        if (off.id === 'off_tokugawa_ieyasu') score += 2000;
        if (off.id === 'off_toyotomi_hideyoshi') score += 2000;
        if (off.id === 'off_kuroda_kanbei') score += 2000;
        if (off.id === 'off_kuroda_nagamasa') score += 2000;
        if (off.id === 'off_ashikaga_yoshiaki') score += 2000;
        if (off.isDaimyo) score += 500;
        if (!off.id.startsWith('off_daimyo_') && !off.id.includes('_clan') && !off.id.includes('_early')) score += 100;
        return score;
      };

      const clusters = [];
      group.forEach(off => {
        const b = off.birthYear || 1500;
        let matchedCluster = clusters.find(cl => Math.abs((cl[0].birthYear || 1500) - b) <= 100);
        if (matchedCluster) {
          matchedCluster.push(off);
        } else {
          clusters.push([off]);
        }
      });

      clusters.forEach(cl => {
        if (cl.length === 1) {
          deduplicatedOfficers.push(cl[0]);
        } else {
          cl.sort((a, b) => getPriority(b) - getPriority(a));
          deduplicatedOfficers.push(cl[0]);
        }
      });
    });

    this.activeOfficers = deduplicatedOfficers;

    // 2. 時代考証・史実に沿った確実な城主任命
    this.ensureClanCapitalsMatchMap();
    this.activeOfficers.forEach(o => { o.assignedProvId = null; });
    this.provinces.forEach(p => {
      p.governorId = null;
      // 城主不在時の「城代」能力比率 (大名能力の40%〜75%の間で固定決定)
      const hash = ((p.id.charCodeAt(0) * 17) + (p.id.length * 23) + (p.ownerId ? p.ownerId.charCodeAt(0) * 7 : 11)) % 36;
      p.jodaiRatio = 0.40 + (hash / 100);
    });

    // 【絶対原則ステップ1: 大名本拠地への大名配置（最優先・傘下武将は絶対に城代にならない）】
    // ユーザー要件: 「大名が本拠地としている城では傘下の武将は城代になりません。本拠親政となるのは大名の居城だけです」
    this.provinces.forEach(p => {
      if (p.ownerId && this.isCapitalProvince(p.id, p.ownerId)) {
        const daimyoOfficer = this.activeOfficers.find(o => o.clanId === p.ownerId && o.isDaimyo && !o.assignedProvId && !o.isDead);
        if (daimyoOfficer) {
          p.governorId = daimyoOfficer.id;
          daimyoOfficer.assignedProvId = p.id;
        }
      }
    });

    // 【ステップ2: 支城（本拠地以外の城）への史実城代・有力家臣の配置】
    const histGovMap = (window.SCENARIO_HISTORICAL_GOVERNORS && window.SCENARIO_HISTORICAL_GOVERNORS[String(scenarioId)]) 
      ? window.SCENARIO_HISTORICAL_GOVERNORS[String(scenarioId)] 
      : null;

    // 2-A: シナリオ固有の史実城代マッピングの適用（※本拠地以外の城かつ自勢力所属の一般武将のみ）
    if (histGovMap) {
      this.provinces.forEach(p => {
        // 本拠地ではなく、かつまだ城主が未定の支城のみが対象
        if (!p.governorId && p.ownerId && !this.isCapitalProvince(p.id, p.ownerId) && histGovMap[p.id]) {
          const targetIdOrName = histGovMap[p.id];
          const forcedClan = window.JODAI_CLAN_BY_SCENARIO
            && window.JODAI_CLAN_BY_SCENARIO[String(scenarioId)]
            && window.JODAI_CLAN_BY_SCENARIO[String(scenarioId)][targetIdOrName];
          if (forcedClan) {
            const named = this.activeOfficers.find(o => (o.id === targetIdOrName || o.name === targetIdOrName) && !o.isDead && (!o.isDaimyo || !o.assignedProvId));
            if (named && !this.isNamedLandedLeader(named)) named.clanId = forcedClan;
          }
          const matchHist = (o) => (o.id === targetIdOrName || o.name === targetIdOrName) && !o.assignedProvId && !o.isDead && (!o.isDaimyo || !o.assignedProvId) && !(this.isNamedLandedLeader(o) && o.clanId !== p.ownerId);
          let histOff = this.activeOfficers.find(o => matchHist(o) && o.clanId === p.ownerId);
          if (!histOff) {
            histOff = this.activeOfficers.find(o => matchHist(o));
            if (histOff) histOff.clanId = p.ownerId;
          }
          if (histOff) {
            p.governorId = histOff.id;
            histOff.assignedProvId = p.id;
          }
        }
      });
    }

    const scenarioGovIds = new Set(Object.values(
      (window.SCENARIO_HISTORICAL_GOVERNORS && this.currentScenario)
        ? (window.SCENARIO_HISTORICAL_GOVERNORS[String(this.currentScenario.id)] || {})
        : {}
    ));
    // 特定の年の史実城代は、名簿のない別シナリオの支城へ流さない
    const isUnlistedJodai = (o) => String(o.id || '').startsWith('off_jd_') && !scenarioGovIds.has(o.id);

    // 2-B: 空き城で、同一勢力(clanId)かつ初期拠点(defaultProv)が一致する一般武将を配置
    this.provinces.forEach(p => {
      if (!p.governorId && p.ownerId && !this.isCapitalProvince(p.id, p.ownerId)) {
        const matchingOfficer = this.activeOfficers.find(o => 
          o.defaultProv === p.id && 
          o.clanId === p.ownerId && 
          !o.assignedProvId && 
          !o.isDead && 
          !o.isDaimyo &&
          !this.isCourtFigure(o) &&
          !isUnlistedJodai(o)
        );
        if (matchingOfficer) {
          p.governorId = matchingOfficer.id;
          matchingOfficer.assignedProvId = p.id;
        }
      }
    });

    // 2-C: ゆかりの地でも史実城代でもない支城へ、能力の高い待機武将は流さない。
    // 隠岐のように該当者がいない国は城主名を置かず、城代のままにする。

    this.foundingLeaderNames = {};
    (this.activeOfficers || []).forEach(o => {
      if (o.clanId && o.isDaimyo && !o.isDead && o.name && !this.foundingLeaderNames[o.clanId]) {
        this.foundingLeaderNames[o.clanId] = o.name;
      }
    });
    this.lastDaimyoNames = { ...this.foundingLeaderNames };

    // 空白地に過去に大名になったことのある武将がいれば旗揚げ・御家再興
    this.processBlankProvinceUprisings();
    // 初期配置は史実城代とゆかりの地だけ。進行が始まってから前線へ配る
    this.appointHistoricalHomeGovernors();
    this.autoAppointComputerCastellans();

    const allPlayables = this.ensureAllPlayables(scen);
    this.renderDaimyoGrid(allPlayables, scen.recommendedClan);
    // ここで領主データが反映された正確な位置・家紋でSVGマップを再構築する
    this.initSvgMap();
    this.updateMapDisplay();
  },

  ensureAllPlayables(scen) {
    if (!scen || !this.provinces) return scen?.playables || [];

    // 現在のマップ上で実際に領国を持っている全勢力（null, roninを除く）
    const ownedProvsByClan = {};
    this.provinces.forEach(p => {
      const cid = p.ownerId;
      if (!cid || cid === 'null' || cid === 'ronin') return;
      if (!ownedProvsByClan[cid]) ownedProvsByClan[cid] = [];
      ownedProvsByClan[cid].push(p.id);
    });

    const activeClanIds = Object.keys(ownedProvsByClan);
    const existingPlayables = Array.isArray(scen.playables) ? [...scen.playables] : [];
    const existingMap = new Map(existingPlayables.map(p => [p.id, p]));

    const allPlayables = [];

    activeClanIds.forEach(clanId => {
      const owned = ownedProvsByClan[clanId] || [];
      const provCount = owned.length;
      if (provCount === 0) return;

      const existing = existingMap.get(clanId);
      if (existing) {
        const master = (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA[clanId]) || {};
        const ability = (typeof getClanAbility === 'function') ? getClanAbility(clanId) : {};
        const item = { ...existing };
        item.provCount = provCount;
        item.myProvinces = owned;

        // シナリオ既定の本拠が今の領国にないとき、または登録本拠と食い違うときは実際の本拠に合わせる
        const capId = this.resolveClanCapitalId(clanId, owned);
        if (capId) item.startProvId = capId;

        // 当主武将の特定 (officerId または生存中の大名武将)
        let leaderOfficer = null;
        if (item.officerId && Array.isArray(window.OFFICERS_MASTER)) {
          leaderOfficer = window.OFFICERS_MASTER.find(o => o.id === item.officerId);
        }
        if (!leaderOfficer) {
          leaderOfficer = this.getClanDaimyoOfficer(clanId);
        }

        // 当主名
        let leaderName = leaderOfficer ? leaderOfficer.name : (item.name || item.leaderName || this.getDaimyoLeaderName(clanId));
        if (!leaderName || leaderName === clanId || leaderName === '空白地') {
          leaderName = master.family || clanId;
        }
        // シナリオ原本の当主名は残す（再訪時に前回の表示名で当主を選ばない）
        item.scenarioLeaderName = existing.scenarioLeaderName || existing.name || existing.leaderName || leaderName;
        // 当主名の最新化（生存中の大名武将を反映）
        const currentLeader = this.getClanDaimyoOfficer(clanId);
        if (currentLeader && currentLeader.name) {
          item.name = currentLeader.name;
        } else {
          item.name = leaderName;
        }

        // 家名
        let clanFamily = item.clan || this.getClanFamilyName(clanId);
        if (clanId === 'kakizaki' && scen.year >= 1599) {
          clanFamily = '松前家';
        }
        if (!clanFamily || clanFamily === clanId) {
          clanFamily = master.family || `${item.name}家`;
        }
        item.clan = clanFamily;

        // カラー、家紋、crest
        item.color = item.color || master.color || '#445566';
        item.crest = item.crest || (item.clan ? item.clan.slice(0, 1) : '武');
        item.kamonSvgId = (!item.kamonSvgId || item.kamonSvgId === 'kamon-default') ? this.getClanKamonId(clanId) : item.kamonSvgId;

        // 戦術
        item.tactic = item.tactic || master.tactic || '威風の指揮';
        item.tacticDesc = item.tacticDesc || master.tacticDesc || '士気を高め、軍の進軍と戦闘威力を底上げする。';

        // 能力値 (stats)
        if (!item.stats) {
          if (leaderOfficer) {
            item.stats = {
              military: leaderOfficer.military || ability.military || 60,
              politics: leaderOfficer.politics || ability.politics || 60,
              intellect: leaderOfficer.stratagem || ability.stratagem || 55,
              stratagem: leaderOfficer.stratagem || ability.stratagem || 55
            };
          } else {
            item.stats = {
              military: ability.military || 60,
              politics: ability.politics || 60,
              intellect: ability.stratagem || 55,
              stratagem: ability.stratagem || 55
            };
          }
        }

        // personality
        item.personality = item.personality || ability.personality || 'balanced';

        allPlayables.push(item);
      } else {
        const master = (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA[clanId]) || {};
        const ability = getClanAbility(clanId);

        // 当主武将の特定
        let leaderName = '';
        const daimyoOff = this.getClanDaimyoOfficer(clanId);
        if (daimyoOff) {
          leaderName = daimyoOff.name;
        } else {
          leaderName = this.getDaimyoLeaderName(clanId);
        }
        if (!leaderName || leaderName === clanId || leaderName === '空白地') {
          leaderName = master.family || clanId;
        }

        // 家名
        let clanFamily = this.getClanFamilyName(clanId);
        if (clanId === 'kakizaki' && scen.year >= 1599) {
          clanFamily = '松前家';
        }
        if (!clanFamily || clanFamily === clanId) {
          clanFamily = master.family || `${leaderName}家`;
        }

        // 難易度・勝率
        let difficulty = '上級';
        let winRate = 58;
        if (provCount >= 5) {
          difficulty = '初級';
          winRate = 85;
        } else if (provCount >= 3) {
          difficulty = '中級';
          winRate = 75;
        } else if (provCount >= 2) {
          difficulty = '中級';
          winRate = 68;
        } else {
          difficulty = '上級';
          winRate = 58;
        }

        // 本拠は実際の本拠判定と同じ関数で決める（画面の「本拠」とゲーム内の居城を一致させる）
        const startProvId = this.resolveClanCapitalId(clanId, owned) || owned[0];

        const desc = master.desc 
          ? master.desc 
          : `${clanFamily}の当主・${leaderName}。${provCount}国を領有し、領民を守りつつ天下統一の覇業に挑む。`;

        const tactic = master.tactic || '剛勇の指揮';
        const tacticDesc = master.tacticDesc || '士気を高め、軍勢の進軍と戦闘威力を向上させる。';

        allPlayables.push({
          id: clanId,
          name: leaderName,
          clan: clanFamily,
          color: master.color || '#445566',
          crest: clanFamily.slice(0, 1),
          kamonSvgId: this.getClanKamonId(clanId),
          difficulty: difficulty,
          winRate: winRate,
          startProvId: startProvId,
          provCount: provCount,
          myProvinces: owned,
          gold: Math.max(2500, provCount * 2000 + 1000),
          rice: Math.max(3000, provCount * 2500 + 1200),
          desc: desc,
          tactic: tactic,
          tacticDesc: tacticDesc,
          stats: {
            military: ability.military || 60,
            politics: ability.politics || 60,
            intellect: ability.stratagem || 55,
            stratagem: ability.stratagem || 55
          },
          personality: ability.personality || 'balanced'
        });
      }
    });

    // ソート: 北の勢力から順に（本拠の北緯の降順。同緯度は領国の平均北緯、次に東から）
    this.sortPlayablesNorthToSouth(allPlayables);

    scen.playables = allPlayables;
    return allPlayables;
  },

  /** 勢力カードを北→南に並べる。鍵は本拠（startProvId）の北緯、同値なら領国の平均北緯 */

  sortPlayablesNorthToSouth(playables) {
    if (!Array.isArray(playables)) return playables;
    const keyOf = (d) => {
      const provs = (d.myProvinces && d.myProvinces.length) ? d.myProvinces : [d.startProvId].filter(Boolean);
      const capId = d.startProvId || provs[0];
      const capLat = capId ? this.provinceLatitude(capId) : 0;
      const avgLat = provs.length ? provs.reduce((t, id) => t + this.provinceLatitude(id), 0) / provs.length : capLat;
      const capProv = (this.provinces || []).find(p => p.id === capId);
      const c = this.provinceCenterXY(capProv || { id: capId });
      return { capLat, avgLat, east: c ? c.x : 0 };
    };
    const keys = new Map(playables.map(d => [d, keyOf(d)]));
    playables.sort((a, b) => {
      const ka = keys.get(a), kb = keys.get(b);
      if (kb.capLat !== ka.capLat) return kb.capLat - ka.capLat;
      if (kb.avgLat !== ka.avgLat) return kb.avgLat - ka.avgLat;
      if (kb.east !== ka.east) return kb.east - ka.east;
      return String(a.id).localeCompare(String(b.id));
    });
    return playables;
  },

  getCastleName(provId) {
    const prov = this.provinces.find(p => p.id === provId);
    if (!prov) return '城';
    return prov.castleName || prov.castle || '城';
  },

  // ============================================================================
  // 武将システム & 大名本拠地親政（100%）・城代（40%〜75%ランダム）エンジン
  // ============================================================================
  // 武将ライフサイクル（元服・寿命・死亡）管理 (要件1: 年齢15歳未満は絶対に登場させない),

  updateActiveOfficers() {
    if (!window.OFFICERS_MASTER) return;

    // 既存の activeOfficers の状態（assignedProvId, isDaimyo, isDead等）を保持するためのマップ
    const existingMap = new Map();
    if (this.activeOfficers) {
      this.activeOfficers.forEach(o => existingMap.set(o.id, o));
    }

    const nextActive = [];

    // window.OFFICERS_MASTER から、(現在年 - birthYear >= 15) かつ (現在年 <= deathYear) かつ !isDead を満たす武将のみを抽出
    for (const master of window.OFFICERS_MASTER) {
      const existing = existingMap.get(master.id);
      const isNew = !existing;
      const officer = existing || JSON.parse(JSON.stringify(master));
      if (isNew) {
        officer.isDaimyo = false;
      }
      // セーブに残った誤生年で、まだ生まれていない人物を登場させない
      officer.birthYear = master.birthYear;
      officer.deathYear = master.deathYear;

      const bYear = Number(officer.birthYear);
      const dYear = Number(officer.deathYear);

      // 生没年が無効な場合はスキップ
      if (isNaN(bYear) || isNaN(dYear)) continue;

      const age = this.year - bYear;
      // 15歳未満（およびマイナス年齢・まだ生まれていない武将）は絶対に登場させない
      const isGenpuku = (age >= 15);
      const isAlive = (this.year <= dYear) && !officer.isDead;

      if (officer.name && /[（(][^）)]+[）)]/.test(officer.name)) {
        officer.name = officer.name.replace(/\s*[（(][^）)]+[）)]/g, '').trim();
      }

      if (isGenpuku && isAlive) {
        nextActive.push(officer);
      } else if (existing && this.year > dYear) {
        officer.isDead = true;
      }
    }

    // 動的生成された大名等（window.OFFICERS_MASTER 外の武将）も同様に15歳以上かつ寿命内のみ保持
    if (this.activeOfficers) {
      for (const o of this.activeOfficers) {
        if (!window.OFFICERS_MASTER.some(m => m.id === o.id)) {
          if (o.name && /[（(][^）)]+[）)]/.test(o.name)) {
            o.name = o.name.replace(/\s*[（(][^）)]+[）)]/g, '').trim();
          }
          const bYear = Number(o.birthYear);
          const dYear = Number(o.deathYear);
          if (!isNaN(bYear) && !isNaN(dYear)) {
            const age = this.year - bYear;
            if (age >= 15 && this.year <= dYear && !o.isDead) {
              nextActive.push(o);
            }
          }
        }
      }
    }

    this.activeOfficers = nextActive;
    this.officers = this.activeOfficers; // 後方互換性

    // 現在の各領国 (this.provinces) を巡回し、城主 (governorId) が activeOfficers 内に存在しない場合は governorId = null として解任しログ出力
    if (this.provinces) {
      this.provinces.forEach(p => {
        if (p.governorId) {
          const exists = this.activeOfficers.some(o => o.id === p.governorId);
          if (!exists) {
            const prevName = existingMap.get(p.governorId)?.name || '城主';
            p.governorId = null;
            this.log(`【城主逝去】${p.name}の城主・${prevName}は天寿を全うし逝去しました。城主を解任します。`);
          }
        }
      });
    }
  },

  // 各シナリオにおける所属大名不在武将の史実振り替え・浪人化処理 (要件2),

  resolveOfficerAffiliations(scen) {
    if (!this.activeOfficers || !this.provinces) return;
    const ownersSet = new Set(this.provinces.map(p => p.ownerId).filter(Boolean));
    const year = this.year;
    const clanBefore = new Map(this.activeOfficers.map(o => [o.id, o.clanId]));

    const scenGovMap = (window.SCENARIO_HISTORICAL_GOVERNORS && window.SCENARIO_HISTORICAL_GOVERNORS[String(scen.id)]) || {};

    // 各領国の城主（城代または大名居城当主）の事前把握
    const provCastellans = [];
    (this.provinces || []).forEach(p => {
      if (!p.ownerId || !ownersSet.has(p.ownerId)) return;
      const govId = scenGovMap[p.id];
      if (govId) {
        provCastellans.push({ provId: p.id, ownerId: p.ownerId, officerId: govId });
      } else if (this.isCapitalProvince(p.id, p.ownerId)) {
        const daimyoOff = this.activeOfficers.find(o => o.clanId === p.ownerId && o.isDaimyo);
        if (daimyoOff) {
          provCastellans.push({ provId: p.id, ownerId: p.ownerId, officerId: daimyoOff.id });
        }
      }
    });

    this.activeOfficers.forEach(off => {
      // プレイヤー配下に仕官済みの武将は、年が変わってもシナリオ補正で引き抜かない
      if (off.clanId === this.playerClanId && ownersSet.has(this.playerClanId)) return;
      // 領地を持つ家の現当主は、年次の再判定で家臣に戻さない（CPU大名が毎年入れ替わるのを防ぐ）
      if (off.isDaimyo && !off.isDead && ownersSet.has(off.clanId)) return;

      // 【史実城代・配置武将の絶対保証】
      // シナリオの史実城代（SCENARIO_HISTORICAL_GOVERNORS）に指名されている武将は、
      // その領国の領主（ownerId）に確実に配属（浪人化・城主不在を完全防止）
      const myGovProv = Object.keys(scenGovMap).find(pId => scenGovMap[pId] === off.id);
      if (myGovProv) {
        const pObj = this.provinces.find(p => p.id === myGovProv);
        const provOwner = pObj ? pObj.ownerId : null;
        // 本拠（当主の居城）は城代を置かないので、そこへの指名では他家へ移さない
        if (provOwner && ownersSet.has(provOwner) && !this.isCapitalProvince(myGovProv, provOwner)) {
          // シナリオ当主は城代名簿で吸収しない（清衡が義家配下になる、など）
          if (this.isNamedLandedLeader(off)) return;
          off.clanId = provOwner;
          off.isDaimyo = false;
          return;
        }
      }

      // 秀頼は浪人・所領のない家にいるときだけ豊臣本家へ戻す。仕官中の武将は引き抜かない
      if (ownersSet.has('toyotomi') && this.isHideyoriOfficer(off) && !this.isServingLandedClan(off, ownersSet)) {
        off.clanId = 'toyotomi';
        return;
      }

      // 時代・シナリオ固有の所属は data.js の OFFICER_AFFILIATION_RULES（ID完全一致）で適用
      if (this.applyOfficerAffiliationRules(off, { year, scenId: scen && scen.id, ownersSet })) return;

      // 一門ロスター（ID集合）による城代領国への配属
      const familyRosters = window.OFFICER_FAMILY_ROSTERS || {};
      const assignByFamily = (familyKey, fallbackProvIds) => {
        const ids = familyRosters[familyKey] || [];
        if (!this.officerIdIn(off, ids)) return false;
        const target = provCastellans.find(c => {
          const cOff = this.activeOfficers.find(o => o.id === c.officerId);
          return cOff && this.officerIdIn(cOff, ids);
        }) || (fallbackProvIds || []).map(pid => provCastellans.find(c => c.provId === pid && ownersSet.has(c.ownerId))).find(Boolean);
        if (!target) return false;
        off.clanId = target.ownerId;
        off.isDaimyo = false;
        off.assignedProvId = null;
        if (!this.provinces.some(p => p.id === off.defaultProv && p.ownerId === target.ownerId)) off.defaultProv = target.provId;
        return true;
      };
      if (assignByFamily('chosokabe', ['tosa'])) return;
      if (assignByFamily('nanbu', ['rikuchu', 'mutsu'])) return;

      const homeClan = clanBefore.get(off.id) || off.clanId;

      // 主家が地図上に残っていれば、ゆかりの地が他家領でも主家の家臣のまま（他家吸収・浪人化しない）
      if (homeClan && homeClan !== 'ronin' && homeClan !== 'independent' && ownersSet.has(homeClan)) {
        off.clanId = homeClan;
        return;
      }

      // 主家が地図にないときは data.js の CLAN_SERVICE_FALLBACKS（年代つき）で史実の仕官先へ
      if (this.applyClanServiceFallback(off, homeClan, year, ownersSet)) return;

      // 朝廷・院・公家方は、城代の配置先を理由に武家へ吸収しない
      const nonAbsorbable = new Set(window.NON_ABSORBABLE_CLANS || ['heian_court', 'court']);

      // 一般一門：元々の主家clanIdが一致する城主がいる領国へ配属（城主の多い主家を優先）
      if (homeClan && homeClan !== 'ronin' && homeClan !== 'independent' && homeClan !== 'court' && !nonAbsorbable.has(homeClan)) {
        const matches = provCastellans.filter(c => {
          const cOff = this.activeOfficers.find(o => o.id === c.officerId);
          if (!cOff) return false;
          const cOrig = clanBefore.get(cOff.id) || cOff.clanId;
          return cOrig === homeClan;
        });
        const votes = new Map();
        matches.forEach(c => votes.set(c.ownerId, (votes.get(c.ownerId) || 0) + 1));
        const target = matches.slice().sort((a, b) => (votes.get(b.ownerId) || 0) - (votes.get(a.ownerId) || 0))[0];
        if (target) {
          off.clanId = target.ownerId;
          off.isDaimyo = false;
          off.assignedProvId = null;
          // 自分のゆかりの地が新しい主家の領内にあれば、それを上書きしない（本拠・城主選びに使う）
          if (!this.provinces.some(p => p.id === off.defaultProv && p.ownerId === target.ownerId)) off.defaultProv = target.provId;
          return;
        }
      }

      // 2. 所属大名が不在の武将は「浪人（諸国流浪・未仕官）」とし、仕官・登用の対象とする
      // 滅んだ家の旧臣を征服大名へ自動で吸収せず、浪人として登場させる
      // 天皇・親王は浪人にしない。新政府が地図に出るまで登場させない。
      if (this.isCourtFigure(off)) return;

      off.clanId = 'ronin';
      off.assignedProvId = null;
      off.isDaimyo = false;
      if (off.id === 'off_ashikaga_yoshiaki') {
        off.defaultProv = 'bingo';
        off.assignedProvId = 'bingo';
      }
    });

    this.activeOfficers = this.activeOfficers.filter(off => {
      if (!this.isCourtFigure(off)) return true;
      return ownersSet.has(off.clanId);
    });

    // 領地のない滅家の名跡を浪人の山にしない。史実城代に指名した者だけ残す。
    if (scen && scen.fieldLandedOnly) {
      const govIds = new Set(Object.values(
        (window.SCENARIO_HISTORICAL_GOVERNORS && window.SCENARIO_HISTORICAL_GOVERNORS[String(scen.id)]) || {}
      ));
      this.activeOfficers = this.activeOfficers.filter(off => off.clanId !== 'ronin' || govIds.has(off.id));
    }

    // 他家へ移った元当主は、移動先の当主にしない（史実振り替えは配下としての移籍）
    this.activeOfficers.forEach(off => {
      if (clanBefore.get(off.id) !== off.clanId) off.isDaimyo = false;
      if (off.id === 'off_ashikaga_yoshiaki' && off.clanId === 'ronin') {
        off.defaultProv = 'bingo';
        off.assignedProvId = 'bingo';
      }
    });
    this.reconcileDaimyoWithMap();
  },

  // 史実名簿上の当主名（生存中の isDaimyo には依存しない）,

  getRosterLeaderName(ownerId) {
    if (ownerId === 'anesanokoji' || ownerId === 'anesakoji') ownerId = 'anekoji';
    if (ownerId === 'hattori') ownerId = 'momochi';
    if (ownerId === 'saika') ownerId = 'suzuki';

    const profile = (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA[ownerId]) ? window.CLAN_MASTER_DATA[ownerId] : null;
    if (profile && profile.leaders) {
      const curY = Number(this.year || 0);
      const validYears = Object.keys(profile.leaders)
        .map(Number)
        .filter(y => !isNaN(y) && y <= curY)
        .sort((a, b) => b - a);
      if (validYears.length > 0) return profile.leaders[String(validYears[0])];
      if (profile.leaders.default) return profile.leaders.default;
    }
    const playable = this.currentScenario?.playables?.find(d => d.id === ownerId);
    return playable?.name || '';
  },

  // 領地を持つ家のシナリオ当主は、城代名簿で他家の配下にしない,

  isNamedLandedLeader(off) {
    if (!off || !off.name) return false;
    const owners = new Set((this.provinces || []).map(p => p.ownerId).filter(Boolean));
    const playables = this.currentScenario?.playables || [];
    for (const clanId of owners) {
      const playable = playables.find(d => d.id === clanId);
      if (playable && playable.name) {
        if (this.leaderNamesMatch(off.name, playable.name)) return true;
        continue;
      }
      if (this.leaderNamesMatch(off.name, this.getRosterLeaderName(clanId))) return true;
    }
    return false;
  },

  leaderNamesMatch(a, b) {
    if (!a || !b) return false;
    if (a === b) return true;
    // 別名は data.js の LEADER_NAME_ALIASES（完全一致のグループ）だけで名寄せする。部分一致はしない
    const groups = window.LEADER_NAME_ALIASES || [];
    const canon = (n) => {
      const g = groups.find(arr => Array.isArray(arr) && arr.includes(n));
      return g ? g[0] : n;
    };
    return canon(a) === canon(b);
  },

  isHideyoriOfficer(off) {
    if (!off) return false;
    return off.id === 'off_dm_toyotomi_1600' || off.id === 'off_toyotomi_hideyori';
  },



  // 武将IDがID配列（OFFICER_AFFILIATION_RULES / 一門ロスター）に含まれるか（ID完全一致）,

  officerIdIn(off, ids) {
    if (!off || !off.id || !ids) return false;
    if (ids instanceof Set) return ids.has(off.id);
    return Array.isArray(ids) && ids.includes(off.id);
  },

  // 主家が地図にない武将を、年代に応じた史実の仕官先へ（data.js の CLAN_SERVICE_FALLBACKS）,

  applyClanServiceFallback(off, homeClan, year, ownersSet) {
    if (!off || !homeClan) return false;
    const list = window.CLAN_SERVICE_FALLBACKS || [];
    for (const fb of list) {
      if (!fb || !Array.isArray(fb.clanIds) || !fb.clanIds.includes(homeClan)) continue;
      if (fb.fromYear != null && year < fb.fromYear) continue;
      if (fb.toYear != null && year > fb.toYear) continue;
      if (!ownersSet.has(fb.setClanId)) continue;
      off.clanId = fb.setClanId;
      off.isDaimyo = false;
      off.assignedProvId = null;
      return true;
    }
    return false;
  },

  applyOfficerAffiliationRules(off, { year, scenId, ownersSet }) {
    const rules = window.OFFICER_AFFILIATION_RULES || [];
    for (const rule of rules) {
      if (!rule || !this.officerIdIn(off, rule.officerIds || [])) continue;
      if (rule.unlessOwner && ownersSet.has(rule.unlessOwner)) continue;
      if (rule.fromYear != null || rule.toYear != null) {
        // 年代幅（fromYear〜toYear）。シナリオ指定があればそちらでも可
        const scenOk = rule.scenarioIds && rule.scenarioIds.some(id => String(id) === String(scenId));
        const inRange = (rule.fromYear == null || year >= rule.fromYear) && (rule.toYear == null || year <= rule.toYear);
        if (!inRange && !scenOk) continue;
      } else if (rule.years && rule.years.length) {
        const scenOk = rule.scenarioIds && rule.scenarioIds.some(id => String(id) === String(scenId));
        if (!rule.years.includes(year) && !scenOk) continue;
      } else if (rule.scenarioIds && rule.scenarioIds.length) {
        if (!rule.scenarioIds.some(id => String(id) === String(scenId))) continue;
      }
      if (rule.requireOwners && rule.requireOwners.length) {
        if (!rule.requireOwners.some(c => ownersSet.has(c))) continue;
      }
      off.clanId = rule.setClanId;
      if (rule.setDaimyo === false) off.isDaimyo = false;
      if (rule.setDaimyo === true) off.isDaimyo = true;
      if (rule.setDefaultProv) off.defaultProv = rule.setDefaultProv;
      if (rule.setAssignedProv) off.assignedProvId = rule.setAssignedProv;
      if (rule.clearAssignment) off.assignedProvId = null;
      return true;
    }
    return false;
  },

  /** ダイアログ表示直前に発火済みフラグを立てる。既に発火済みなら false */

  markHistoricalEventTriggered(eventId) {
    this.triggeredHistoricalEvents = this.triggeredHistoricalEvents || new Set();
    this.happenedEvents = this.happenedEvents || new Set();
    if (!eventId) return false;
    if (this.triggeredHistoricalEvents.has(eventId)) return false;
    this.triggeredHistoricalEvents.add(eventId);
    this.happenedEvents.add(eventId);
    return true;
  },

  isHistoricalEventBusy() {
    return !!(this._historyQueueRunning
      || this._historyEventDone
      || this._historyCheckPending
      || (this.pendingHistoryQueue && this.pendingHistoryQueue.length)
      || this.isEventChoiceOpen());
  },

  /** 歴史イベント判定を予約する。予約中は季節を進めないので、連打で季節イベントを飛ばさない */

  scheduleHistoricalEventCheck(delayMs = 0) {
    this._historyCheckPending = true;
    if (this._historyCheckTimer) {
      clearTimeout(this._historyCheckTimer);
      this._historyCheckTimer = null;
    }
    const run = () => {
      this._historyCheckTimer = null;
      // 合戦中は判定を見送らず、合戦が終わるまで待ってから同じ季節の判定を行う
      if (this.inBattle) {
        this._historyCheckTimer = setTimeout(run, 500);
        return;
      }
      this._historyCheckPending = false;
      this.checkHistoricalEvents();
    };
    if (delayMs > 0) this._historyCheckTimer = setTimeout(run, delayMs);
    else run();
  },

  /** 合戦で中断した歴史イベントの待ち行列を、合戦後に再開する */

  resumeHistoryQueueWhenFree() {
    if (this._historyQueueResumeTimer) return;
    const tick = () => {
      this._historyQueueResumeTimer = null;
      if (!this.pendingHistoryQueue || !this.pendingHistoryQueue.length) return;
      if (this.inBattle || this._historyQueueRunning) {
        this._historyQueueResumeTimer = setTimeout(tick, 500);
        return;
      }
      void this.processHistoricalEventQueue();
    };
    this._historyQueueResumeTimer = setTimeout(tick, 500);
  },

  isServingLandedClan(off, ownersSet) {
    if (!off?.clanId || off.clanId === 'ronin' || off.clanId === 'toyotomi') return false;
    return ownersSet.has(off.clanId);
  },

  // 当主は「地図上に領国がある勢力」につき1人だけ。領地のない家の旗は外す。,

  reconcileDaimyoWithMap() {
    if (!this.activeOfficers || !this.provinces) return;
    const owners = new Set(this.provinces.map(p => p.ownerId).filter(Boolean));

    this.activeOfficers.forEach(o => {
      if (!owners.has(o.clanId)) o.isDaimyo = false;
    });

    owners.forEach(ownerId => {
      const flagged = this.activeOfficers.filter(o => o.clanId === ownerId && o.isDaimyo && !o.isDead);
      if (flagged.length <= 1) return;

      const rosterName = this.getRosterLeaderName(ownerId);
      const capitalId = window.CLAN_CAPITAL_PROVINCES ? window.CLAN_CAPITAL_PROVINCES[ownerId] : null;
      const score = (o) => {
        const prov = o.assignedProvId
          ? this.provinces.find(p => p.id === o.assignedProvId && p.ownerId === ownerId && p.governorId === o.id)
          : null;
        let s = 0;
        if (prov && (prov.id === capitalId || this.isCapitalProvince(prov.id, ownerId))) s += 4;
        else if (prov) s += 2;
        if (this.leaderNamesMatch(o.name, rosterName)) s += 3;
        return s;
      };
      flagged.sort((a, b) => score(b) - score(a));
      const keep = flagged[0];
      flagged.forEach(o => {
        if (o.id !== keep.id) o.isDaimyo = false;
      });
    });
  },

  // 蝦夷から薩摩まで、地方を北から南、地方内も北から南,

  provinceGeoRank(provId) {
    if (!SengokuGame._provinceGeoRank) {
      // 並びは data.js の PROVINCE_NORTH_TO_SOUTH
      const order = window.PROVINCE_NORTH_TO_SOUTH || [];
      SengokuGame._provinceGeoRank = new Map(order.map((id, i) => [id, i]));
    }
    if (provId && SengokuGame._provinceGeoRank.has(provId)) return SengokuGame._provinceGeoRank.get(provId);
    return 10000;
  },

  officerBaseProvinceId(off) {
    if (!off) return '';
    if (off.assignedProvId) return off.assignedProvId;
    if (off.clanId === 'ronin') return off.defaultProv || '';
    // 自勢力が領有しているゆかりの支城（城主と同族など）があれば、その領国で待機中
    if (off.defaultProv) {
      const ownedBranch = (this.provinces || []).find(p => p.id === off.defaultProv && p.ownerId === off.clanId);
      if (ownedBranch) return ownedBranch.id;
    }
    const home = this.getDaimyoHomeProvince(off);
    return home ? home.id : (off.defaultProv || '');
  },

  // 当主の居城は、その家が現に領有している国だけを返す,

  getDaimyoHomeProvince(off) {
    if (!off || !off.clanId || off.clanId === 'ronin') return null;
    const owned = (this.provinces || []).filter(p => p.ownerId === off.clanId);
    if (owned.length === 0) return null;
    const capId = window.CLAN_CAPITAL_PROVINCES && window.CLAN_CAPITAL_PROVINCES[off.clanId];
    if (capId) {
      const cap = owned.find(p => p.id === capId);
      if (cap) return cap;
    }
    return owned.find(p => this.isCapitalProvince(p.id, off.clanId)) || this.pickFallbackCapital(owned, off.clanId) || owned[0];
  },

  // 領国奪取時の城主解任・退避・滅亡処理 (要件4 & 捕縛連携),

  handleProvinceLoss(dstProv, oldOwnerId, isPlayerConquest = false) {
    if (!dstProv || !oldOwnerId) return;

    const oldGovId = dstProv.governorId;
    // 1. 必ず陥落した城の governorId = null にリセット
    dstProv.governorId = null;

    // 陥落時の城主武将を取得
    const gov = oldGovId ? (this.activeOfficers || []).find(o => o.id === oldGovId) : null;
    const remainingProvs = this.provinces.filter(p => p.ownerId === oldOwnerId && p.id !== dstProv.id);
    const isDestroyed = (remainingProvs.length === 0);

    // 【フェーズ1: 本拠地陥落時の大名逃亡・遷都フェイルセーフ】
    // 城主が大名かどうかの判定(gov.isDaimyo)に依存せず、陥落した領国が本拠地だった場合は確実に残存領国(remainingProvs[0])へ本拠地を移転
    const isCapitalLoss = (window.CLAN_CAPITAL_PROVINCES && window.CLAN_CAPITAL_PROVINCES[oldOwnerId] === dstProv.id) || this.isCapitalProvince(dstProv.id, oldOwnerId);
    if (isCapitalLoss && !isDestroyed && remainingProvs.length > 0) {
      const escapeProv = remainingProvs[0];
      if (window.CLAN_CAPITAL_PROVINCES) {
        window.CLAN_CAPITAL_PROVINCES[oldOwnerId] = escapeProv.id;
      }
      const daimyo = (this.activeOfficers || []).find(o => o.clanId === oldOwnerId && o.isDaimyo && !o.isDead);
      const daimyoName = daimyo ? daimyo.name : this.getDaimyoLeaderName(oldOwnerId);
      this.log(`🏛️【本拠陥落・遷都】${this.getClanFamilyName(oldOwnerId)}の本拠地・${dstProv.name}が陥落したため、${daimyoName}公は${escapeProv.name}へと本拠地を移転しました。`, 'battle');
    }

    // 陥落した城にいた大名・待機武将が敵領地に取り残されないよう所在を安全に解除
    (this.activeOfficers || []).forEach(o => {
      if (o.clanId === oldOwnerId && o.assignedProvId === dstProv.id) {
        o.assignedProvId = null;
      }
    });

    if (gov) {
      // 2. 陥落時に城主がいた場合、その武将の assignedProvId = null にする
      gov.assignedProvId = null;

      // 3. もしその城主が大名（isDaimyo: true）だった場合
      if (gov.isDaimyo) {
        if (!isDestroyed) {
          // 他に自勢力の領国が残っていれば、そちらへ本拠地を移して逃亡した旨をログ出力
          const escapeProv = remainingProvs[0];
          if (window.CLAN_CAPITAL_PROVINCES) {
            window.CLAN_CAPITAL_PROVINCES[oldOwnerId] = escapeProv.id;
          }
          this.log(`🏃【本拠陥落・当主退避】${gov.name}公は居城を脱出し、${escapeProv.name}へと本拠地を移して退避しました！`, 'battle');
        } else {
          // 最後の領国だった場合
          if (!isPlayerConquest) {
            // AI同士の滅亡なら自刃
            gov.isDead = true;
            this.log(`💀【御家滅亡・自刃】${gov.name}公は最後の居城にて討死または自刃し、${this.getClanFamilyName(oldOwnerId)}は滅亡しました……`, 'important');
          }
          // プレイヤー攻略時は捕縛処理(handleCapturedOfficers)にて処断
        }
      } else {
        // 4. 一般武将だった場合
        if (!isDestroyed) {
          this.log(`🏃【城主敗走】城主・${gov.name}は陥落する城から落ち延び、本国へと逃げ帰りました（待機状態）。`);
        } else {
          if (!isPlayerConquest) {
            // AI同士で滅亡した場合は浪人化
            gov.clanId = 'ronin';
            // 【追加】元大名だった場合も含め大名フラグを初期化
            gov.isDaimyo = false;
            if (gov.id === 'off_ashikaga_yoshiaki') {
              gov.defaultProv = 'bingo';
              gov.assignedProvId = 'bingo';
            }
            this.log(`🍂【旧臣浪人】${gov.name}は主家滅亡に伴い浪人となりました。`);
          }
        }
      }
    } else {
      // 城主不在でも最後の領国なら
      if (isDestroyed && !isPlayerConquest) {
        const oldDaimyo = (this.activeOfficers || []).find(o => o.clanId === oldOwnerId && o.isDaimyo && !o.isDead);
        if (oldDaimyo) {
          oldDaimyo.isDead = true;
          oldDaimyo.assignedProvId = null;
        }
      }
    }

    // AI同士で滅亡した場合、残る全家臣（城にいなかった当主を含む）を浪人化
    if (isDestroyed && !isPlayerConquest) {
      (this.activeOfficers || []).forEach(o => {
        if (o.clanId === oldOwnerId && !o.isDead) {
          o.clanId = 'ronin';
          o.assignedProvId = null;
          o.isDaimyo = false;
          if (o.id === 'off_ashikaga_yoshiaki') {
            o.defaultProv = 'bingo';
            o.assignedProvId = 'bingo';
          }
        }
      });
    }

    if (isDestroyed) {
      this.removeClanFromAlliances(oldOwnerId);
    }
  },

  // 本拠の選び方（登録本拠が領内にないとき）：
  //  1) 存命当主のゆかりの地（defaultProv） 2) 家中の武将のゆかりの地（当主級→人数の多い国）
  //  3) 史実本拠（CLAN_CAPITAL_PROVINCES / シナリオ本拠 / CLAN_MASTER_DATA.capital_pref）
  //  4) 領国の地理的な中心に最も近い国。北端・石高最大では選ばない,

  pickFallbackCapital(owned, clanIdArg = null) {
    if (!owned || owned.length === 0) return null;
    const list = owned.filter(Boolean);
    if (list.length === 1) return list[0];
    const clanId = clanIdArg || list[0].ownerId;
    const byId = new Map(list.map(p => [p.id, p]));
    const homeOf = (o) => this.officerHomeProvince(o);
    const officers = (this.activeOfficers || []).filter(o => o && o.clanId === clanId && !o.isDead && homeOf(o));
    const power = (o) => (Number(o.military) || 0) + (Number(o.politic || o.politics) || 0) + (Number(o.intel || o.intelligence) || 0);

    // 1) 当主のゆかりの地
    const lords = officers.filter(o => o.isDaimyo).sort((a, b) => power(b) - power(a));
    for (const lord of lords) {
      if (byId.has(homeOf(lord))) return byId.get(homeOf(lord));
    }

    // 2) 家中のゆかりの地：大名経験者を重く、次に同郷の人数、同点は能力
    const votes = new Map();
    officers.forEach(o => {
      const home = homeOf(o);
      if (!byId.has(home)) return;
      const w = (o.hasBeenDaimyo || (this.formerDaimyoIds && this.formerDaimyoIds.has(o.id))) ? 5 : 1;
      const cur = votes.get(home) || { score: 0, best: 0 };
      cur.score += w;
      cur.best = Math.max(cur.best, power(o));
      votes.set(home, cur);
    });
    if (votes.size) {
      const [bestId] = [...votes.entries()].sort((a, b) => (b[1].score - a[1].score) || (b[1].best - a[1].best))[0];
      if (byId.has(bestId)) return byId.get(bestId);
    }

    // 3) 史実本拠
    const prefs = [];
    const scenCaps = (this.currentScenario && this.currentScenario.capitals) || {};
    if (scenCaps[clanId]) prefs.push(scenCaps[clanId]);
    prefs.push(...this.eraCapitalCandidates(clanId));
    const base = window.CLAN_CAPITAL_PROVINCES_BASE || {};
    if (base[clanId]) prefs.push(base[clanId]);
    const cur = window.CLAN_CAPITAL_PROVINCES || {};
    if (cur[clanId]) prefs.push(cur[clanId]);
    const master = (window.CLAN_MASTER_DATA || {})[clanId];
    if (master && Array.isArray(master.capital_pref)) prefs.push(...master.capital_pref);
    for (const pid of prefs) {
      if (byId.has(pid)) return byId.get(pid);
    }

    // 4) 地理的な中心
    return this.pickCentralProvince(list);
  },

  /** 武将本来のゆかりの地（OFFICERS_MASTER の defaultProv。所属替えで書き換わった値より優先） */

  officerHomeProvince(o) {
    if (!o) return '';
    const master = window.OFFICERS_MASTER || [];
    if (SengokuGame._homeProvSrc !== master) {
      SengokuGame._homeProvSrc = master;
      SengokuGame._homeProvMap = new Map(master.map(m => [m.id, m.defaultProv]));
    }
    return SengokuGame._homeProvMap.get(o.id) || o.defaultProv || '';
  },

  /** 国の中心座標（地図の cx/cy。無ければ PROVINCES_DATA） */

  pickCentralProvince(list) {
    if (!list || !list.length) return null;
    const pts = list.map(p => ({ p, c: this.provinceCenterXY(p) })).filter(item => item.c);
    if (!pts.length) {
      // 座標が無いときは北→南の並びの中央
      const sorted = list.slice().sort((a, b) => this.provinceGeoRank(a.id) - this.provinceGeoRank(b.id));
      return sorted[Math.floor((sorted.length - 1) / 2)];
    }
    const mx = pts.reduce((t, item) => t + item.c.x, 0) / pts.length;
    const my = pts.reduce((t, item) => t + item.c.y, 0) / pts.length;
    pts.sort((a, b) => {
      const da = (a.c.x - mx) ** 2 + (a.c.y - my) ** 2;
      const db = (b.c.x - mx) ** 2 + (b.c.y - my) ** 2;
      if (da !== db) return da - db;
      return (Number(b.p.kokudaka) || 0) - (Number(a.p.kokudaka) || 0);
    });
    return pts[0].p;
  },

  /** 勢力の現在の本拠（登録本拠が領内ならそれ、なければ pickFallbackCapital）。勢力選択画面の「本拠」もこれを使う */

  resolveClanCapitalId(clanId, ownedIds = null) {
    const owned = (this.provinces || []).filter(p => p.ownerId === clanId && (!ownedIds || ownedIds.includes(p.id)));
    if (!owned.length) return null;
    const registered = (window.CLAN_CAPITAL_PROVINCES || {})[clanId];
    if (registered && owned.some(p => p.id === registered)) return registered;
    const home = this.pickFallbackCapital(owned, clanId);
    return home ? home.id : owned[0].id;
  },

  /** 国のおおよその北緯（data.js の PROVINCE_LATITUDE）。無ければ北→南の並びから推定 */

  isCourtFigure(off) {
    if (!off || !off.name) return false;
    return /天皇|上皇|法皇|神祇/.test(off.name);
  },

  // 史実イベントで「預かり」の城代を指定する。領地の主君は変えず、武将だけを家臣として座らせる。,

  appointHistoricalCastellans(appoint) {
    if (!appoint || !this.activeOfficers) return;
    for (const [pId, offId] of Object.entries(appoint)) {
      const prov = this.provinces.find(p => p.id === pId);
      if (!prov || !prov.ownerId) continue;
      const aliasId = (window.OFFICER_ID_ALIASES || {})[offId] || offId;
      const off = this.activeOfficers.find(o => o.id === offId || o.id === aliasId);
      if (!off || off.isDead) continue;
      if (off.isDaimyo && off.clanId === prov.ownerId && this.isCapitalProvince(prov.id, prov.ownerId)) continue;
      const prev = this.provinces.find(p => p.governorId === off.id);
      if (prev && prev.id !== prov.id) {
        prev.governorId = null;
      }
      off.clanId = prov.ownerId;
      off.isDaimyo = false;
      off.assignedProvId = prov.id;
      prov.governorId = off.id;
    }
  },

  // ============================================================================
  // 空白地での旗揚げ・御家再興システム
  // 要望1: 空白地に過去に大名になったことのある武将がいれば、その武将が旗揚げして、その空白地で大名となるようにする
  // ============================================================================,

  appointHistoricalHomeGovernors(targetClanId = null) {
    if (!this.provinces || !this.activeOfficers) return 0;

    const clansToCheck = targetClanId 
      ? [targetClanId] 
      : [...new Set(this.provinces.map(p => p.ownerId).filter(Boolean))];

    let totalAppointed = 0;
    const pinnedGovs = (window.PINNED_SCENARIO_GOVERNORS && this.currentScenario)
      ? (window.PINNED_SCENARIO_GOVERNORS[String(this.currentScenario.id)] || {})
      : {};

    for (const clanId of clansToCheck) {
      if (clanId === 'ronin' || clanId === 'null') continue;

      // その勢力の待機武将（生存武将・一般武将）
      const waitingOfficers = this.activeOfficers.filter(o => 
        o.clanId === clanId && 
        !o.assignedProvId && 
        !o.isDaimyo && 
        !o.isDead &&
        !this.isCourtFigure(o)
      );
      if (waitingOfficers.length === 0) continue;

      // その勢力が領有している全領国
      const ownedProvs = this.provinces.filter(p => p.ownerId === clanId);

      for (const off of waitingOfficers) {
        if (off.assignedProvId) continue;

        // この武将の歴史上本拠地
        const homeProvId = off.defaultProv;
        if (!homeProvId) continue;

        // 自勢力がその歴史上本拠地を領有しているか？
        const homeProv = ownedProvs.find(p => p.id === homeProvId);
        if (!homeProv) continue;

        // 大名居城（本拠地）は本拠親政ルールの対象なので、傘下武将は城主にならない
        if (this.isCapitalProvince(homeProv.id, clanId)) continue;

        // 現在の城主の確認
        const currentGovId = homeProv.governorId;
        const currentGov = currentGovId 
          ? this.activeOfficers.find(o => o.id === currentGovId && !o.isDead) 
          : null;

        // もしすでに城主がいて、かつその城主もこの国を歴史上本拠地としているなら交代させない
        if (currentGov && currentGov.defaultProv === homeProv.id) {
          continue;
        }
        // data.js の PINNED_SCENARIO_GOVERNORS で固定した史実城代は、ゆかりの家臣でも交代させない
        if (currentGov && pinnedGovs[homeProv.id] === currentGov.id) {
          continue;
        }

        // 任命実行！
        if (currentGov) {
          currentGov.assignedProvId = null;
        }

        homeProv.governorId = off.id;
        off.assignedProvId = homeProv.id;
        totalAppointed++;

        const castleName = homeProv.castleName || homeProv.castle || '城';
        if (clanId === this.playerClanId) {
          this.log(`🏯【城主任命】${off.name}公は、歴史的本拠地である${homeProv.name}国（${castleName}）の城主に任命されました！(武${off.military} 内${off.politic} 謀${off.intel})`, 'important');
        } else {
          const clanName = this.getClanFamilyName(clanId);
          this.log(`🏯【城主任命】${clanName}は、${off.name}をその本拠地たる${homeProv.name}国（${castleName}）の城主に任命しました。`);
        }
      }
    }

    if (totalAppointed > 0) {
      this.updateUI();
    }

    return totalAppointed;
  },

  // 他勢力や空白地と接する支城。進出と守りがかかる前線。,

  isClanFrontline(p) {
    if (!p || !p.ownerId) return false;
    return (p.neighbors || []).some(nId => {
      const n = this.provinces.find(x => x.id === nId);
      return n && n.ownerId !== p.ownerId;
    });
  },

  frontlineWeight(p) {
    let borders = 0;
    (p.neighbors || []).forEach(nId => {
      const n = this.provinces.find(x => x.id === nId);
      if (n && n.ownerId !== p.ownerId) borders++;
    });
    return borders * 1000 + (Number(p.kokudaka) || 0);
  },

  // ゆかりの地の城主は動かさない。空いた前線へ戦力の高い家臣を、残った城へ政務向きの家臣を置く。,

  ensureClanCapitalsMatchMap() {
    if (!window.CLAN_CAPITAL_PROVINCES_BASE) {
      window.CLAN_CAPITAL_PROVINCES_BASE = JSON.parse(JSON.stringify(window.CLAN_CAPITAL_PROVINCES || {}));
    }
    window.CLAN_CAPITAL_PROVINCES = JSON.parse(JSON.stringify(window.CLAN_CAPITAL_PROVINCES_BASE));
    const scenCaps = (this.currentScenario && this.currentScenario.capitals) || {};
    const owners = [...new Set((this.provinces || []).map(p => p.ownerId).filter(Boolean))];
    owners.forEach(ownerId => {
      const owned = this.provinces.filter(p => p.ownerId === ownerId);
      if (owned.length === 0) return;
      // シナリオ本拠 → 時代別本拠（CLAN_CAPITAL_ERAS）→ 史実本拠（CLAN_CAPITAL_PROVINCES）の順に、領内にあるものを採る
      const candidates = [scenCaps[ownerId], ...this.eraCapitalCandidates(ownerId), window.CLAN_CAPITAL_PROVINCES_BASE[ownerId]].filter(Boolean);
      const registered = candidates.find(pid => owned.some(p => p.id === pid));
      if (registered) {
        window.CLAN_CAPITAL_PROVINCES[ownerId] = registered;
        return;
      }
      const home = this.pickFallbackCapital(owned, ownerId);
      if (home) window.CLAN_CAPITAL_PROVINCES[ownerId] = home.id;
    });
    Object.keys(scenCaps).forEach(clanId => {
      if (!owners.includes(clanId)) window.CLAN_CAPITAL_PROVINCES[clanId] = scenCaps[clanId];
    });
  },

  /** data.js の CLAN_CAPITAL_ERAS から、今の年までに移った本拠を新しい順に返す */

  eraCapitalCandidates(clanId) {
    const eras = (window.CLAN_CAPITAL_ERAS || {})[clanId];
    if (!Array.isArray(eras)) return [];
    const year = Number(this.year || (this.currentScenario && this.currentScenario.year) || 0);
    return eras.filter(e => Array.isArray(e) && Number(e[0]) <= year)
      .sort((a, b) => Number(b[0]) - Number(a[0]))
      .map(e => e[1]);
  },

  isCapitalProvince(provId, ownerId) {
    if (!ownerId || !provId) return false;
    const owned = (this.provinces || []).filter(p => p.ownerId === ownerId);
    if (!owned.some(p => p.id === provId)) return false;
    const capitals = window.CLAN_CAPITAL_PROVINCES || {};
    const registered = capitals[ownerId];
    if (registered && owned.some(p => p.id === registered)) {
      return registered === provId;
    }
    const home = this.pickFallbackCapital(owned, ownerId);
    return !!(home && home.id === provId);
  },

  allianceMembers(group) {
    if (!group) return [];
    if (Array.isArray(group)) {
      // 配列末尾の数は同盟期間（季）なのでメンバーから除く
      return group.filter(x => typeof x === 'string' && x);
    }
    return Array.isArray(group.members) ? group.members.filter(x => typeof x === 'string' && x) : [];
  },

  normalizeAlliances(raw, year, seasonIdx, defaultDuration) {
    if (!Array.isArray(raw)) return [];
    const fallback = Number.isFinite(defaultDuration) ? defaultDuration : ALLIANCE_DURATION_SEASONS;
    return raw.map(group => {
      let durationSeasons = fallback;
      let formedYear = year;
      let formedSeason = seasonIdx;
      let members;
      if (Array.isArray(group)) {
        const ids = [];
        for (const x of group) {
          if (typeof x === 'number' && Number.isFinite(x) && x > 0) durationSeasons = x;
          else if (typeof x === 'string' && x) ids.push(x);
        }
        members = [...new Set(ids)];
      } else {
        members = [...new Set(this.allianceMembers(group))];
        if (Number.isFinite(group.formedYear)) formedYear = group.formedYear;
        if (Number.isFinite(group.formedSeason)) formedSeason = group.formedSeason;
        if (Number.isFinite(group.durationSeasons)) durationSeasons = group.durationSeasons;
      }
      if (members.length < 2) return null;
      return { members, formedYear, formedSeason, durationSeasons };
    }).filter(Boolean);
  },

  allianceDurationOf(group) {
    const n = Number(!Array.isArray(group) && group ? group.durationSeasons : NaN);
    return Number.isFinite(n) && n > 0 ? n : ALLIANCE_DURATION_SEASONS;
  },

  isClanExtant(clanId) {
    if (!clanId) return false;
    return (this.provinces || []).some(p => p.ownerId === clanId);
  },

  // 史実イベントの受け取り先IDを、いま地図上にいる同じ当主・同じ家系の勢力へ寄せる。
  // 例: 保元シナリオで源義朝家を頼朝が継いでいる時、壇ノ浦の genji_yoritomo を別勢力として生やさない。,

  resolveEventTargetClan(clanId) {
    if (!clanId || this.isClanExtant(clanId)) return clanId;

    // 1. その家の史実当主が、すでに別IDの勢力を率いていればそこへ渡す
    const leaderName = this.getDaimyoLeaderName(clanId);
    if (leaderName && !this.looksLikeClanId(leaderName)) {
      const lord = (this.activeOfficers || []).find(o =>
        o && !o.isDead && o.isDaimyo && o.name && this.isClanExtant(o.clanId)
        && this.leaderNamesMatch(o.name, leaderName)
      );
      if (lord) return lord.clanId;
    }

    // 2. 同じ家系の別ID（データ上の表記揺れ・家督継承）を探す
    const lineage = EVENT_CLAN_LINEAGE.find(group => group.includes(clanId));
    if (lineage) {
      const heir = lineage.find(id => id !== clanId && this.isClanExtant(id));
      if (heir) return heir;
    }
    // 3. 本能寺の変が起きず信長が健在なら、秀吉は織田家臣のまま。羽柴宛ての領地は織田へ
    if (clanId === 'toyotomi' && this.honnoujiAverted && this.isClanExtant('oda')) return 'oda';
    return clanId;
  },

  allianceClanLabel(clanId) {
    return this.getClanFamilyName(clanId);
  },

  allianceTurnsElapsed(group) {
    const formedYear = Array.isArray(group) ? this.year : (group.formedYear ?? this.year);
    const formedSeason = Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx);
    return (this.year - formedYear) * 4 + (this.seasonIdx - formedSeason);
  },

  getAllianceRemainingSeasons(clanA, clanB) {
    let best = -1;
    (this.alliances || []).forEach(group => {
      const members = this.allianceMembers(group);
      if (!members.includes(clanA) || !members.includes(clanB)) return;
      const left = this.allianceDurationOf(group) - this.allianceTurnsElapsed(group);
      if (left > best) best = left;
    });
    return best;
  },

  rememberAllianceBreak(members) {
    if (!this.allianceCooldown) this.allianceCooldown = {};
    const now = this.year * 4 + this.seasonIdx;
    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        const key = [members[i], members[j]].sort().join('|');
        this.allianceCooldown[key] = now;
      }
    }
  },

  logAllianceExpired(members, seasons) {
    const years = Math.max(1, Math.round((Number(seasons) || ALLIANCE_DURATION_SEASONS) / 4));
    const span = years === 2 ? '二年' : years === 5 ? '五年' : `${years}年`;
    const living = members.filter(id => this.isClanExtant(id));
    if (members.includes(this.playerClanId)) {
      const others = living.filter(id => id !== this.playerClanId).map(id => this.allianceClanLabel(id));
      if (others.length > 0) {
        this.log(`⌛【同盟満期】${others.join('・')}との同盟は${span}の約定を満了し、解消されました。`, 'important');
      }
      return;
    }
    if (living.length >= 2) {
      const names = living.map(id => this.allianceClanLabel(id));
      this.log(`⌛【同盟満期】${names.join('・')}の同盟は${span}の約定を満了し、解消されました。`);
    }
  },

  // 滅亡大名を同盟から外し、二年（八季）を過ぎた盟約を解消する,

  maintainAlliances() {
    const next = [];
    (this.alliances || []).forEach(group => {
      const members = this.allianceMembers(group);
      const formedYear = Array.isArray(group) ? this.year : (group.formedYear ?? this.year);
      const formedSeason = Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx);
      const durationSeasons = this.allianceDurationOf(group);
      if (this.allianceTurnsElapsed({ formedYear, formedSeason }) >= durationSeasons) {
        this.logAllianceExpired(members, durationSeasons);
        this.rememberAllianceBreak(members);
        return;
      }
      const alive = members.filter(id => this.isClanExtant(id));
      const dead = members.filter(id => !this.isClanExtant(id));
      dead.forEach(id => {
        if (members.includes(this.playerClanId)) {
          this.log(`💀【同盟消滅】${this.allianceClanLabel(id)}が滅亡したため、同盟一覧から除かれました。`, 'important');
        }
      });
      if (alive.length >= 2) {
        next.push({ members: alive, formedYear, formedSeason, durationSeasons });
      }
    });
    this.alliances = next;
  },

  removeClanFromAlliances(clanId) {
    if (!clanId || !this.alliances) return;
    let playerLost = false;
    this.alliances = this.alliances.map(group => {
      const members = this.allianceMembers(group);
      if (!members.includes(clanId)) {
        return {
          members,
          formedYear: Array.isArray(group) ? this.year : (group.formedYear ?? this.year),
          formedSeason: Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx),
          durationSeasons: this.allianceDurationOf(group)
        };
      }
      if (members.includes(this.playerClanId)) playerLost = true;
      const alive = members.filter(id => id !== clanId);
      if (alive.length < 2) return null;
      return {
        members: alive,
        formedYear: Array.isArray(group) ? this.year : (group.formedYear ?? this.year),
        formedSeason: Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx),
        durationSeasons: this.allianceDurationOf(group)
      };
    }).filter(Boolean);
    if (playerLost) {
      this.log(`💀【同盟消滅】${this.allianceClanLabel(clanId)}が滅亡したため、同盟一覧から除かれました。`, 'important');
    }
  },

  clansShareBorder(clanA, clanB) {
    return (this.provinces || []).some(p => {
      if (p.ownerId !== clanA) return false;
      return (p.neighbors || []).some(nId => {
        const n = this.provinces.find(x => x.id === nId);
        return n && n.ownerId === clanB;
      });
    });
  },

  clanFeelsThreatened(clanId) {
    const mine = (this.provinces || []).filter(p => p.ownerId === clanId).length;
    if (mine === 0) return false;
    const neighbors = new Set();
    this.provinces.filter(p => p.ownerId === clanId).forEach(p => {
      (p.neighbors || []).forEach(nId => {
        const n = this.provinces.find(x => x.id === nId);
        if (n && n.ownerId && n.ownerId !== clanId) neighbors.add(n.ownerId);
      });
    });
    for (const nid of neighbors) {
      const nCount = this.provinces.filter(p => p.ownerId === nid).length;
      if (nCount >= mine + 2) return true;
    }
    return false;
  },

  // 同盟関係の判定 (フェーズ2: 同盟システム),

  isAllied(clanA, clanB) {
    if (!clanA || !clanB || clanA === clanB) return false;
    if (!this.isClanExtant(clanA) || !this.isClanExtant(clanB)) return false;
    const alliances = this.alliances || [];
    return alliances.some(group => {
      const members = this.allianceMembers(group);
      return members.includes(clanA) && members.includes(clanB);
    });
  },

  // 同盟相手の取得（滅亡済み大名は含めない）,

  getAllies(clanId) {
    if (!clanId) return [];
    const alliances = this.alliances || [];
    const allies = new Set();
    alliances.forEach(group => {
      const members = this.allianceMembers(group);
      if (members.includes(clanId)) {
        members.forEach(id => {
          if (id !== clanId && this.isClanExtant(id)) allies.add(id);
        });
      }
    });
    return Array.from(allies);
  },

  // 同盟締結アクション,

  formAlliance(targetClanId, onComplete) {
    if (this.ap < 1) {
      this.showOrderResult('⚠ 行動力不足', '外交には行動力(AP)が1点必要です。次期ターンまでお待ちください。', '#e74c3c');
      return;
    }
    const costGold = 500;
    if (this.gold < costGold) {
      this.showOrderResult('⚠ 軍資金不足', `同盟締結の使者・結納の贈答費用として軍資金が${costGold}両必要です。`, '#e74c3c');
      return;
    }
    const targetName = this.getClanFamilyName(targetClanId);
    const targetDaimyo = this.getDaimyoLeaderName(targetClanId);

    const executeForm = () => {
      this.ap -= 1;
      this.gold -= costGold;

      if (!this.alliances) {
        this.alliances = this.normalizeAlliances(this.currentScenario?.alliances || [], this.year, this.seasonIdx);
      }

      if (!this.isAllied(this.playerClanId, targetClanId)) {
        this.alliances.push({
          members: [this.playerClanId, targetClanId],
          formedYear: this.year,
          formedSeason: this.seasonIdx
        });
      }

      this.updateUI();
      this.audio?.playFanfare();
      this.log(`🤝【同盟締結】${targetName}（当主・${targetDaimyo}公）と固い同盟の契りを結びました！二年間は相互に攻撃不可となり、防衛戦での援軍出兵が行われます。`, 'important');
      this.autoSave();
      if (onComplete) onComplete();
      this.showOrderResult('🤝 同盟締結 成功', `${targetName}（当主：${targetDaimyo}公）との同盟が成立しました！\n\n・相互に領国への攻撃が不可となります\n・合戦時に隣接領国から援軍として参陣します\n・約定は二年（八季）で自然に解消されます`, 'var(--gold-bright)');
    };

    if (typeof Swal !== 'undefined') {
      Swal.fire({
        title: '【同盟締結の使者】',
        html: `<div style="text-align:left; font-size:12pt; line-height:1.6; color:#ddd;">
                 <p><strong style="color:var(--gold-bright);">${targetName}</strong>（当主：${targetDaimyo}公）に使者を派遣し、同盟を締結しますか？</p>
                 <div style="background:rgba(0,0,0,0.4); padding:10px 14px; border-radius:5px; border-left:3px solid var(--gold); margin-top:10px;">
                   <div>💰 贈答費用: <strong style="color:#ffd700;">金${costGold}両</strong> (所持金: ${this.gold}両)</div>
                   <div>⚡ 消費行動力: <strong style="color:#5dade2;">AP 1点</strong> (残AP: ${this.ap})</div>
                   <div style="margin-top:6px; color:#2ecc71;">🛡️ 効果: 相互不可侵 ＆ 合戦時の援軍協力（二年で解消）</div>
                 </div>
               </div>`,
        icon: 'question',
        background: '#1b140e',
        color: '#f5eedc',
        showCancelButton: true,
        confirmButtonColor: '#27ae60',
        cancelButtonColor: '#555',
        confirmButtonText: '同盟を結ぶ',
        cancelButtonText: '取りやめる'
      }).then((result) => {
        if (result.isConfirmed) {
          executeForm();
        }
      });
    } else {
      if (confirm(`${targetName}（当主：${targetDaimyo}公）と同盟を締結しますか？（金${costGold}両・AP 1点消費）`)) {
        executeForm();
      }
    }
  },

  // 同盟破棄アクション,

  breakAlliance(targetClanId, onComplete) {
    if (this.ap < 1) {
      this.showOrderResult('⚠ 行動力不足', '同盟破棄には使者を送るため行動力(AP)が1点必要です。', '#e74c3c');
      return;
    }
    const targetName = this.getClanFamilyName(targetClanId);
    const targetDaimyo = this.getDaimyoLeaderName(targetClanId);

    const executeBreak = () => {
      this.ap -= 1;

      if (this.alliances) {
        const brokenPairs = [];
        this.alliances = this.alliances.map(group => {
          const members = this.allianceMembers(group);
          if (members.includes(this.playerClanId) && members.includes(targetClanId)) {
            brokenPairs.push(members);
            const nextMembers = members.filter(id => id !== targetClanId);
            if (nextMembers.length < 2) return null;
            return {
              members: nextMembers,
              formedYear: Array.isArray(group) ? this.year : (group.formedYear ?? this.year),
              formedSeason: Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx),
              durationSeasons: this.allianceDurationOf(group)
            };
          }
          return {
            members,
            formedYear: Array.isArray(group) ? this.year : (group.formedYear ?? this.year),
            formedSeason: Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx),
            durationSeasons: this.allianceDurationOf(group)
          };
        }).filter(Boolean);
        brokenPairs.forEach(members => this.rememberAllianceBreak(members));
      }

      this.updateUI();
      this.audio?.playHyoshigi();
      this.log(`⚡【同盟破棄・手切れ】${targetName}（当主・${targetDaimyo}公）との同盟を一方的に破棄しました！両家は手切れとなり、交戦状態に入りました。`, 'important');
      this.autoSave();
      if (onComplete) onComplete();
      this.showOrderResult('⚡ 手切れ・同盟破棄', `${targetName}との同盟を破棄しました。\n両家は手切れとなり、互いの領国への侵攻が可能となります。`, '#e74c3c');
    };

    if (typeof Swal !== 'undefined') {
      Swal.fire({
        title: '【同盟破棄の確認】',
        html: `<div style="text-align:left; font-size:12pt; line-height:1.6; color:#ddd;">
                 <p>本当に <strong style="color:var(--gold-bright);">${targetName}</strong>（当主：${targetDaimyo}公）との同盟を破棄しますか？</p>
                 <div style="background:rgba(192,57,43,0.15); padding:10px 14px; border-radius:5px; border-left:3px solid #e74c3c; margin-top:10px;">
                   <div>⚡ 消費行動力: <strong style="color:#5dade2;">AP 1点</strong> (残AP: ${this.ap})</div>
                   <div style="margin-top:6px; color:#ff6b6b;">⚠ 警告: 同盟破棄により両家は手切れとなり、互いに領国への武力侵攻が可能となります。</div>
                 </div>
               </div>`,
        icon: 'warning',
        background: '#1b140e',
        color: '#f5eedc',
        showCancelButton: true,
        confirmButtonColor: '#c0392b',
        cancelButtonColor: '#555',
        confirmButtonText: '同盟を破棄する',
        cancelButtonText: '取りやめる'
      }).then((result) => {
        if (result.isConfirmed) {
          executeBreak();
        }
      });
    } else {
      if (confirm(`本当に${targetName}との同盟を破棄しますか？\n両家は手切れとなり、交戦状態に入ります。`)) {
        executeBreak();
      }
    }
  },

  getDaimyoLeaderName(ownerId) {
    if (!ownerId || ownerId === 'null' || ownerId === 'undefined') return '空白地';

    // 1. 生存中の大名武将を最優先（複数いれば pickClanLeader で一意に）
    const currentDaimyo = this.getClanDaimyoOfficer(ownerId);
    if (currentDaimyo && currentDaimyo.name) return currentDaimyo.name;

    const profile = (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA[ownerId]) ? window.CLAN_MASTER_DATA[ownerId] : null;
    if (profile && profile.leaders) {
      const curY = Number(this.year || 0);
      // curY 以下の年代キーを降順ソートし、最も近い年代の史実当主名を取得
      const validYears = Object.keys(profile.leaders)
        .map(Number)
        .filter(y => !isNaN(y) && y <= curY)
        .sort((a, b) => b - a);
      if (validYears.length > 0) {
        return profile.leaders[String(validYears[0])];
      }
      // 【修正】下の名前がない苗字(family)より前に、フルネーム(leaders.default)を最優先で返却
      if (profile.leaders.default) return profile.leaders.default;
      // 年代が合致しない場合でも、登録されている全年代の中から最も近いフルネームを取得
      const allYears = Object.keys(profile.leaders)
        .map(Number)
        .filter(y => !isNaN(y))
        .sort((a, b) => Math.abs(a - curY) - Math.abs(b - curY));
      if (allYears.length > 0) {
        return profile.leaders[String(allYears[0])];
      }
      if (profile.family) return profile.family;
    }
    return this.getClanDisplayName(ownerId);
  },

  // 豊臣姓・羽柴姓の年代連動切り替え（史実: 天正14年(1586年)に正親町天皇より豊臣姓を賜姓）,

  updateToyotomiSurname(announce = false) {
    const isToyotomiEra = (this.year >= 1586);
    const targetSurname = isToyotomiEra ? '豊臣' : '羽柴';
    const oldSurname = isToyotomiEra ? '羽柴' : '豊臣';

    // 1. 武将名の更新 (activeOfficers & OFFICERS_MASTER)
    const allOffs = [...(this.activeOfficers || []), ...(window.OFFICERS_MASTER || [])];
    allOffs.forEach(o => {
      if (!o.name) return;
      // 改姓対象は data.js の TOYOTOMI_SURNAME_OFFICERS（ID→名）だけ。苗字の前方一致では選ばない
      const toyoGiven = (window.TOYOTOMI_SURNAME_OFFICERS || {})[o.id];
      if (toyoGiven) {
        o.name = `${targetSurname}${toyoGiven}`;
      } else if (o.id === 'off_tokugawa_ieyasu') {
        // 永禄6年（1563）に元康から家康へ改名。同一人物を二枚にしない
        o.name = (this.year >= 1563) ? '徳川家康' : '松平元康';
      }
    });

    // 徳川家康の改名連動（桶狭間の戦い・自立連動）
    this.updateTokugawaSurname(announce);

    // 2. プレイヤー大名情報の更新
    if (this.playerClanId === 'toyotomi') {
      if (this.playerDaimyo) {
        this.playerDaimyo.clan = `${targetSurname}家`;
        const playerHideIds = ['off_toyotomi_hideyoshi', 'off_toyotomi_hidenaga'];
        if (playerHideIds.includes(this.playerDaimyo.officerId)) {
          this.playerDaimyo.name = `${targetSurname}` + (this.playerDaimyo.officerId === 'off_toyotomi_hidenaga' ? '秀長' : '秀吉');
        }
      }
    }

    // 3. CLAN_MASTER_DATA の更新
    if (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA['toyotomi']) {
      window.CLAN_MASTER_DATA['toyotomi'].family = `${targetSurname}家`;
      if (window.CLAN_MASTER_DATA['toyotomi'].leaders) {
        window.CLAN_MASTER_DATA['toyotomi'].leaders.default = `${targetSurname}秀吉`;
      }
    }

    // 4. プレイアブル大名リストの更新
    if (this.currentScenario && this.currentScenario.playables) {
      const pToyo = this.currentScenario.playables.find(d => d.id === 'toyotomi');
      if (pToyo) {
        pToyo.clan = `${targetSurname}家`;
        if (pToyo.officerId === 'off_toyotomi_hidenaga') {
          pToyo.name = `${targetSurname}秀長`;
        } else {
          pToyo.name = `${targetSurname}秀吉`;
        }
      }
    }

    // 5. 1585 -> 1586 年越しの改姓アナウンス
    if (announce && this.year === 1586) {
      this.log('👑【豊臣賜姓】羽柴秀吉公は朝廷より「豊臣」の姓を賜りました！羽柴家はこれより「豊臣家」となり天下平定の総仕上げへ邁進します。', 'important');
      if (this.audio) this.audio.playHyoshigi();
    }

    this.updateKiyohiraSurname(false);
  },

  // 清原清衡は寛治2年（1088）春、実父藤原経清の姓に復して藤原清衡となる,

  kiyohiraInFujiwaraEra() {
    if (this.kiyohiraSurnameDeclined) return false;
    if (this.kiyohiraFujiwaraAccepted) return true;
    const y = Number(this.year);
    // 史実: 寛治2年(1088年)春以降、または1087年冬金沢柵陥落後
    if (y > 1088) return true;
    // 1088年春は復姓イベントで決める。決断前に名前だけ先に変えない
    if (y === 1088 && Number(this.seasonIdx) >= 1) return true;
    return false;
  },

  updateKiyohiraSurname(announce = false) {
    const isFujiwaraEra = this.kiyohiraInFujiwaraEra();
    const targetName = isFujiwaraEra ? '藤原清衡' : '清原清衡';

    // 1. 武将名の更新 (activeOfficers & OFFICERS_MASTER)
    const allOffs = [...(this.activeOfficers || []), ...(window.OFFICERS_MASTER || [])];
    const seen = new Set();
    allOffs.forEach(o => {
      if (!o || seen.has(o)) return;
      seen.add(o);
      if (this.officerIdIn(o, window.KIYOHIRA_OFFICER_IDS || ['off_fujiwara_kiyohira'])) {
        o.name = targetName;
      }
    });

    // 2. プレイヤー大名情報の更新
    if (this.playerClanId === 'kiyohara') {
      if (this.playerDaimyo) {
        if (!this.playerDaimyo._origClan) this.playerDaimyo._origClan = this.playerDaimyo.clan;
        if (!this.playerDaimyo._origCrest) this.playerDaimyo._origCrest = this.playerDaimyo.crest;
        if (!this.playerDaimyo._origKamon) this.playerDaimyo._origKamon = this.playerDaimyo.kamonSvgId;
        if (!this.playerDaimyo._origColor) this.playerDaimyo._origColor = this.playerDaimyo.color;

        if (this.playerDaimyo.name && this.leaderNamesMatch(this.playerDaimyo.name, '清原清衡')) {
          this.playerDaimyo.name = targetName;
        }
        if (isFujiwaraEra) {
          this.playerDaimyo.clan = '奥州藤原氏';
          this.playerDaimyo.crest = '奥州藤原氏';
          this.playerDaimyo.kamonSvgId = 'kamon-fujiwara';
          this.playerDaimyo.color = '#d4ac0d';
          this.playerDaimyo.desc = '安倍頼時の孫で藤原経清の子。後三年の役を経て実父の藤原姓へ復姓し、平泉に奥州藤原氏百年の黄金文化を築いた。';
        } else {
          this.playerDaimyo.clan = this.playerDaimyo._origClan || '清原清衡党';
          this.playerDaimyo.crest = this.playerDaimyo._origCrest || '清原清衡党';
          this.playerDaimyo.kamonSvgId = this.playerDaimyo._origKamon || 'kamon-kiyohara';
          this.playerDaimyo.color = this.playerDaimyo._origColor || '#4a235a';
        }
      }
    }

    // 3. プレイアブル大名リストの更新
    if (this.currentScenario && this.currentScenario.playables) {
      const pKiyo = this.currentScenario.playables.find(d =>
        d.id === 'kiyohara' && d.name && this.leaderNamesMatch(d.name, '清原清衡')
      );
      if (pKiyo) {
        if (!pKiyo._origClan) pKiyo._origClan = pKiyo.clan;
        if (!pKiyo._origCrest) pKiyo._origCrest = pKiyo.crest;
        if (!pKiyo._origKamon) pKiyo._origKamon = pKiyo.kamonSvgId;
        if (!pKiyo._origColor) pKiyo._origColor = pKiyo.color;
        pKiyo.name = targetName;
        if (isFujiwaraEra) {
          pKiyo.clan = '奥州藤原氏';
          pKiyo.crest = '奥州藤原氏';
          pKiyo.kamonSvgId = 'kamon-fujiwara';
          pKiyo.color = '#d4ac0d';
          pKiyo.tactic = '黄金王国の威風';
          pKiyo.tacticDesc = '莫大な砂金と名馬の富により全軍の装備と士気を最大化する。';
          pKiyo.desc = '安倍頼時の孫で藤原経清の子。後三年の役を経て実父の藤原姓へ復姓し、平泉に奥州藤原氏百年の黄金文化を築いた。';
        } else {
          pKiyo.clan = pKiyo._origClan;
          pKiyo.crest = pKiyo._origCrest;
          pKiyo.kamonSvgId = pKiyo._origKamon;
          pKiyo.color = pKiyo._origColor || '#4a235a';
        }
      }
    }

    // 4. CLAN_MASTER_DATA の更新
    if (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA.kiyohara) {
      const master = window.CLAN_MASTER_DATA.kiyohara;
      if (!master._origFamily) master._origFamily = master.family;
      if (!master._origKamon) master._origKamon = master.kamon;
      if (!master._origColor) master._origColor = master.color;
      const scenarioLeaderIsKiyohira = !!(this.currentScenario && this.currentScenario.playables &&
        this.currentScenario.playables.some(d => d.id === 'kiyohara' && d.name && this.leaderNamesMatch(d.name, '清原清衡')));
      if (isFujiwaraEra && scenarioLeaderIsKiyohira) {
        master.family = '奥州藤原氏';
        master.kamon = 'kamon-fujiwara';
        master.color = '#d4ac0d';
        master.tactic = '黄金王国の威風';
        master.tacticDesc = '莫大な砂金と名馬の富により全軍の装備と士気を最大化する。';
        master.desc = '平泉に三代百年の黄金文化を築いた奥州藤原氏。清衡・基衡・秀衡が陸奥・出羽十七万石の独立王国を支配した。';
        if (master.leaders) {
          master.leaders['1088'] = '藤原清衡';
          master.leaders.default = '藤原清衡';
        }
      } else if (!isFujiwaraEra && scenarioLeaderIsKiyohira) {
        master.family = master._origFamily || '清原氏';
        master.kamon = master._origKamon || 'kamon-kiyohara';
        master.color = master._origColor || '#4a235a';
      }
    }

    // 5. アナウンス
    if (announce && isFujiwaraEra && !this._kiyohiraAnnounced) {
      this._kiyohiraAnnounced = true;
      this.log('👑【藤原復姓】清原清衡公は実父・藤原経清の姓に復し、「藤原清衡」と改姓しました。奥羽の主はこれより奥州藤原氏を称します。', 'important');
      if (this.audio) this.audio.playHyoshigi();
    }
  },

  // 徳川家康・松平元康の改名連動（桶狭間イベント・年代連動）,

  updateTokugawaSurname(announce = false) {
    const okehazamaDone = Boolean(this.okehazamaOccurred || (this.happenedEvents && (this.happenedEvents.has('evt_1560_okehazama') || this.happenedEvents.has('okehazama'))));
    const isIeyasuEra = okehazamaDone || (this.year > 1560) || (this.year === 1560 && this.seasonIdx >= 2);
    const targetName = isIeyasuEra ? '徳川家康' : '松平元康';
    const oldName = isIeyasuEra ? '松平元康' : '徳川家康';
    const targetClanName = isIeyasuEra ? '徳川家' : '松平家';

    // 1. 武将名の更新 (activeOfficers & OFFICERS_MASTER)
    const allOffs = [...(this.activeOfficers || []), ...(window.OFFICERS_MASTER || [])];
    allOffs.forEach(o => {
      if (!o.name) return;
      if (o.id === 'off_tokugawa_ieyasu' || o.id === 'off_matsudaira_motoyasu' || o.id === 'off_matsudaira_ieyasu_early') {
        o.name = targetName;
      }
    });

    // 2. プレイヤー大名情報の更新
    if (this.playerClanId === 'tokugawa' || this.playerClanId === 'matsudaira') {
      if (this.playerDaimyo) {
        this.playerDaimyo.clan = targetClanName;
        this.playerDaimyo.name = targetName;
      }
    }

    // 3. CLAN_MASTER_DATA の更新
    if (window.CLAN_MASTER_DATA) {
      ['tokugawa', 'matsudaira'].forEach(cid => {
        if (window.CLAN_MASTER_DATA[cid]) {
          if (isIeyasuEra) {
            window.CLAN_MASTER_DATA[cid].family = '徳川家';
          }
          if (window.CLAN_MASTER_DATA[cid].leaders) {
            window.CLAN_MASTER_DATA[cid].leaders.default = targetName;
            if (window.CLAN_MASTER_DATA[cid].leaders['1560']) {
              window.CLAN_MASTER_DATA[cid].leaders['1560'] = targetName;
            }
          }
        }
      });
    }

    // 4. プレイアブル大名リストの更新
    if (this.currentScenario && this.currentScenario.playables) {
      const pToku = this.currentScenario.playables.find(d => d.id === 'tokugawa' || d.id === 'matsudaira');
      if (pToku) {
        if (pToku.name && this.leaderNamesMatch(pToku.name, '徳川家康')) {
          pToku.name = targetName;
          pToku.clan = targetClanName;
        }
      }
    }

    // 5. アナウンス
    if (announce && isIeyasuEra) {
      this.log('📜【独立改名】松平元康公は今川の束縛を脱して三河岡崎城にて自立を果たし、「徳川家康」へと改名しました！', 'important');
      if (this.audio) this.audio.playHyoshigi();
    }
  },

  // 領国の実効統治能力（本拠親政は大名本人の居城のみ、それ以外は通常の城代）
  // 旧国名を和名（尾張、三河、甲斐など）に変換するヘルパー,

  getProvinceJapaneseName(provId) {
    if (!provId) return '諸国';
    const cleanId = String(provId).replace(/^prov_/, '').toLowerCase();
    const p = (this.provinces || []).find(x => x.id === provId || x.id === cleanId || x.id === `prov_${cleanId}`)
           || (window.PROVINCES_DATA || []).find(x => x.id === provId || x.id === cleanId || x.id === `prov_${cleanId}`);
    const jpFromProv = p && p.name && !/^[a-z0-9_]+$/i.test(String(p.name)) ? p.name : '';
    if (jpFromProv) return jpFromProv;
    const map = {
      'owari': '尾張', 'mikawa': '三河', 'totomi': '遠江', 'suruga': '駿河', 'kai': '甲斐', 'shinano': '信濃',
      'kitashinano': '北信濃', 'minamishinano': '南信濃', 'north_shinano': '北信濃', 'south_shinano': '南信濃',
      'mino': '美濃', 'hida': '飛騨', 'echizen': '越前', 'kaga': '加賀', 'noto': '能登', 'ecchu': '越中',
      'etchu': '越中', 'echigo': '越後', 'sado': '佐渡', 'kozuke': '上野', 'shimotsuke': '下野', 'hitachi': '常陸',
      'shimousa': '下総', 'kazusa': '上総', 'awa': '安房', 'awa_boshu': '安房', 'musashi': '武蔵', 'sagami': '相模',
      'izu': '伊豆', 'omi': '近江', 'north_omi': '北近江', 'south_omi': '南近江', 'yamashiro': '山城', 'yamato': '大和',
      'kawachi': '河内', 'izumi': '和泉', 'settsu': '摂津', 'tanba': '丹波', 'tamba': '丹波', 'tango': '丹後',
      'tajima': '但馬', 'inaba': '因幡', 'hoki': '伯耆', 'izumo': '出雲', 'iwami': '石見', 'oki': '隠岐',
      'harima': '播磨', 'mimasaka': '美作', 'bizen': '備前', 'bitchu': '備中', 'bicchu': '備中', 'bingo': '備後',
      'aki': '安芸', 'suo': '周防', 'nagato': '長門', 'kii': '紀伊', 'awa_shikoku': '阿波', 'sanuki': '讃岐',
      'iyo': '伊予', 'tosa': '土佐', 'chikuzen': '筑前', 'chikugo': '筑後', 'buzen': '豊前', 'bungo': '豊後',
      'hizen': '肥前', 'higo': '肥後', 'hyuga': '日向', 'osumi': '大隅', 'satsuma': '薩摩', 'tsushima': '対馬',
      'iki': '壱岐', 'mutsu': '陸奥', 'dewa': '出羽', 'ezo': '蝦夷', 'tsugaru': '津軽', 'rikuchu': '陸中',
      'rikuzen': '陸前', 'iwaki': '磐城', 'iwashiro': '岩代', 'ugo': '羽後', 'uzen': '羽前', 'wakasa': '若狭',
      'shimanokuni': '志摩', 'shima': '志摩', 'ise': '伊勢', 'iga': '伊賀', 'awaji': '淡路',
      'okayama': '備前', 'wakayama': '紀伊', 'niigata': '越後', 'osaka': '摂津', 'kanagawa': '相模',
      'tottori': '因幡', 'mie': '伊勢', 'fukui': '越前', 'aichi_w': '尾張', 'aichi_e': '三河',
      'tokushima': '阿波', 'fukuoka': '筑前', 'kumamoto': '肥後', 'kochi': '土佐', 'shimane': '出雲',
      'ibaraki': '常陸'
    };
    return map[cleanId] || '諸国';
  },

  // 武将列伝テキスト内の英語国名・ID（izumo, bungo, higo等）を綺麗な日本語和名に変換・サニタイズ,

  cleanOfficerLore(lore) {
    if (!lore) return '';
    let res = String(lore);
    const map = {
      'iwashiro': '岩代', 'rikuchu': '陸中', 'rikuzen': '陸前', 'iwaki': '磐城', 'mutsu': '陸奥',
      'ugo': '羽後', 'uzen': '羽前', 'dewa': '出羽', 'echigo': '越後', 'ecchu': '越中', 'etchu': '越中',
      'noto': '能登', 'kaga': '加賀', 'echizen': '越前', 'sado': '佐渡', 'kai': '甲斐', 'shinano': '信濃',
      'north_shinano': '北信濃', 'south_shinano': '南信濃', 'kitashinano': '北信濃', 'minamishinano': '南信濃',
      'hida': '飛騨', 'mino': '美濃', 'owari': '尾張', 'mikawa': '三河', 'totomi': '遠江', 'suruga': '駿河',
      'izu': '伊豆', 'sagami': '相模', 'musashi': '武蔵', 'kazusa': '上総', 'shimousa': '下総', 'hitachi': '常陸',
      'shimotsuke': '下野', 'kozuke': '上野', 'awa_boshu': '安房', 'awa': '安房', 'omi': '近江',
      'north_omi': '北近江', 'south_omi': '南近江', 'yamashiro': '山城', 'yamato': '大和', 'kawachi': '河内',
      'izumi': '和泉', 'settsu': '摂津', 'iga': '伊賀', 'ise': '伊勢', 'shima': '志摩', 'kii': '紀伊',
      'tanba': '丹波', 'tamba': '丹波', 'tango': '丹後', 'tajima': '但馬', 'inaba': '因幡', 'hoki': '伯耆',
      'izumo': '出雲', 'iwami': '石見', 'oki': '隠岐', 'harima': '播磨', 'mimasaka': '美作', 'bizen': '備前',
      'bicchu': '備中', 'bitchu': '備中', 'bingo': '備後', 'aki': '安芸', 'suo': '周防', 'nagato': '長門',
      'awa_shikoku': '阿波', 'sanuki': '讃岐', 'iyo': '伊予', 'tosa': '土佐', 'chikuzen': '筑前',
      'chikugo': '筑後', 'buzen': '豊前', 'bungo': '豊後', 'hizen': '肥前', 'higo': '肥後', 'hyuga': '日向',
      'osumi': '大隅', 'satsuma': '薩摩', 'tsushima': '対馬', 'iki': '壱岐', 'ezo': '蝦夷', 'tsugaru': '津軽',
      'okayama': '備前・美作', 'wakayama': '紀伊', 'niigata': '越後', 'osaka': '摂津・大坂', 'kanagawa': '相模',
      'tottori': '因幡・伯耆', 'mie': '伊勢', 'fukui': '越前', 'aichi_w': '尾張', 'aichi_e': '三河',
      'tokushima': '阿波', 'fukuoka': '筑前', 'kumamoto': '肥後', 'kochi': '土佐', 'shimane': '出雲・石見',
      'ibaraki': '常陸'
    };
    const sortedKeys = Object.keys(map).sort((a, b) => b.length - a.length);
    for (const k of sortedKeys) {
      const jp = map[k];
      // 単語境界 \b は「prov_izumo」や和文に挟まれた国名IDを取りこぼす
      const re = new RegExp('(?<![A-Za-z0-9_])(?:prov_)?' + k + '(?![A-Za-z0-9_])', 'gi');
      res = res.replace(re, jp);
    }
    res = res.replace(/本拠地(?!・)(?=[\u4e00-\u9fff])/g, '本拠地・');
    return res;
  },

  // 起点国から各国までの隣接ホップ数（BFS）,

  getProvinceDistanceMap(fromId) {
    const dist = new Map();
    if (!fromId) return dist;
    const byId = new Map((this.provinces || []).map(p => [p.id, p]));
    if (!byId.has(fromId)) return dist;
    const q = [fromId];
    dist.set(fromId, 0);
    while (q.length) {
      const cur = q.shift();
      const d = dist.get(cur);
      const p = byId.get(cur);
      if (!p) continue;
      for (const nId of (p.neighbors || [])) {
        if (dist.has(nId)) continue;
        dist.set(nId, d + 1);
        q.push(nId);
      }
    }
    return dist;
  },

  // 浪人の流浪国から、指定勢力の最寄り領国までのホップ数,

  getRoninDistanceToClan(ronin, clanId, distMap = null) {
    const fromId = ronin && ronin.defaultProv;
    if (!fromId || !clanId) return Infinity;
    const map = distMap || this.getProvinceDistanceMap(fromId);
    let best = Infinity;
    for (const p of (this.provinces || [])) {
      if (p.ownerId !== clanId) continue;
      const d = map.get(p.id);
      if (d != null && d < best) best = d;
      if (best === 0) break;
    }
    return best;
  },

  // 家中に継げる成人がいない（当主のみ、または世継ぎ不在）,

  householdLacksHeir(clanId) {
    if (!clanId || clanId === 'ronin') return false;
    const daimyo = (this.activeOfficers || []).find(o => o.clanId === clanId && o.isDaimyo && !o.isDead);
    const name = daimyo?.name || this.deceasedDaimyoName(clanId);
    const heirs = (this.activeOfficers || []).filter(o =>
      o && o.clanId === clanId && !o.isDaimyo && this.officerCanInherit(o)
    );
    if (!heirs.length) return true;
    return this.sortHeirCandidates(heirs, clanId, name).length === 0;
  },

  // 仕官圏: 流浪国・隣国に加え、遠国も登用可。遠いほど成功率は下がる,

  getRoninServiceReach(ronin, clanId) {
    const dist = this.getRoninDistanceToClan(ronin, clanId);
    const lacksHeir = this.householdLacksHeir(clanId);
    if (dist === 0) {
      return { dist, reachable: true, label: '流浪国', bonus: lacksHeir ? 32 : 20, penalty: 0, lacksHeir };
    }
    if (dist === 1) {
      return { dist, reachable: true, label: '隣国', bonus: lacksHeir ? 16 : 0, penalty: lacksHeir ? 4 : 22, lacksHeir };
    }
    if (Number.isFinite(dist)) {
      const extra = Math.max(0, dist - 2);
      return {
        dist,
        reachable: true,
        label: '遠国',
        bonus: lacksHeir ? 22 : 0,
        penalty: (lacksHeir ? 24 : 46) + extra * 6,
        lacksHeir
      };
    }
    return { dist: 6, reachable: true, label: '諸国流浪', bonus: lacksHeir ? 12 : 0, penalty: lacksHeir ? 28 : 52, lacksHeir };
  },

  // プレイヤー登用の成功率（流浪国が高く、隣国・遠国は下がる。跡継ぎ不在なら上昇）,

  calcPlayerRoninRecruitRate(off) {
    const reach = this.getRoninServiceReach(off, this.playerClanId);
    if (!reach.reachable) return { ...reach, rate: 0 };

    let rate = 60 + reach.bonus - reach.penalty;
    const myDaimyoOff = (this.activeOfficers || []).find(o => o.clanId === this.playerClanId && o.isDaimyo && !o.isDead);
    const daimyoIntel = myDaimyoOff ? (myDaimyoOff.intel || 50) : 50;
    const daimyoPol = myDaimyoOff ? (myDaimyoOff.politic || 50) : 50;
    rate += Math.round((daimyoIntel + daimyoPol - 100) * 0.15);

    const offTotal = (off.military || 50) + (off.politic || 50) + (off.intel || 50);
    rate -= Math.round((offTotal - 150) * 0.08);

    const cap = reach.dist === 0 ? 95 : (reach.dist === 1 ? (reach.lacksHeir ? 88 : 72) : (reach.lacksHeir ? 62 : 32));
    const floor = reach.dist === 0 ? (reach.lacksHeir ? 55 : 40) : (reach.dist === 1 ? (reach.lacksHeir ? 32 : 15) : (reach.lacksHeir ? 22 : 6));
    rate = Math.max(floor, Math.min(cap, rate));
    return { ...reach, rate };
  },

  // 武将の現在所在国・拠点情報を取得（城主・大名・待機武将・浪人の所在国を特定）,

  getOfficerLocationInfo(off) {
    if (!off) return { prov: null, provName: '諸国', castleName: '', label: '流浪', type: 'unknown', isMine: false };

    // 1. 城主任命中の武将（任地領国）
    if (off.assignedProvId) {
      const p = (this.provinces || []).find(x => x.id === off.assignedProvId);
      if (p) {
        return {
          prov: p,
          provName: this.getProvinceJapaneseName(p.id),
          castleName: p.castleName || p.castle || '居城',
          label: p.castleName || p.castle || '城主',
          type: 'governor',
          isMine: p.ownerId === this.playerClanId
        };
      }
    }

    // 2. 浪人武将（未仕官・在野）
    if (off.clanId === 'ronin') {
      const defProvId = off.defaultProv;
      const p = defProvId ? (this.provinces || []).find(x => x.id === defProvId) : null;
      const provName = defProvId ? this.getProvinceJapaneseName(defProvId) : '諸国';
      const isMine = p && p.ownerId === this.playerClanId;
      return {
        prov: p,
        provName: provName,
        castleName: p ? (p.castleName || p.castle) : '',
        label: isMine ? '自領内' : '在野',
        type: 'ronin',
        isMine: isMine
      };
    }

    // 3. 大名武将（本拠は、その家が現に領有している国だけ）
    if (off.isDaimyo) {
      const capProv = this.getDaimyoHomeProvince(off);
      if (!capProv) {
        return {
          prov: null,
          provName: '所領なし',
          castleName: '',
          label: '浪々',
          type: 'daimyo',
          isMine: false
        };
      }
      return {
        prov: capProv,
        provName: this.getProvinceJapaneseName(capProv.id),
        castleName: capProv.castleName || capProv.castle || '',
        label: '居城',
        type: 'daimyo',
        isMine: off.clanId === this.playerClanId
      };
    }

    // 4. 配下待機武将（主君の本拠地国に待機）
    const clanProvs = (this.provinces || []).filter(p => p.ownerId === off.clanId);
    const capProv = clanProvs.find(p => this.isCapitalProvince(p.id, off.clanId))
                 || (window.CLAN_CAPITAL_PROVINCES && (this.provinces || []).find(p => p.id === window.CLAN_CAPITAL_PROVINCES[off.clanId]))
                 || clanProvs[0]
                 || (off.defaultProv ? (this.provinces || []).find(p => p.id === off.defaultProv) : null);
    const provName = capProv ? this.getProvinceJapaneseName(capProv.id) : (off.defaultProv ? this.getProvinceJapaneseName(off.defaultProv) : '本国');
    const isMine = off.clanId === this.playerClanId;
    return {
      prov: capProv,
      provName: provName,
      castleName: capProv ? (capProv.castleName || capProv.castle) : '',
      label: '本拠待機',
      type: 'waiting',
      isMine: isMine
    };
  },

  // 城主不在のとき、国司在京・天領代官・無名の城代を分ける,

  getVacantRule(p, ownerId) {
    const scen = this.currentScenario;
    if (scen && Array.isArray(scen.kokufuClans) && scen.kokufuClans.includes(ownerId)) {
      return {
        label: '国司',
        skill: '在京国司',
        badge: '国司在京',
        noPercentage: true,
        lore: '国司は京に駐まっており、現地に武士の城代は置いていない。国衙の在庁が政務を預かる。'
      };
    }
    if (scen && Array.isArray(scen.daikanProvinces) && scen.daikanProvinces.includes(p.id)) {
      return {
        label: '代官',
        skill: '天領代官',
        badge: '代官支配',
        lore: '幕府の天領、または幼主・預かりの国。城主は置かず代官が治める。'
      };
    }
    return null;
  },

  // 領国の実効統治能力（ユーザー要件: 基本的に大名の本拠地では城代はいません。大名の能力が適用されます）,

  getEffectiveStats(provId) {
    const p = this.provinces.find(x => x.id === provId);
    if (!p) return { military: 60, politics: 60, stratagem: 60, ratio: 1.0, isCapital: false };
    const ownerId = p.ownerId || this.playerClanId;
    const daimyoAb = getClanAbility(ownerId) || { military: 75, politics: 75, stratagem: 75 };
    
    // 大名武将の検索
    const daimyoOff = (this.activeOfficers || this.officers || []).find(o => o.clanId === ownerId && o.isDaimyo && !o.isDead);
    const daimyoName = daimyoOff?.name || this.getDaimyoLeaderName(ownerId);
    const daimyoMil = daimyoOff?.military ?? daimyoAb.military ?? 75;
    const daimyoPol = daimyoOff?.politic ?? daimyoAb.politics ?? 75;
    const daimyoIntel = daimyoOff?.intel ?? daimyoAb.stratagem ?? 75;

    // 城主武将の検索
    const governor = (p.governorId && (this.officers || this.activeOfficers)) 
      ? (this.officers || this.activeOfficers).find(o => o.id === p.governorId) 
      : null;

    const isCap = this.isCapitalProvince(p.id, ownerId);

    // 【絶対原則】大名の本拠地では城代はいません。大名の能力（100%）が適用されます
    // 【修正】governor.isDaimyo への依存を削除し、現在の真の当主(daimyoOff)と一致するかのみを判定
    if (isCap || (governor && daimyoOff && governor.id === daimyoOff.id)) {
      return {
        governor: daimyoOff || governor,
        isCapital: true,
        isDirectRule: false,
        isDaimyo: true,
        isJodai: false,
        name: daimyoName,
        military: daimyoMil,
        politics: daimyoPol,
        stratagem: daimyoIntel,
        skill: daimyoOff?.skill || '本拠親政',
        lore: daimyoOff?.lore || `${daimyoName}公の居城・本拠地。大名本人が親政を行い能力を100%発揮します。`,
        ratio: 1.0
      };
    } else if (governor) {
      // 本拠地以外の支城で一般武将が城主（能力100%発揮）
      return {
        governor: governor,
        isCapital: false,
        isDirectRule: false,
        isDaimyo: false,
        isJodai: false,
        name: governor.name,
        military: governor.military,
        politics: governor.politic,
        stratagem: governor.intel,
        skill: governor.skill || '武辺者',
        lore: governor.lore || '',
        ratio: 1.0
      };
    } else {
      // 本拠地以外の支城で城主不在 ＝ 通常の城代統治（大名能力の40%〜75%）
      if (!p.jodaiRatio) {
        const hash = ((provId.charCodeAt(0) * 17) + (provId.length * 23) + (ownerId ? ownerId.charCodeAt(0) * 7 : 11)) % 36;
        p.jodaiRatio = 0.40 + (hash / 100); // 0.40 〜 0.75
      }
      const ratio = p.jodaiRatio;
      const jMil = Math.max(20, Math.round(daimyoMil * ratio));
      const jPol = Math.max(20, Math.round(daimyoPol * ratio));
      const jStrat = Math.max(20, Math.round(daimyoIntel * ratio));
      const vacant = this.getVacantRule(p, ownerId);
      const pct = Math.round(ratio * 100);

      const vacantBadge = vacant
        ? (vacant.noPercentage || vacant.badge === '国司在京' ? vacant.badge : `${vacant.badge}（${pct}%）`)
        : `城代統治（${pct}%）`;

      return {
        governor: null,
        isCapital: false,
        isDirectRule: true,
        isJodai: true,
        isDaimyo: false,
        name: vacant ? vacant.label : '城代',
        military: jMil,
        politics: jPol,
        stratagem: jStrat,
        skill: vacant ? vacant.skill : '城代統治',
        lore: vacant ? vacant.lore : `大名不在の支城のため城代が統治。大名能力の${pct}%を発揮。`,
        vacantBadge: vacantBadge,
        ratio: ratio
      };
    }
  },

  // 武将の一言コメント取得ヘルパー,

  getOfficerComment(off) {
    if (!off) return '忠勇の士';
    if (off.skill && typeof off.skill === 'string' && off.skill.trim()) {
      return off.skill.trim();
    }
    if (off.isDaimyo) {
      return '当主の威令';
    }
    const mil = Number(off.military) || 0;
    const pol = Number(off.politic || off.politics) || 0;
    const intel = Number(off.intel || off.stratagem) || 0;
    
    if (mil >= 90) return '天下無双の豪傑';
    if (intel >= 90) return '神算鬼謀の軍師';
    if (pol >= 90) return '天下屈指の治世家';
    if (mil >= 80) return '一騎当千の猛将';
    if (intel >= 80) return '深謀遠慮の智将';
    if (pol >= 80) return '富国強兵の能吏';
    if (mil >= 70) return '歴戦の武辺者';
    if (intel >= 70) return '機略に富む謀士';
    if (pol >= 70) return '民政巧者';
    if (mil >= 60 || pol >= 60 || intel >= 60) return '気鋭の将';
    return '忠勇の士';
  },

  // 武将詳細・人物列伝ポップアップモーダル（ワンクリック展開・文字サイズ12pt以上）,

  commitGovernorAppointment(provId, officerId, opts = {}) {
    const p = (this.provinces || []).find(x => x.id === provId);
    const newGov = (this.activeOfficers || []).find(o => o.id === officerId && o.clanId === this.playerClanId && !o.isDead);
    if (!p || p.ownerId !== this.playerClanId || !newGov) return false;
    if (newGov.id === p.governorId && newGov.assignedProvId === p.id) return false;

    const currentGov = p.governorId
      ? (this.activeOfficers || []).find(o => o.id === p.governorId && o.id !== newGov.id)
      : null;
    if (currentGov) currentGov.assignedProvId = null;

    if (newGov.isDaimyo) {
      const oldCapitalProvId = (window.CLAN_CAPITAL_PROVINCES && window.CLAN_CAPITAL_PROVINCES[this.playerClanId])
        ? window.CLAN_CAPITAL_PROVINCES[this.playerClanId]
        : newGov.assignedProvId;
      const oldProv = oldCapitalProvId ? this.provinces.find(x => x.id === oldCapitalProvId) : null;
      if (oldProv && oldProv.id !== p.id) {
        oldProv.governorId = null;
        if (!opts.silent) {
          this.log(`👑【本拠移転】${newGov.name}公は居城を${oldProv.name}から${p.name}国（${p.castleName || p.castle}）へ移転させました！旧本拠地・${oldProv.name}は城代統治となります。`, 'important');
        }
      }
      if (!window.CLAN_CAPITAL_PROVINCES) window.CLAN_CAPITAL_PROVINCES = {};
      window.CLAN_CAPITAL_PROVINCES[this.playerClanId] = p.id;
    } else if (newGov.assignedProvId && newGov.assignedProvId !== p.id) {
      const oldProv = this.provinces.find(x => x.id === newGov.assignedProvId);
      if (oldProv) {
        oldProv.governorId = null;
        if (!opts.silent) this.log(`【城主異動】${newGov.name}が${oldProv.name}から${p.name}へ転任しました。`);
      }
    }

    p.governorId = newGov.id;
    newGov.assignedProvId = p.id;
    if (!opts.silent) {
      this.log(`【城主任命】${newGov.name}を${p.name}国（${p.castleName || p.castle}）の城主に任命！(武${newGov.military} 内${newGov.politic} 謀${newGov.intel})`, 'important');
      this.audio.playTaiko();
    }
    return true;
  },

  clearCastleGovernor(provId, opts = {}) {
    const p = (this.provinces || []).find(x => x.id === provId);
    if (!p || p.ownerId !== this.playerClanId || !p.governorId) return false;
    const currentGov = (this.activeOfficers || []).find(o => o.id === p.governorId);
    if (currentGov) currentGov.assignedProvId = null;
    p.governorId = null;
    if (!opts.silent) {
      const isCap = this.isCapitalProvince(p.id, p.ownerId);
      if (isCap) {
        this.log(`【城主解任】${p.name}の城主を解任し、大名本拠地親政（能力100%発揮）としました。`);
      } else {
        this.log(`【城主解任】${p.name}の城主を解任し、城代統治（大名能力の${Math.round((p.jodaiRatio || 0.55) * 100)}%発揮）としました。`);
      }
    }
    return true;
  },

  // 自領の城主を一覧で選び、まとめて任命する,

  extractPersonSurname(fullName) {
    if (!fullName) return '';
    const name = String(fullName).replace(/家$/, '');
    const prefixes = ['長宗我部', '宇喜多', '龍造寺', '竜造寺', '小早川', '宇都宮', '西園寺', '小笠原', '佐々木', '豊臣', '羽柴', '木下', '徳川', '松平', '藤原', '清原'];
    const list = [...new Set([...prefixes, ...this.getKnownSurnames()])].sort((a, b) => b.length - a.length);
    for (const surname of list) {
      if (!surname) continue;
      if (name === surname) return surname;
      if (name.startsWith(surname) && name.length > surname.length) return surname;
    }
    if (name.length === 3) return name[0];
    if (name.length >= 4) return name.slice(0, 2);
    return name;
  },

  // 同じ一門とみなす苗字（賜姓・改姓を含む）,

  surnameGroup(surname) {
    const groups = [
      ['豊臣', '羽柴', '木下'],
      ['徳川', '松平'],
      ['藤原', '清原']
    ];
    if (!surname) return [];
    const found = groups.find(arr => arr.includes(surname));
    return found ? found.slice() : [surname];
  },

  // その家の一門（宗家の苗字、または先代当主と同じ苗字）,

  ichimonSurnames(clanId, deceasedName) {
    const set = new Set();
    const add = (raw) => {
      const sur = this.extractPersonSurname(raw);
      this.surnameGroup(sur).forEach(s => { if (s) set.add(s); });
    };
    const master = (window.CLAN_MASTER_DATA || {})[clanId];
    if (master?.family) add(String(master.family).replace(/家$/, ''));
    if (this.foundingLeaderNames?.[clanId]) add(this.foundingLeaderNames[clanId]);
    if (deceasedName) add(deceasedName);
    return set;
  },

  isIchimonName(officerName, clanId, deceasedName) {
    const sur = this.extractPersonSurname(officerName);
    return this.ichimonSurnames(clanId, deceasedName).has(sur);
  },

  // 一門判定：OFFICER_FAMILY_ROSTERS に家の一門 ID 名簿があればそれを優先、なければ苗字（完全一致）で判定,

  isIchimonOfficer(off, clanId, deceasedName) {
    if (!off) return false;
    const roster = (window.OFFICER_FAMILY_ROSTERS || {})[clanId];
    if (Array.isArray(roster) && roster.length && this.officerIdIn(off, roster)) return true;
    return this.isIchimonName(off.name, clanId, deceasedName);
  },

  isHideyoshiHouseHead(name) {
    if (!name) return false;
    const sur = this.extractPersonSurname(name);
    return this.surnameGroup(sur).includes('豊臣') && this.leaderNamesMatch(name, '豊臣秀吉');
  },

  officerCanInherit(off) {
    if (!off || off.isDead) return false;
    const year = Number(this.year || 0);
    const birth = Number(off.birthYear);
    const death = Number(off.deathYear);
    if (!Number.isNaN(birth) && year - birth < 15) return false;
    if (!Number.isNaN(death) && year > death) return false;
    return true;
  },

  deceasedDaimyoName(clanId) {
    return this.lastDaimyoNames?.[clanId] || this.foundingLeaderNames?.[clanId] || '';
  },

  snapshotLivingDaimyoNames() {
    this.lastDaimyoNames = this.lastDaimyoNames || {};
    (this.activeOfficers || []).forEach(o => {
      if (o && o.clanId && o.isDaimyo && !o.isDead && o.name) {
        this.lastDaimyoNames[o.clanId] = o.name;
      }
    });
  },

  nextRosterHeirName(clanId, deceasedName) {
    const profile = (window.CLAN_MASTER_DATA || {})[clanId];
    if (!profile?.leaders) return '';
    const years = Object.keys(profile.leaders).map(Number).filter(y => !Number.isNaN(y)).sort((a, b) => a - b);
    const cur = Number(this.year || 0);
    const past = years.filter(y => y <= cur);
    if (past.length) {
      const name = profile.leaders[String(past[past.length - 1])];
      if (name && !this.leaderNamesMatch(name, deceasedName)) return name;
    }
    const futureYear = years.find(y => y > cur);
    if (futureYear) {
      const name = profile.leaders[String(futureYear)];
      if (name && !this.leaderNamesMatch(name, deceasedName)) return name;
    }
    return '';
  },

  // 一門を家臣より優先。秀吉の家なら秀頼、秀次、秀長の順。同格は能力で決める,

  scoreHeir(off, clanId, deceasedName) {
    const ichimon = this.isIchimonOfficer(off, clanId, deceasedName);
    let score = ichimon ? 1000000 : 0;
    const nextName = this.nextRosterHeirName(clanId, deceasedName);
    if (nextName && this.leaderNamesMatch(off.name, nextName)) score += 80000;
    const houseHead = this.isHideyoshiHouseHead(deceasedName) || this.isHideyoshiHouseHead(this.foundingLeaderNames?.[clanId]);
    if (ichimon && houseHead) {
      // 家督順は data.js の HIDEYOSHI_HEIR_ORDER_IDS（ID 完全一致）
      const order = window.HIDEYOSHI_HEIR_ORDER_IDS || [];
      const idx = order.indexOf(off.id);
      if (idx >= 0) score += 20000 - idx * 100;
    }
    score += (off.military || 0) + (off.politic || off.politics || 0) + (off.intel || off.intelligence || 0);
    return score;
  },

  sortHeirCandidates(candidates, clanId, deceasedName) {
    return [...candidates].sort((a, b) => this.scoreHeir(b, clanId, deceasedName) - this.scoreHeir(a, clanId, deceasedName));
  },

  // 家中の後継者に加え、浪人や所領のない家にいる一門だけを候補に足す,

  collectHeirPool(clanId, deceasedName) {
    const living = (this.activeOfficers || []).filter(o => this.officerCanInherit(o));
    const landed = (id) => id && id !== 'ronin' && (this.provinces || []).some(p => p.ownerId === id);
    const inClan = living.filter(o => o.clanId === clanId && !o.isDaimyo);
    const extras = living.filter(o => {
      if (!o || o.clanId === clanId || o.isDaimyo) return false;
      if (!this.isIchimonOfficer(o, clanId, deceasedName)) return false;
      return !landed(o.clanId);
    });
    return this.sortHeirCandidates([...inClan, ...extras], clanId, deceasedName);
  },

  // 動的世継ぎシステム (要件5),

  checkDaimyoLifespan() {
    // 1. プレイヤーの大名 (this.playerDaimyo) が this.activeOfficers に存在しなくなった場合を判定
    const currentDaimyo = (this.activeOfficers || []).find(o => 
      o.clanId === this.playerClanId && o.isDaimyo && !o.isDead
    );

    if (!currentDaimyo) {
      const oldName = this.deceasedDaimyoName(this.playerClanId) || this.playerDaimyo?.name || '';
      const oldLabel = oldName || '前当主';
      // 2. 一門を家臣より前に並べた世継ぎ候補（秀吉の後は秀頼）
      const candidates = this.collectHeirPool(this.playerClanId, oldName);

      // 3. 候補がいる場合は SweetAlert2 等で「世継ぎ（次の大名）を選択するダイアログ」を表示
      if (candidates.length > 0) {
        if (this.isAutoPlay) this.pauseAutoPlayForEvent();
        this.music.playTrack('crisis');
        this.audio.playHoragai();

        const inputOptions = {};
        candidates.forEach(o => {
          const age = this.year ? (this.year - (o.birthYear || 1530)) : null;
          const ageStr = age ? ` (${age}歳)` : '';
          const kin = this.isIchimonOfficer(o, this.playerClanId, oldName) ? '【一門】' : '【家臣】';
          inputOptions[o.id] = `${kin}${o.name}${ageStr} ⚔️${o.military} 🌾${o.politic ?? o.politics ?? 0} 📜${o.intel ?? o.intelligence ?? 0}${o.skill ? ' [' + o.skill + ']' : ''}`;
        });

        Swal.fire({
          title: `<span style="font-size:1.25rem; color:#f5eedc; font-weight:bold; letter-spacing:1px;">❖ 当主逝去と世継ぎ家督相続 ❖</span>`,
          width: '560px',
          customClass: {
            popup: 'heir-selection-popup',
            input: 'heir-selection-select'
          },
          html: `
            <div style="text-align:center; padding:0; font-family:'Noto Serif JP',serif;">
              <p style="font-size:11.5pt; color:#e74c3c; margin:2px 0 6px 0; letter-spacing:1px;"><strong>【当主・${oldLabel} 公、天寿を全うし逝去】</strong></p>
              <p style="font-size:9.5pt; color:#ded6c8; line-height:1.5; margin:0 0 8px 0;">
                当主の御逝去に伴い重臣評定を召集いたしました。<br>
                一門を優先し、我が家の血脈と志を継ぐ【新当主】を指名してください。
              </p>
              ${this.autoPlayPausedForEvent ? '<p class="event-auto-pause-note" style="margin:4px 0 8px 0; font-size:10.5pt; color:#f5b041; text-align:center; font-weight:bold;">⏸ オート進行を一時停止しています。新当主を決定すると再開します。</p>' : ''}
              <div style="font-size:10pt; color:#c59b27; margin-bottom:2px; font-weight:bold; display:flex; align-items:center; justify-content:center; gap:6px;">
                <span>▼</span><span>世継ぎ（新当主）候補武将を選択</span><span>▼</span>
              </div>
            </div>
          `,
          input: 'select',
          inputOptions: inputOptions,
          inputValue: candidates[0].id,
          allowOutsideClick: false,
          allowEscapeKey: false,
          showCancelButton: false,
          confirmButtonText: 'この武将に家督を継承させる',
          confirmButtonColor: '#922b21',
          background: '#1c130d',
          color: '#f5eedc',
          didOpen: (popup) => {
            const selectEl = popup.querySelector('.swal2-select');
            if (selectEl) {
              selectEl.style.setProperty('color-scheme', 'dark');
              selectEl.style.setProperty('background-color', '#241710', 'important');
              selectEl.style.setProperty('color', '#f5eedc', 'important');
              selectEl.style.setProperty('border', '1.5px solid #a07840', 'important');
              selectEl.style.setProperty('border-radius', '6px', 'important');
              selectEl.style.setProperty('padding', '8px 12px', 'important');
              selectEl.style.setProperty('font-size', '10.5pt', 'important');
              selectEl.style.setProperty('width', '92%', 'important');
              selectEl.style.setProperty('max-width', '480px', 'important');
              selectEl.style.setProperty('margin', '6px auto 10px auto', 'important');
              selectEl.style.setProperty('display', 'block', 'important');

              Array.from(selectEl.options).forEach(opt => {
                opt.style.setProperty('color-scheme', 'dark');
                opt.style.setProperty('background-color', '#241710', 'important');
                opt.style.setProperty('color', '#f5eedc', 'important');
                opt.style.setProperty('padding', '8px 10px', 'important');
              });

              // プレビュー表示エリアの生成・挿入
              const previewDiv = document.createElement('div');
              previewDiv.id = 'heir-preview-container';
              previewDiv.style.cssText = 'width:92%; max-width:480px; margin:4px auto 12px auto; background:rgba(0,0,0,0.5); border:1px solid #7d633b; border-radius:6px; padding:8px 12px; font-family:"Noto Serif JP",serif; text-align:left; box-sizing:border-box; box-shadow:inset 0 1px 4px rgba(0,0,0,0.5);';
              
              const updatePreview = (officerId) => {
                const off = candidates.find(c => c.id === officerId) || candidates[0];
                if (!off) return;
                const age = this.year ? (this.year - (off.birthYear || 1530)) : null;
                const ageText = age ? ` (${age}歳)` : '';
                const skillBadge = off.skill ? `<span style="background:#8c6d3b; color:#fff; padding:2px 8px; border-radius:3px; font-size:9pt; margin-left:6px; border:1px solid #c59b27;">特性: ${off.skill}</span>` : '';
                
                previewDiv.innerHTML = `
                  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #5a4638; padding-bottom:4px; margin-bottom:8px;">
                    <div>
                      <span style="font-size:13pt; font-weight:bold; color:#ffd700;">${off.name}</span>
                      <span style="color:#ded6c8; font-size:9.5pt; margin-left:4px;">${ageText}</span>
                    </div>
                    <div>${skillBadge}</div>
                  </div>
                  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; text-align:center;">
                    <div style="background:rgba(231,76,60,0.22); border:1px solid #c0392b; padding:4px 6px; border-radius:4px;">
                      <div style="font-size:9.5pt; color:#ff7675; font-weight:bold;">⚔️ 武勇</div>
                      <div style="font-size:13.5pt; font-weight:bold; color:#ff7675;">${off.military}</div>
                    </div>
                    <div style="background:rgba(52,152,219,0.22); border:1px solid #2980b9; padding:4px 6px; border-radius:4px;">
                      <div style="font-size:9.5pt; color:#74b9ff; font-weight:bold;">🌾 内政</div>
                      <div style="font-size:13.5pt; font-weight:bold; color:#74b9ff;">${off.politic ?? off.politics ?? '-'}</div>
                    </div>
                    <div style="background:rgba(46,204,113,0.22); border:1px solid #27ae60; padding:4px 6px; border-radius:4px;">
                      <div style="font-size:9.5pt; color:#2ecc71; font-weight:bold;">📜 知略</div>
                      <div style="font-size:13.5pt; font-weight:bold; color:#2ecc71;">${off.intel ?? off.intelligence ?? '-'}</div>
                    </div>
                  </div>
                `;
              };

              updatePreview(selectEl.value || candidates[0].id);

              selectEl.addEventListener('change', (e) => {
                updatePreview(e.target.value);
              });

              selectEl.insertAdjacentElement('afterend', previewDiv);
            }
          }
        }).then((result) => {
          const chosenId = result.value || candidates[0].id;
          const chosen = candidates.find(o => o.id === chosenId) || candidates[0];
          chosen.clanId = this.playerClanId;
          chosen.isDaimyo = true;
          chosen.assignedProvId = null; // 本拠地親政のため

          if (this.playerDaimyo) {
            this.playerDaimyo.name = chosen.name;
            this.playerDaimyo.officerId = chosen.id;
            this.playerDaimyo.clan = this.getClanFamilyName(this.playerClanId);
          }

          // 自勢力の全武将の所属先を新当主へ確実に連動
          (this.activeOfficers || []).forEach(o => {
            if (o.clanId === this.playerClanId && o.id !== chosen.id) {
              o.isDaimyo = false;
            }
          });

          const newFamilyName = this.getClanFamilyName(this.playerClanId);
          if (this.playerDaimyo) this.playerDaimyo.clan = newFamilyName;
          this.resyncOfficerPlacements();
          this.lastDaimyoNames = this.lastDaimyoNames || {};
          this.lastDaimyoNames[this.playerClanId] = chosen.name;
          this.log(`【家督相続】${oldLabel}公の御逝去に伴い、世継ぎ・${chosen.name}公が新当主へ就任。家名は${newFamilyName}となりました。`, 'important');
          this.audio.playFanfare();
          this.updateUI();
          this.music.playTrack(this.getSeasonTrackKey());
          if (this.autoPlayPausedForEvent) {
            this.resumeAutoPlayAfterEvent();
          }
        });
      } else {
        // ★【大名滅亡防止】自家に後継候補武将がいない場合：浪人から新当主（客将・名跡継承）を推戴！
        const roninCandidates = (this.activeOfficers || []).filter(o => o.clanId === 'ronin' && !o.isDead);

        if (roninCandidates.length > 0 && window.Swal) {
          if (this.isAutoPlay) this.pauseAutoPlayForEvent();
          this.music.playTrack('crisis');
          this.audio.playHoragai();

          // 能力順にソート
          roninCandidates.sort((a, b) => {
            const scoreA = (a.military || 0) + (a.politic || 0) + (a.intel || 0);
            const scoreB = (b.military || 0) + (b.politic || 0) + (b.intel || 0);
            return scoreB - scoreA;
          });

          const inputOptions = {};
          roninCandidates.forEach(o => {
            const defProv = o.defaultProv ? this.getProvinceJapaneseName(o.defaultProv) : '諸国';
            inputOptions[o.id] = `${o.name} [滞在:${defProv}] (武:${o.military} 内:${o.politic} 謀:${o.intel})`;
          });

          Swal.fire({
            title: `❖ 断絶危機！名将推戴による御家再興 ❖`,
            html: `
              <div style="text-align:center; padding:10px; font-family:'Noto Serif JP',serif;">
                <p style="font-size:13pt; color:#e74c3c; margin-bottom:12px;"><strong>【当主・${oldLabel} 公、御逝去／世継ぎ不在の危機】</strong></p>
                <p style="font-size:11.5pt; color:#f5eedc; line-height:1.7; margin-bottom:15px;">
                  当主が御逝去されましたが、直系の後継武将がおらず、このままでは御家断絶となります！<br>
                  しかし、領民・忠臣らが天下の流浪の士に檄を飛ばしたところ、名立たる浪人たちが我が家の名跡を継ぎ、御家を再興すべく参陣いたしました。<br>
                  <strong style="color:var(--gold-bright);">【新当主】として推戴・迎える名将を指名してください。</strong>
                </p>
                ${this.autoPlayPausedForEvent ? '<p class="event-auto-pause-note" style="margin:4px 0 8px 0; font-size:10.5pt; color:#f5b041; text-align:center; font-weight:bold;">⏸ オート進行を一時停止しています。新当主を推戴すると再開します。</p>' : ''}
              </div>
            `,
            input: 'select',
            inputOptions: inputOptions,
            inputValue: roninCandidates[0].id,
            allowOutsideClick: false,
            allowEscapeKey: false,
            showCancelButton: false,
            confirmButtonText: 'この名将を新当主に迎えて御家を再興する',
            confirmButtonColor: '#27ae60',
            background: '#1c130d',
            color: '#f5eedc'
          }).then((result) => {
            const chosenId = result.value || roninCandidates[0].id;
            const chosen = roninCandidates.find(o => o.id === chosenId) || roninCandidates[0];
            chosen.clanId = this.playerClanId;
            chosen.isDaimyo = true;
            chosen.assignedProvId = null;

            if (this.playerDaimyo) {
              this.playerDaimyo.name = chosen.name;
              this.playerDaimyo.officerId = chosen.id;
              this.playerDaimyo.clan = this.getClanFamilyName(this.playerClanId);
            }

            const newFamilyName = this.getClanFamilyName(this.playerClanId);
            if (this.playerDaimyo) this.playerDaimyo.clan = newFamilyName;
            this.resyncOfficerPlacements();
            this.lastDaimyoNames = this.lastDaimyoNames || {};
            this.lastDaimyoNames[this.playerClanId] = chosen.name;
            this.log(`🔥【御家再興・名跡継承】${oldLabel}公の御逝去に伴い、${chosen.name}公が新当主に推戴され、家名は${newFamilyName}となりました。`, 'important');
            this.audio.playGrandFanfare?.();
            this.updateUI();
            this.music.playTrack(this.getSeasonTrackKey());
            if (this.autoPlayPausedForEvent) {
              this.resumeAutoPlayAfterEvent();
            }
          });
        } else {
          // 世界に浪人が1人もいない極限状況のみ滅亡
          this.log(`💀【御家滅亡】後継ぎがいないため滅亡`, 'important');
          this.triggerDefeat('no-heir');
        }
      }
    }

    // 他勢力の大名代替わり処理（大名の断絶・空白地化を防止）
    const livingClanIds = [...new Set(this.provinces.map(p => p.ownerId).filter(id => id && id !== this.playerClanId))];
    for (const clanId of livingClanIds) {
      const hasDaimyo = (this.activeOfficers || []).some(o => o.clanId === clanId && o.isDaimyo && !o.isDead);
      if (!hasDaimyo) {
        const deceasedName = this.deceasedDaimyoName(clanId);
        const otherCandidates = this.collectHeirPool(clanId, deceasedName);
        if (otherCandidates.length > 0) {
          const oldClanName = this.getClanFamilyName(clanId);
          const heir = otherCandidates[0];
          heir.clanId = clanId;
          heir.isDaimyo = true;
          heir.assignedProvId = null;
          // 他の武将の大名フラグを解除し、新当主へ所属を連動
          (this.activeOfficers || []).forEach(o => {
            if (o.clanId === clanId && o.id !== heir.id) {
              o.isDaimyo = false;
            }
          });
          const newClanFamily = this.getClanFamilyName(clanId);
          const kinLabel = this.isIchimonOfficer(heir, clanId, deceasedName) ? '一門の' : '';
          this.lastDaimyoNames = this.lastDaimyoNames || {};
          this.lastDaimyoNames[clanId] = heir.name;
          this.resyncOfficerPlacements();
          this.log(`【家督相続】${oldClanName}にて当主が逝去、世継ぎの${kinLabel}${heir.name}が新当主へ就任。家名は${newClanFamily}となりました。`, 'important');
        } else {
          // ★【CPU大名滅亡防止】後継武将が不在の場合：領内滞在または全国の浪人から新当主を推戴！
          const roninCandidates = (this.activeOfficers || []).filter(o => o.clanId === 'ronin' && !o.isDead);
          if (roninCandidates.length > 0) {
            const myProvIds = this.provinces.filter(p => p.ownerId === clanId).map(p => p.id);
            // 領内に滞在している浪人を最優先、いなければ能力順
            let chosenRonin = roninCandidates.find(r => r.defaultProv && myProvIds.includes(r.defaultProv));
            if (!chosenRonin) {
              roninCandidates.sort((a, b) => {
                const scoreA = (a.military || 0) + (a.politic || 0) + (a.intel || 0);
                const scoreB = (b.military || 0) + (b.politic || 0) + (b.intel || 0);
                return scoreB - scoreA;
              });
              chosenRonin = roninCandidates[0];
            }

            chosenRonin.clanId = clanId;
            chosenRonin.isDaimyo = true;
            chosenRonin.assignedProvId = null;
            this.lastDaimyoNames = this.lastDaimyoNames || {};
            this.lastDaimyoNames[clanId] = chosenRonin.name;

            const clanName = this.getClanFamilyName(clanId);
            this.resyncOfficerPlacements();
            this.log(`🔥【名跡継承】当主逝去により、${chosenRonin.name}が家督を継承し、家名は${clanName}となりました。`, 'important');
          } else {
            // 全国に浪人が1人もいない場合：ゆかり城主の独立 → 残り空白地化
            const clanName = this.getClanFamilyName(clanId);
            this.log(`💀【御家滅亡】${clanName}は後継ぎがいないため滅亡。領国の再編が始まります。`, 'important');
            this.resolveClanCollapseIndependence(clanId);
          }
        }
      }
    }
  },

  // イベント発生後の新勢力一斉滅亡・名前欠落バグの完全修正（大名・武将の自動補正・復帰・創設）,

  namedLordForClan(ownerId) {
    const playable = this.currentScenario?.playables?.find(d => d.id === ownerId);
    const scenarioName = playable?.scenarioLeaderName || playable?.name;
    if (scenarioName) return scenarioName;
    const scenLeaders = this.currentScenario?.leaders;
    if (scenLeaders && scenLeaders[ownerId]) return scenLeaders[ownerId];
    const profile = (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA[ownerId]) ? window.CLAN_MASTER_DATA[ownerId] : null;
    if (profile?.leaders) {
      const curY = Number(this.year || 0);
      const years = Object.keys(profile.leaders).map(Number).filter(y => !isNaN(y) && y <= curY).sort((a, b) => b - a);
      if (years.length) return profile.leaders[String(years[0])];
      if (profile.leaders.default) return profile.leaders.default;
    }
    return '';
  },

  // 同じ家に当主候補が複数いるときの一意な選び方。
  // 1) シナリオの勢力当主名と完全一致 2) scen.leaders[家] 3) CLAN_MASTER_DATA の年代当主
  // 4) 内政（politic）が高い順 5) 先頭,

  pickClanLeader(clanId, candidates) {
    const list = (candidates || []).filter(Boolean);
    if (list.length <= 1) return list[0] || null;
    const playable = this.currentScenario?.playables?.find(d => d.id === clanId);
    const names = [
      playable?.scenarioLeaderName || playable?.name,
      this.currentScenario?.leaders?.[clanId],
      this.getRosterLeaderName ? this.getRosterLeaderName(clanId) : ''
    ].filter(Boolean);
    for (const n of names) {
      const hit = list.find(o => o.name && this.leaderNamesMatch(o.name, n));
      if (hit) return hit;
    }
    const pol = (o) => Number(o.politic ?? o.politics ?? 0);
    return [...list].sort((a, b) => pol(b) - pol(a))[0] || list[0];
  },

  // 生存中の当主武将（isDaimyo）。複数いれば pickClanLeader で一人に絞る,

  getClanDaimyoOfficer(clanId) {
    const flagged = (this.activeOfficers || this.officers || []).filter(o => o.clanId === clanId && o.isDaimyo && !o.isDead);
    return this.pickClanLeader(clanId, flagged);
  },

  seatNamedLord(ownerId) {
    const leaderName = this.namedLordForClan(ownerId);
    if (!leaderName || !this.activeOfficers) return null;
    const matches = (o) => o && this.officerCanInherit(o) && o.name && this.leaderNamesMatch(o.name, leaderName);
    let lord = this.activeOfficers.find(o => matches(o) && o.clanId === ownerId)
      || this.activeOfficers.find(matches);
    if (lord && lord.clanId !== ownerId && lord.isDaimyo && this.isClanExtant(lord.clanId)) {
      const theirName = this.namedLordForClan(lord.clanId);
      if (theirName && this.leaderNamesMatch(lord.name, theirName)) lord = null;
    }
    if (!lord && window.OFFICERS_MASTER) {
      const master = window.OFFICERS_MASTER.find(o => matches(o));
      if (master && !this.activeOfficers.some(o => o.id === master.id)) {
        lord = JSON.parse(JSON.stringify(master));
        lord.isDead = false;
        this.activeOfficers.push(lord);
      } else if (master) {
        lord = this.activeOfficers.find(o => o.id === master.id && this.officerCanInherit(o)) || null;
      }
    }
    if (!lord) return null;
    lord.clanId = ownerId;
    lord.isDaimyo = true;
    lord.isDead = false;
    lord.hasBeenDaimyo = true;
    if (this.formerDaimyoIds) this.formerDaimyoIds.add(lord.id);
    this.activeOfficers.filter(o => o.clanId === ownerId && o.id !== lord.id).forEach(o => {
      o.isDaimyo = false;
    });
    this.lastDaimyoNames = this.lastDaimyoNames || {};
    this.lastDaimyoNames[ownerId] = lord.name;
    return lord;
  },

  syncDaimyoStatus() {
    if (!this.provinces) return;
    this.activeOfficers = this.activeOfficers || [];

    const activeOwners = [...new Set(this.provinces.map(p => p.ownerId).filter(Boolean))];
    activeOwners.forEach(ownerId => {
      // 1. 自勢力に生存中の大名武将(isDaimyo: true)がいるかチェック
      let daimyoOfficer = this.activeOfficers.find(o => o.clanId === ownerId && o.isDaimyo && !o.isDead);

      // シナリオと史実名簿に名前がある当主が存命なら、家臣より先にその人を当主にする
      if (!daimyoOfficer) daimyoOfficer = this.seatNamedLord(ownerId);

      // 2. いない場合、一門を家臣より優先して大名に格上げ（秀吉の後は秀頼）
      if (!daimyoOfficer) {
        const deceasedName = this.deceasedDaimyoName(ownerId);
        const clanOfficers = this.collectHeirPool(ownerId, deceasedName);
        if (clanOfficers.length > 0) {
          daimyoOfficer = clanOfficers[0];
          daimyoOfficer.clanId = ownerId;
          daimyoOfficer.isDaimyo = true;
          this.lastDaimyoNames = this.lastDaimyoNames || {};
          this.lastDaimyoNames[ownerId] = daimyoOfficer.name;
        }
      }

      // 3. それでもいない場合（新勢力で武将が0人の場合: 生存している史実当主を呼び戻す、または創設）
      if (!daimyoOfficer) {
        let leaderName = this.getDaimyoLeaderName(ownerId);
        const deadLord = this.deceasedDaimyoName(ownerId);
        if (deadLord && this.leaderNamesMatch(leaderName, deadLord)) {
          const nextHeir = this.nextRosterHeirName(ownerId, deadLord);
          if (nextHeir) leaderName = nextHeir;
        }

        const canSpawn = (off) => this.officerCanInherit(off);

        // 秀吉がまだ寿命内のときだけ名寄せする。没した秀吉は復活させない
        if (this.leaderNamesMatch(leaderName, '豊臣秀吉')) {
          daimyoOfficer = this.activeOfficers.find(o =>
            this.officerIdIn(o, ['off_toyotomi_hideyoshi', 'toyotomi']) && canSpawn(o)
          );
        }

        // 以前のイベントで作った当主を使い回し、二重生成しない
        if (!daimyoOfficer) {
          daimyoOfficer = this.activeOfficers.find(o => o.id === `off_event_${ownerId}` && canSpawn(o));
        }

        // (A) 浪人、または領地を持たない家にいる史実当主だけを自勢力へ移す。他国の当主は奪わない
        if (!daimyoOfficer) {
          daimyoOfficer = this.activeOfficers.find(o => {
            if (!canSpawn(o) || !o.name) return false;
            // 名前の部分一致は使わない（別名は LEADER_NAME_ALIASES で完全一致）
            const nameHit = this.leaderNamesMatch(o.name, leaderName);
            if (!nameHit) return false;
            if (o.clanId !== ownerId && o.isDaimyo && this.isClanExtant(o.clanId)) return false;
            return true;
          });
        }

        // (B) 同名の生存武将だけを写す。没年を過ぎた武将と、すでに居る武将は複製しない
        if (!daimyoOfficer && window.OFFICERS_MASTER) {
          const masterOff = window.OFFICERS_MASTER.find(o => this.leaderNamesMatch(o.name, leaderName));
          if (masterOff && canSpawn(masterOff)) {
            const existing = this.activeOfficers.find(o => o.id === masterOff.id);
            if (existing && canSpawn(existing)) {
              daimyoOfficer = existing;
            } else if (!existing) {
              daimyoOfficer = JSON.parse(JSON.stringify(masterOff));
              daimyoOfficer.isDead = false;
              daimyoOfficer.isDaimyo = false;
              this.activeOfficers.push(daimyoOfficer);
            }
          }
        }

        // (C) それでも見つからない場合、正規の当主武将オブジェクトを自動生成
        if (!daimyoOfficer) {
          const profile = (window.CLAN_MASTER_DATA && window.CLAN_MASTER_DATA[ownerId]) ? window.CLAN_MASTER_DATA[ownerId] : null;
          const clanAbility = getClanAbility(ownerId);
          const finalName = (leaderName && leaderName !== ownerId && !leaderName.endsWith('家')) 
            ? leaderName : `${this.getClanDisplayName(ownerId)}`;
          daimyoOfficer = {
            id: `off_event_${ownerId}`,
            name: finalName,
            clanId: ownerId,
            defaultProv: this.provinces.find(p => p.ownerId === ownerId)?.id || null,
            military: clanAbility.military || 75,
            politic: clanAbility.politics || 75,
            intel: clanAbility.stratagem || 75,
            era: 'sengoku',
            skill: profile?.tactic || '威風堂々',
            lore: profile?.desc || `${this.getClanDisplayName(ownerId)}の当主。`,
            birthYear: Math.max(900, (this.year || 1560) - 30),
            deathYear: (this.year || 1560) + 40,
            isDaimyo: true,
            isDead: false
          };
          this.activeOfficers.push(daimyoOfficer);
        }

        if (daimyoOfficer && this.officerCanInherit(daimyoOfficer)) {
          daimyoOfficer.clanId = ownerId;
          daimyoOfficer.isDaimyo = true;
          daimyoOfficer.isDead = false;
          daimyoOfficer.assignedProvId = null;
          this.lastDaimyoNames = this.lastDaimyoNames || {};
          this.lastDaimyoNames[ownerId] = daimyoOfficer.name;
        } else {
          daimyoOfficer = null;
        }
      }

      // 4. 当主武将の確定と、同勢力他武将の大名フラグ解除
      if (daimyoOfficer) {
        this.activeOfficers.filter(o => o.clanId === ownerId && o.id !== daimyoOfficer.id).forEach(o => {
          o.isDaimyo = false;
        });
      }

      // 5. プレイヤー勢力の場合は playerDaimyo とも同期（家名は後継当主の名字）
      if (ownerId === this.playerClanId && this.playerDaimyo && daimyoOfficer) {
        this.playerDaimyo.name = daimyoOfficer.name;
        this.playerDaimyo.officerId = daimyoOfficer.id;
        this.playerDaimyo.clan = this.getClanFamilyName(this.playerClanId);
      }
    });
    this.reconcileDaimyoWithMap();
    // 領地が移った城に旧主の城主を残さず、新当主は本拠のみ、家臣は支城のみに置き直す
    this.resyncOfficerPlacements();
  },

  // イベント・家督相続のあと、城主配置を領有関係と一致させる,

  resyncOfficerPlacements() {
    if (!this.provinces || !this.activeOfficers) return;

    if (window.CLAN_CAPITAL_PROVINCES) {
      const ownersNow = [...new Set(this.provinces.map(p => p.ownerId).filter(Boolean))];
      ownersNow.forEach(ownerId => {
        const myProvs = this.provinces.filter(p => p.ownerId === ownerId);
        if (myProvs.length === 0) return;
        const mapped = window.CLAN_CAPITAL_PROVINCES[ownerId];
        if (mapped && myProvs.some(p => p.id === mapped)) return;
        const daimyo = this.activeOfficers.find(o => o.clanId === ownerId && o.isDaimyo && !o.isDead);
        const seated = daimyo && myProvs.find(p => p.governorId === daimyo.id || p.id === daimyo.assignedProvId);
        window.CLAN_CAPITAL_PROVINCES[ownerId] = (seated || this.pickFallbackCapital(myProvs, ownerId) || myProvs[0]).id;
      });
    }

    const officerById = new Map(this.activeOfficers.map(o => [o.id, o]));
    const cleared = new Set();
    const clearGov = (p) => {
      if (!p || !p.governorId) return;
      const gov = officerById.get(p.governorId);
      p.governorId = null;
      if (gov && gov.assignedProvId === p.id) gov.assignedProvId = null;
      cleared.add(p.id);
    };

    const seenGov = new Map();
    this.provinces.forEach(p => {
      if (!p.governorId) return;
      if (seenGov.has(p.governorId)) {
        clearGov(p);
        return;
      }
      seenGov.set(p.governorId, p.id);
    });

    this.provinces.forEach(p => {
      if (!p.governorId) return;
      const gov = officerById.get(p.governorId);
      const foreign = !gov || gov.isDead || !p.ownerId || gov.clanId !== p.ownerId;
      const daimyoOnBranch = gov && gov.isDaimyo && !gov.isDead && !this.isCapitalProvince(p.id, p.ownerId);
      if (foreign || daimyoOnBranch) clearGov(p);
    });

    this.activeOfficers.forEach(o => {
      if (!o.assignedProvId) return;
      const p = this.provinces.find(x => x.id === o.assignedProvId);
      if (!p || o.isDead || p.ownerId !== o.clanId || p.governorId !== o.id) {
        if (p && p.governorId === o.id) clearGov(p);
        o.assignedProvId = null;
      }
    });

    const owners = [...new Set(this.provinces.map(p => p.ownerId).filter(Boolean))];
    owners.forEach(ownerId => {
      const daimyo = this.activeOfficers.find(o => o.clanId === ownerId && o.isDaimyo && !o.isDead);
      if (!daimyo) return;
      const myProvs = this.provinces.filter(p => p.ownerId === ownerId);
      const cap = myProvs.find(p => this.isCapitalProvince(p.id, ownerId)) || myProvs[0];
      if (!cap) return;

      myProvs.forEach(p => {
        if (p.id !== cap.id && p.governorId === daimyo.id) clearGov(p);
      });
      if (daimyo.assignedProvId && daimyo.assignedProvId !== cap.id) {
        const old = this.provinces.find(p => p.id === daimyo.assignedProvId);
        if (old && old.governorId === daimyo.id) clearGov(old);
        daimyo.assignedProvId = null;
      }
      if (cap.governorId && cap.governorId !== daimyo.id) {
        const prev = officerById.get(cap.governorId);
        if (prev) prev.assignedProvId = null;
        cap.governorId = null;
        cleared.add(cap.id);
      }
      cap.governorId = daimyo.id;
      daimyo.assignedProvId = cap.id;
      cleared.delete(cap.id);
    });

    const seatVassal = (p, officer) => {
      p.governorId = officer.id;
      officer.assignedProvId = p.id;
    };

    const openBranches = () => this.provinces.filter(p =>
      cleared.has(p.id) && p.ownerId && !p.governorId && !this.isCapitalProvince(p.id, p.ownerId)
    );

    openBranches().forEach(p => {
      const match = this.activeOfficers.find(o =>
        o.defaultProv === p.id && o.clanId === p.ownerId && !o.assignedProvId && !o.isDead && !o.isDaimyo && !this.isCourtFigure(o)
      );
      if (match) seatVassal(p, match);
    });

    this.autoAppointComputerCastellans({ fillVacancies: true });
  },

  // プレイヤー勢力の切り替え（本能寺の変・後継選択用）,

  switchPlayerClan(newClanId) {
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const targetPlayable = scen?.playables?.find(p => p.id === newClanId);
    const profile = window.CLAN_MASTER_DATA ? window.CLAN_MASTER_DATA[newClanId] : null;

    this.playerClanId = newClanId;

    // 当主武将の特定
    const daimyoOff = (this.activeOfficers || []).find(o => o.clanId === newClanId && o.isDaimyo && !o.isDead) ||
                      (this.activeOfficers || []).find(o => o.clanId === newClanId && !o.isDead);

    if (daimyoOff) {
      daimyoOff.isDaimyo = true;
    }

    if (targetPlayable) {
      this.playerDaimyo = JSON.parse(JSON.stringify(targetPlayable));
      if (daimyoOff) {
        this.playerDaimyo.name = daimyoOff.name;
        this.playerDaimyo.officerId = daimyoOff.id;
      }
      this.playerDaimyo.clan = this.getClanFamilyName(newClanId);
    } else if (profile) {
      this.playerDaimyo = {
        id: newClanId,
        name: daimyoOff ? daimyoOff.name : (profile.leaders?.['1582'] || profile.leaders?.default || newClanId),
        clan: this.getClanFamilyName(newClanId),
        color: profile.color || '#884422',
        crest: (profile.family || '').replace('家', '紋'),
        kamonSvgId: profile.kamon || `kamon-${newClanId}`,
        officerId: daimyoOff?.id,
        gold: 800,
        rice: 1200
      };
    }

    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    if (myProvs.length > 0) {
      this.selectProvince(myProvs[0].id);
    }

    this.updateUI();
    this.audio.playFanfare();
    this.log(`【後継就任】${this.playerDaimyo?.name || ''}公として乱世の覇権を継承いたしました！`, 'important');
  },

  // 本能寺の変・後継勢力分割＆各武将の所属先切り替え,

  executeHonnoujiSuccession(chosenSuccessorClanId = null) {

    // 【ここを追加】すでに本能寺の変が発生している場合は、処理を中断して重複を防ぐ
    if (this.honnojiSplit) {
      // 分裂は一度だけ。後継選択（2回目の呼び出し）ではプレイヤー勢力の切替だけ行う
      if (chosenSuccessorClanId && chosenSuccessorClanId !== this.playerClanId) {
        this.switchPlayerClan(chosenSuccessorClanId);
        this.syncDaimyoStatus();
        if (this.playerDaimyo) this.playerDaimyo.clan = this.getClanFamilyName(this.playerClanId);
        this.updateUI();
      }
      return;
    }
    
    this.honnojiSplit = true;
    // 本能寺の変の中身は data.js の HONNOUJI_SUCCESSION_DATA（落命・領地・後継・家臣団、すべて ID 完全一致）
    const H = window.HONNOUJI_SUCCESSION_DATA || {};
    const formerClan = H.formerClan || 'oda';
    const minTroops = Number(H.minTroops) || 3000;

    // 1. 落命退場
    const deadIds = Array.isArray(H.deadOfficerIds) ? H.deadOfficerIds : [];
    const markDead = (list) => {
      (list || []).forEach(o => {
        if (!o || !this.officerIdIn(o, deadIds)) return;
        o.isDead = true;
        o.isDaimyo = false;
        o.assignedProvId = null;
      });
    };
    markDead(this.activeOfficers);
    markDead(this.officers);

    // 2. 領地再編
    for (const [pId, newOwner] of Object.entries(H.territory || {})) {
      const prov = this.provinces.find(p => p.id === pId);
      if (prov) {
        prov.ownerId = newOwner;
        prov.troops = Math.max(minTroops, prov.troops || minTroops);
      }
    }

    // 3. 各跡継ぎ大名本人の設定
    const findByIds = (ids) => {
      const hit = (list) => (list || []).find(o => this.officerIdIn(o, ids || []));
      return hit(this.activeOfficers) || hit(this.officers);
    };
    const successorClans = [];
    const successorIds = new Set();
    let nobukatsu = null; // 旧主家を継ぐ当主（houseHeir）
    (H.successors || []).forEach(spec => {
      if (!spec || !spec.clanId) return;
      successorClans.push(spec.clanId);
      let lord = findByIds(spec.officerIds);
      if (!lord && spec.houseHeir) {
        lord = (this.activeOfficers || []).find(o => o.clanId === formerClan && !o.isDead && !o.isDaimyo);
      }
      if (!lord) return;
      lord.clanId = spec.clanId;
      lord.isDaimyo = true;
      lord.isDead = false;
      lord.assignedProvId = null;
      successorIds.add(lord.id);
      if (spec.houseHeir) nobukatsu = lord;
    });

    // 4. 跡継ぎ大名への所属切替（名前部分一致禁止・ID 配列のみ）
    const retainerGroups = Array.isArray(H.retainers) ? H.retainers : [];
    const unseatIfNotOwned = (off) => {
      if (!off.assignedProvId) return;
      const prov = this.provinces.find(p => p.id === off.assignedProvId);
      if (!prov || prov.ownerId !== off.clanId) {
        if (prov && prov.governorId === off.id) prov.governorId = null;
        off.assignedProvId = null;
      }
    };

    const lists = (this.officers && this.officers !== this.activeOfficers)
      ? [this.activeOfficers, this.officers]
      : [this.activeOfficers];
    lists.forEach(list => {
      if (!list) return;
      list.forEach(off => {
        if (!off || off.isDead) return;
        // 領地を持つ他家の当主は引き抜かない
        if (off.isDaimyo && !successorIds.has(off.id) && this.isClanExtant(off.clanId)) return;

        const group = retainerGroups.find(g => g && this.officerIdIn(off, g.officerIds || []));
        if (group) {
          off.clanId = group.clanId;
          unseatIfNotOwned(off);
          return;
        }

        // 旧主家の城主だけ、領地の新しい領主（跡継ぎ）に所属を合わせる
        if (off.clanId === formerClan && off.assignedProvId && off.id !== nobukatsu?.id) {
          const prov = this.provinces.find(p => p.id === off.assignedProvId);
          if (prov && prov.ownerId && successorClans.includes(prov.ownerId)) {
            off.clanId = prov.ownerId;
            return;
          }
        }

        unseatIfNotOwned(off);
      });
    });

    // 5. プレイヤーが指定勢力に切り替える場合
    if (chosenSuccessorClanId) {
      this.switchPlayerClan(chosenSuccessorClanId);
    } else if (this.playerClanId === formerClan) {
      // 旧主家のままであれば houseHeir（信雄）が新当主に
      if (this.playerDaimyo && nobukatsu) {
        this.playerDaimyo.name = nobukatsu.name;
        this.playerDaimyo.officerId = nobukatsu.id;
      }
    }

    this.updateCastlesForYear();
    this.updateToyotomiSurname(false);
    this.syncDaimyoStatus();
    if (this.playerDaimyo) this.playerDaimyo.clan = this.getClanFamilyName(this.playerClanId);
    this.updateUI();
    if (H.log) this.log(H.log, 'important');
  },

  startGame() {
    this.music.init();
    if (this.playerDaimyo) {
      this.playerDaimyo = JSON.parse(JSON.stringify(this.playerDaimyo));
    }
    const modal = document.getElementById('startModal');
    if (modal) modal.classList.add('hidden');

    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    if (!this.playerDaimyo && scen) {
      this.playerDaimyo = scen.playables[0];
      this.playerClanId = this.playerDaimyo.id;
    }

    let goldBase = this.playerDaimyo?.gold || 500;
    let riceBase = this.playerDaimyo?.rice || 800;
    if (this.currentDifficulty === 'easy') { goldBase += 400; riceBase += 500; }
    else if (this.currentDifficulty === 'normal') { goldBase += 150; riceBase += 200; }
    else if (this.currentDifficulty === 'hard') { goldBase -= 50; riceBase -= 100; }
    else if (this.currentDifficulty === 'hell') { goldBase -= 100; riceBase -= 200; }

    this.gold = Math.max(250, goldBase);
    this.rice = Math.max(350, riceBase);
    this.ap = 3;

    // シナリオ開始前・時代背景＆天下情勢解説モーダルの表示
    const introModal = document.getElementById('scenarioIntroModal');
    if (introModal && scen) {
      document.getElementById('introModalTitle').textContent = `❖ ${scen.year}年 【${scen.title}】 〜時代背景と天下情勢〜 ❖`;
      document.getElementById('introBackgroundText').textContent = scen.lore_background || scen.desc;
      document.getElementById('introFactionsText').textContent = scen.lore_factions || '全国諸侯が覇を競う天下の情勢。';
      document.getElementById('introFocusText').textContent = scen.lore_focus || '自領を固め、天下統一への覇道を切り拓け！';
      document.getElementById('introDaimyoOath').textContent = `「我ら${this.playerDaimyo?.clan || ''}、当主・${this.playerDaimyo?.name || ''}！この乱世に義の旗を掲げ、必ずや天下を静謐に導かん！」`;

      introModal.classList.remove('hidden');

      const startIntroBtn = document.getElementById('introStartBtn');
      if (startIntroBtn) {
        startIntroBtn.onclick = () => {
          introModal.classList.add('hidden');
          this.executeStartGameFlow();
        };
      }
    } else {
      this.executeStartGameFlow();
    }
  },

  executeStartGameFlow() {
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    this.updateUI();

    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    if (myProvs.length > 0) {
      this.selectProvince(myProvs[0].id);
    }
    this.updateSeasonVisuals();
    this.showSeasonNoticeBanner(this.year, this.seasonNames[this.seasonIdx], this.currentWeather);

    this.music.playTrack(this.getSeasonTrackKey());
    this.audio.playFanfare();

    this.log(`【覇業開幕】${this.playerDaimyo?.name || ''}公、${scen?.title || ''}の乱世へ出陣！`, 'important');
    this.autoSave();
  },

// ============================================================================
  // SVG日本地図の初期化と描画
  // ============================================================================,

  getFormationMeta(key) {
    const table = window.FORMATIONS_DATA || FORMATIONS_DATA || {};
    return table[key] || table.gyorin || { key: 'gyorin', name: '魚鱗', type: 'assault', label: '魚鱗' };
  },

  getFormationType(key) {
    return this.getFormationMeta(key).type || 'assault';
  },

  getFormationTypeLabel(type) {
    return (window.FORMATION_TYPES && window.FORMATION_TYPES[type] && window.FORMATION_TYPES[type].label) || type || '不明';
  },

  getRpsMultipliers(myKey, enemyKey) {
    const rps = window.FORMATION_RPS || {};
    const myType = this.getFormationType(myKey);
    const enType = this.getFormationType(enemyKey);
    const rel = rps[myType];
    if (rel && rel.beats === enType) return { ...(rps.advantage || { dealt: 1.18, taken: 0.9 }), outcome: 'advantage', myType, enType };
    if (rel && rel.losesTo === enType) return { ...(rps.disadvantage || { dealt: 0.85, taken: 1.12 }), outcome: 'disadvantage', myType, enType };
    return { ...(rps.neutral || { dealt: 1, taken: 1 }), outcome: 'neutral', myType, enType };
  },

  inferProvinceTerrain(prov) {
    if (!prov) return { id: 'plain', label: '平地', boost: 'assault' };
    if (prov._terrainCache) return prov._terrainCache;
    const blob = `${prov.specialty || ''} ${prov.culturalNotes || ''} ${prov.castleLore || ''} ${prov.region || ''} ${prov.name || ''}`;
    const table = window.TERRAIN_KEYWORDS || {};
    let best = { id: 'plain', label: '平地', boost: 'assault', score: 0 };
    for (const [id, meta] of Object.entries(table)) {
      const re = meta.keywords;
      if (!re) continue;
      const m = blob.match(re);
      const score = m ? m.length + (id === 'mountain' && /山城|険/.test(blob) ? 2 : 0) : 0;
      if (score > best.score) best = { id, label: meta.label, boost: meta.boost, score };
    }
    if (best.score === 0 && /北海道|九州|四国|中国/.test(prov.region || '') && /島|港|湊/.test(blob)) {
      best = { id: 'coast', label: '沿岸', boost: 'encircle', score: 1 };
    }
    prov._terrainCache = { id: best.id, label: best.label, boost: best.boost };
    return prov._terrainCache;
  },

  getTerrainDealtBonus(formationKey, prov) {
    const terrain = this.inferProvinceTerrain(prov);
    const type = this.getFormationType(formationKey);
    if (terrain.boost === type) return 1.10;
    if ((terrain.id === 'mountain' && type === 'assault') || (terrain.id === 'plain' && type === 'defense')) return 0.95;
    return 1.0;
  },

  pickEnemyFormation(enemyClanId, dstProv, playerKey) {
    const forms = Object.keys(window.FORMATIONS_DATA || FORMATIONS_DATA || { gyorin:1, kakuyoku:1, hoen:1 });
    const ability = getClanAbility(enemyClanId || 'default') || {};
    const personality = ability.personality || 'balanced';
    const terrain = this.inferProvinceTerrain(dstProv);
    const weights = {};
    forms.forEach(k => {
      const t = this.getFormationType(k);
      let w = 1;
      if (personality === 'aggressive' && t === 'assault') w += 2.2;
      if (personality === 'domestic' && t === 'defense') w += 2.2;
      if (personality === 'balanced' && t === 'encircle') w += 1.2;
      if (terrain.boost === t) w += 1.5;
      const counter = (window.FORMATION_RPS || {})[t];
      if (playerKey && counter && counter.beats === this.getFormationType(playerKey)) w += 1.3;
      weights[k] = w;
    });
    const total = Object.values(weights).reduce((a, b) => a + b, 0) || 1;
    let r = Math.random() * total;
    for (const k of forms) {
      r -= weights[k];
      if (r <= 0) return k;
    }
    return forms[0] || 'kakuyoku';
  },

  getClanStratagemPower(clanId, preferredProvId = null) {
    const ability = getClanAbility(clanId) || {};
    let best = Number(ability.stratagem) || 55;
    const offs = (this.activeOfficers || []).filter(o => o && !o.isDead && o.clanId === clanId);
    offs.forEach(o => {
      const intel = Number(o.intel || o.intelligence || o.stratagem) || 0;
      let score = intel;
      if (o.isDaimyo) score += 3;
      if (preferredProvId && (o.assignedProvId === preferredProvId || o.defaultProv === preferredProvId)) score += 5;
      if (score > best) best = score;
    });
    return Math.max(0, Math.min(100, best));
  },

  predictEnemyFormation(trueKey, stratagem) {
    const meta = this.getFormationMeta(trueKey);
    const s = Number(stratagem) || 0;
    if (s < 50) {
      return { text: '軍師の読み：敵陣形は【不明】（知略不足）', level: 'unknown', displayName: '不明' };
    }
    if (s < 70) {
      const typeLabel = this.getFormationTypeLabel(meta.type);
      return { text: `軍師の読み：敵は【${typeLabel}】の構えと見る（確度:カテゴリ）`, level: 'category', displayName: typeLabel, type: meta.type };
    }
    const conf = Math.min(96, Math.round(55 + (s - 70) * 1.35));
    return { text: `軍師の読み：敵陣形は【${meta.name}】と看破（確度 ${conf}%）`, level: 'exact', displayName: meta.name, key: trueKey, confidence: conf };
  },

  describeFormationMatchup(myKey, enemyKey, prov) {
    const mine = this.getFormationMeta(myKey);
    const enemy = this.getFormationMeta(enemyKey);
    const rps = this.getRpsMultipliers(myKey, enemyKey);
    const terrain = this.inferProvinceTerrain(prov);
    const tBonus = this.getTerrainDealtBonus(myKey, prov);
    const outcomeLabel = rps.outcome === 'advantage' ? '有利' : rps.outcome === 'disadvantage' ? '不利' : '互角';
    const color = rps.outcome === 'advantage' ? '#7dffa0' : rps.outcome === 'disadvantage' ? '#ff9a9a' : '#ffe9a8';
    return {
      html: `陣形: 我【${mine.name}】vs 敵【${enemy.name}】→ <strong style="color:${color}">${outcomeLabel}</strong>（与ダメ×${rps.dealt.toFixed(2)} / 被ダメ×${rps.taken.toFixed(2)}）｜地形:${terrain.label}（自陣×${tBonus.toFixed(2)}）`,
      rps, terrain, tBonus
    };
  },

  refreshDeployFormationIntel() {
    const box = document.getElementById('formationIntelBox');
    const hint = document.getElementById('formationMatchupHint');
    const dstSelect = document.getElementById('deployDstSelect');
    if (!box) return;
    const target = this.provinces.find(x => x.id === dstSelect?.value);
    if (!target || !target.ownerId) {
      box.textContent = '軍師の読み：空白地・無主地のため陣形予測は不要です';
      if (hint) hint.textContent = '三すくみ：突撃系 > 包囲系 > 防御系 > 突撃系';
      return;
    }
    if (!this._deployPredictedEnemyForm || this._deployPredictedFor !== target.id) {
      this._deployPredictedEnemyForm = this.pickEnemyFormation(target.ownerId, target, this.selectedFormationKey);
      this._deployPredictedFor = target.id;
    }
    const strat = this.getClanStratagemPower(this.playerClanId, this.selectedProvId);
    const pred = this.predictEnemyFormation(this._deployPredictedEnemyForm, strat);
    box.textContent = pred.text + `（自軍最高知略 ${strat}）`;
    if (hint) {
      const rps = this.getRpsMultipliers(this.selectedFormationKey, this._deployPredictedEnemyForm);
      const mine = this.getFormationMeta(this.selectedFormationKey);
      const outcome = rps.outcome === 'advantage' ? '有利' : rps.outcome === 'disadvantage' ? '不利' : '互角';
      hint.textContent = `選択中【${mine.name}】vs 予測敵陣 → ${outcome}（与×${rps.dealt.toFixed(2)} / 被×${rps.taken.toFixed(2)}）｜地形補正は開戦地で確定`;
    }
  },

  provinceMatchesSpecialty(prov, rule) {
    if (!prov || !rule) return false;
    const blob = `${prov.specialty || ''} ${prov.culturalNotes || ''} ${prov.castleLore || ''}`;
    return rule.keywords.test(blob);
  },

  clanOwnsSpecialty(clanId, synergyId) {
    const rule = (window.SPECIALTY_SYNERGY || []).find(r => r.id === synergyId);
    if (!rule) return false;
    return (this.provinces || []).some(p => p.ownerId === clanId && this.provinceMatchesSpecialty(p, rule));
  },

  getMilitaryGoldCost(prov) {
    let cost = 50;
    const iron = (window.SPECIALTY_SYNERGY || []).find(r => r.id === 'iron');
    if (iron && (this.provinceMatchesSpecialty(prov, iron) || this.clanOwnsSpecialty(this.playerClanId, 'iron'))) {
      cost = Math.round(cost * (1 - (iron.effects.militaryGoldDiscount || 0.2)));
    }
    return Math.max(30, cost);
  },

  getAutumnRiceMultiplier(prov) {
    const rice = (window.SPECIALTY_SYNERGY || []).find(r => r.id === 'rice');
    if (rice && this.provinceMatchesSpecialty(prov, rice)) {
      return 1 + (rice.effects.autumnRiceBonus || 0.2);
    }
    return 1;
  },

  setMapHeatMode(mode) {
    const valid = ['owner', 'diplomacy', 'troops', 'rice'];
    this.mapHeatMode = valid.includes(mode) ? mode : 'owner';
    if (this.mapHeatMode === 'diplomacy' && !this.mapPerspectiveClanId) {
      this.mapPerspectiveClanId = this.playerClanId;
    }
    document.querySelectorAll('#mapHeatFilter .map-heat-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.heat === this.mapHeatMode);
    });
    this.updateUI({ panel: false });
  },

  getHeatPerspectiveClanId() {
    return this.mapPerspectiveClanId || this.playerClanId;
  },

  getHeatRange(key) {
    let min = Infinity, max = -Infinity;
    (this.provinces || []).forEach(p => {
      let v = 0;
      if (key === 'troops') v = Number(p.troops) || 0;
      else if (key === 'rice') v = Number(p.rice || p.kokudaka) || 0;
      else v = Number(p[key]) || 0;
      if (v < min) min = v;
      if (v > max) max = v;
    });
    if (!Number.isFinite(min)) { min = 0; max = 1; }
    if (max <= min) max = min + 1;
    return { min, max };
  },

  // ヒートマップの配色（暗い地図に映える 4 段階ランプ）。兵力は深い藍→翠→水色、石高は焦茶→金→淡金,

  heatRampStops(mode) {
    return mode === 'rice'
      ? ['#1c1408', '#6b4e12', '#c9a227', '#ffe9a0']
      : ['#0e2233', '#135e72', '#1abc9c', '#7fdbff'];
  },

  heatRampColor(t, mode) {
    const stops = this.heatRampStops(mode).map(h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)));
    // 少ない国どうしの差も見えるよう、低い側をやや持ち上げる
    const x = Math.pow(Math.max(0, Math.min(1, Number(t) || 0)), 0.8) * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(x));
    const f = x - i;
    const rgb = stops[i].map((v, k) => Math.round(v + (stops[i + 1][k] - v) * f));
    return `#${rgb.map(v => v.toString(16).padStart(2, '0')).join('')}`;
  },

  heatRampCss(mode) {
    return `linear-gradient(90deg, ${this.heatRampStops(mode).join(', ')})`;
  },

  // 互換用（旧名）。兵力ランプを返す,

  cyanHeatColor(t) {
    return this.heatRampColor(t, 'troops');
  },

  getDiplomacyProvinceColor(p) {
    const perspective = this.getHeatPerspectiveClanId();
    if (!p.ownerId) return '#4a4a4a';
    if (p.ownerId === perspective) {
      return this.brightenHexColor(this.getRegisteredProvinceColor(p), 25);
    }
    if (this.isAllied(perspective, p.ownerId)) return '#2f6fb5';
    const borders = (p.neighbors || []).some(nId => {
      const n = this.provinces.find(x => x.id === nId);
      return n && n.ownerId === perspective;
    });
    if (borders) return '#c0392b';
    return '#7f8c8d';
  },

  updateMapHeatLegend() {
    const legend = document.getElementById('mapHeatLegend');
    if (!legend) return;
    const mode = this.mapHeatMode || 'owner';
    const sw = (c, t) => `<span><span class="heat-sw" style="background:${c}"></span>${t}</span>`;
    if (mode === 'owner') {
      legend.innerHTML = '<span class="heat-note">各大名家の領国色</span>';
    } else if (mode === 'diplomacy') {
      const pers = this.getHeatPerspectiveClanId();
      const name = this.getClanFamilyName(pers) || '視点大名';
      legend.innerHTML = [
        `<span class="heat-note">視点:${name}</span>`,
        sw(this.brightenHexColor(this.getRegisteredProvinceColor({ ownerId: pers }) || '#d4af37', 25), '自勢力'),
        sw('#2f6fb5', '同盟'),
        sw('#7f8c8d', '中立'),
        sw('#c0392b', '敵対'),
        sw('#4a4a4a', '空白')
      ].join('');
    } else {
      const key = mode === 'rice' ? 'rice' : 'troops';
      const { min, max } = this.getHeatRange(key);
      const unit = key === 'rice' ? '石' : '人';
      legend.innerHTML = `<span class="heat-num heat-num-${key}">${min.toLocaleString()}${unit}</span><span class="heat-grad heat-grad-${key}" style="background:${this.heatRampCss(key)}"></span><span class="heat-num heat-num-${key}">${max.toLocaleString()}${unit}</span>`;
    }
  },

  getProvinceColor(p) {
    const mode = this.mapHeatMode || 'owner';
    if (mode === 'diplomacy') return this.getDiplomacyProvinceColor(p);
    if (mode === 'troops' || mode === 'rice') {
      if (!this._heatRangeCache || this._heatRangeCache.mode !== mode) {
        this._heatRangeCache = { mode, ...this.getHeatRange(mode) };
      }
      const { min, max } = this._heatRangeCache;
      const v = mode === 'troops' ? (Number(p.troops) || 0) : (Number(p.rice || p.kokudaka) || 0);
      return this.heatRampColor(max > min ? (v - min) / (max - min) : 0.5, mode);
    }
    if (!p.ownerId) {
      return '#3b322a'; // 空白地：落ち着いた無所属カラー
    }
    return this.getRegisteredProvinceColor(p);
  },

  // シナリオまたは大名家マスターに登録された、その大名固有の領国色,

  getRegisteredProvinceColor(p) {
    if (!p || !p.ownerId) return '#3b322a';
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === p.ownerId);
    if (playable && playable.color) return playable.color;

    const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[p.ownerId];
    if (master && master.color) return master.color;
    return '#5a4638';
  },

  getClanKamonId(clanId) {
    if (!clanId || clanId === 'null' || clanId === 'ronin') return 'kamon-default';

    // 勢力IDエイリアスの正規化
    if (clanId === 'anesanokoji' || clanId === 'anesakoji') clanId = 'anekoji';
    if (clanId === 'hattori') clanId = 'momochi';
    if (clanId === 'saika') clanId = 'suzuki';

    let candidate = null;
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    if (playable && playable.kamonSvgId && playable.kamonSvgId !== 'kamon-default') {
      candidate = playable.kamonSvgId.replace(/^#/, '');
    }

    if (!candidate) {
      const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[clanId];
      if (master && master.kamon) {
        candidate = master.kamon.replace(/^#/, '');
      } else {
        candidate = `kamon-${clanId}`;
      }
    }

    // 大名固有の家紋IDが特定できていればそれを最優先で返す
    // (非同期初期化やSVG外部シンボル参照環境でも各大名の家紋IDを確実に維持)
    if (candidate) {
      return candidate;
    }
    return 'kamon-default';
  },

  // 指定した領国に滞在している武将（城主・居城当主・本拠地待機家臣・浪人）を取得,

  getOfficersInProvince(provId) {
    const p = (this.provinces || []).find(x => x.id === provId);
    if (!p) return [];

    const activeList = (this.activeOfficers || this.officers || []).filter(o => !o.isDead);
    const result = [];
    const addedIds = new Set();

    const addOfficer = (off, roleCategory) => {
      if (!off || addedIds.has(off.id)) return;
      addedIds.add(off.id);
      result.push({
        officer: off,
        roleCategory: roleCategory // 'daimyo', 'governor', 'vassal', 'ronin'
      });
    };

    // 1. 城主 (governorId または assignedProvId)
    if (p.governorId) {
      const gov = activeList.find(o => o.id === p.governorId);
      if (gov) {
        addOfficer(gov, gov.isDaimyo ? 'daimyo' : 'governor');
      }
    }
    activeList.forEach(o => {
      if (o.assignedProvId === p.id) {
        const isGov = (p.governorId === o.id);
        addOfficer(o, o.isDaimyo ? 'daimyo' : (isGov ? 'governor' : 'vassal'));
      }
    });

    // 2. 本拠地・支城の待機家臣：
    // - 当該領国に滞在している待機家臣（拠点領国がこの国と一致）
    // - または本拠地の場合は、特定の支城に配属されていない一般待機家臣
    if (p.ownerId) {
      const isCapital = this.isCapitalProvince(p.id, p.ownerId);
      activeList.forEach(o => {
        if (o.clanId === p.ownerId) {
          if (o.isDaimyo) {
            if (!o.assignedProvId) {
              const home = this.getDaimyoHomeProvince(o);
              if ((home && home.id === p.id) || isCapital) {
                addOfficer(o, 'daimyo');
              }
            }
          } else if (!o.assignedProvId && (!p.governorId || p.governorId !== o.id)) {
            const baseProvId = this.officerBaseProvinceId(o);
            if (baseProvId === p.id) {
              addOfficer(o, 'vassal');
            } else if (!baseProvId && isCapital) {
              addOfficer(o, 'vassal');
            }
          }
        }
      });
    }

    // 3. この国に滞在している浪人 (defaultProv === p.id)
    activeList.forEach(o => {
      if (o.clanId === 'ronin' && o.defaultProv === p.id) {
        addOfficer(o, 'ronin');
      }
    });

    // 優先順ソート：当主(0) -> 城主(1) -> 家臣(2) -> 浪人(3)、同格なら武勇降順
    const rolePriority = { daimyo: 0, governor: 1, vassal: 2, ronin: 3 };
    result.sort((a, b) => {
      const pDiff = (rolePriority[a.roleCategory] ?? 99) - (rolePriority[b.roleCategory] ?? 99);
      if (pDiff !== 0) return pDiff;
      return (b.officer.military || 0) - (a.officer.military || 0);
    });

    return result.map(item => item.officer);
  },

  // 特定の領国に滞在している武将一覧モーダルを開く,

  isProvinceFrontier(p) {
    if (p.ownerId !== this.playerClanId) return false;
    return (p.neighbors || []).some(nId => {
      const neighbor = this.provinces.find(x => x.id === nId);
      return neighbor && neighbor.ownerId !== this.playerClanId;
    });
  },

  getGovernModeName(mode) {
    const map = {
      direct: '直轄',
      military: '軍事進攻型',
      domestic: '内政型',
      balanced: '均衡型',
      logistics: '兵站輸送型'
    };
    return map[mode] || '直轄';
  },

  getClanDisplayName(clanId) {
    if (!clanId || clanId === 'null' || clanId === 'undefined') return '空白地';
    if (clanId === 'ronin') return '浪人';

    // 1. ユーザー要件: 跡継ぎに大名が切り替わった場合、世継ぎ・新当主の氏名を最優先で返却！
    if (this.playerClanId === clanId && this.playerDaimyo?.name) {
      return this.playerDaimyo.name;
    }
    const currentDaimyo = (this.activeOfficers || this.officers || []).find(o => o.clanId === clanId && o.isDaimyo && !o.isDead);
    if (currentDaimyo && currentDaimyo.name) {
      return currentDaimyo.name;
    }

    // 2. 現在のシナリオのプレイアブル大名に完全一致するものがあればそれを優先
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    if (playable && playable.name) return playable.name;

    // 3. 史実マスターデータから現在年以下の最新年代の当主名を取得
    const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[clanId];
    if (master) {
      if (master.leaders) {
        const curY = Number(this.year || (scen ? scen.year : 0));
        const validYears = Object.keys(master.leaders)
          .map(Number)
          .filter(y => !isNaN(y) && y <= curY)
          .sort((a, b) => b - a);
        if (validYears.length > 0) {
          return master.leaders[String(validYears[0])];
        }
        // 【修正】下の名前がない苗字(family)より前に、フルネーム(leaders.default)を優先
        if (master.leaders.default) return master.leaders.default;
        const allYears = Object.keys(master.leaders)
          .map(Number)
          .filter(y => !isNaN(y))
          .sort((a, b) => Math.abs(a - curY) - Math.abs(b - curY));
        if (allYears.length > 0) {
          return master.leaders[String(allYears[0])];
        }
        if (master.family) return master.family;
      }
      if (master.family) return master.family;
    }
    return clanId;
  },

  getKnownSurnames() {
    if (this._knownSurnames) return this._knownSurnames;
    const set = new Set([
      '長宗我部', '宇喜多', '龍造寺', '竜造寺', '宇都宮', '西園寺', '小笠原', '佐々木',
      '小早川', '佐渡本間', '北畠', '六角', '一色', '山名', '大内', '最上'
    ]);
    const master = window.CLAN_MASTER_DATA || CLAN_MASTER || {};
    Object.values(master).forEach(m => {
      if (!m || !m.family) return;
      const stem = String(m.family).replace(/(将軍家|幕府|政府|衆|党|家)$/, '');
      if (stem && stem.length >= 2 && stem.length <= 5) set.add(stem);
    });
    this._knownSurnames = [...set].sort((a, b) => b.length - a.length);
    return this._knownSurnames;
  },

  // 当主名（氏名）から名字・家名を動的算出,

  extractFamilyNameFromLeader(fullName) {
    if (!fullName || fullName === '空白地' || fullName === '無所属' || fullName === '浪人') return fullName || '武家';
    for (const special of ['天皇', '上皇', '朝廷', '幕府', '政府', '首長']) {
      if (fullName.includes(special)) return fullName;
    }
    for (const surname of this.getKnownSurnames()) {
      if (fullName.startsWith(surname) && fullName.length > surname.length) return `${surname}家`;
    }
    if (fullName.length === 3) return `${fullName[0]}家`;
    if (fullName.length >= 4) return `${fullName.slice(0, 2)}家`;
    return `${fullName}家`;
  },

  getLivingDaimyoName(clanId) {
    const living = (this.activeOfficers || this.officers || []).find(o => o.clanId === clanId && o.isDaimyo && !o.isDead);
    if (living?.name) return living.name;
    if (this.playerClanId === clanId && this.playerDaimyo?.name) return this.playerDaimyo.name;
    return '';
  },

  familyStemOf(familyLabel) {
    if (!familyLabel) return '';
    return String(familyLabel).replace(/(将軍家|幕府|政府|衆|党|家)$/, '');
  },

  // その勢力の史実当主名簿（初期当主・年代別当主）に名があるか,

  isClanRosterLeader(clanId, name) {
    if (!name || !clanId) return false;
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    if (playable && this.leaderNamesMatch(playable.name, name)) return true;
    const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[clanId];
    if (!master?.leaders) return false;
    return Object.values(master.leaders).some(n => typeof n === 'string' && this.leaderNamesMatch(n, name));
  },

  getClanFamilyName(clanId) {
    if (!clanId || clanId === 'null' || clanId === 'undefined') return '空白地';
    if (clanId === 'ronin') return '浪人';
    if (clanId === 'anesanokoji' || clanId === 'anesakoji') clanId = 'anekoji';
    if (clanId === 'hattori') clanId = 'momochi';
    if (clanId === 'saika') clanId = 'suzuki';

    let currentLeaderName = this.getLivingDaimyoName(clanId);
    if (!currentLeaderName && this.lastDaimyoNames?.[clanId]) {
      currentLeaderName = this.lastDaimyoNames[clanId];
    }
    const foundingName = this.foundingLeaderNames?.[clanId];
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[clanId];
    const canonical = (playable && playable.clan) || master?.family || '';

    if (currentLeaderName) {
      const sur = this.extractPersonSurname(currentLeaderName);
      const extracted = sur ? `${sur}家` : this.extractFamilyNameFromLeader(currentLeaderName);
      const stem = this.familyStemOf(canonical);
      const surGroup = this.surnameGroup(sur);
      const sameHouse = !!(stem && (currentLeaderName.startsWith(stem) || surGroup.includes(stem) || this.surnameGroup(stem).includes(sur)));
      const originalPerson = foundingName
        ? this.leaderNamesMatch(currentLeaderName, foundingName)
        : this.isClanRosterLeader(clanId, currentLeaderName);

      // 史実名簿（CLAN_MASTER_DATA.leaders）に載る後継者や、朝廷・在庁などの家名でない勢力名は、代替わりしても勢力名を保つ
      if (canonical && !originalPerson) {
        const rosterHeir = this.isClanRosterLeader(clanId, currentLeaderName);
        const institutional = /(朝廷|幕府|在庁|豪族|部族|上皇方|天皇方|院方)$/.test(canonical);
        if (rosterHeir || institutional) return canonical;
      }
      // 開幕時の当主は登録された家名を保つ。別家が継いだときだけ、その当主の名字を家名にする。
      if (!originalPerson && sur && stem && sur !== stem && surGroup.includes(stem)) return extracted;
      if (!originalPerson && !sameHouse) return extracted;
      if (canonical) return canonical;
      return extracted;
    }

    if (canonical) return canonical;
    const dName = this.getClanDisplayName(clanId);
    if (!dName || dName === '空白地' || dName === '無所属') return '空白地';
    return this.extractFamilyNameFromLeader(dName);
  },

  applyBatchGovernance(mode) {
    const checkboxes = document.querySelectorAll('.govern-select-cb:checked');
    if (checkboxes.length === 0) {
      Swal.fire({ icon: 'warning', title: '領国を選択してください', text: '一覧のチェックボックスで対象の領国を選択してください。', background: '#241710', color: '#fff' });
      return;
    }
    let count = 0;
    checkboxes.forEach(cb => {
      const p = this.provinces.find(x => x.id === cb.dataset.provId);
      if (p) {
        p.governance = mode;
        count++;
      }
    });
    this.renderGovernTable();
    this.audio.playHyoshigi();
    this.log(`【一括委任】${count}カ国の領国を「${this.getGovernModeName(mode)}」に一括設定しました。`, 'important');
  },

  applyPresetGovernance(presetType) {
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    let count = 0;

    myProvs.forEach(p => {
      const isFrontier = this.isProvinceFrontier(p);
      if (presetType === 'rear_domestic' && !isFrontier) {
        p.governance = 'domestic';
        count++;
      } else if (presetType === 'rear_logistics' && !isFrontier) {
        p.governance = 'logistics';
        count++;
      } else if (presetType === 'front_military' && isFrontier) {
        p.governance = 'military';
        count++;
      } else if (presetType === 'all_direct') {
        p.governance = 'direct';
        count++;
      }
    });

    this.renderGovernTable();
    this.audio.playHyoshigi();
    const names = {
      rear_domestic: '後方領地を全て【内政型】委任',
      rear_logistics: '後方領地を全て【兵站輸送型】委任',
      front_military: '前線国境領地を全て【軍事進攻型】委任（自律攻略）',
      all_direct: '全領国を【直轄】指揮'
    };
    this.log(`【方針一括適用】${names[presetType]} (${count}カ国) を実施しました。`, 'important');
    this.showOrderResult('📋 委任方針 適用', `${names[presetType]} (${count}カ国)`, '#ffd700');
  },

  // ============================================================================
  // 軍令結果通知 (心得たボタン不要・結果が1秒で流れて自動消去)
  // ============================================================================,

  showOrderResult(title, message, accentColor = '#ffd700') {
    let toast = document.getElementById('orderResultToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'orderResultToast';
      toast.className = 'order-result-toast';
      document.body.appendChild(toast);
    }

    if (this._toastTimer) {
      clearTimeout(this._toastTimer);
      this._toastTimer = null;
    }

    toast.innerHTML = `
      <strong style="color:${accentColor}; font-size:12pt; white-space:nowrap;">${title}</strong>
      <span style="color:#eee; font-size: 12pt; border-left:1px solid #665544; padding-left:10px;">${message}</span>
    `;
    toast.style.borderColor = accentColor;

    toast.classList.remove('hide');
    toast.classList.add('show');

    // ちょうど1秒(1000ms)で流れて自動終了
    this._toastTimer = setTimeout(() => {
      toast.classList.remove('show');
      toast.classList.add('hide');
    }, 1000);
  },

  // ============================================================================
  // 厳選4大コマンド処理 (出陣、内政、軍備、調略)
  // ============================================================================,

  executeDomestic() {
    let p = this.provinces.find(x => x.id === this.selectedProvId);
    if (!p || p.ownerId !== this.playerClanId) {
      const myProvs = this.provinces.filter(x => x.ownerId === this.playerClanId);
      if (myProvs.length === 0) {
        this.showOrderResult('⚠ 御家滅亡', '貴家の支配領国が存在しません', '#e74c3c');
        return;
      }
      p = myProvs[0];
      this.selectProvince(p.id);
    }
    if (this.ap <= 0) {
      this.showOrderResult('⚠ 行動力不足', '今季の行動力(AP)を使い果たしました。「次季へ進む」を押してください。', '#e67e22');
      return;
    }
    if (this.gold < 40) {
      this.showOrderResult('⚠ 資金不足', `内政振興には金40貫が必要です (現在:${this.gold}貫)`, '#e74c3c');
      return;
    }

    const effStats = this.getEffectiveStats(p.id);
    // 城主武将の政治力（城主不在の直轄地は大名能力半減ペナルティ発動）による明確な成果差
    const polRatio = (effStats.politics || 50) / 100;
    const riceGain = Math.round(15 + polRatio * 25);       // 22〜40石
    const commerceGain = Math.round(15 + polRatio * 25);   // 22〜40貫
    const orderGain = Math.round(3 + polRatio * 6);         // 4〜9%

    // 【フェーズ2: 内政コマンドによる無限インフレの抑制】
    // 初期マスターデータ (INITIAL_PROVINCES) の石高を基準とした上限キャップ（初期値の3倍）
    const initMaster = (INITIAL_PROVINCES || window.PROVINCES_DATA || []).find(x => x.id === p.id);
    const baseKokudaka = Number(initMaster?.kokudaka) || 50000;
    const baseRice = Math.max(20, Math.round(baseKokudaka / 1000));
    const baseCommerce = Math.max(10, Math.round(baseKokudaka / 2000));
    const maxRice = baseRice * 3;
    const maxCommerce = baseCommerce * 3;

    this.gold -= 40;
    this.ap -= 1;
    p.rice = Math.min(maxRice, p.rice + riceGain);
    p.commerce = Math.min(maxCommerce, p.commerce + commerceGain);
    p.order = Math.min(100, (p.order || 80) + orderGain);

    try { this.audio.playCoin?.(); } catch(e) {}
    const govTag = effStats.isDirectRule ? '【⚠️直轄領・大名能力半減】' : `【城主: ${effStats.name}】`;
    const polDesc = effStats.politics >= 85 ? '【名君の仁政】' : effStats.politics <= 50 ? '【拙劣な民政】' : '【内政振興】';
    this.log(`${govTag}${polDesc}${p.name}にて新田開墾・商業振興を推進！(実効内政:${effStats.politics}) 石高+${riceGain}, 商業+${commerceGain}, 治安+${orderGain}%。`);
    this.showOrderResult('🌾 内政振興 完了', `${p.name} 石高+${riceGain} (${p.rice}石) ｜ 商業+${commerceGain} (${p.commerce}貫) ｜ 治安+${orderGain}%`, '#2ecc71');
    this.updateUI({ provId: p.id });
  },

  executeMilitary() {
    let p = this.provinces.find(x => x.id === this.selectedProvId);
    if (!p || p.ownerId !== this.playerClanId) {
      const myProvs = this.provinces.filter(x => x.ownerId === this.playerClanId);
      if (myProvs.length === 0) {
        this.showOrderResult('⚠ 御家滅亡', '貴家の支配領国が存在しません', '#e74c3c');
        return;
      }
      p = myProvs[0];
      this.selectProvince(p.id);
    }
    if (this.ap <= 0) {
      this.showOrderResult('⚠ 行動力不足', '今季の行動力(AP)を使い果たしました。「次季へ進む」を押してください。', '#e67e22');
      return;
    }
    const milGoldCost = this.getMilitaryGoldCost(p);
    if (this.gold < milGoldCost) {
      this.showOrderResult('⚠ 資金不足', `軍備増強には金${milGoldCost}貫が必要です (現在:${this.gold}貫)`, '#e74c3c');
      return;
    }

    const effStats = this.getEffectiveStats(p.id);
    // 石高に基づく兵力上限（石高×12 + 2500）でインフレを防止
    const maxTroops = p.rice * 12 + 2500;
    const milRatio = (effStats.military || 50) / 100;

    let troopsGain = 0;
    let note = '';
    if (p.troops >= maxTroops) {
      troopsGain = 0;
      note = ' (石高扶養上限に達しており兵力増員なし、城防と士気を集中的に強化)';
    } else {
      // 城主武将の軍事力（城主不在の直轄地は大名能力半減ペナルティ発動）と石高に応じた徴兵数
      const potential = Math.round(150 + milRatio * 180 + (p.rice * 0.08));
      troopsGain = Math.min(potential, maxTroops - p.troops);
    }

    const defenseGain = Math.round(5 + milRatio * 6); // 6〜11
    const moraleGain = Math.round(6 + milRatio * 7);  // 8〜13

    this.gold -= milGoldCost;
    this.ap -= 1;
    p.troops += troopsGain;
    p.defense = Math.min(100, p.defense + defenseGain);
    p.morale = Math.min(100, p.morale + moraleGain);
    // 徴兵による治安度への微小な影響
    if (troopsGain > 0) {
      const orderPenalty = Math.max(1, Math.round(3 - milRatio * 2));
      p.order = Math.max(30, (p.order || 80) - orderPenalty);
    }

    try { this.audio.playTaiko?.(); } catch(e) {}
    const govTag = effStats.isDirectRule ? '【⚠️直轄領・大名能力半減】' : `【城主: ${effStats.name}】`;
    const milDesc = effStats.military >= 88 ? '【名将の練兵】' : '【軍備増強】';
    const ironNote = milGoldCost < 50 ? `（鉄産地シナジー:金${milGoldCost}貫）` : '';
    this.log(`${govTag}${milDesc}${p.name}にて徴兵と城郭修築！(実効軍事:${effStats.military}) 兵力+${troopsGain.toLocaleString()}, 城防+${defenseGain}, 士気+${moraleGain}。${note}${ironNote}`);
    this.showOrderResult('⚔️ 軍備増強 完了', `${p.name} 兵力+${troopsGain} (${p.troops.toLocaleString()}/${maxTroops.toLocaleString()}) ｜ 城防+${defenseGain} ｜ 士気+${moraleGain}`, '#e74c3c');
    this.updateUI({ provId: p.id });
  },

  executeStratagem() {
    let p = this.provinces.find(x => x.id === this.selectedProvId);
    let target = null;

    if (p && p.ownerId !== this.playerClanId) {
      // 敵国を選択中に調略を押した場合：その敵国に工作を仕掛ける
      target = p;
      const friendlyNeighbor = (p.neighbors || []).map(nId => this.provinces.find(x => x.id === nId)).find(x => x && x.ownerId === this.playerClanId);
      if (!friendlyNeighbor) {
        this.showOrderResult('⚠ 調略不可', `${target.name}は貴家の領国と隣接していないため、忍びを潜入させられません。`, '#e74c3c');
        return;
      }
      p = friendlyNeighbor;
    } else {
      if (!p || p.ownerId !== this.playerClanId) {
        const myProvs = this.provinces.filter(x => x.ownerId === this.playerClanId);
        if (myProvs.length > 0) {
          p = myProvs[0];
          this.selectProvince(p.id);
        }
      }
      if (!p) {
        this.showOrderResult('⚠ 調略不可', '工作を発令する自領国を選択してください。', '#e74c3c');
        return;
      }
      const enemyNeighbors = (p.neighbors || []).map(nId => this.provinces.find(x => x.id === nId)).filter(x => x && x.ownerId !== this.playerClanId);
      if (enemyNeighbors.length === 0) {
        this.showOrderResult('⚠ 調略不可', `${p.name}の隣接領国に敵対勢力がいません。前線領国を選択してください。`, '#e74c3c');
        return;
      }
      target = enemyNeighbors.sort((a, b) => b.troops - a.troops)[0];
    }

    if (this.ap <= 0) {
      this.showOrderResult('⚠ 行動力不足', '今季の行動力(AP)を使い果たしました。「次季へ進む」を押してください。', '#e67e22');
      return;
    }
    if (this.gold < 40) {
      this.showOrderResult('⚠ 資金不足', `敵国調略には金40貫が必要です (現在:${this.gold}貫)`, '#e74c3c');
      return;
    }

    const srcEff = this.getEffectiveStats(p.id);
    const targetEff = this.getEffectiveStats(target.id);

    // 調略成功判定：城主（または直轄地）の知謀差による判定
    const diff = (srcEff.stratagem || 50) - (targetEff.stratagem || 50);
    const successRate = Math.max(0.35, Math.min(0.95, 0.70 + diff * 0.005));
    const isSuccess = Math.random() < successRate;

    this.gold -= 40;
    this.ap -= 1;

    if (isSuccess) {
      const stratRatio = (srcEff.stratagem || 50) / 100;
      const moraleReduction = Math.round(14 + stratRatio * 20); // 20〜34
      const defenseReduction = Math.round(8 + stratRatio * 15);  // 12〜23

      target.morale = Math.max(15, target.morale - moraleReduction);
      target.defense = Math.max(10, target.defense - defenseReduction);

      let extraMsg = '';
      // 知謀85以上の知将は兵員離反・内応を誘発！
      if (srcEff.stratagem >= 85 && Math.random() < 0.65) {
        const betrayTroops = Math.min(Math.round(target.troops * 0.10), 500);
        target.troops -= betrayTroops;
        extraMsg = ` さらに敵将の内応を誘発し兵員${betrayTroops.toLocaleString()}人が離反脱走！`;
      }

      try { this.audio.playSlash?.(); } catch(e) {}
      const govTag = srcEff.isDirectRule ? '【⚠️直轄・能力半減発令】' : `【城主: ${srcEff.name}発令】`;
      this.log(`${govTag}【敵国調略・成功】${target.name}へ忍者衆を放ち放火・流言工作！(発令知謀:${srcEff.stratagem} vs 防備知謀:${targetEff.stratagem}) 敵士気-${moraleReduction}, 城防-${defenseReduction}。${extraMsg}`, 'important');
      this.showOrderResult('🗡️ 敵国調略 成功！', `${target.name} 敵士気-${moraleReduction} ｜ 城防-${defenseReduction}${extraMsg}`, '#9b59b6');
    } else {
      try { this.audio.playHyoshigi?.(); } catch(e) {}
      this.log(`【敵国調略・失敗】${target.name}への忍びの侵入は敵警戒網に阻まれました。(敵防備知謀:${targetEff.stratagem})`, 'important');
      this.showOrderResult('⚠ 調略 失敗', `${target.name}の警戒が厳しく工作は阻止されました`, '#888');
    }

    this.updateUI({ provId: p.id });
  },

  // 兵力移動モーダル,

  confirmTransfer() {
    const p = this.provinces.find(x => x.id === this.selectedProvId);
    const dstSelect = document.getElementById('transferDstSelect');
    const range = document.getElementById('transferTroopRange');
    const target = this.provinces.find(x => x.id === dstSelect?.value);
    const amount = parseInt(range?.value, 10) || 0;

    if (!p || !target || amount <= 0 || p.troops - amount < 500) return;

    p.troops -= amount;
    target.troops += amount;

    document.getElementById('transferModal')?.classList.add('hidden');
    this.audio.playTaiko();
    this.log(`【前線兵力移動】${p.name}から${target.name}へ兵力 ${amount.toLocaleString()} 人を配置転換しました。`);
    this.showOrderResult('🚚 兵力移動 完了', `${p.name} から ${target.name} へ兵力 ${amount.toLocaleString()}人 移動`, '#3498db');
    this.updateUI({ provId: p.id });
  },

  // ============================================================================
  // 出陣侵攻 ＆ 野戦合戦 ＆ 攻城戦 (完全連動)
  // ============================================================================
  // ============================================================================
  // 出陣侵攻 ＆ 野戦合戦 ＆ 攻城戦 (完全連動)
  // ============================================================================,

  confirmDeploy() {
    const p = this.provinces.find(x => x.id === this.selectedProvId);
    const dstSelect = document.getElementById('deployDstSelect');
    const range = document.getElementById('deployTroopRange');
    const target = this.provinces.find(x => x.id === dstSelect?.value);
    const troopCount = parseInt(range?.value, 10) || 1000;
    // 出陣規模に応じた兵糧消費（兵100人につき約8石）
    const riceCost = Math.round(troopCount * 0.08);

    if (!p || !target || this.rice < riceCost || this.ap <= 0) {
      this.showOrderResult('⚠ 出陣不能', '兵糧または軍令権(AP)が不足しています。', '#e74c3c');
      return;
    }

    this.rice -= riceCost;
    this.ap -= 1;
    p.troops -= troopCount;

    document.getElementById('deployModal')?.classList.add('hidden');

    // ユーザー要件: 「空白地となったエリアは侵攻しても戦争せずに領地取得できるようにする」
    if (!target.ownerId) {
      target.ownerId = this.playerClanId;
      target.troops = (target.troops || 0) + troopCount;
      target.defense = Math.max(50, target.defense || 50);
      target.morale = 80;
      target.governorId = null;
      target.governance = 'military';
      target.justConquered = true;

      try {
        this.audio.playTaiko?.(1.4);
        this.audio.playFanfare?.();
        this.music.playTrack(this.getSeasonTrackKey());
      } catch(e) {}

      if (window.Swal) {
        Swal.fire({
          title: `❖ 空白地 接収完了 ❖`,
          html: `
            <div style="text-align:center; padding:10px; font-family:'Noto Serif JP',serif;">
              <p style="font-size:14pt; color:#ffd700; margin-bottom:12px;"><strong>【${target.name}（${target.castleName || target.castle || '城'}）無血領有！】</strong></p>
              <p style="font-size:11.5pt; color:#f5eedc; line-height:1.6;">
                領主不在の空白地であった【${target.name}】へ兵${troopCount.toLocaleString()}人を率いて進駐し、<br>
                戦火を交えることなく我が軍の支配下に組み入れました！
              </p>
            </div>
          `,
          background: '#1c130d',
          color: '#f5eedc',
          confirmButtonText: '善き哉！',
          confirmButtonColor: '#922b21'
        }).then(() => {
          this.updateUI({ provId: target.id });
        });
      }

      this.log(`🏯【無血占領】領主不在の空白地【${target.name}】に兵${troopCount.toLocaleString()}人を進駐させ、戦争を経ずに無血で領有いたしました！`, 'important');
      this.appointHistoricalHomeGovernors(this.playerClanId);
      this.updateUI({ provId: target.id });
      return;
    }

    // 攻め込んだ時の勇壮な効果音！（法螺貝 ＋ 轟く陣太鼓）
    try {
      this.audio.playHoragai?.(1.0);
      setTimeout(() => {
        try { this.audio.playTaiko?.(1.4); } catch(e) {}
      }, 280);
    } catch(e) {}

    // 場面BGM: 合戦BGMへ（大軍勢激突なら決戦・修羅の道）
    try {
      const isLarge = (troopCount + (target.troops || 0)) >= 6000;
      this.music.playTrack(isLarge ? 'battle_intense' : 'battle');
    } catch(e) {}

    this.startFieldBattle(p, target, troopCount);
  },

  startFieldBattle(srcProv, dstProv, playerTroops) {
    this.inBattle = true;
    let enemyFieldTroops = Math.max(300, Math.round(dstProv.troops * 0.6)); // 6割が野戦迎撃に出陣

    // 【フェーズ2: 同盟援軍システム】
    // 防衛側の領国に隣接する「防衛側の同盟国」の領国がある場合、その同盟国の兵力の30%を援軍として加算
    let reinforceTotal = 0;
    const reinforceMsgs = [];
    (dstProv.neighbors || []).forEach(nId => {
      const neighbor = this.provinces.find(x => x.id === nId);
      if (neighbor && neighbor.ownerId && this.isAllied(dstProv.ownerId, neighbor.ownerId)) {
        const rf = Math.round(neighbor.troops * 0.30);
        if (rf > 0) {
          reinforceTotal += rf;
          reinforceMsgs.push(`${this.getClanFamilyName(neighbor.ownerId)}（${neighbor.name}領国より援軍 ${rf.toLocaleString()}人）`);
        }
      }
    });
    enemyFieldTroops += reinforceTotal;

    const playerFormKey = this.selectedFormationKey || 'gyorin';
    let enemyFormKey = (this._deployPredictedFor === dstProv.id && this._deployPredictedEnemyForm)
      ? this._deployPredictedEnemyForm
      : this.pickEnemyFormation(dstProv.ownerId, dstProv, playerFormKey);
    this._deployPredictedEnemyForm = null;
    this._deployPredictedFor = null;

    this.currentBattle = {
      srcProv,
      dstProv,
      playerMax: playerTroops,
      playerTroops: playerTroops,
      playerMorale: 90,
      enemyMax: enemyFieldTroops,
      enemyTroops: enemyFieldTroops,
      enemyMorale: dstProv.morale || 80,
      turn: 1,
      isActionProcessing: false,
      playerFormationKey: playerFormKey,
      enemyFormationKey: enemyFormKey
    };

    const bModal = document.getElementById('battleModal');
    if (bModal) {
      document.getElementById('battleTitle').textContent = `⚔️ ${dstProv.name}の野戦決戦 (${srcProv.name}進軍)`;
      document.getElementById('playerArmyClan').textContent = `${this.playerDaimyo.clan} (我が軍)`;
      document.getElementById('playerGeneralName').textContent = `総大将: ${this.playerDaimyo.name}`;
      document.getElementById('enemyArmyClan').textContent = `${this.getClanFamilyName(dstProv.ownerId)}軍`;
      document.getElementById('enemyGeneralName').textContent = `総大将: ${this.getClanDisplayName(dstProv.ownerId)}`;

      const pForm = this.getFormationMeta(playerFormKey);
      const eForm = this.getFormationMeta(enemyFormKey);
      const pLabel = document.getElementById('playerFormationLabel');
      const eLabel = document.getElementById('enemyFormationLabel');
      if (pLabel) pLabel.textContent = `陣形: ${pForm.name}`;
      const strat = this.getClanStratagemPower(this.playerClanId, srcProv.id);
      const pred = this.predictEnemyFormation(enemyFormKey, strat);
      if (eLabel) {
        if (pred.level === 'unknown') eLabel.textContent = '陣形: 不明';
        else if (pred.level === 'category') eLabel.textContent = `陣形: ${pred.displayName}？`;
        else eLabel.textContent = `陣形: ${eForm.name}（看破${pred.confidence}%）`;
      }
      const bonusEl = document.getElementById('battleFormationBonus');
      if (bonusEl) bonusEl.innerHTML = this.describeFormationMatchup(playerFormKey, enemyFormKey, dstProv).html;

      ['bCmdAssault', 'bCmdShoot', 'bCmdDefend', 'bCmdTactic', 'bCmdRetreat'].forEach(id => {
        document.getElementById(id)?.removeAttribute('disabled');
      });

      this.updateBattleUI();
      bModal.classList.remove('hidden');
    }

    try { this.audio.playTaiko?.(1.3); } catch(e) {}
    const openMatch = this.describeFormationMatchup(playerFormKey, enemyFormKey, dstProv);
    this.logBattle(`【野戦開戦】${dstProv.name}（${openMatch.terrain.label}）にて敵軍と激突！ 我が軍:${playerTroops.toLocaleString()}【${this.getFormationMeta(playerFormKey).name}】 vs 敵迎撃軍:${this.currentBattle.enemyTroops.toLocaleString()}【${this.getFormationMeta(enemyFormKey).name}】`);
    if (reinforceTotal > 0) {
      reinforceMsgs.forEach(msg => {
        this.logBattle(`🤝【同盟援軍参戦】${msg}が防衛軍に合流！`);
      });
    }
  },

  updateBattleUI() {
    if (!this.currentBattle) return;
    const b = this.currentBattle;

    const pPct = Math.max(0, Math.min(100, (b.playerTroops / b.playerMax) * 100));
    const ePct = Math.max(0, Math.min(100, (b.enemyTroops / b.enemyMax) * 100));

    document.getElementById('playerArmyBar').style.width = `${pPct}%`;
    document.getElementById('playerArmyTroopsText').textContent = `${b.playerTroops.toLocaleString()} / ${b.playerMax.toLocaleString()}`;
    document.getElementById('playerArmyMorale').textContent = b.playerMorale;

    document.getElementById('enemyArmyBar').style.width = `${ePct}%`;
    document.getElementById('enemyArmyTroopsText').textContent = `${b.enemyTroops.toLocaleString()} / ${b.enemyMax.toLocaleString()}`;
    document.getElementById('enemyArmyMorale').textContent = b.enemyMorale;
  },

  logBattle(msg) {
    const log = document.getElementById('battleLog');
    if (log) {
      log.innerHTML = `<div>${msg}</div>` + log.innerHTML;
    }
  },

  handleBattleAction(actionType) {
    if (!this.currentBattle) return;
    const b = this.currentBattle;
    if (b.isActionProcessing) return;

    const ability = getClanAbility(this.playerClanId);
    const milBonus = (ability.military || 70) / 70; // 0.6〜1.4

    // 合戦中の兵糧消費（兵力に応じた兵站米消費：1ターンあたり8〜25石）
    const battleRiceCost = Math.max(8, Math.round(b.playerTroops * 0.006));
    if (this.rice >= battleRiceCost) {
      this.rice -= battleRiceCost;
    } else {
      b.playerMorale = Math.max(10, b.playerMorale - 15);
      this.logBattle(`⚠【兵糧枯渇】軍糧が尽き、将兵の士気が著しく低下！(士気-15)`);
    }

    let pDamage = 0;
    let eDamage = 0;

    if (actionType === 'assault') {
      // 突撃：ハイリスク・ハイリターンな決死の突入（敵の槍衾・反撃により自損が劇的に増加）
      eDamage = Math.max(180, Math.round((b.playerTroops * 0.28 * milBonus) * (b.playerMorale / 80) + Math.random() * 300));
      pDamage = Math.max(120, Math.round((b.enemyTroops * 0.22) * (b.enemyMorale / 85) + Math.random() * 150));
      b.playerMorale = Math.min(100, b.playerMorale + 5);

      try {
        this.audio.playGachaGacha?.(1.2);
        this.audio.playSword?.();
      } catch(e) {}
      this.logBattle(`⚔️ 我が軍の猛烈な突撃！ 敵に${eDamage.toLocaleString()}の打撃！(自損:${pDamage.toLocaleString()})`);
    } else if (actionType === 'shoot') {
      // 弓・鉄砲斉射：安定ダメージと鉄砲轟音
      eDamage = Math.max(120, Math.round((b.playerTroops * 0.16) + Math.random() * 180));
      pDamage = Math.round(b.enemyTroops * 0.02);

      try {
        this.audio.playTeppo?.();
      } catch(e) {}
      this.logBattle(`🏹 弓砲の一斉射撃！ 敵前衛を削り${eDamage.toLocaleString()}の損害！(自損:${pDamage.toLocaleString()})`);
    } else if (actionType === 'defend') {
      pDamage = Math.round(b.enemyTroops * 0.02);
      eDamage = Math.max(60, Math.round(b.playerTroops * 0.08));
      b.playerMorale = Math.min(100, b.playerMorale + 8);

      try {
        this.audio.playGachaGacha?.(0.9);
        this.audio.playTaiko?.(0.8);
      } catch(e) {}
      this.logBattle(`🛡️ 鉄壁の盾陣で反撃！ 敵に${eDamage.toLocaleString()}打撃！(自損:${pDamage.toLocaleString()})`);
    } else if (actionType === 'tactic') {
      eDamage = Math.max(300, Math.round((b.playerTroops * 0.38) + 400));
      pDamage = Math.round(b.enemyTroops * 0.02);
      b.enemyMorale = Math.max(10, b.enemyMorale - 35);

      try {
        this.audio.playGachaGacha?.(1.3);
        this.audio.playFanfare?.();
      } catch(e) {}
      this.logBattle(`⚡【戦術奥義・${this.playerDaimyo?.tactic || '全軍突撃'}】が炸裂！ 敵陣粉砕・${eDamage.toLocaleString()}の超絶打撃！`);
    } else if (actionType === 'retreat') {
      this.log(`【野戦撤退】我が軍は損害を抑えて${b.srcProv.name}へ撤退しました。`);
      b.srcProv.troops += b.playerTroops;
      this.endBattle();
      return;
    }

    // 陣形三すくみ＋地形補正
    {
      const myForm = b.playerFormationKey || this.selectedFormationKey || 'gyorin';
      const enForm = b.enemyFormationKey || 'kakuyoku';
      const rps = this.getRpsMultipliers(myForm, enForm);
      const myTerrain = this.getTerrainDealtBonus(myForm, b.dstProv);
      const enTerrain = this.getTerrainDealtBonus(enForm, b.dstProv);
      eDamage = Math.max(0, Math.round(eDamage * rps.dealt * myTerrain));
      pDamage = Math.max(0, Math.round(pDamage * rps.taken * enTerrain));
      if (rps.outcome === 'advantage') {
        this.logBattle(`📜【陣形有利】${this.getFormationMeta(myForm).name}が${this.getFormationMeta(enForm).name}を制す！与ダメ強化／被ダメ軽減`);
      } else if (rps.outcome === 'disadvantage') {
        this.logBattle(`⚠【陣形不利】敵の${this.getFormationMeta(enForm).name}に${this.getFormationMeta(myForm).name}が飲まれる！`);
      }
    }

    b.enemyTroops = Math.max(0, b.enemyTroops - eDamage);
    b.playerTroops = Math.max(0, b.playerTroops - pDamage);
    this.updateBattleUI();

    // 戦況に応じた動的オーケストラBGM遷移（劣勢：孤城落日 / 優勢：勝機来たる）
    if (b.enemyTroops > 0 && b.playerTroops > 0) {
      if (b.playerTroops <= b.playerMax * 0.4 || b.playerTroops < b.enemyTroops * 0.45) {
        if (this.music.currentTrack !== 'crisis') {
          try { this.music.playTrack('crisis'); } catch(e) {}
        }
      } else if (b.enemyTroops < b.playerTroops * 0.35) {
        if (this.music.currentTrack !== 'advantage') {
          try { this.music.playTrack('advantage'); } catch(e) {}
        }
      }
    }

    // 勝敗判定
    if (b.enemyTroops <= 0 || b.enemyMorale <= 15) {
      b.isActionProcessing = true;
      try { this.audio.playKachi?.(); } catch(e) {}

      // ボタンを無効化して重複クリックを防止
      ['bCmdAssault', 'bCmdShoot', 'bCmdDefend', 'bCmdTactic', 'bCmdRetreat'].forEach(id => {
        document.getElementById(id)?.setAttribute('disabled', 'true');
      });

      // 敵の城がすでに無防備（城防15以下または城兵200以下）なら即座に完全落城制覇！
      if ((b.dstProv.defense || 0) <= 15 || (b.dstProv.troops || 0) <= 300) {
        this.logBattle(`🎉 敵野戦軍を完全壊滅！ 城郭は無防備となり、我が軍は一気に本丸へ突入・完全制圧しました！`);
        setTimeout(() => {
          this.conquerProvince(b.dstProv, b.playerTroops);
        }, 800);
      } else {
        this.logBattle(`🎉 敵野戦軍を完全壊滅！ 残敵は城内へ敗走！ ただちに城郭包囲・攻城戦へ移行します！`);
        setTimeout(() => this.proceedToSiege(), 800);
      }
    } else if (b.playerTroops <= 0) {
      b.isActionProcessing = true;
      try { this.audio.playHyoshigi?.(); } catch(e) {}
      this.log(`【野戦敗北】我が軍は${b.dstProv.name}の野戦で壊滅しました。`, 'battle');
      setTimeout(() => this.endBattle(), 800);
    }
  },

  // 攻城戦へ移行 (確実に動作する設計),

  proceedToSiege() {
    const b = this.currentBattle;
    if (!b) return;

    document.getElementById('battleModal')?.classList.add('hidden');

    // 場面BGM切り替え: 攻城戦BGMへ！
    try { this.music.playTrack('siege'); } catch(e) {}

    // 城内籠城兵力 (野戦前の残存40% + 壊滅後の落武者)
    const castleGarrison = Math.max(300, Math.round(b.dstProv.troops * 0.4));

    this.currentSiege = {
      dstProv: b.dstProv,
      srcProv: b.srcProv,
      playerMax: b.playerTroops,
      playerTroops: b.playerTroops,
      castleWall: b.dstProv.defense || 60,
      castleWallMax: Math.max(60, b.dstProv.defense || 60),
      enemyTroops: castleGarrison,
      enemyTroopsMax: castleGarrison,
      castleMorale: Math.round(b.dstProv.morale * 0.75) || 70,
      isActionProcessing: false
    };

    const sModal = document.getElementById('siegeModal');
    if (sModal) {
      document.getElementById('siegeCastleName').textContent = `🏯 ${b.dstProv.name} (${b.dstProv.castleName || b.dstProv.castle || "居城"}) 包囲戦`;

      // 攻城戦ボタンのdisabledを全解除
      ['sCmdAssault', 'sCmdShoot', 'sCmdSurround', 'sCmdPersuade', 'sCmdRetreat'].forEach(id => {
        document.getElementById(id)?.removeAttribute('disabled');
      });

      this.updateSiegeUI();
      sModal.classList.remove('hidden');
    }

    this.logSiege(`【城壁包囲】${b.dstProv.castleName || b.dstProv.castle || "居城"}を完全包囲！ 城攻め作戦を選択してください。`);
  },

  updateSiegeUI() {
    if (!this.currentSiege) return;
    const s = this.currentSiege;

    // 自軍包囲兵力
    const pPct = Math.max(0, Math.min(100, (s.playerTroops / s.playerMax) * 100));
    document.getElementById('siegePlayerBar').style.width = `${pPct}%`;
    document.getElementById('siegePlayerTroopsText').textContent = `${s.playerTroops.toLocaleString()} / ${s.playerMax.toLocaleString()}`;
    document.getElementById('siegePlayerTroopsBadge').textContent = `包囲我が軍: ${s.playerTroops.toLocaleString()} 人`;

    // 城壁耐久度
    const wallPct = Math.max(0, Math.min(100, (s.castleWall / s.castleWallMax) * 100));
    document.getElementById('siegeWallBar').style.width = `${wallPct}%`;
    document.getElementById('siegeWallText').textContent = `${s.castleWall} / ${s.castleWallMax}`;

    // 城内兵力
    const ePct = Math.max(0, Math.min(100, (s.enemyTroops / s.enemyTroopsMax) * 100));
    document.getElementById('siegeEnemyTroopsBar').style.width = `${ePct}%`;
    document.getElementById('siegeEnemyTroopsText').textContent = `${s.enemyTroops.toLocaleString()} 人`;

    // 城内士気
    const morPct = Math.max(0, Math.min(100, s.castleMorale));
    document.getElementById('siegeMoraleBar').style.width = `${morPct}%`;
    document.getElementById('siegeMoraleText').textContent = `${s.castleMorale}`;
  },

  logSiege(msg) {
    const log = document.getElementById('siegeLog');
    if (log) log.innerHTML = `<div>${msg}</div>` + log.innerHTML;
  },

  handleSiegeAction(actionType) {
    if (!this.currentSiege) return;
    const s = this.currentSiege;
    if (s.isActionProcessing) return;

    if (actionType === 'assault') {
      // 城壁残存率の計算 (0.0 〜 1.0)
      const wallMax = Math.max(1, s.castleWallMax || 60);
      const wallRatio = Math.max(0, Math.min(1.0, s.castleWall / wallMax));

      // 城壁が残っているほど自軍被害が劇的に増加し、敵兵への被害は激減
      const wallDmg = 20 + Math.floor(Math.random() * 15);
      // 敵へのダメージ：城壁健在時は激減
      const baseEnemyLoss = 200 + Math.floor(Math.random() * 150);
      const enemyLoss = Math.max(30, Math.round(baseEnemyLoss * (1.1 - wallRatio * 0.75)));
      // 自軍ダメージ：城壁残存率に比例して劇的に増加
      const basePlayerLoss = 150 + Math.floor(Math.random() * 100);
      const playerLoss = Math.round(basePlayerLoss * (1.0 + wallRatio * 3.0) + (s.playerTroops * 0.08 * wallRatio));

      s.castleWall = Math.max(0, s.castleWall - wallDmg);
      s.enemyTroops = Math.max(0, s.enemyTroops - enemyLoss);
      s.playerTroops = Math.max(0, s.playerTroops - playerLoss);
      s.castleMorale = Math.max(0, s.castleMorale - 12);

      try {
        this.audio.playGachaGacha?.(1.1);
        this.audio.playTaiko?.(1.4);
      } catch(e) {}
      this.logSiege(`🔨 梯子・攻城櫓で強襲！ (城壁残存率:${Math.round(wallRatio * 100)}%) 城壁耐久-${wallDmg}, 敵兵-${enemyLoss}！(自損:${playerLoss})`);

      // 自軍兵力が0になった場合の敗北処理
      if (s.playerTroops <= 0) {
        s.isActionProcessing = true;
        this.updateSiegeUI();
        try { this.audio.playHyoshigi?.(); } catch(e) {}
        this.log(`💀【攻城戦敗北】堅固な城壁に阻まれ強襲部隊は全滅・壊滅しました……`, 'battle');
        ['sCmdAssault', 'sCmdShoot', 'sCmdSurround', 'sCmdPersuade', 'sCmdRetreat'].forEach(id => {
          document.getElementById(id)?.setAttribute('disabled', 'true');
        });
        setTimeout(() => this.endBattle(), 800);
        return;
      }
    } else if (actionType === 'shoot') {
      // 矢砲斉射 (城内兵削り)
      const enemyLoss = 250 + Math.floor(Math.random() * 200);
      s.enemyTroops = Math.max(0, s.enemyTroops - enemyLoss);
      s.castleMorale = Math.max(0, s.castleMorale - 8);

      try {
        this.audio.playTeppo?.();
      } catch(e) {}
      this.logSiege(`🏹 城内へ矢砲の雨を浴びせる！ 籠城兵-${enemyLoss}！(自軍損害なし)`);
    } else if (actionType === 'surround') {
      // 兵糧遮断 (自軍の兵糧を消費、足りない場合は強制撤退)
      const siegeRiceCost = Math.max(10, Math.round(s.playerTroops * 0.008));
      if (this.rice < siegeRiceCost) {
        s.isActionProcessing = true;
        this.log(`⚠️【兵糧枯渇・攻城失敗】包囲軍の兵糧が底をつき（必要:${siegeRiceCost}石/所持:${this.rice}石）、城囲みを維持できず強制撤退しました！`, 'battle');
        s.srcProv.troops += s.playerTroops;
        ['sCmdAssault', 'sCmdShoot', 'sCmdSurround', 'sCmdPersuade', 'sCmdRetreat'].forEach(id => {
          document.getElementById(id)?.setAttribute('disabled', 'true');
        });
        setTimeout(() => this.endBattle(), 800);
        return;
      }

      this.rice -= siegeRiceCost;
      this.updateStatusHeader();

      const morLoss = 22 + Math.floor(Math.random() * 12);
      s.castleMorale = Math.max(0, s.castleMorale - morLoss);
      s.enemyTroops = Math.max(0, s.enemyTroops - 100);

      try {
        this.audio.playHyoshigi?.();
      } catch(e) {}
      this.logSiege(`🌾 外部からの補給路を遮断！(軍糧消費:${siegeRiceCost}石) 飢えにより敵士気-${morLoss}！`);
    } else if (actionType === 'persuade') {
      // 開城勧告
      if (s.castleMorale <= 40 || s.castleWall <= 20 || s.enemyTroops <= 400) {
        s.castleMorale = 0;
        this.logSiege(`📜 開城勧告を受諾！ 「兵の命を救うため、城を明け渡す！」 無血開城！`);
      } else {
        s.castleMorale = Math.max(0, s.castleMorale - 10);
        try { this.audio.playSlash?.(); } catch(e) {}
        this.logSiege(`📜 勧告使者を追い返された！ 「城を枕に討死あるのみ！」(敵士気-10)`);
      }
    } else if (actionType === 'retreat') {
      // 包囲解除撤退
      this.log(`【攻城撤退】我が軍は包囲を解き、${s.srcProv.name}へ兵力を帰還させました。`);
      s.srcProv.troops += s.playerTroops;
      this.endBattle();
      return;
    }

    this.updateSiegeUI();

    // 陥落判定 (城壁が0、または城内兵が0、または士気が0)
    if (s.castleWall <= 0 || s.enemyTroops <= 0 || s.castleMorale <= 0) {
      s.isActionProcessing = true;
      try { this.audio.playKachi?.(); } catch(e) {}
      this.logSiege(`🎉【城門突破・城池陥落】${s.dstProv.castleName || s.dstProv.castle || "居城"}は完全に陥落しました！！`);

      // 攻城ボタンを無効化して重複を防止
      ['sCmdAssault', 'sCmdShoot', 'sCmdSurround', 'sCmdPersuade', 'sCmdRetreat'].forEach(id => {
        document.getElementById(id)?.setAttribute('disabled', 'true');
      });

      setTimeout(() => this.conquerProvince(s.dstProv, s.playerTroops), 800);
    }
  },

  async conquerProvince(dstProv, remainTroops) {
    const oldOwner = dstProv.ownerId;
    const remainingProvs = this.provinces.filter(p => p.ownerId === oldOwner && p.id !== dstProv.id);
    const isClanDestroyed = (remainingProvs.length === 0);

    // 滅亡時に捕縛する対象武将（大名および勢力の全存命武将） (要件3)
    let capturedList = [];
    if (isClanDestroyed && oldOwner && oldOwner !== this.playerClanId) {
      capturedList = (this.activeOfficers || []).filter(o => o.clanId === oldOwner && !o.isDead);
    }

    this.handleProvinceLoss(dstProv, oldOwner, true);
    dstProv.ownerId = this.playerClanId;
    dstProv.troops = Math.max(500, remainTroops);
    dstProv.defense = 40;
    dstProv.morale = 80;
    dstProv.governance = 'direct';

    document.getElementById('battleModal')?.classList.add('hidden');
    document.getElementById('siegeModal')?.classList.add('hidden');
    this.endBattle();

    this.stats.battlesWon++;
    try { this.audio.playGrandFanfare?.(); } catch(e) {}
    this.log(`🚩【城池陥落・領国平定】${dstProv.name} (${dstProv.castleName || dstProv.castle || "居城"}) を完全制圧！ 貴家の支配領国となりました！`, 'important');
    this.showOrderResult('🏯 領国制覇！', `${dstProv.name} (${dstProv.castleName || dstProv.castle || "居城"}) を完全平定・占領しました！`, '#2ecc71');

    if (isClanDestroyed) {
      this.log(`💀【御家滅亡】${this.getClanFamilyName(oldOwner)}はすべての領国を失い、完全に滅亡しました！`, 'important');
    }

    // 自動セーブ実行
    this.autoSave();

    // 領国表示とマップ更新（必ず先行実行して領土色・バッジを確実に自国へ切り替え）
    this.selectProvince(dstProv.id);
    this.appointHistoricalHomeGovernors(this.playerClanId);
    this.autoAppointComputerCastellans({ fillVacancies: true });
    this.updateUI();

    // 敵大名滅亡時の捕縛武将処断・登用ダイアログ (要件3, 4, 5)
    if (capturedList.length > 0) {
      await this.handleCapturedOfficers(capturedList, oldOwner);
    }

    // 天下統一 ＆ 征夷大将軍就任判定
    if (this.checkEndGameConditions()) {
      return;
    }
  },

  // 敵大名滅亡時の捕縛武将処断・登用システム (要件3: 捕縛/登用/斬首/解放, 要件4: 登用確率6割, 要件5: 浪人化)
  async handleCapturedOfficers(officers, oldOwnerId) {
    if (!officers || officers.length === 0) return;
    const clanName = this.getClanFamilyName(oldOwnerId);

    // 捕縛アナウンスダイアログ
    if (window.Swal) {
      await Swal.fire({
        title: '⚔️【敵将捕縛・滅亡処断】⚔️',
        html: `
          <div style="font-size:12pt; text-align:left; line-height:1.7; color:#f5eedc; font-family:'Noto Serif JP',serif;">
            <p style="font-size:13pt; color:var(--gold-bright); margin-bottom:8px;">
              <strong>【${clanName}】</strong>は最後の居城を失い、完全に滅亡いたしました！
            </p>
            <p>
              城内にて敵大名および麾下の武将 <strong>${officers.length}名</strong> を全員捕縛いたしました。
            </p>
            <div style="background:rgba(0,0,0,0.4); padding:10px 14px; border-radius:5px; border-left:3px solid var(--gold); margin-top:10px;">
              捕縛した武将一人ひとりと対面し、<strong>【登用】</strong>（登用確率60%）、<strong>【斬首】</strong>（処刑）、<strong>【解放】</strong>（放免・浪人）の処遇をご決断ください。
            </div>
          </div>
        `,
        background: '#1c130d',
        color: '#f5eedc',
        confirmButtonText: '武将と対面する',
        confirmButtonColor: '#922b21'
      });
    }

    // 1人ずつ対面処断
    for (let i = 0; i < officers.length; i++) {
      const off = officers[i];
      const comment = this.getOfficerComment(off);
      const isDaimyo = off.isDaimyo;
      const roleText = isDaimyo ? '👑 旧当主' : '🏯 配下武将';
      const age = this.year - (off.birthYear || 1530);

      let decision = 'release'; // デフォルト

      if (window.Swal) {
        const res = await Swal.fire({
          title: `❖ 捕縛武将 (${i + 1}/${officers.length}) ❖`,
          html: `
            <div style="font-size:12pt; text-align:left; color:#f5eedc; font-family:'Noto Serif JP',serif;">
              <!-- 武将ヘッダー -->
              <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #5a4638; padding-bottom:8px; margin-bottom:12px;">
                <div>
                  <span style="font-size:18pt; font-weight:bold; color:#fff;">${off.name}</span>
                  <span style="background:${isDaimyo ? '#b7950b' : '#2980b9'}; color:#fff; padding:2px 10px; border-radius:3px; font-size:11pt; margin-left:8px; font-weight:bold;">${roleText}</span>
                  <span style="color:#aaa; font-size:11.5pt; margin-left:6px;">(${age}歳)</span>
                </div>
              </div>

              <!-- 能力値カード -->
              <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:12px; text-align:center;">
                <div style="background:rgba(231,76,60,0.18); border:1px solid #c0392b; padding:6px; border-radius:4px;">
                  <div style="font-size:11pt; color:#ff7675;">⚔️ 武勇</div>
                  <div style="font-size:16pt; font-weight:bold; color:#ff7675;">${off.military}</div>
                </div>
                <div style="background:rgba(52,152,219,0.18); border:1px solid #2980b9; padding:6px; border-radius:4px;">
                  <div style="font-size:11pt; color:#74b9ff;">🌾 内政</div>
                  <div style="font-size:16pt; font-weight:bold; color:#74b9ff;">${off.politic || off.politics}</div>
                </div>
                <div style="background:rgba(46,204,113,0.18); border:1px solid #27ae60; padding:6px; border-radius:4px;">
                  <div style="font-size:11pt; color:#55efc4;">📜 知略</div>
                  <div style="font-size:16pt; font-weight:bold; color:#55efc4;">${off.intel || off.stratagem}</div>
                </div>
              </div>

              <!-- 列伝ダイアログ -->
              <div style="font-size:11.5pt; color:#ddd; max-height:95px; overflow-y:auto; line-height:1.6; margin-bottom:14px; background:rgba(0,0,0,0.4); padding:8px 10px; border-radius:4px; border:1px solid #4a3b2c;">
                <strong>【列伝】</strong> ${this.cleanOfficerLore(off.lore) || '歴史に名高い名将。'}
              </div>

              <div style="text-align:center; padding:4px; color:#ffd700; font-size:12pt; font-weight:bold;">
                いかが処遇なさいますか？
              </div>
            </div>
          `,
          background: '#1c130d',
          color: '#f5eedc',
          showCancelButton: true,
          showDenyButton: true,
          confirmButtonText: '🤝 登用 (確率60%)',
          confirmButtonColor: '#27ae60',
          denyButtonText: '🗡️ 斬首 (処刑)',
          denyButtonColor: '#c0392b',
          cancelButtonText: '🕊️ 解放 (放免・浪人)',
          cancelButtonColor: '#7f8c8d',
          allowOutsideClick: false
        });

        if (res.isConfirmed) {
          decision = 'recruit';
        } else if (res.isDenied) {
          decision = 'execute';
        } else {
          decision = 'release';
        }
      }

      // 処遇判定
      if (decision === 'recruit') {
        // 登用確率 60% (要件4: 登用できる確率は6割)
        const isSuccess = Math.random() < 0.60;
        if (isSuccess) {
          off.clanId = this.playerClanId;
          off.isDaimyo = false;
          off.assignedProvId = null;
          this.log(`🤝【登用成功】「我が命、貴殿に捧げましょう！」${off.name}が我が軍の配下に加わりました！`, 'important');
          this.appointHistoricalHomeGovernors(this.playerClanId);
          try { this.audio.playTaiko?.(); } catch(e) {}
          if (window.Swal) {
            await Swal.fire({
              icon: 'success',
              title: '登用成功！',
              html: `
                <div style="font-size:13pt; color:#2ecc71; font-weight:bold; margin-bottom:8px;">「我が命、貴殿に捧げましょう！」</div>
                <div style="font-size:12pt; color:#eee;">${off.name}公が我が軍の配下に加わりました！</div>
              `,
              background: '#1c130d',
              color: '#fff',
              confirmButtonColor: '#27ae60'
            });
          }
        } else {
          // 登用拒絶 -> 浪人化 (要件5: 解放された武将は浪人となり、他家に仕官できるようになります)
          off.clanId = 'ronin';
          off.isDaimyo = false;
          off.assignedProvId = null;
          if (off.id === 'off_ashikaga_yoshiaki') {
            off.defaultProv = 'bingo';
            off.assignedProvId = 'bingo';
          }
          this.log(`💢【登用拒絶】「主君を討たれ、仇敵に仕えるつもりはない！」${off.name}は登用を拒絶し、浪人となりました。`, 'battle');
          try { this.audio.playHyoshigi?.(); } catch(e) {}
          if (window.Swal) {
            await Swal.fire({
              icon: 'error',
              title: '登用拒絶……',
              html: `
                <div style="font-size:13pt; color:#e74c3c; font-weight:bold; margin-bottom:8px;">「仇敵に仕えるつもりはない！」</div>
                <div style="font-size:12pt; color:#eee;">${off.name}は登用を断固拒絶し、陣を立ち去りました（浪人となりました）。</div>
              `,
              background: '#1c130d',
              color: '#fff',
              confirmButtonColor: '#7f8c8d'
            });
          }
        }
      } else if (decision === 'execute') {
        // 斬首 (処刑)
        off.isDead = true;
        off.assignedProvId = null;
        this.log(`💀【斬首処刑】${off.name}を処刑いたしました。「無念……！」`, 'important');
        try { this.audio.playHyoshigi?.(); } catch(e) {}
        if (window.Swal) {
          await Swal.fire({
            icon: 'warning',
            title: '処刑執行',
            html: `
              <div style="font-size:13pt; color:#e74c3c; margin-bottom:8px;">「無念……！」</div>
              <div style="font-size:12pt; color:#eee;">${off.name}を処刑いたしました。</div>
            `,
            background: '#1c130d',
            color: '#fff',
            confirmButtonColor: '#c0392b'
          });
        }
      } else {
        // 解放 (放免・浪人)
        off.clanId = 'ronin';
        off.isDaimyo = false;
        off.assignedProvId = null;
        if (off.id === 'off_ashikaga_yoshiaki') {
          off.defaultProv = 'bingo';
          off.assignedProvId = 'bingo';
        }
        this.log(`🕊️【放免解放】「情けは無用なれど……忝い」${off.name}を放免いたしました（浪人となりました）。`);
        if (window.Swal) {
          await Swal.fire({
            icon: 'info',
            title: '放免・解放',
            html: `
              <div style="font-size:13pt; color:#3498db; margin-bottom:8px;">「情けは無用なれど……忝い」</div>
              <div style="font-size:12pt; color:#eee;">${off.name}を放免いたしました（浪人となり各地へ落ち延びました）。</div>
            `,
            background: '#1c130d',
            color: '#fff',
            confirmButtonColor: '#3498db'
          });
        }
      }
    }

    this.updateActiveOfficers();
    this.updateUI();
  },

  // 浪人の他家・自軍仕官システム（大名の武将不足・滅亡を防止）,

  processRoninEmployment() {
    const ronins = (this.activeOfficers || []).filter(o => o.clanId === 'ronin' && !o.isDead);
    if (ronins.length === 0) return;

    const aliveClans = [...new Set(this.provinces.map(p => p.ownerId).filter(Boolean))];
    if (aliveClans.length === 0) return;

    const myOfficers = (this.activeOfficers || []).filter(o => o.clanId === this.playerClanId && !o.isDead);

    // 1. プレイヤーへの仕官希望者（遠国も可。跡継ぎ不在なら確率が上がり、遠国からも来る）
    let applicantForPlayer = null;
    const playerLacksHeir = aliveClans.includes(this.playerClanId) && this.householdLacksHeir(this.playerClanId);
    if (aliveClans.includes(this.playerClanId)) {
      const eligible = ronins
        .map(r => ({ r, dist: this.getRoninDistanceToClan(r, this.playerClanId) }))
        .filter(x => Number.isFinite(x.dist) && (playerLacksHeir || x.dist <= 1));
      const hasLocal = eligible.some(x => x.dist === 0);
      const hasNear = eligible.some(x => x.dist <= 1);
      const isCrisis = myOfficers.length <= 3;
      const applyChance = playerLacksHeir
        ? (hasLocal ? 0.90 : (hasNear ? 0.74 : 0.58))
        : (hasLocal ? (isCrisis ? 0.80 : 0.32) : (isCrisis ? 0.40 : 0.12));

      if (eligible.length > 0 && Math.random() < applyChance) {
        const pool = [];
        eligible.forEach(x => {
          const weight = x.dist === 0 ? 5 : (x.dist === 1 ? 2 : 1);
          for (let i = 0; i < weight; i++) pool.push(x.r);
        });
        applicantForPlayer = pool[Math.floor(Math.random() * pool.length)];
      }
    }

    // 2. CPU大名への仕官（遠国も可。跡継ぎ不在の家には遠い浪人も仕官しやすい）
    const aiClans = aliveClans.filter(c => c !== this.playerClanId);
    if (aiClans.length > 0) {
      const clanOfficerCounts = {};
      const lacksHeirByClan = {};
      aiClans.forEach(c => {
        clanOfficerCounts[c] = (this.activeOfficers || []).filter(o => o.clanId === c && !o.isDead).length;
        lacksHeirByClan[c] = this.householdLacksHeir(c);
      });

      ronins.forEach(ronin => {
        if (applicantForPlayer && ronin.id === applicantForPlayer.id) return;

        const distMap = this.getProvinceDistanceMap(ronin.defaultProv);
        const candidates = aiClans
          .map(c => ({
            clan: c,
            dist: this.getRoninDistanceToClan(ronin, c, distMap),
            officers: clanOfficerCounts[c] || 0,
            lacksHeir: !!lacksHeirByClan[c]
          }))
          .filter(x => Number.isFinite(x.dist) && (x.lacksHeir || x.dist <= 1));
        if (candidates.length === 0) return;

        const weightOf = (c) => {
          let w = c.dist === 0 ? 6 : (c.dist === 1 ? 2 : 1);
          if (c.officers <= 2) w += 2;
          if (c.lacksHeir) w += 3;
          return w;
        };
        const total = candidates.reduce((s, c) => s + weightOf(c), 0);
        let roll = Math.random() * total;
        let target = candidates[0];
        for (const c of candidates) {
          roll -= weightOf(c);
          if (roll <= 0) { target = c; break; }
        }

        // 流浪国は高く、隣国・遠国は低い。跡継ぎ不在なら全体が上がる
        let chance = target.dist === 0 ? 0.38 : (target.dist === 1 ? 0.14 : 0.08);
        if (target.lacksHeir) {
          chance = target.dist === 0 ? 0.64 : (target.dist === 1 ? 0.42 : 0.30);
        }
        if (Math.random() < chance) {
          ronin.clanId = target.clan;
          ronin.assignedProvId = null;
          ronin.isDaimyo = false;
          const where = target.dist === 0 ? '流浪の国' : (target.dist === 1 ? '隣国' : '遠国');
          const heirNote = target.lacksHeir ? '（跡継ぎ不在を聞きつけて）' : '';
          this.log(`📜【仕官報】${where}に身を寄せていた${ronin.name}が、${heirNote}${this.getClanFamilyName(target.clan)}に仕官いたしました。`);
          this.appointHistoricalHomeGovernors(target.clan);
        }
      });
    }

    // 3. プレイヤーへの仕官願い出イベント（モーダル対面表示）
    if (applicantForPlayer) {
      const ronin = applicantForPlayer;
      const defProvName = ronin.defaultProv ? this.getProvinceJapaneseName(ronin.defaultProv) : '諸国';
      const reach = this.getRoninServiceReach(ronin, this.playerClanId);
      const isDefProvMine = reach.dist === 0;
      const isNeighbor = reach.dist === 1;
      const age = this.year - (ronin.birthYear || 1530);
      const arriveBadge = isDefProvMine
        ? { bg: 'rgba(46,204,113,0.3)', border: '#27ae60', color: '#2ecc71', text: `🏯 流浪国（自領） (${defProvName})` }
        : isNeighbor
          ? { bg: 'rgba(230,126,34,0.3)', border: '#e67e22', color: '#f5b041', text: `隣国より参上 (${defProvName})` }
          : { bg: 'rgba(52,152,219,0.28)', border: '#2980b9', color: '#85c1e9', text: `遠国より参上 (${defProvName})` };
      const arriveLine = reach.lacksHeir
        ? '「貴家に継ぐべき者がおらぬと聞き、はるばる馳せ参じました。我が槍を貴家に捧げたく存じます。」'
        : '「殿の仁政と天下泰平の志を慕い、馳せ参じましてございます！我が槍を貴家に捧げたく存じます。」';

      if (this.isAutoPlay) {
        this.acceptRoninApplicant(ronin);
        this.log(`⏩【オート承諾】${ronin.name}の仕官の申し出を自動で受け入れました。`);
      } else {
      setTimeout(async () => {
        if (!window.Swal) {
          this.acceptRoninApplicant(ronin);
          return;
        }

        try { this.audio.playTaiko?.(); } catch(e) {}

        const res = await Swal.fire({
          title: `❖ 浪人仕官の願い出 ❖`,
          html: `
            <div style="text-align:left; font-size:12pt; color:#f5eedc; font-family:'Noto Serif JP',serif; line-height:1.6;">
              <div style="border-bottom:1px solid #5a4638; padding-bottom:8px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <span style="font-size:16pt; font-weight:bold; color:var(--gold-bright);">${ronin.name}</span>
                  <span style="font-size:11.5pt; color:#ccc; margin-left:6px;">(${age}歳)</span>
                </div>
                <div>
                  <span style="background:${arriveBadge.bg}; border:1px solid ${arriveBadge.border}; color:${arriveBadge.color}; padding:2px 8px; border-radius:3px; font-size:11pt;">
                    ${arriveBadge.text}
                  </span>
                </div>
              </div>
              <p style="font-size:12pt; color:#ffd700; margin-bottom:10px;">
                ${arriveLine}
              </p>
              <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; text-align:center; margin-bottom:12px;">
                <div style="background:rgba(231,76,60,0.2); border:1px solid #c0392b; padding:4px; border-radius:4px;">
                  <div style="font-size:10pt; color:#ff7675;">⚔️ 武勇</div>
                  <div style="font-size:14pt; font-weight:bold; color:#ff7675;">${ronin.military}</div>
                </div>
                <div style="background:rgba(52,152,219,0.2); border:1px solid #2980b9; padding:4px; border-radius:4px;">
                  <div style="font-size:10pt; color:#74b9ff;">🌾 内政</div>
                  <div style="font-size:14pt; font-weight:bold; color:#74b9ff;">${ronin.politic}</div>
                </div>
                <div style="background:rgba(46,204,113,0.2); border:1px solid #27ae60; padding:4px; border-radius:4px;">
                  <div style="font-size:10pt; color:#55efc4;">📜 知略</div>
                  <div style="font-size:14pt; font-weight:bold; color:#55efc4;">${ronin.intel}</div>
                </div>
              </div>
              <div style="background:rgba(0,0,0,0.4); padding:8px 10px; border-radius:4px; margin-bottom:12px; font-size:11.5pt; color:#ddd; line-height:1.5;">
                <strong>【列伝】</strong> ${this.cleanOfficerLore(ronin.lore) || '天下に名を響かせる士。'}
              </div>
              <div style="text-align:center; color:#ccc; font-size:11.5pt;">
                この武将を召し抱えますか？（召し抱えると直ちに配下武将となります）
              </div>
            </div>
          `,
          showCancelButton: true,
          confirmButtonText: '🤝 召し抱える (登用)',
          confirmButtonColor: '#27ae60',
          cancelButtonText: '🕊️ 辞退する (見送る)',
          cancelButtonColor: '#7f8c8d',
          background: '#1c130d',
          color: '#f5eedc',
          allowOutsideClick: false
        });

        if (res.isConfirmed) {
          this.acceptRoninApplicant(ronin);
        } else {
          this.log(`🕊️【仕官見送り】${ronin.name}の仕官願いを見送りました（浪人を継続します）。`);
        }
      }, 800);
      }
    }

    this.updateActiveOfficers();
  },

  acceptRoninApplicant(ronin) {
    if (!ronin || ronin.clanId === this.playerClanId) return;
    ronin.clanId = this.playerClanId;
    ronin.assignedProvId = null;
    ronin.isDaimyo = false;
    this.log(`🤝【名将仕官】浪人の${ronin.name}公が、仕官を願い出て我が軍の配下に加わりました！`, 'important');
    try { this.audio.playGrandFanfare?.(); } catch(e) {}
    this.appointHistoricalHomeGovernors(this.playerClanId);
    this.updateActiveOfficers();
    this.updateUI(); // 選択中の国パネルも updateUI 内で再描画
  },

  endBattle() {
    this.inBattle = false;
    this.currentBattle = null;
    this.currentSiege = null;
    document.getElementById('battleModal')?.classList.add('hidden');
    document.getElementById('siegeModal')?.classList.add('hidden');

    // ボタンの無効化をリセット
    ['bCmdAssault', 'bCmdShoot', 'bCmdDefend', 'bCmdTactic', 'bCmdRetreat'].forEach(id => {
      document.getElementById(id)?.removeAttribute('disabled');
    });
    ['sCmdAssault', 'sCmdShoot', 'sCmdSurround', 'sCmdPersuade', 'sCmdRetreat'].forEach(id => {
      document.getElementById(id)?.removeAttribute('disabled');
    });

    try { this.music.playTrack(this.getSeasonTrackKey()); } catch(e) {}
    this.updateUI();
  },

  // ============================================================================
  // オートプレーモード (自動季節進行)
  // ============================================================================,

  startAutoPlay() {
    if (this.inBattle) {
      this.showOrderResult('⚠ オート不可', '合戦中はオート進行を開始できません。', '#e74c3c');
      return;
    }
    if (!this.playerDaimyo) {
      return;
    }

    this.isAutoPlay = true;
    this.autoPlayPausedForEvent = false;
    this.updateAutoPlayUI(true);
    this.log(`⏩【季節オート進行】オートプレーを開始しました（速度: ${this.autoPlaySpeed.toFixed(1)}秒/期）。仕官の申し出は自動承諾し、歴史イベントは選択のため一時停止します。`);

    // 次の進行をスケジュール
    this.scheduleNextAutoSeason();
  },

  stopAutoPlay(reason = '') {
    if (!this.isAutoPlay && !this.autoPlayTimer && !this.autoPlayPausedForEvent) return;
    this.isAutoPlay = false;
    this.autoPlayPausedForEvent = false;
    if (this.autoPlayTimer) {
      clearTimeout(this.autoPlayTimer);
      this.autoPlayTimer = null;
    }
    this.setEventPauseNote(false);
    this.updateAutoPlayUI(false);
    if (reason && reason !== '手動停止') {
      this.log(`⏹【季節オート進行】${reason}によりオート進行を停止しました。`);
    } else if (reason === '手動停止') {
      this.log('⏹【季節オート進行】オートプレーを停止しました。');
    }
    // 停止時に最新状態を確実に保存
    this.autoSave(true);
  },

  updateAutoPlaySpeed(val) {
    const num = Math.max(0.1, Math.min(3.0, parseFloat(val) || 0.5));
    this.autoPlaySpeed = Math.round(num * 10) / 10;
    
    const valEl = document.getElementById('autoPlaySpeedVal');
    if (valEl) {
      valEl.textContent = `${this.autoPlaySpeed.toFixed(1)}秒`;
    }

    // 稼働中なら即座に新しい速度で再スケジュール
    if (this.isAutoPlay) {
      this.scheduleNextAutoSeason();
    }
  },

  updateAutoPlayUI(isRunning) {
    const paused = !!(isRunning && this.autoPlayPausedForEvent);
    const btn = document.getElementById('autoPlayToggleBtn');
    const icon = document.getElementById('autoPlayBtnIcon');
    const text = document.getElementById('autoPlayBtnText');
    const indicator = document.getElementById('autoPlayIndicator');
    const label = document.getElementById('autoPlayLabel');

    if (btn) {
      btn.classList.toggle('running', isRunning && !paused);
      btn.classList.toggle('paused', paused);
    }
    if (icon) {
      icon.textContent = isRunning ? '⏸' : '▶';
    }
    if (text) {
      text.textContent = isRunning ? '停止' : '開始';
    }
    if (label) {
      label.textContent = paused ? '⏸ イベント選択待ち' : '⏩ 季節オート進行';
    }
    if (indicator) {
      indicator.classList.toggle('active', isRunning && !paused);
      indicator.classList.toggle('paused', paused);
    }
  },

  setEventPauseNote(visible) {
    document.querySelectorAll('.event-auto-pause-note').forEach(el => {
      el.classList.toggle('hidden', !visible);
    });
  },

  isEventChoiceOpen() {
    const eventModal = document.getElementById('historicalEventModal');
    if (eventModal && !eventModal.classList.contains('hidden')) return true;

    const histModal = document.getElementById('historyEventModal');
    if (histModal && !histModal.classList.contains('hidden')) return true;

    const honnouji = document.getElementById('honnoujiSuccessorModal');
    if (honnouji && honnouji.style.display !== 'none' && getComputedStyle(honnouji).display !== 'none') return true;

    return false;
  },

  pauseAutoPlayForEvent() {
    if (!this.isAutoPlay) return;
    const already = this.autoPlayPausedForEvent;
    this.autoPlayPausedForEvent = true;
    if (this.autoPlayTimer) {
      clearTimeout(this.autoPlayTimer);
      this.autoPlayTimer = null;
    }
    this.setEventPauseNote(true);
    this.updateAutoPlayUI(true);
    if (!already) {
      this.log('⏸【季節オート進行】イベント発生のため一時停止しました。選択後に再開します。');
    }
  },

  resumeAutoPlayAfterEvent() {
    if (!this.autoPlayPausedForEvent) return;
    this.autoPlayPausedForEvent = false;
    this.setEventPauseNote(false);
    if (!this.isAutoPlay) return;
    if (this.inBattle) {
      this.stopAutoPlay('合戦発生のため');
      return;
    }
    const defeatModal = document.getElementById('defeatModal');
    if (defeatModal && !defeatModal.classList.contains('hidden')) {
      this.stopAutoPlay('御家滅亡のため');
      return;
    }
    this.updateAutoPlayUI(true);
    this.log('⏩【季節オート進行】選択を確認し、オートプレーを再開しました。');
    this.scheduleNextAutoSeason();
  },

  scheduleNextAutoSeason() {
    if (!this.isAutoPlay || this.autoPlayPausedForEvent) return;
    if (this.autoPlayTimer) {
      clearTimeout(this.autoPlayTimer);
      this.autoPlayTimer = null;
    }
    const delayMs = Math.max(100, Math.round(this.autoPlaySpeed * 1000));
    this.autoPlayTimer = setTimeout(() => {
      this.runAutoStep();
    }, delayMs);
  },

  tryAutoAcknowledgeDialogs() {
    if (this.isEventChoiceOpen()) return false;
    if (!(window.Swal && typeof Swal.isVisible === 'function' && Swal.isVisible())) return false;
    // 世継ぎ指名など、入力が必要な画面はプレイヤーの選択を待つ
    if (document.querySelector('.swal2-popup .swal2-select, .swal2-popup .swal2-input, .swal2-popup .swal2-textarea')) {
      return false;
    }

    try { Swal.clickConfirm(); } catch (e) {}
    if (typeof Swal.isVisible === 'function' && Swal.isVisible()) {
      try { Swal.close(); } catch (e) {}
    }
    return typeof Swal.isVisible === 'function' && Swal.isVisible();
  },

  /**
   * 演算（Tick）と描画（Render）を分離した季節進行処理
   */
  async nextSeason() {
    if (this.inBattle) return;
    if (this.isHistoricalEventBusy()) {
      this.log('📜【待機】歴史イベントの選択が終わるまで季節は進みません。');
      return;
    }

    const nextBtn = document.getElementById('nextSeasonBtn');
    if (nextBtn) nextBtn.disabled = true;

    try {
      // 1. 演算（Tick）フェーズ: 各種収支・人事・AI思考（非同期ループ）
      const tickResult = await this.processSeasonTick();
      if (tickResult === 'defeat') return;

      // 2. 描画（Render）フェーズ: UI・マップ・バナー・エフェクト更新
      this.renderSeason();
    } finally {
      if (nextBtn) nextBtn.disabled = false;
    }
  },

  /**
   * 季節進行の演算（Tick）処理
   * @returns {Promise<string|void>}
   */
  async processSeasonTick() {
    this.seasonIdx = (this.seasonIdx + 1) % 4;
    if (this.seasonIdx === 0) {
      this.year += 1;
      this.snapshotLivingDaimyoNames();
      this.updateToyotomiSurname(true);
      this.updateActiveOfficers();
      if (this.currentScenario) {
        this.resolveOfficerAffiliations(this.currentScenario);
      }
      this.updateCastlesForYear();
      // 大名の寿命判定と世継ぎ家督相続
      this.checkDaimyoLifespan();
    }
    this.maintainAlliances();
    this.ap = this.maxAp;

    const weathers = ['晴天', '晴天', '曇天', '恵みの雨', '豪雨', '晴天'];
    if (this.seasonIdx === 3) weathers.push('大雪', '吹雪');
    this.currentWeather = weathers[Math.floor(Math.random() * weathers.length)];

    // 委任統治の実行
    this.executeGovernanceTurn();

    // 収支計算（直轄地は大名能力半減ペナルティにより収穫・商業が50%）
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    let totalRiceHarvest = 0;
    let totalCommerceIncome = 0;
    let directRuleCount = 0;

    let ikkiCount = 0;
    let specialtyRiceBonus = 0;
    let portGunNotes = 0;
    myProvs.forEach(p => {
      const effStats = this.getEffectiveStats(p.id);
      const mult = effStats.isDirectRule ? 0.5 : 1.0;
      if (effStats.isDirectRule) directRuleCount++;

      const order = Number(p.order);
      const ikkiThreshold = window.IKKI_ORDER_THRESHOLD || 50;
      const inIkki = Number.isFinite(order) && order <= ikkiThreshold;
      if (inIkki) {
        ikkiCount++;
        const desert = Math.min(p.troops || 0, Math.round((p.troops || 0) * 0.04) + 20);
        p.troops = Math.max(200, (p.troops || 0) - desert);
        p.order = Math.min(100, (p.order || 0) + 5);
        this.log(`🔥【一揆】${p.name}で領民・土豪が蜂起！今季の収入が途絶（兵力-${desert}, 治安+5）`, 'important');
        return;
      }

      if (this.seasonIdx === 2) {
        const riceMult = this.getAutumnRiceMultiplier(p);
        const gained = Math.round(p.rice * 1.2 * mult * riceMult);
        totalRiceHarvest += gained;
        if (riceMult > 1) specialtyRiceBonus += Math.round(gained * (riceMult - 1) / riceMult);
        const port = (window.SPECIALTY_SYNERGY || []).find(r => r.id === 'port');
        if (port && this.provinceMatchesSpecialty(p, port)) {
          p.defense = Math.min(100, (p.defense || 50) + (port.effects.autumnDefenseBonus || 2));
          p.troops = (p.troops || 0) + (port.effects.autumnTroopBonus || 80);
          this.playerGunSupply = true;
          portGunNotes++;
        }
      }
      if (this.seasonIdx === 1 || this.seasonIdx === 3) {
        totalCommerceIncome += Math.round(p.commerce * 0.8 * mult);
      }
    });

    this.rice = Math.max(0, this.rice + totalRiceHarvest);
    this.gold += totalCommerceIncome;

    if (this.seasonIdx === 2 && totalRiceHarvest > 0) {
      const extras = [];
      if (directRuleCount > 0) extras.push(`直轄領${directRuleCount}カ国は能力半減`);
      if (specialtyRiceBonus > 0) extras.push(`穀倉シナジー+${specialtyRiceBonus.toLocaleString()}石`);
      if (portGunNotes > 0) extras.push(`南蛮貿易港${portGunNotes}カ国から鉄砲・砲術資材を補給`);
      const extraNote = extras.length ? `（※${extras.join('／')}）` : '。全城主の善政により満額の収穫を達成！';
      this.log(`🌾【秋の収穫】領国より兵糧 ${totalRiceHarvest.toLocaleString()} 石を収納${extras.length ? '。' + extraNote : extraNote}`);
    }
    if ((this.seasonIdx === 1 || this.seasonIdx === 3) && totalCommerceIncome > 0) {
      const directNote = directRuleCount > 0 ? `（※直轄領${directRuleCount}カ国は能力半減で金収入50%）` : '（全城配備により満額収納）';
      this.log(`💰【商港・城下町運上】領国より金 ${totalCommerceIncome.toLocaleString()} 貫を徴収。${directNote}`);
    }
    if (ikkiCount > 0) {
      this.log(`⚠【一揆報告】今季 ${ikkiCount} カ国で一揆が発生し、当該領の収入が途絶しました。`, 'important');
    }

    // 浪人の他家・自軍仕官判定
    this.processRoninEmployment();

    // 空白地での過去大名武将の旗揚げ・御家再興
    this.processBlankProvinceUprisings();

    // 途中雇用・待機武将の本拠城主任命（全勢力）
    this.appointHistoricalHomeGovernors();

    // AI大名の行動（非同期実行でUIフリーズを防止）
    await this.executeAiTurn();
    this.maintainAlliances();

    // 攻略で空いた支城と、本拠に残った家臣を、ゆかりの地優先で城主にする
    this.autoAppointComputerCastellans({ fillVacancies: true });

    // 反覇道包囲網判定
    if (!this.coalitionFormed && myProvs.length >= 15) {
      this.coalitionFormed = true;
      document.getElementById('coalitionBanner').style.display = 'block';
      this.music.playTrack('crisis');
      this.log('⚠【反覇道包囲網 結成】貴家の急拡大を恐れた諸大名が同盟を結成しました！', 'important');
      this.formCoalitionAlliances();
      const coalOpts = {
        icon: 'warning',
        title: '⚠ 反覇道包囲網 結成！',
        text: '天下の諸大名が密かに結託し、貴家打倒の包囲網を結成しました！国境各城の防備を固めてください！',
        background: '#241710',
        color: '#ffaaaa'
      };
      if (this.isAutoPlay) {
        coalOpts.timer = Math.max(120, Math.round(this.autoPlaySpeed * 700));
        coalOpts.timerProgressBar = true;
      }
      Swal.fire(coalOpts);
    } else {
      this.music.playTrack(this.getSeasonTrackKey());
    }

    const now = Date.now();
    if (!this.isAutoPlay || this.autoPlaySpeed >= 0.3 || (now - (this._lastHyoshigiTime || 0)) > 350) {
      this.audio.playHyoshigi();
      this._lastHyoshigiTime = now;
    }
    this.log(`【季節進行】${this.year}年 ${this.seasonNames[this.seasonIdx]}へ。軍令権が回復しました。`);

    const updatedMyProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    if (updatedMyProvs.length === 0) {
      if (this.isAutoPlay) this.stopAutoPlay('御家滅亡のため');
      this.triggerDefeat();
      return 'defeat';
    }
  },

  /**
   * 季節進行の画面描画（Render）処理
   */
  renderSeason() {
    // 領国・勢力ステータスとマップ表示を必ず先行更新（委任進攻結果を確実に画面へ反映）
    this.updateUI();

    if (this.checkEndGameConditions()) {
      if (this.isAutoPlay) this.stopAutoPlay('天下統一達成のため');
      return;
    }

    // 季節ビジュアルとバナーの更新
    this.updateSeasonVisuals();
    this.showSeasonNoticeBanner(this.year, this.seasonNames[this.seasonIdx], this.currentWeather);

    // 歴史大イベントの判定と発火（予約中は次の季節へ進めない）
    this.scheduleHistoricalEventCheck(this.isAutoPlay ? 0 : 700);

    // 攻略保護フラグの解除
    this.provinces.forEach(p => { delete p.justConquered; });

    // 自動セーブ実行
    this.autoSave();
  },

  // ============================================================================
  // AI大名の行動処理（攻撃・内政・成長）
  // ============================================================================,

  formCoalitionAlliances() {
    const neighbors = new Set();
    (this.provinces || []).filter(p => p.ownerId === this.playerClanId).forEach(p => {
      (p.neighbors || []).forEach(nId => {
        const n = this.provinces.find(x => x.id === nId);
        if (n && n.ownerId && n.ownerId !== this.playerClanId) neighbors.add(n.ownerId);
      });
    });
    HISTORICAL_ALLIANCE_BONDS.forEach(bond => {
      if (this.year < bond.from || this.year > bond.to) return;
      if (!neighbors.has(bond.a) || !neighbors.has(bond.b)) return;
      if (bond.a === this.playerClanId || bond.b === this.playerClanId) return;
      if (!this.isClanExtant(bond.a) || !this.isClanExtant(bond.b)) return;
      if (this.isAllied(bond.a, bond.b)) return;
      if (!bond.remote && !this.clansShareBorder(bond.a, bond.b)) return;
      this.alliances.push({
        members: [bond.a, bond.b],
        formedYear: this.year,
        formedSeason: this.seasonIdx
      });
      this.log(`🤝【包囲網同盟】${this.allianceClanLabel(bond.a)}と${this.allianceClanLabel(bond.b)}が${bond.label}を結び、貴家に対抗します。`);
    });
  },


  // AI大名の兵糧事情：現在の石高合計 / 基準石高合計（飢饉直後は 1 を大きく下回る）,

  clanHasLivingLord(clanId) {
    if (!clanId) return false;
    return (this.activeOfficers || []).some(o => o && o.clanId === clanId && o.isDaimyo && !o.isDead);
  },

  autoSave(force = false) {
    const now = Date.now();
    if (!force && this.isAutoPlay && (now - (this._lastAutoSaveTime || 0)) < 2000) {
      return;
    }
    this._lastAutoSaveTime = now;
    try {
      // 領国データの差分抽出（SVGパスや座標などの静的マスターは除外）
      const provincesDelta = (this.provinces || []).map(p => ({
        id: p.id,
        ownerId: p.ownerId,
        troops: p.troops,
        rice: p.rice,
        gold: p.gold,
        commerce: p.commerce,
        defense: p.defense,
        order: p.order,
        governance: p.governance,
        jodaiId: p.jodaiId || p.governorId || null,
        isCapital: !!p.isCapital
      }));

      // アクティブ武将の差分抽出（列伝・能力値・生没年などの静的マスターは除外）
      const officersDelta = (this.activeOfficers || []).map(o => ({
        id: o.id,
        clanId: o.clanId,
        assignedProvId: o.assignedProvId || o.provId || null,
        isDaimyo: !!o.isDaimyo,
        hasBeenDaimyo: !!o.hasBeenDaimyo,
        isCastellan: !!o.isCastellan,
        isDead: !!o.isDead,
        loyalty: o.loyalty,
        actionDone: !!o.actionDone
      }));

      const saveData = {
        version: 2, // 差分セーブフォーマット
        year: this.year,
        seasonIdx: this.seasonIdx,
        playerClanId: this.playerClanId,
        gold: this.gold,
        rice: this.rice,
        ap: this.ap,
        coalitionFormed: this.coalitionFormed,
        alliances: this.alliances,
        allianceCooldown: this.allianceCooldown || {},
        currentScenarioId: this.currentScenarioId,
        currentDifficulty: this.currentDifficulty,
        provincesDelta: provincesDelta,
        officersDelta: officersDelta,
        foundingLeaderNames: this.foundingLeaderNames || {},
        lastDaimyoNames: this.lastDaimyoNames || {},
        kiyohiraFujiwaraAccepted: !!this.kiyohiraFujiwaraAccepted,
        kiyohiraSurnameDeclined: !!this.kiyohiraSurnameDeclined,
        // 歴史イベントの進行（再読込で同じイベントが二重に出ないように）
        historyStateVersion: 1,
        triggeredHistoricalEvents: [...(this.triggeredHistoricalEvents || [])],
        happenedEvents: [...(this.happenedEvents || [])],
        pendingHistoricalEvents: this.pendingHistoricalEventItems(),
        historyCheckPending: !!this._historyCheckPending,
        honnojiSplit: !!this.honnojiSplit,
        honnoujiAverted: !!this.honnoujiAverted,
        okehazamaOccurred: !!this.okehazamaOccurred,
        kanazawaOccurred: !!this.kanazawaOccurred,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem('sengoku_save_data', JSON.stringify(saveData));
    } catch (e) {
      console.warn('Auto-save failed:', e);
    }
  },

  loadGameData(data) {
    this.resetHistoricalEventRuntime();
    this.year = data.year;
    this.seasonIdx = data.seasonIdx;
    this.playerClanId = data.playerClanId;
    this.gold = data.gold;
    this.rice = data.rice;
    this.ap = data.ap;
    this.coalitionFormed = data.coalitionFormed;
    this.currentScenarioId = data.currentScenarioId || '1560';
    this.currentDifficulty = data.currentDifficulty || 'normal';
    this.alliances = this.normalizeAlliances(
      data.alliances || this.currentScenario?.alliances || [],
      this.year,
      this.seasonIdx
    );
    this.allianceCooldown = data.allianceCooldown || {};

    // 1. 領国データの復元 (差分マージ or 旧形式復元)
    if (Array.isArray(data.provincesDelta)) {
      const baseProvs = (window.PROVINCES_DATA && window.PROVINCES_DATA.length > 0)
        ? window.PROVINCES_DATA
        : (typeof INITIAL_PROVINCES !== 'undefined' ? INITIAL_PROVINCES : []);
      const deltaMap = new Map(data.provincesDelta.map(d => [d.id, d]));
      this.provinces = baseProvs.map(bp => {
        const p = JSON.parse(JSON.stringify(bp));
        const delta = deltaMap.get(p.id);
        if (delta) {
          if (delta.ownerId !== undefined) p.ownerId = delta.ownerId;
          if (delta.troops !== undefined) p.troops = delta.troops;
          if (delta.rice !== undefined) p.rice = delta.rice;
          if (delta.gold !== undefined) p.gold = delta.gold;
          if (delta.commerce !== undefined) p.commerce = delta.commerce;
          if (delta.defense !== undefined) p.defense = delta.defense;
          if (delta.order !== undefined) p.order = delta.order;
          if (delta.governance !== undefined) p.governance = delta.governance;
          if (delta.jodaiId !== undefined) {
            p.jodaiId = delta.jodaiId;
            p.governorId = delta.jodaiId;
          }
          if (delta.isCapital !== undefined) p.isCapital = delta.isCapital;
        }
        return p;
      });
    } else if (Array.isArray(data.provinces)) {
      this.provinces = data.provinces;
    }
    // 古い壊れたセーブデータ (NaN・undefined) もここで修復する
    (this.provinces || []).forEach(p => this.normalizeProvince(p));

    // 2. 武将データの復元 (差分マージ or 旧形式復元)
    if (Array.isArray(data.officersDelta) && Array.isArray(window.OFFICERS_MASTER)) {
      const deltaMap = new Map(data.officersDelta.map(d => [d.id, d]));
      const masterMap = new Map(window.OFFICERS_MASTER.map(m => [m.id, m]));
      this.activeOfficers = [];
      data.officersDelta.forEach(d => {
        const master = masterMap.get(d.id);
        if (master) {
          const off = JSON.parse(JSON.stringify(master));
          if (d.clanId !== undefined) off.clanId = d.clanId;
          off.assignedProvId = d.assignedProvId || null;
          off.provId = off.assignedProvId;
          off.isDaimyo = !!d.isDaimyo;
          off.hasBeenDaimyo = !!d.hasBeenDaimyo;
          off.isCastellan = !!d.isCastellan;
          off.isDead = !!d.isDead;
          if (d.loyalty !== undefined) off.loyalty = d.loyalty;
          if (d.actionDone !== undefined) off.actionDone = !!d.actionDone;
          this.activeOfficers.push(off);
        }
      });
      this.officers = this.activeOfficers;
    } else if (data.activeOfficers) {
      this.activeOfficers = data.activeOfficers;
      this.officers = this.activeOfficers;
    }
    this.updateActiveOfficers();

    const loadedScen = (typeof SCENARIOS !== 'undefined' ? SCENARIOS : []).find(s => String(s.id) === String(this.currentScenarioId));
    if (loadedScen) this.currentScenario = loadedScen;
    if (this.currentScenario && this.activeOfficers) {
      this.resolveOfficerAffiliations(this.currentScenario);
    }
    this.foundingLeaderNames = data.foundingLeaderNames || this.foundingLeaderNames || {};
    this.lastDaimyoNames = data.lastDaimyoNames || { ...(this.foundingLeaderNames || {}) };
    this.kiyohiraFujiwaraAccepted = !!data.kiyohiraFujiwaraAccepted;
    this.kiyohiraSurnameDeclined = !!data.kiyohiraSurnameDeclined;
    this.triggeredHistoricalEvents = new Set(Array.isArray(data.triggeredHistoricalEvents) ? data.triggeredHistoricalEvents : []);
    this.happenedEvents = new Set(Array.isArray(data.happenedEvents) ? data.happenedEvents : []);
    this.honnojiSplit = !!data.honnojiSplit;
    this.honnoujiAverted = !!data.honnoujiAverted;
    this.okehazamaOccurred = !!data.okehazamaOccurred;
    this.kanazawaOccurred = !!data.kanazawaOccurred;
    const hasHistoryState = Number(data.historyStateVersion) >= 1;
    if (hasHistoryState) {
      this.releasePendingHistoricalEvents(data.pendingHistoricalEvents);
    } else {
      this.sealCurrentSeasonHistoricalEvents();
    }
    this.updateKiyohiraSurname(false);

    const templateDaimyo = (typeof DAIMYOS !== 'undefined' ? DAIMYOS : []).find(x => x.id === this.playerClanId);
    if (templateDaimyo) {
      this.playerDaimyo = JSON.parse(JSON.stringify(templateDaimyo));
    } else {
      const scen = (typeof SCENARIOS !== 'undefined' ? SCENARIOS : []).find(s => String(s.id) === String(this.currentScenarioId));
      const found = scen?.playables.find(d => d.id === this.playerClanId) || scen?.playables[0];
      this.playerDaimyo = found ? JSON.parse(JSON.stringify(found)) : null;
    }
    const livingLord = (this.activeOfficers || []).find(o => o.clanId === this.playerClanId && o.isDaimyo && !o.isDead);
    if (livingLord && this.playerDaimyo) {
      this.playerDaimyo.name = livingLord.name;
      this.playerDaimyo.officerId = livingLord.id;
      this.playerDaimyo.clan = this.getClanFamilyName(this.playerClanId);
    }

    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    if (myProvs.length > 0) {
      this.selectProvince(myProvs[0].id);
    }

    this.music.init();
    this.music.playTrack(this.getSeasonTrackKey());
    this.updateUI();
    this.log(`【戦況再開】${this.year}年 ${this.seasonNames[this.seasonIdx]}の記録から戦況を再開しました！`, 'important');
    Swal.fire({ icon: 'success', title: '戦況再開完了', text: `${this.playerDaimyo?.name || ''}公の覇業を再開しました。`, background: '#241710', color: '#fff' });
    // 選ぶ前に保存された今季のイベントを出し直す（発火済みのものは出ない）
    if (hasHistoryState) this.scheduleHistoricalEventCheck(900);
  },

  // ============================================================================
  // 天下統一偉業 ＆ 征夷大将軍宣下 ＆ 御家滅亡
  // ============================================================================,

  checkEndGameConditions() {
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    
    // 全領国完全統一（全72州制覇）
    if (myProvs.length >= this.provinces.length && this.provinces.length > 0) {
      this.triggerVictory(false);
      return true;
    }

    // 山城(yamashiro/kyoto)領有 かつ 天下の過半（または30州以上）領有で征夷大将軍宣下
    const hasKyoto = myProvs.some(p => p.id === 'yamashiro' || p.id === 'kyoto');
    const threshold = Math.min(30, Math.floor(this.provinces.length * 0.45));
    if (!this.shogunAppointed && hasKyoto && myProvs.length >= threshold) {
      this.triggerShogunAppointment();
      return true;
    }

    return false;
  },

  triggerShogunAppointment() {
    this.shogunAppointed = true; // 確実にフラグを立てて毎ターンブロックを防止
    this.audio.playHoragai();
    this.music.playTrack('advantage');

    // 領国・勢力マップを確実に最新状態に更新
    this.updateUI();

    const modal = document.getElementById('shogunModal');

    if (!modal) {
      // 万一モーダルDOMが見つからない場合のフォールバック
      this.shogunAppointed = true;
      this.log('👑【征夷大将軍宣下】朝廷より正二位・征夷大将軍の宣下を受けました！全土統一の覇道を邁進します！', 'important');
      if (window.Swal) {
        Swal.fire({
          icon: 'success',
          title: '👑 征夷大将軍 宣下！',
          text: '朝廷より正二位・征夷大将軍に補任されました！天下統一へ向け全軍を指揮しましょう！',
          background: '#241710',
          color: '#ffd700'
        });
      }
      return;
    }

    const daimyoTitle = `${this.playerDaimyo?.clan || ''} 当主 ${this.playerDaimyo?.name || ''} 公`;
    const nameEl = document.getElementById('shogunDaimyoName');
    if (nameEl) nameEl.textContent = daimyoTitle;

    try {
      this.audio.playGrandFanfare?.();
      this.music.playTrack('shogun');
    } catch(e) {}

    modal.classList.remove('hidden');
  },

  closeEndingRoll() {
    const rollModal = document.getElementById('endingRollModal');
    if (rollModal) rollModal.classList.add('hidden');

    if (this._rollAnimId) cancelAnimationFrame(this._rollAnimId);
    if (this._sakuraAnimId) cancelAnimationFrame(this._sakuraAnimId);

    // victoryModal（詳細結果モーダル）を表示
    const modal = document.getElementById('victoryModal');
    if (modal) modal.classList.remove('hidden');
  },

  triggerVictory(isShogunRoute = false) {
    this._isShogunRoute = isShogunRoute;

    const modal = document.getElementById('victoryModal');
    if (!modal) return;

    const subTitleEl = document.getElementById('victorySubTitle');
    const mainTitleEl = document.getElementById('victoryMainTitle');
    const daimyoNameEl = document.getElementById('victoryDaimyoName');
    const statsEl = document.getElementById('victoryStatsSummary');
    const chronicleEl = document.getElementById('victoryChronicleText');

    const clanName = this.playerDaimyo.clan;
    const daimyoName = this.playerDaimyo.name;
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);

    if (isShogunRoute) {
      if (subTitleEl) subTitleEl.textContent = '【朝廷勅命・天下静謐の武門棟梁】';
      if (mainTitleEl) mainTitleEl.textContent = '❖ 征夷大将軍就任・天下泰平の幕府開府 ❖';
    } else {
      if (subTitleEl) subTitleEl.textContent = '【前人未到・日本全五拾州完全統一】';
      if (mainTitleEl) mainTitleEl.textContent = '❖ 天下布武・不滅の大覇業達成 ❖';
    }

    if (daimyoNameEl) daimyoNameEl.textContent = `${clanName} 征夷大将軍 ${daimyoName}`;
    if (statsEl) {
      statsEl.textContent = `${this.year}年 ${this.seasonNames[this.seasonIdx]} 達成 ｜ 支配領国: ${myProvs.length}州 ｜ 激闘戦歴: ${this.stats.battlesWon}勝 (${this.stats.battlesFought}戦)`;
    }

    const ep = DAIMYO_EPILOGUES[this.playerClanId] || {
      regime: `${clanName}幕府・天下泰平の新体制`,
      capital: `${daimyoName}公の居城（京洛ならびに天下の要衝）`,
      pillar1: '万民の生業を安堵し、武力による横暴を厳禁とする徳政令と武家諸法度を敷いた。',
      pillar2: '新田開拓と街道・河川の整備を全国で推進し、飢饉なき豊かな国づくりを成し遂げた。',
      pillar3: '諸大名との和睦と公正な統治を確立し、百余年にわたる乱世の争乱を永遠に終焉させた。',
      future10: '【統一後十年：礎の時代】天下普請と新法度の敷設。荒廃した山河が蘇り、民百姓の安穏な耕作が戻った。',
      future50: '【統一後五十年：文化と産業の開花】二代・三代へと政権が継承され、街道と港湾が結ばれ空前の好景気を迎えた。',
      future100: '【統一後百年〜近代へ：悠久の泰平】百年の平和が人々の心を潤し、夜も戸を鎖さぬ世界無比の平和国家が完成した。',
      historianQuote: '『乱世の塗炭の苦しみから人々を救い出し、永遠の泰平を築いたその英名は、未来永劫語り継がれるであろう』'
    };

    const routeStory = isShogunRoute
      ? `<p style="margin-bottom:12px; color:#ffd700; font-size:12.5pt; font-weight:bold;">
          「山城に入洛し都の戦乱を鎮定、天下三十有余州を統べる武威と仁徳を讃え、朝廷より征夷大将軍の重職を拝命す――」
        </p>
        <p style="margin-bottom:12px; text-indent:1.5em;">
          公儀の威信はここに甦り、荒廃していた都大路には満開の桜とともに歓喜の民の声が響き渡りました。諸国の武将たちは争いの太刀を収め、新たな武門の棟梁の前に恭しくひれ伏しました。武力による威嚇のみに頼らず、法と信義、そして民への慈悲を以て治める新たな武家政権がここに誕生したのです。
        </p>`
      : `<p style="margin-bottom:10px; color:#ffd700; font-size:12.5pt; font-weight:bold;">
          「北は蝦夷松前より南は薩摩大隅まで、日の本全土を完全に統一せり――」
        </p>
        <p style="margin-bottom:10px; text-indent:1.5em;">
          日本全土の完全平定。幾多の激闘を戦い抜き、倒れていった忠勇の将兵たちの想いを胸に、貴家はついに日の本すべての頂点へと登りつめました。もはやこの国土に刀を向け合う敵はなく、八百万の民が夜を徹して平和を喜び合いました。
        </p>`;

    if (chronicleEl) {
      chronicleEl.innerHTML = `
        <div style="border-bottom: 1px solid rgba(255,215,0,0.35); padding-bottom: 8px; margin-bottom: 12px;">
          ${routeStory}
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
          <!-- 左カラム：施政大綱・公儀の礎 -->
          <div style="background: rgba(212,175,55,0.08); border: 1px solid #8c734b; border-radius: 6px; padding: 12px 16px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <h3 style="color:var(--gold-bright); font-size:12.5pt; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
                <span>📜</span> <span>施政大綱：${ep.regime}</span>
              </h3>
              <p style="margin-bottom:6px; font-size: 11.5pt; color:#e0d0b0;"><strong>【政庁本拠】：</strong>${ep.capital}</p>
              <ul style="padding-left:18px; line-height:1.8; font-size: 11.5pt; color:#f7f1e3; margin: 0;">
                <li style="margin-bottom: 4px;"><strong>【法治・道義】：</strong>${ep.pillar1}</li>
                <li style="margin-bottom: 4px;"><strong>【産業・民生】：</strong>${ep.pillar2}</li>
                <li style="margin-bottom: 4px;"><strong>【秩序・泰平】：</strong>${ep.pillar3}</li>
              </ul>
            </div>
          </div>

          <!-- 右カラム：百年の変遷と歴史家の総評 -->
          <div style="background: rgba(0,0,0,0.45); border: 1px solid #775533; border-radius: 6px; padding: 12px 16px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <h3 style="color:#ffd700; font-size:12pt; margin-bottom:6px;">
                ❖ この幕府が紡いだ「その後の日本」（百年の変遷）
              </h3>
              <div style="font-size: 11pt; color:#ddd; margin-bottom:6px; line-height: 1.6;">${ep.future10}</div>
              <div style="font-size: 11pt; color:#ddd; margin-bottom:6px; line-height: 1.6;">${ep.future50}</div>
              <div style="font-size: 11pt; color:#ddd; margin-bottom:6px; line-height: 1.6;">${ep.future100}</div>
            </div>
            <div style="font-size: 11pt; color:#ffd700; font-style:italic; margin-top:6px; border-top:1px dashed #664422; padding-top:6px;">
              ${ep.historianQuote}
            </div>
          </div>
        </div>

        <div style="border-top: 1px dashed #665533; padding-top: 8px; font-style: italic; color: #ffd700; font-size: 11.5pt; text-align: center; line-height: 1.8;">
          「武士が捧げし至誠は豊かなる国土を育み、民が流した汗は永遠の泰平の礎となった。<br>
          乱世の闇を切り裂き、輝かしき黎明をもたらした貴家の徳政と英名は、歴史の彼方まで語り継がれるであろう――」
        </div>
      `;
    }

    // 特別な体験として、まずは感動の全画面シアター・エンドロールから幕を開ける！
    this.startEndingRoll(isShogunRoute);
  },

  triggerDefeat(reason) {
    this.music.playTrack('defeat');
    const modal = document.getElementById('defeatModal');
    if (modal) {
      const msgEl = document.getElementById('defeatMessage');
      if (msgEl) {
        msgEl.textContent = reason === 'no-heir'
          ? '後継ぎがいないため滅亡'
          : '全ての領国を失い、貴家の覇業は露と消え去りました。';
      }
      document.getElementById('defeatQuoteText').textContent = '「露と落ち 露と消えにし 我が身かな 浪速のことも 夢のまた夢」';
      modal.classList.remove('hidden');
    }
  },

  brightenHexColor(hex, percent) {
    if (!hex || hex[0] !== '#') return '#ffd700';
    let r = parseInt(hex.substring(1, 3), 16) || 0;
    let g = parseInt(hex.substring(3, 5), 16) || 0;
    let b = parseInt(hex.substring(5, 7), 16) || 0;

    r = Math.min(255, Math.floor(r + (255 - r) * (percent / 100)));
    g = Math.min(255, Math.floor(g + (255 - g) * (percent / 100)));
    b = Math.min(255, Math.floor(b + (255 - b) * (percent / 100)));

    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  },

  // 大名家カラーの半透明Glow用RGBA文字列生成,

  getClanGlowColor(clanId, alpha = 0.75) {
    const hex = this.getClanHighlightColor(clanId);
    let r = parseInt(hex.substring(1, 3), 16) || 255;
    let g = parseInt(hex.substring(3, 5), 16) || 215;
    let b = parseInt(hex.substring(5, 7), 16) || 0;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  },

  // ============================================================================
  // 単一方向データフロー: 状態を変えたら必ず updateUI() で HUD・地図・選択国パネルを再描画
  // updateStatusHeader / updateMapDisplay は低レベルの描画関数（直接呼ばず updateUI を使う）
  // ============================================================================,

  updateUI(opts = {}) {
    if (this._inUpdateUI) return; // selectProvince 経由の再入を防止
    this._inUpdateUI = true;
    try {
      this.updateStatusHeader();
      const provId = opts.provId !== undefined ? opts.provId : this.selectedProvId;
      const refreshPanel = opts.panel !== false;
      const prov = provId ? (this.provinces || []).find(x => x.id === provId) : null;
      if (refreshPanel && prov && document.getElementById('provDetailBox')) {
        this.selectProvince(provId); // 内部で updateMapDisplay も実行
      } else {
        this.updateMapDisplay();
      }
      this.updateMapHeatLegend();
    } finally {
      this._inUpdateUI = false;
    }
  },

  initSeasonParticles() {
    if (!this.seasonCanvas) return;
    const w = this.seasonCanvas.width || 800;
    const h = this.seasonCanvas.height || 600;
    this.seasonParticles = [];

    const s = this.seasonIdx; // 0:春, 1:夏, 2:秋, 3:冬
    const isBlizzard = this.currentWeather === '大雪' || this.currentWeather === '吹雪';
    const count = (s === 3 && isBlizzard) ? 60 : 35;

    for (let i = 0; i < count; i++) {
      this.seasonParticles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        size: Math.random() * 5 + 3,
        speedY: Math.random() * 1.5 + 0.8,
        speedX: (Math.random() - 0.5) * 1.2,
        angle: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.04,
        opacity: Math.random() * 0.5 + 0.35,
        flip: Math.random() * Math.PI,
        flipSpeed: Math.random() * 0.03 + 0.01
      });
    }
  },

  updateSeasonVisuals() {
    this.initSeasonParticles();
  },

  showSeasonNoticeBanner(year, seasonName, weather) {
    const banner = document.getElementById('seasonNoticeBanner');
    if (!banner) return;
    const icons = ['🌸', '☀️', '🍁', '❄️'];
    const seasonIcon = icons[this.seasonIdx] || '📜';
    banner.innerHTML = `
      <div style="font-size: 12pt; color:var(--gold); letter-spacing:3px; margin-bottom:4px;">❖ 季節の移ろい ❖</div>
      <div style="display:flex; align-items:center; justify-content:center; gap:10px;">
        <span style="font-size:24pt;">${seasonIcon}</span>
        <span>${year}年 ${seasonName}</span>
        <span style="font-size:13pt; color:#ffdd88; font-weight:normal; margin-left:6px;">【${weather}】</span>
      </div>
    `;
    banner.classList.add('show');
    const bannerDuration = this.isAutoPlay ? Math.min(1800, Math.round(this.autoPlaySpeed * 800)) : 1800;
    setTimeout(() => {
      banner.classList.remove('show');
    }, bannerDuration);
  },

  getHistoricalEventsMaster() {
    return window.HISTORICAL_CHOICE_EVENTS || [];
  },

  /** data.js の HISTORICAL_EVENT_RULES（イベントIDごとの特殊扱い） */

  historicalEventRules() {
    return window.HISTORICAL_EVENT_RULES || {};
  },

  /** ルールの ID 配列にイベントが含まれるか */

  eventRuleHas(listKey, evId) {
    const list = this.historicalEventRules()[listKey];
    return Array.isArray(list) && !!evId && list.includes(evId);
  },

  /** ルールの ID→値 表から値を取る */

  eventRuleFor(mapKey, evId) {
    const map = this.historicalEventRules()[mapKey];
    return (map && evId && Object.prototype.hasOwnProperty.call(map, evId)) ? map[evId] : null;
  },

  /** 本能寺型（領地分割＋後継選択）のイベントか */

  isSuccessionEvent(ev) {
    return !!(ev && (ev.isHonnouji || ev.chooseSuccessor || this.eventRuleHas('successionEvents', ev.id)));
  },

  /** フラグが立っていると起こさないイベントか */

  eventBlockedByFlag(evId) {
    const gates = this.historicalEventRules().skipWhenFlag || {};
    return Object.entries(gates).some(([flag, ids]) => !!this[flag] && Array.isArray(ids) && ids.includes(evId));
  },

  /** ルールが指定するフラグを立てる（許可された真偽フラグだけ） */

  setHistoricalFlag(flag) {
    const allowed = ['honnoujiAverted', 'okehazamaOccurred', 'kanazawaOccurred'];
    if (allowed.includes(flag)) this[flag] = true;
  },

  /** 史実適用時の付帯処理（フラグ・改名）。hook は許可リストのみ */

  runHistoricalApplyHooks(evId) {
    const rule = this.eventRuleFor('onApply', evId);
    if (!rule) return;
    if (rule.flag) this.setHistoricalFlag(rule.flag);
    const hooks = {
      updateTokugawaSurname: () => this.updateTokugawaSurname(true),
      updateKiyohiraSurname: () => this.updateKiyohiraSurname(true)
    };
    if (rule.hook && hooks[rule.hook]) hooks[rule.hook]();
  },

  historicalEventLinks() {
    return window.HISTORICAL_EVENT_LINKS || [];
  },

  /** 豊作など再発しうるイベントは年・季節付きで発火済みを記録する */

  historicalOccurrenceId(ev) {
    if (!ev || !ev.id) return null;
    if (this.eventRuleHas('repeatablePerSeason', ev.id)) return `${ev.id}:${this.year}:${this.seasonIdx}`;
    return ev.id;
  },

  continueAfterHistoricalEvent() {
    const resolve = this._historyEventDone;
    this._historyEventDone = null;
    if (typeof resolve === 'function') {
      resolve();
      return;
    }
    // フォールバック（Promise 外から呼ばれた場合）。走行中の待ち行列には触らない
    if (!this._historyQueueRunning) void this.processHistoricalEventQueue();
  },

  async processHistoricalEventQueue() {
    if (this._historyQueueRunning) return;
    if (!this.pendingHistoryQueue || !this.pendingHistoryQueue.length) {
      this.resumeAutoPlayAfterEvent();
      return;
    }
    this._historyQueueRunning = true;
    if (this.isAutoPlay) this.pauseAutoPlayForEvent();
    let interruptedByBattle = false;
    try {
      while (this.pendingHistoryQueue && this.pendingHistoryQueue.length) {
        if (this.inBattle) { interruptedByBattle = true; break; }
        const next = this.pendingHistoryQueue.shift();
        if (!next || !next.ev) continue;
        // ダイアログ呼び出し直前に確実に発火済みフラグを立てる
        this.triggeredHistoricalEvents = this.triggeredHistoricalEvents || new Set();
        this.happenedEvents = this.happenedEvents || new Set();
        const occId = this.historicalOccurrenceId(next.ev);
        this.triggeredHistoricalEvents.add(occId);
        this.happenedEvents.add(occId);
        this._historyCurrentItem = next;
        await new Promise((resolve) => {
          this._historyEventDone = resolve;
          try {
            if (next.type === 'data') this.fireHistoricalEvent(next.ev);
            else this.showHistoricalEvent(next.ev);
          } catch (e) {
            console.error('historical event failed', next.ev && next.ev.id, e);
            this._historyEventDone = null;
            resolve();
          }
        });
        this._historyCurrentItem = null;
      }
    } finally {
      this._historyQueueRunning = false;
      this._historyEventDone = null;
      this._historyCurrentItem = null;
      if (interruptedByBattle) {
        // 残りは合戦後に出す（取りこぼし・永久待機を防ぐ）
        this.resumeHistoryQueueWhenFree();
      } else {
        this.resumeAutoPlayAfterEvent();
        // 選択結果を記録しておき、再読込で同じイベントが出直さないようにする
        if ((this.provinces || []).some(p => p.ownerId === this.playerClanId)) this.autoSave(true);
      }
    }
  },

  /** 史実の前提（当事者の家が地図上にいるか）。満たさない出来事は起こさない */

  historicalEventPrereqMet(ev) {
    if (!ev) return false;
    const required = Array.isArray(ev.requiresClans) ? ev.requiresClans : [];
    return required.every(clanId => this.isClanExtant(this.resolveEventTargetClan(clanId) || clanId));
  },

  /** 実際に動かす領地。onlyFrom があれば、その家の領国だけを動かす（よそへ移った国は奪わない） */

  eventTerritoryFor(ev, changes) {
    const territory = changes && changes.territory;
    if (!territory || typeof territory !== 'object') return territory;
    const collapse = ev ? this.eventRuleFor('clanCollapse', ev.id) : null;
    if (collapse && collapse.from && collapse.to) {
      // 家の滅亡（山崎の明智など）：その家に残る領国をすべて勝者へ。手を離れた国は動かさない
      const result = {};
      (this.provinces || []).forEach(p => { if (p.ownerId === collapse.from) result[p.id] = collapse.to; });
      return result;
    }
    const from = ev && Array.isArray(ev.onlyFrom) ? ev.onlyFrom : null;
    if (!from || !from.length) return territory;
    const fromIds = new Set(from.map(id => this.resolveEventTargetClan(id) || id).concat(from));
    const result = {};
    for (const [pId, owner] of Object.entries(territory)) {
      const prov = (this.provinces || []).find(p => p.id === pId);
      if (prov && fromIds.has(prov.ownerId)) result[pId] = owner;
    }
    return result;
  },

  /** 史実を適用しても何も変わらない出来事（領地がすでに史実どおり）か */

  isHistoricalEventNoop(ev) {
    if (!ev || ev.forced || ev.onReject || this.isSuccessionEvent(ev)) return false;
    if (this.eventRuleHas('neverNoop', ev.id)) return false;
    const ch = ev.changes || {};
    if (!ch.territory) return false;
    if (ch.famine || ch.appoint || Number(ch.gold) || Number(ch.rice) || Number(ch.troops)) return false;
    if (this.hasEventExtras(ch)) return false;
    const territory = this.eventTerritoryFor(ev, ch) || {};
    return Object.entries(territory).every(([pId, raw]) => {
      const prov = (this.provinces || []).find(p => p.id === pId);
      if (!prov) return true;
      const to = this.resolveEventTargetClan(raw) || raw;
      return prov.ownerId === to;
    });
  },

  /** 前提を欠いた・効果のない出来事を、出さずに済ませる（対の選択イベントも封じる） */

  sealSkippedHistoricalEvent(ev, link, reason) {
    this.happenedEvents.add(ev.id);
    this.triggeredHistoricalEvents.add(ev.id);
    if (link) this.triggeredHistoricalEvents.add(link.choiceId);
    this.sealRebellionPair(ev.id);
    if (reason === 'prereq') {
      const flag = this.eventRuleFor('setFlagOnPrereqSkip', ev.id);
      if (flag) this.setHistoricalFlag(flag);
    }
    if (reason === 'noop') {
      this.log(`📜【歴史の流れ】${ev.title}：領地はすでに史実どおりのため、変化はありません。`, 'normal');
    }
  },

  checkHistoricalEvents() {
    if (this.inBattle) return;
    if (this.isHistoricalEventBusy()) return;

    this.happenedEvents = this.happenedEvents || new Set();
    this.triggeredHistoricalEvents = this.triggeredHistoricalEvents || new Set();
    const currentSeasonName = this.seasonNames[this.seasonIdx];
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId));
    const master = this.getHistoricalEventsMaster();
    const links = this.historicalEventLinks();
    const choiceById = new Map(master.map(ev => [ev.id, ev]));
    const queue = [];

    const linkForData = (id) => links.find(link => link.dataIds.includes(id));
    const choiceEligible = (link) => {
      if (!link || this.year !== link.year || currentSeasonName !== link.season) return false;
      if (this.triggeredHistoricalEvents.has(link.choiceId)) return false;
      const choice = choiceById.get(link.choiceId);
      if (!choice) return false;
      if (choice.scenarioId !== '*' && String(choice.scenarioId) !== String(this.currentScenarioId)) return false;
      try { return !!choice.check(this); } catch (e) { return false; }
    };
    const queueChoice = (ev, link) => {
      if (!ev) return;
      const occId = this.historicalOccurrenceId(ev);
      if (this.triggeredHistoricalEvents.has(occId) || this.happenedEvents.has(occId)) return;
      // キュー投入時点でもフラグを立て、同一ターン内の再収集を防ぐ
      this.triggeredHistoricalEvents.add(occId);
      this.happenedEvents.add(occId);
      if (link) link.dataIds.forEach(id => {
        this.happenedEvents.add(id);
        this.triggeredHistoricalEvents.add(id);
      });
      queue.push({ type: 'choice', ev });
    };

    if (window.HISTORICAL_EVENTS_DATA) {
      for (const ev of window.HISTORICAL_EVENTS_DATA) {
        if (ev.skipAuto) continue;
        if (this.happenedEvents.has(ev.id) || this.triggeredHistoricalEvents.has(ev.id)) continue;
        if (ev.scenarioId && ev.scenarioId !== '*' && scen && String(ev.scenarioId) !== String(scen.id) && String(ev.scenarioId) !== ('scen_' + scen.id)) continue;
        if (ev.year !== undefined && ev.year !== this.year) continue;
        if (ev.season !== undefined && ev.season !== currentSeasonName) continue;

        const link = linkForData(ev.id);
        if (link && this.triggeredHistoricalEvents.has(link.choiceId)) {
          this.happenedEvents.add(ev.id);
          this.triggeredHistoricalEvents.add(ev.id);
          continue;
        }
        // フラグで封じる出来事（本能寺を回避した世界の山崎・賤ヶ岳など。HISTORICAL_EVENT_RULES.skipWhenFlag）
        if (this.eventBlockedByFlag(ev.id)) {
          this.sealSkippedHistoricalEvent(ev, link, 'prereq');
          continue;
        }
        // 当事者の家が既に滅んでいる等、前提がない出来事は対の選択イベントごと起こさない
        if (!this.historicalEventPrereqMet(ev)) {
          this.sealSkippedHistoricalEvent(ev, link, 'prereq');
          continue;
        }
        if (link && choiceEligible(link)) {
          queueChoice(choiceById.get(link.choiceId), link);
          continue;
        }
        if (this.isHistoricalEventNoop(ev)) {
          this.sealSkippedHistoricalEvent(ev, link, 'noop');
          continue;
        }

        this.happenedEvents.add(ev.id);
        this.triggeredHistoricalEvents.add(ev.id);
        queue.push({ type: 'data', ev });
      }
    }

    for (const ev of master) {
      const occId = this.historicalOccurrenceId(ev);
      if (this.triggeredHistoricalEvents.has(occId) || this.happenedEvents.has(occId)) continue;
      if (ev.scenarioId !== '*' && String(ev.scenarioId) !== String(this.currentScenarioId)) continue;
      const link = links.find(item => item.choiceId === ev.id);
      if (link && (this.year !== link.year || currentSeasonName !== link.season)) continue;
      if (link) {
        const twin = (window.HISTORICAL_EVENTS_DATA || []).find(d => link.dataIds.includes(d.id));
        if (twin && !this.historicalEventPrereqMet(twin)) continue;
      }
      let ok = false;
      try { ok = !!ev.check(this); } catch (e) { ok = false; }
      if (ok) queueChoice(ev, link);
    }

    const deferred = (item) => item.type === 'choice' && this.eventRuleHas('deferToSeasonEnd', item.ev.id);
    queue.sort((a, b) => Number(deferred(a)) - Number(deferred(b)));
    this.pendingHistoryQueue = queue;
    if (queue.length) {
      if (this.isAutoPlay) this.pauseAutoPlayForEvent();
      void this.processHistoricalEventQueue();
    }
  },

  /** セーブ用：まだ選ばれていない（表示中・待機中の）歴史イベント */

  pendingHistoricalEventItems() {
    const items = [];
    if (this._historyCurrentItem && this._historyCurrentItem.ev) items.push(this._historyCurrentItem);
    (this.pendingHistoryQueue || []).forEach(item => { if (item && item.ev) items.push(item); });
    return items.map(item => ({ type: item.type, id: item.ev.id }));
  },

  /** ロード時：選ばれる前に保存されたイベントの発火済みフラグを外し、同じ季節に出し直す */

  releasePendingHistoricalEvents(pending) {
    if (!Array.isArray(pending) || !pending.length) return;
    const links = this.historicalEventLinks();
    const release = (id) => {
      this.triggeredHistoricalEvents.delete(id);
      this.happenedEvents.delete(id);
    };
    pending.forEach(item => {
      if (!item || !item.id) return;
      release(item.id);
      const link = links.find(l => l.choiceId === item.id || l.dataIds.includes(item.id));
      if (link) { release(link.choiceId); link.dataIds.forEach(release); }
      const pair = this.rebellionPairs().find(p => p.includes(item.id));
      if (pair) pair.forEach(release);
    });
  },

  /** 旧形式のセーブ：その季節のイベントは既に出たものとみなし、二重発火を防ぐ */

  sealCurrentSeasonHistoricalEvents() {
    const seasonName = this.seasonNames[this.seasonIdx];
    (window.HISTORICAL_EVENTS_DATA || []).forEach(ev => {
      if (ev.year === this.year && ev.season === seasonName) {
        this.triggeredHistoricalEvents.add(ev.id);
        this.happenedEvents.add(ev.id);
      }
    });
    this.historicalEventLinks().forEach(link => {
      if (link.year === this.year && link.season === seasonName) this.triggeredHistoricalEvents.add(link.choiceId);
    });
  },

  /** 新しいゲーム・ロードの前に、歴史イベントの進行状態を片付ける */

  resetHistoricalEventRuntime() {
    if (this._historyCheckTimer) clearTimeout(this._historyCheckTimer);
    if (this._historyQueueResumeTimer) clearTimeout(this._historyQueueResumeTimer);
    this._historyCheckTimer = null;
    this._historyQueueResumeTimer = null;
    this._historyCheckPending = false;
    this.pendingHistoryQueue = [];
    this._historyCurrentItem = null;
    const done = this._historyEventDone;
    this._historyEventDone = null;
    if (typeof done === 'function') done();
    ['historicalEventModal', 'historyEventModal'].forEach(id => {
      const el = typeof document !== 'undefined' ? document.getElementById(id) : null;
      if (el) el.classList.add('hidden');
    });
    const succ = typeof document !== 'undefined' ? document.getElementById('honnoujiSuccessorModal') : null;
    if (succ) succ.style.display = 'none';
  },

  updateCastlesForYear() {
    if (!window.HISTORICAL_CASTLE_CHANGES) return;
    this.provinces.forEach(p => {
      const changes = window.HISTORICAL_CASTLE_CHANGES[p.id];
      if (changes && Array.isArray(changes)) {
        for (const [cutoff, castleName] of changes) {
          if (this.year <= cutoff) {
            p.castle = castleName;
            p.castleName = castleName;
            break;
          }
        }
      }
    });
  },

  rebellionPairs() {
    return window.REBELLION_EVENT_PAIRS || [];
  },

  sealRebellionPair(eventId) {
    const pair = this.rebellionPairs().find(p => p.includes(eventId));
    if (!pair) return;
    this.happenedEvents = this.happenedEvents || new Set();
    this.triggeredHistoricalEvents = this.triggeredHistoricalEvents || new Set();
    this.happenedEvents.add(pair[0]);
    this.happenedEvents.add(pair[2]);
    this.triggeredHistoricalEvents.add(pair[1]);
  },

  /** 史実イベントの付帯効果：武将の死（killOfficerIds）・同盟（alliances）・兵力打撃（troopShock） */

  applyEventExtras(changes, { late = true } = {}) {
    if (!changes) return;
    let changed = false;
    const ids = (Array.isArray(changes.killOfficerIds) ? changes.killOfficerIds : []).slice();
    // chanceKills：[{ id, chance }] 合戦での討死など、確率で落命する武将（適用時に一度だけ判定）
    (Array.isArray(changes.chanceKills) ? changes.chanceKills : []).forEach(item => {
      if (!item || !item.id) return;
      const p = Number(item.chance);
      if (p > 0 && Math.random() < p && !ids.includes(item.id)) ids.push(item.id);
    });
    if (ids.length) {
      const aliases = window.OFFICER_ID_ALIASES || {};
      const idSet = new Set(ids.concat(ids.map(id => aliases[id]).filter(Boolean)));
      const fallen = [];
      const lists = [this.activeOfficers, this.officers].filter((l, i, arr) => Array.isArray(l) && arr.indexOf(l) === i);
      lists.forEach(list => list.forEach(o => {
        if (!o || !idSet.has(o.id) || o.isDead) return;
        if (o.assignedProvId) {
          const prov = (this.provinces || []).find(p => p.id === o.assignedProvId);
          if (prov && prov.governorId === o.id) prov.governorId = null;
        }
        o.isDead = true;
        o.isDaimyo = false;
        o.assignedProvId = null;
        if (!fallen.includes(o.name)) fallen.push(o.name);
      }));
      if (fallen.length) {
        this.log(`⚰️【落命】${fallen.join('・')}が世を去りました。`, 'important');
        changed = true;
      }
    }
    const shock = changes.troopShock && typeof changes.troopShock === 'object' ? changes.troopShock : null;
    if (shock) {
      for (const [rawClan, rate] of Object.entries(shock)) {
        const r = Number(rate);
        if (!(r > 0) || r === 1) continue;
        const clanId = this.resolveEventTargetClan(rawClan) || rawClan;
        (this.provinces || []).filter(p => p.ownerId === clanId).forEach(p => {
          p.troops = Math.max(300, Math.round((Number(p.troops) || 0) * r));
        });
        changed = true;
      }
    }
    const pacts = Array.isArray(changes.alliances) ? changes.alliances : [];
    pacts.forEach(pact => {
      if (!pact || !pact.a || !pact.b) return;
      const a = this.resolveEventTargetClan(pact.a) || pact.a;
      const b = this.resolveEventTargetClan(pact.b) || pact.b;
      if (a === b || !this.isClanExtant(a) || !this.isClanExtant(b)) return;
      if (typeof this.isAllied === 'function' && this.isAllied(a, b)) return;
      this.alliances = this.alliances || [];
      this.alliances.push({
        members: [a, b],
        formedYear: this.year,
        formedSeason: this.seasonIdx,
        durationSeasons: Number(pact.durationSeasons) > 0 ? Number(pact.durationSeasons) : ALLIANCE_DURATION_SEASONS
      });
      this.log(`🤝【史実同盟】${this.allianceClanLabel(a)}と${this.allianceClanLabel(b)}が${pact.label || '同盟'}を結びました。`, 'important');
      changed = true;
    });
    // breakAlliances：[{ a, b }] 謀反・決裂で同盟を破棄
    (Array.isArray(changes.breakAlliances) ? changes.breakAlliances : []).forEach(pact => {
      if (!pact || !pact.a || !pact.b || !this.alliances) return;
      const a = this.resolveEventTargetClan(pact.a) || pact.a;
      const b = this.resolveEventTargetClan(pact.b) || pact.b;
      let broke = false;
      this.alliances = this.alliances.map(group => {
        const members = this.allianceMembers(group);
        if (!members.includes(a) || !members.includes(b)) return group;
        broke = true;
        const rest = members.filter(id => id !== b);
        if (rest.length < 2) return null;
        return {
          members: rest,
          formedYear: Array.isArray(group) ? this.year : (group.formedYear ?? this.year),
          formedSeason: Array.isArray(group) ? this.seasonIdx : (group.formedSeason ?? this.seasonIdx),
          durationSeasons: this.allianceDurationOf(group)
        };
      }).filter(Boolean);
      if (broke) {
        if (typeof this.rememberAllianceBreak === 'function') this.rememberAllianceBreak([a, b]);
        this.log(`💔【同盟破棄】${this.allianceClanLabel(a)}と${this.allianceClanLabel(b)}の盟約が破れました。`, 'important');
        changed = true;
      }
    });
    // clanResources：{ clanId: { gold, rice } } 金・兵糧の増減（金蔵を持つのはプレイヤー家のみ）
    Object.entries(changes.clanResources || {}).forEach(([rawClan, res]) => {
      const clanId = this.resolveEventTargetClan(rawClan) || rawClan;
      if (!res || clanId !== this.playerClanId) return;
      if (Number(res.gold)) this.gold = Math.max(0, (Number(this.gold) || 0) + Number(res.gold));
      if (Number(res.rice)) this.rice = Math.max(0, (Number(this.rice) || 0) + Number(res.rice));
      changed = true;
    });
    if (ids.length) {
      this.syncDaimyoStatus();
      this.updateActiveOfficers();
    }
    if (late && this.applyEventLateExtras(changes)) changed = true;
    if (changed) {
      this.updateUI();
    }
  },

  /** 領地を動かした後にかける効果：国ごと・家ごとの兵力／防御／治安の変化 */

  applyEventLateExtras(changes) {
    if (!changes) return false;
    let changed = false;
    const apply = (prov, fx) => {
      if (!prov || !fx) return;
      if (Number(fx.troopsRate) > 0) prov.troops = Math.max(100, Math.round((Number(prov.troops) || 0) * Number(fx.troopsRate)));
      if (fx.troops !== undefined && Number.isFinite(Number(fx.troops))) prov.troops = Math.max(100, Math.round(Number(fx.troops)));
      if (fx.defense !== undefined && Number.isFinite(Number(fx.defense))) prov.defense = Math.max(0, Math.min(100, Math.round(Number(fx.defense))));
      if (Number(fx.defenseDelta)) prov.defense = Math.max(0, Math.min(100, (Number(prov.defense) || 0) + Number(fx.defenseDelta)));
      if (Number(fx.orderDelta)) prov.order = Math.max(0, Math.min(100, (Number(prov.order) || 0) + Number(fx.orderDelta)));
      if (Number(fx.moraleDelta)) prov.morale = Math.max(0, Math.min(100, (Number(prov.morale) || 0) + Number(fx.moraleDelta)));
      changed = true;
    };
    Object.entries(changes.clanEffects || {}).forEach(([rawClan, fx]) => {
      const clanId = this.resolveEventTargetClan(rawClan) || rawClan;
      (this.provinces || []).filter(p => p.ownerId === clanId).forEach(p => apply(p, fx));
    });
    Object.entries(changes.provinceEffects || {}).forEach(([pId, fx]) => {
      apply((this.provinces || []).find(p => p.id === pId), fx);
    });
    return changed;
  },

  /** 付帯効果のキー（リンク先データの転記・判定用） */

  eventExtraKeys() {
    return ['killOfficerIds', 'chanceKills', 'troopShock', 'alliances', 'breakAlliances', 'clanResources', 'clanEffects', 'provinceEffects'];
  },

  hasEventExtras(changes) {
    if (!changes) return false;
    return this.eventExtraKeys().some(key => {
      const v = changes[key];
      if (Array.isArray(v)) return v.length > 0;
      return !!(v && typeof v === 'object' && Object.keys(v).length > 0);
    });
  },

  describeEventExtras(changes) {
    if (!changes) return [];
    const lines = [];
    const officers = window.OFFICERS_MASTER || [];
    (changes.killOfficerIds || []).forEach(id => {
      const o = (this.activeOfficers || []).find(x => x && x.id === id) || officers.find(x => x && x.id === id);
      if (o && !o.isDead) lines.push(`${o.name}が落命する`);
    });
    Object.entries(changes.troopShock || {}).forEach(([clan, rate]) => {
      const r = Number(rate);
      if (r > 0 && r !== 1) lines.push(`${this.getClanDisplayName(this.resolveEventTargetClan(clan) || clan)}の兵力を${Math.round(r * 100)}%にする`);
    });
    (changes.alliances || []).forEach(pact => {
      if (!pact) return;
      const a = this.getClanDisplayName(this.resolveEventTargetClan(pact.a) || pact.a);
      const b = this.getClanDisplayName(this.resolveEventTargetClan(pact.b) || pact.b);
      lines.push(`${a}と${b}が${pact.label || '同盟'}を結ぶ`);
    });
    (changes.chanceKills || []).forEach(item => {
      if (!item || !item.id) return;
      const o = (this.activeOfficers || []).find(x => x && x.id === item.id) || officers.find(x => x && x.id === item.id);
      if (o && !o.isDead) lines.push(`${o.name}が${Math.round(Number(item.chance || 0) * 100)}%の確率で討死する`);
    });
    (changes.breakAlliances || []).forEach(pact => {
      if (!pact) return;
      const a = this.getClanDisplayName(this.resolveEventTargetClan(pact.a) || pact.a);
      const b = this.getClanDisplayName(this.resolveEventTargetClan(pact.b) || pact.b);
      lines.push(`${a}と${b}の同盟が破れる`);
    });
    Object.entries(changes.clanResources || {}).forEach(([clan, res]) => {
      if (!res) return;
      const clanId = this.resolveEventTargetClan(clan) || clan;
      if (clanId !== this.playerClanId) return;
      if (Number(res.gold)) lines.push(`自家の金 ${res.gold > 0 ? '+' : ''}${Number(res.gold).toLocaleString('ja-JP')}`);
      if (Number(res.rice)) lines.push(`自家の兵糧 ${res.rice > 0 ? '+' : ''}${Number(res.rice).toLocaleString('ja-JP')}`);
    });
    const fxText = (fx) => {
      const parts = [];
      if (Number(fx.troopsRate) > 0) parts.push(`兵力${Math.round(Number(fx.troopsRate) * 100)}%`);
      if (fx.troops !== undefined) parts.push(`兵力${Number(fx.troops).toLocaleString('ja-JP')}に`);
      if (fx.defense !== undefined) parts.push(`城郭防御${fx.defense}に`);
      if (Number(fx.defenseDelta)) parts.push(`城郭防御${fx.defenseDelta > 0 ? '+' : ''}${fx.defenseDelta}`);
      if (Number(fx.orderDelta)) parts.push(`治安${fx.orderDelta > 0 ? '+' : ''}${fx.orderDelta}`);
      if (Number(fx.moraleDelta)) parts.push(`士気${fx.moraleDelta > 0 ? '+' : ''}${fx.moraleDelta}`);
      return parts.join('・');
    };
    Object.entries(changes.clanEffects || {}).forEach(([clan, fx]) => {
      const t = fx ? fxText(fx) : '';
      if (t) lines.push(`${this.getClanDisplayName(this.resolveEventTargetClan(clan) || clan)}の全領国：${t}`);
    });
    Object.entries(changes.provinceEffects || {}).forEach(([pId, fx]) => {
      const t = fx ? fxText(fx) : '';
      if (t) lines.push(`${this.getProvinceJapaneseName(pId)}：${t}`);
    });
    return lines;
  },

  applyEventTerritory(changes) {
    if (!changes) return;
    if (!changes.territory) {
      this.applyEventExtras(changes);
      return;
    }
    this.applyEventExtras(changes, { late: false });
    const resolvedOwners = {};
    for (const newOwner of new Set(Object.values(changes.territory))) {
      resolvedOwners[newOwner] = this.resolveEventTargetClan(newOwner);
    }
    for (const [pId, rawOwner] of Object.entries(changes.territory)) {
      const newOwner = resolvedOwners[rawOwner] || rawOwner;
      const prov = this.provinces.find(p => p.id === pId);
      if (prov) {
        prov.ownerId = newOwner;
        prov.troops = Math.max(3000, prov.troops || 3000);
      }
    }
    this.syncDaimyoStatus();
    if (changes.appoint) this.appointHistoricalCastellans(changes.appoint);
    this.updateActiveOfficers();
    if (this.currentScenario) this.resolveOfficerAffiliations(this.currentScenario);
    new Set(Object.values(changes.territory)).forEach(rawOwner => {
      const ownerId = this.resolveEventTargetClan(rawOwner) || rawOwner;
      if (!ownerId) return;
      if (!this.activeOfficers.some(o => o.clanId === ownerId && o.isDaimyo && !o.isDead)) {
        this.seatNamedLord(ownerId);
      }
    });
    this.applyEventLateExtras(changes);
    this.updateCastlesForYear();
    this.updateUI();
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    if (myProvs.length === 0) {
      if (this.isAutoPlay) this.stopAutoPlay('御家滅亡のため');
      setTimeout(() => { this.triggerDefeat(); }, 1200);
    }
  },

  applyRebellionFromChoice(choiceId, outcome) {
    const pair = this.rebellionPairs().find(p => p[1] === choiceId);
    const ev = (window.HISTORICAL_EVENTS_DATA || []).find(e => e.id === pair?.[0]);
    const changes = outcome === 'success' ? ev?.onReject : ev?.changes;
    this.sealRebellionPair(choiceId);
    if (changes) this.applyEventTerritory(changes);
    return changes?.message || (outcome === 'success' ? '乱は成功しました。' : '乱は鎮圧されました。');
  },

  escapeEventText(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
  },

  describeTerritoryMoves(territory) {
    if (!territory || typeof territory !== 'object') return [];
    const resolvedOwners = {};
    for (const rawOwner of new Set(Object.values(territory))) {
      resolvedOwners[rawOwner] = this.resolveEventTargetClan(rawOwner);
    }
    const lines = [];
    for (const [pId, rawOwner] of Object.entries(territory)) {
      const newOwner = resolvedOwners[rawOwner] || rawOwner;
      const prov = (this.provinces || []).find(item => item.id === pId);
      const pname = this.getProvinceJapaneseName(pId);
      const fromId = prov ? prov.ownerId : null;
      const fromName = fromId ? this.getClanDisplayName(fromId) : '無主';
      const toName = this.getClanDisplayName(newOwner);
      if (fromId && fromId === newOwner) lines.push(`${pname}は${toName}のまま`);
      else lines.push(`${pname}：${fromName} → ${toName}`);
    }
    return lines;
  },

  describeAppointLines(appoint) {
    if (!appoint || typeof appoint !== 'object') return [];
    const officers = window.OFFICERS_MASTER || [];
    const aliases = window.OFFICER_ID_ALIASES || {};
    return Object.entries(appoint).map(([pId, officerId]) => {
      const resolvedId = aliases[officerId] || officerId;
      const officer = officers.find(item => item && (item.id === officerId || item.id === resolvedId));
      const name = officer && officer.name ? officer.name : '城代';
      return `${this.getProvinceJapaneseName(pId)}の城主：${name}`;
    });
  },

  eventEffectLines(ev, branch) {
    const changes = branch === 'reject' ? ev.onReject : ev.changes;
    const rejectBonus = branch === 'reject' ? this.eventRuleFor('playerRejectBonus', ev.id) : null;
    if (rejectBonus && rejectBonus.clanId === this.playerClanId && Array.isArray(rejectBonus.previewLines)) {
      return rejectBonus.previewLines.slice();
    }
    const lines = [];
    if (changes) {
      lines.push(...this.describeTerritoryMoves(branch === 'reject' ? changes.territory : this.eventTerritoryFor(ev, changes)));
      if (branch === 'accept') lines.push(...this.describeAppointLines(changes.appoint));
      lines.push(...this.describeEventExtras(changes));
      if (changes.famine) lines.push(...this.describeFamineLines(changes.famine));
      if (Number(changes.gold)) lines.push(`金 ${changes.gold > 0 ? '+' : ''}${Number(changes.gold).toLocaleString('ja-JP')}`);
      if (Number(changes.rice)) lines.push(`兵糧 ${changes.rice > 0 ? '+' : ''}${Number(changes.rice).toLocaleString('ja-JP')}`);
      if (Number(changes.troops)) lines.push(`兵力 ${changes.troops > 0 ? '+' : ''}${Number(changes.troops).toLocaleString('ja-JP')}`);
    }
    if (branch === 'accept' && ev.id === 'evt_1088_kiyohira_fujiwara') {
      lines.push('清原領の治安 +15、兵力 +1,000');
      if (this.playerClanId === 'kiyohara') lines.push('清原家として金 +1,500、兵糧 +2,000');
    }
    if (branch === 'accept') lines.push(...(this.eventRuleFor('acceptEffectLines', ev.id) || []));
    return lines;
  },

  describeFamineLines(famine) {
    if (!famine) return [];
    const lines = [];
    const troop = Number(famine.troopRate);
    const rice = Number(famine.riceRate);
    if (troop > 0 && troop < 1) lines.push(`全国の兵力を${Math.round(troop * 100)}%まで減らす`);
    if (rice > 0 && rice < 1) lines.push(`自軍の兵糧と、諸国の収穫を${Math.round(rice * 100)}%まで減らす`);
    return lines;
  },

  describeScriptEffects(src) {
    const text = String(src || '');
    const lines = [];
    const sum = (re) => [...text.matchAll(re)].reduce((total, match) => total + Number(match[1]), 0);
    const goldPlus = sum(/gold\s*\+=\s*(\d+)/g);
    const ricePlus = sum(/rice\s*\+=\s*(\d+)/g);
    const goldMinus = sum(/gold\s*-\s*(\d+)/g);
    const riceMinus = sum(/rice\s*-\s*(\d+)/g);
    const troopPlus = [...text.matchAll(/troops\s*\+=\s*(\d+)/g)].map(match => Number(match[1]));
    const troopRatio = [...text.matchAll(/troops\s*=\s*Math\.round\([^;\n]*?\*\s*(0\.\d+)\s*\)/g)].map(match => Number(match[1]));
    const orderPlus = [...text.matchAll(/order\s*\+\s*(\d+)/g)].map(match => Number(match[1]));
    const orderMax = /order\s*=\s*100/.test(text);
    if (goldPlus) lines.push(`金 +${goldPlus.toLocaleString('ja-JP')}`);
    if (goldMinus) lines.push(`金 −${goldMinus.toLocaleString('ja-JP')}`);
    if (ricePlus) lines.push(`兵糧 +${ricePlus.toLocaleString('ja-JP')}`);
    if (riceMinus) lines.push(`兵糧 −${riceMinus.toLocaleString('ja-JP')}`);
    troopPlus.forEach(amount => lines.push(`兵力 +${amount.toLocaleString('ja-JP')}`));
    troopRatio.forEach(ratio => lines.push(`兵力を${Math.round(ratio * 100)}%まで減らす`));
    orderPlus.forEach(amount => lines.push(`治安 +${amount}`));
    if (orderMax) lines.push('治安が最大になる');
    return lines;
  },

  applyFamineShock(famine) {
    const troopRate = Number(famine?.troopRate);
    const riceRate = Number(famine?.riceRate);
    const baseRice = (prov) => {
      const init = (window.PROVINCES_DATA || []).find(item => item.id === prov.id);
      const koku = Number(init?.kokudaka) || 50000;
      return Math.max(20, Math.round(koku / 1000));
    };
    (this.provinces || []).forEach(prov => {
      if (troopRate > 0 && troopRate < 1) {
        prov.troops = Math.max(300, Math.round((Number(prov.troops) || 0) * troopRate));
      }
      if (riceRate > 0 && riceRate < 1) {
        const floor = Math.round(baseRice(prov) * 0.35);
        prov.rice = Math.max(floor, Math.round((Number(prov.rice) || floor) * riceRate));
      }
    });
    if (riceRate > 0 && riceRate < 1) {
      this.rice = Math.max(0, Math.round((Number(this.rice) || 0) * riceRate));
    }
    this.updateUI();
  },

  eventEffectHtml(lines) {
    if (!lines.length) return '<div style="margin-top:6px;">領地の移動はありません。</div>';
    const items = lines.map(line => `<li>${this.escapeEventText(line)}</li>`).join('');
    return `<ul style="margin:6px 0 0 1.2em; padding:0; text-align:left; font-size:11pt; line-height:1.55; max-height:28vh; overflow:auto;">${items}</ul>`;
  },

  choiceEffectHtml(choice, parentEv = null) {
    const src = typeof choice.action === 'function' ? String(choice.action) : '';
    const lines = [];
    const reb = src.match(/applyRebellionFromChoice\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)/);
    if (reb) {
      const pair = this.rebellionPairs().find(item => item[1] === reb[1]);
      const dataEv = (window.HISTORICAL_EVENTS_DATA || []).find(item => item.id === pair?.[0]);
      if (dataEv) {
        const changes = reb[2] === 'success' ? dataEv.onReject : dataEv.changes;
        lines.push(...this.describeTerritoryMoves(changes && changes.territory));
        if (reb[2] !== 'success') lines.push(...this.describeAppointLines(changes && changes.appoint));
        lines.push(...this.describeEventExtras(changes));
      }
    } else if (choice.isHistorical && parentEv && !/executeHonnoujiSuccession/.test(src)) {
      // 史実ルートでは、リンク先データイベントの領地（選択側が動かさない場合）と付帯効果もプレビューする
      const movesLand = /\.ownerId\s*=\s*(?!=)/.test(src);
      const link = this.historicalEventLinks().find(item => item.choiceId === parentEv.id);
      const dataEv = link ? (window.HISTORICAL_EVENTS_DATA || []).find(item => link.dataIds.includes(item.id)) : null;
      if (dataEv && dataEv.changes && !this.isSuccessionEvent(dataEv)) {
        if (!movesLand) {
          lines.push(...this.describeTerritoryMoves(this.eventTerritoryFor(dataEv, dataEv.changes)));
          lines.push(...this.describeAppointLines(dataEv.changes.appoint));
        }
        lines.push(...this.describeEventExtras(dataEv.changes));
      }
    }
    const assign = /id === '([a-z0-9_]+)'[\s\S]{0,400}?\.ownerId\s*=\s*(?:'([^']+)'|g\.playerClanId)/g;
    const seen = new Set();
    let match;
    while ((match = assign.exec(src))) {
      const pId = match[1];
      if (seen.has(pId)) continue;
      seen.add(pId);
      const raw = match[2] || this.playerClanId;
      const toId = this.resolveEventTargetClan(raw) || raw;
      const prov = (this.provinces || []).find(item => item.id === pId);
      const fromId = prov ? prov.ownerId : null;
      const pname = this.getProvinceJapaneseName(pId);
      const fromName = fromId ? this.getClanDisplayName(fromId) : '無主';
      const toName = this.getClanDisplayName(toId);
      if (fromId && fromId === toId) lines.push(`${pname}は${toName}のまま`);
      else lines.push(`${pname}：${fromName} → ${toName}`);
    }
    const extras = this.describeScriptEffects(src);
    const blocks = [];
    if (lines.length) {
      blocks.push(`<div style="margin-top:8px; font-size:11pt; color:#ffd700;">領地の変化</div>${this.eventEffectHtml(lines)}`);
    }
    if (extras.length) {
      blocks.push(`<div style="margin-top:8px; font-size:11pt; color:#ffd700;">ほかの効果</div>${this.eventEffectHtml(extras)}`);
    }
    return blocks.join('');
  },

  fireHistoricalEvent(ev) {
    this.sealRebellionPair(ev.id);
    if (this.isAutoPlay) this.pauseAutoPlayForEvent();

    try {
      this.audio.playEventNotice?.();
    } catch(e) {}
    this.music.playTrack('event');

    const modal = document.getElementById('historicalEventModal');
    if (!modal) {
      const followUp = this.applyHistoricalEventAccept(ev, { closeModal: false }) === true;
      if (!followUp) this.continueAfterHistoricalEvent();
      return;
    }

    const titleEl = document.getElementById('eventModalTitle');
    if (titleEl) titleEl.textContent = `❖ ${ev.title} ❖`;

    const subEl = document.getElementById('eventModalSubtitle');
    if (subEl) subEl.textContent = `${this.year}年 ${this.seasonNames[this.seasonIdx]}`;

    const descEl = document.getElementById('eventModalDesc');
    if (descEl) descEl.innerHTML = ev.desc;

    const noticeEl = document.getElementById('eventModalNotice');
    if (noticeEl) {
      const acceptFx = this.eventEffectHtml(this.eventEffectLines(ev, 'accept'));
      if (ev.forced) {
        noticeEl.innerHTML = `<strong>【この季節に起きること】</strong>${this.escapeEventText(ev.changes?.message || '')}${acceptFx}`;
      } else if (ev.onReject) {
        const rejectFx = this.eventEffectHtml(this.eventEffectLines(ev, 'reject'));
        noticeEl.innerHTML = `<strong>【史実を適用・乱は鎮圧】</strong>${this.escapeEventText(ev.changes?.message || '乱は鎮圧されます。')}${acceptFx}<br><strong style="color:#f39c12;">【史実を適用しない・乱は成功】</strong>${this.escapeEventText(ev.onReject.message || '乱は成功します。')}${rejectFx}`;
      } else {
        noticeEl.innerHTML = `<strong>【史実を適用すると】</strong>${this.escapeEventText(ev.changes?.message || '')}${acceptFx}<br><span style="font-size:11pt; color:#ffd700; margin-top:4px; display:inline-block;">現状維持を選ぶと、上の効果は起きません。</span>`;
      }
    }

    const acceptBtn = document.getElementById('eventModalAcceptBtn');
    const rejectBtn = document.getElementById('eventModalRejectBtn');

    if (acceptBtn) {
      const newAccept = acceptBtn.cloneNode(true);
      acceptBtn.parentNode.replaceChild(newAccept, acceptBtn);
      newAccept.textContent = ev.forced ? '承知した' : (ev.onReject ? '⚔️ 史実通り効果を適用（乱を鎮圧）' : '⚔️ 史実通り効果を適用');
      newAccept.addEventListener('click', () => {
        if (this._eventDecidedId === ev.id) return;
        this._eventDecidedId = ev.id;
        const followUp = this.applyHistoricalEventAccept(ev, { closeModal: true }) === true;
        if (!followUp) this.continueAfterHistoricalEvent();
      });
    }

    if (rejectBtn) {
      const newReject = rejectBtn.cloneNode(true);
      rejectBtn.parentNode.replaceChild(newReject, rejectBtn);
      newReject.style.display = ev.forced ? 'none' : '';
      newReject.textContent = ev.onReject ? '⚡ 史実を適用しない（乱が成功）' : '🛡️ 史実に抗い現状維持 (効果なし)';
      newReject.addEventListener('click', () => {
        if (this._eventDecidedId === ev.id) return;
        this._eventDecidedId = ev.id;
        this.audio.playHyoshigi();
        if (ev.onReject) {
          this.applyEventTerritory(ev.onReject);
          const bonus = this.eventRuleFor('playerRejectBonus', ev.id);
          if (bonus && bonus.clanId === this.playerClanId) {
            this.rice += Number(bonus.rice) || 0;
            this.gold += Number(bonus.gold) || 0;
            this.updateUI();
          }
          this.log(`⚡【史実を適用せず】${ev.title}：${ev.onReject.message || '乱は成功しました。'}`, 'important');
          modal.classList.add('hidden');
          this.music.playTrack(this.getSeasonTrackKey());
          this.continueAfterHistoricalEvent();
          return;
        }
        // 本能寺の変は起きなかった、など（HISTORICAL_EVENT_RULES.setFlagOnReject）
        const rejectFlag = this.eventRuleFor('setFlagOnReject', ev.id) || (ev.isHonnouji ? 'honnoujiAverted' : null);
        if (rejectFlag) this.setHistoricalFlag(rejectFlag);
        if (ev.id === 'evt_1088_kiyohira_fujiwara') {
          this.kiyohiraSurnameDeclined = true;
          this.kiyohiraFujiwaraAccepted = false;
          this.updateKiyohiraSurname(false);
          this.updateUI();
          this.log('🛡️【現状維持】清原清衡は清原の姓を保ち、奥州藤原氏を称しませんでした。', 'normal');
        } else {
          this.log(`🛡️【現状維持】${ev.title}：史実に抗い、現在の領土秩序を維持しました。（イベント効果なし）`, 'normal');
        }
        modal.classList.add('hidden');
        this.music.playTrack(this.getSeasonTrackKey());
        this.continueAfterHistoricalEvent();
      });
    }

    this._eventDecidedId = null;
    modal.classList.remove('hidden');
    this.log(`📜【歴史の奔流】${ev.title} が発生しました！`, 'important');
  },


  /** 家の滅亡（HISTORICAL_EVENT_RULES.clanCollapse）：当主らを落命させ、残る領国を勝者へ */

  applyClanCollapse(rule) {
    if (!rule || !rule.from || !rule.to) return;
    const deadIds = Array.isArray(rule.killOfficerIds) ? rule.killOfficerIds : [];
    const markDead = (list) => {
      (list || []).forEach(o => {
        if (!o || !this.officerIdIn(o, deadIds)) return;
        o.isDead = true;
        o.isDaimyo = false;
        o.assignedProvId = null;
      });
    };
    markDead(this.activeOfficers);
    markDead(this.officers);
    markDead(window.OFFICERS_MASTER);
    const victor = this.resolveEventTargetClan(rule.to) || rule.to;
    const minTroops = Number(rule.minTroops) || 3000;
    (this.provinces || []).forEach(prov => {
      if (prov.ownerId === rule.from) {
        prov.ownerId = victor;
        prov.troops = Math.max(minTroops, prov.troops || minTroops);
      }
    });
    this.syncDaimyoStatus();
    this.updateActiveOfficers();
    this.updateUI();
  },

  applyHistoricalEventAccept(ev, { closeModal = true } = {}) {
    const modal = document.getElementById('historicalEventModal');
    const cleanUpAndClose = () => {
      if (closeModal && modal) modal.classList.add('hidden');
      this.music.playTrack(this.getSeasonTrackKey());
    };

      if (ev.changes && ev.changes.territory) {
      // onlyFrom 指定の出来事は、その家に残る領国だけを動かす
      const territory = this.eventTerritoryFor(ev, ev.changes) || {};
      // 受け取り先は領地を動かす前に決める（途中で新勢力が出来て判定がぶれないように）
      const resolvedOwners = {};
      for (const newOwner of new Set(Object.values(territory))) {
        resolvedOwners[newOwner] = this.resolveEventTargetClan(newOwner);
      }
      for (const [pId, rawOwner] of Object.entries(territory)) {
        const newOwner = resolvedOwners[rawOwner] || rawOwner;
        const prov = this.provinces.find(p => p.id === pId);
        if (prov) {
          prov.ownerId = newOwner;
          prov.troops = Math.max(3000, prov.troops || 3000);
        }
      }
      const isHonnouji = this.isSuccessionEvent(ev);
      if (!isHonnouji) {
        this.syncDaimyoStatus();
        if (ev.changes.appoint) this.appointHistoricalCastellans(ev.changes.appoint);
        this.updateActiveOfficers();
        if (this.currentScenario) this.resolveOfficerAffiliations(this.currentScenario);
      }
      this.runHistoricalApplyHooks(ev.id);
      const collapse = this.eventRuleFor('clanCollapse', ev.id);
      if (collapse) this.applyClanCollapse(collapse);
      this.updateCastlesForYear();
      this.updateUI();

      if (isHonnouji) {
        this.executeHonnoujiSuccession();
        if (this.playerClanId === ((window.HONNOUJI_SUCCESSION_DATA || {}).formerClan || 'oda')) {
          this.audio.playFanfare();
          this.log(`⚔️【史実受容】${ev.title}：織田信長公落命。天下は分裂し後継勢力の割拠へ突入！`, 'important');
          cleanUpAndClose();
          this.showHonnoujiSuccessorSelectModal(ev);
          return true;
        }
      }

      const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
      if (myProvs.length === 0) {
        if (this.isAutoPlay) this.stopAutoPlay('御家滅亡のため');
        setTimeout(() => { this.triggerDefeat(); }, 1200);
      }
    }
    if (ev.changes && this.hasEventExtras(ev.changes)) this.applyEventExtras(ev.changes);
    if (ev.changes?.famine) this.applyFamineShock(ev.changes.famine);
    if (ev.id === 'evt_1088_kiyohira_fujiwara') {
      this.kiyohiraSurnameDeclined = false;
      this.kiyohiraFujiwaraAccepted = true;
      this.updateKiyohiraSurname(true);
      (this.provinces || []).filter(p => p.ownerId === 'kiyohara').forEach(p => {
        p.order = Math.min(100, (Number(p.order) || 0) + 15);
        p.troops += 1000;
      });
      if (this.playerClanId === 'kiyohara') {
        this.gold += 1500;
        this.rice += 2000;
      }
      this.updateUI();
    }
    this.audio.playFanfare();
    if (ev.changes?.famine && !ev.changes?.territory) {
      this.log(`🌾【飢饉】${ev.title}：${ev.changes?.message || '兵力と兵糧が大きく減りました。'}`, 'important');
    } else if (ev.id !== 'evt_1088_kiyohira_fujiwara' && !ev.changes?.territory) {
      this.log(`⚔️【史実受容】${ev.title}：${ev.changes?.message || '史実どおりの結果になりました。'}`, 'important');
    } else if (ev.id !== 'evt_1088_kiyohira_fujiwara') {
      this.log(`⚔️【史実受容】${ev.title}：史実通り領地が再編されました。（${ev.changes?.message || ''}）`, 'important');
    }
    cleanUpAndClose();
  },

  applyLinkedHistoricalDataFromChoice(ev, choice) {
    if (!ev || !choice || !choice.isHistorical) return;
    const src = typeof choice.action === 'function' ? String(choice.action) : '';
    if (/applyRebellionFromChoice|executeHonnoujiSuccession/.test(src)) return;
    // 選択側が領地を自前で動かす場合も、落命・同盟などの付帯効果はリンク先から補う
    const choiceMovesLand = /\.ownerId\s*=\s*(?!=)/.test(src);
    const link = this.historicalEventLinks().find(item => item.choiceId === ev.id);
    if (!link) return;
    const dataEv = (window.HISTORICAL_EVENTS_DATA || []).find(item => link.dataIds.includes(item.id));
    if (!dataEv || !dataEv.changes) return;
    if (this.isSuccessionEvent(dataEv)) return;

    const territory = choiceMovesLand ? {} : (this.eventTerritoryFor(dataEv, dataEv.changes) || dataEv.changes.territory || {});
    const pending = {};
    for (const [pId, raw] of Object.entries(territory)) {
      const to = this.resolveEventTargetClan(raw) || raw;
      const prov = (this.provinces || []).find(p => p.id === pId);
      if (prov && prov.ownerId !== to) pending[pId] = raw;
    }
    const payload = {};
    if (Object.keys(pending).length) payload.territory = pending;
    if (dataEv.changes.appoint && !choiceMovesLand) payload.appoint = dataEv.changes.appoint;
    this.eventExtraKeys().forEach(key => {
      if (dataEv.changes[key] !== undefined) payload[key] = dataEv.changes[key];
    });
    if (payload.territory || this.hasEventExtras(payload) || payload.appoint) {
      this.applyEventTerritory(payload);
    }
    this.runHistoricalApplyHooks(dataEv.id);
  },

  applyHistoricalChoice(ev, choice) {
    const modal = document.getElementById('historyEventModal');
    if (modal) modal.classList.add('hidden');

    this.audio.playHyoshigi();
    this._historyFollowUp = false;
    if (!choice.isHistorical) {
      const ifFlag = this.eventRuleFor('setFlagOnIfChoice', ev.id);
      if (ifFlag) this.setHistoricalFlag(ifFlag);
    }
    const resultMsg = choice.action(this);
    this.applyLinkedHistoricalDataFromChoice(ev, choice);

    this.updateUI();

    // 本能寺の後継選択など、続きのダイアログがある場合はそちらが閉じてから次へ進む
    if (this._historyFollowUp) {
      this._historyFollowUp = false;
      this.log(`【イベント決断】${resultMsg}`, 'important');
      return;
    }

    if (this.autoPlayPausedForEvent || this.isAutoPlay) {
      this.log(`【イベント決断】${resultMsg}`, 'important');
      this.continueAfterHistoricalEvent();
      return;
    }

    Swal.fire({
      icon: choice.isHistorical ? 'info' : 'success',
      title: choice.isHistorical ? '📜 史実の道を選択' : '⚡ 歴史改変の英断',
      html: `
        <div style="font-size:12pt; color:#ffd700; margin-bottom:8px; font-weight:bold;">${ev.title}</div>
        <div style="font-size: 12pt; color:#eee; line-height:1.7;">${resultMsg}</div>
      `,
      background: '#24160e',
      color: '#fff',
      confirmButtonColor: '#d4af37'
    }).then(() => this.continueAfterHistoricalEvent());
  }
};
