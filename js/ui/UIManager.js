/**
 * @file js/ui/UIManager.js - UI表示・モーダル・HUD・ジュークボックス制御
 * 戦国天下統一伝 ES6モジュール
 * @typedef {import('../types.js').Officer} Officer
 * @typedef {import('../types.js').Province} Province
 * @typedef {import('../types.js').PlayableDaimyo} PlayableDaimyo
 * @typedef {import('../types.js').Scenario} Scenario
 * @typedef {import('../types.js').HistoricalEvent} HistoricalEvent
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
var CLAN_MASTER = _createObjectProxy(() => (typeof window !== 'undefined' && (window.CLAN_MASTER_DATA || window.CLAN_MASTER || {})) || {});
var DAIMYOS = (typeof window !== 'undefined' && window.DAIMYOS) || [];
var DAIMYO_EPILOGUES = (typeof window !== 'undefined' && window.DAIMYO_EPILOGUES) || {};
var triggerCelebrationConfetti = (typeof window !== 'undefined' && window.triggerCelebrationConfetti) || (() => {});

export class UIManager {
  constructor(game) {
    this.game = game;
  }
}

export const UIManagerMethods = {
  savedDaimyoName(data) {
    const clanId = data?.playerClanId;
    if (!clanId) return '無名';

    const living = (data.activeOfficers || []).find(o =>
      o && o.clanId === clanId && o.isDaimyo && !o.isDead && !this.looksLikeClanId(o.name)
    );
    if (living) return living.name;

    const last = data.lastDaimyoNames?.[clanId];
    if (!this.looksLikeClanId(last)) return last;

    const scens = (window.SCENARIOS_DATA && window.SCENARIOS_DATA.length > 0) ? window.SCENARIOS_DATA : (SCENARIOS || []);
    const scen = scens.find(s => String(s.id) === String(data.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    if (playable && !this.looksLikeClanId(playable.name)) return playable.name;

    const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[clanId];
    if (master?.leaders) {
      const curY = Number(data.year || 0);
      const validYears = Object.keys(master.leaders)
        .map(Number)
        .filter(y => !isNaN(y) && y <= curY)
        .sort((a, b) => b - a);
      const dated = validYears.length > 0 ? master.leaders[String(validYears[0])] : '';
      if (!this.looksLikeClanId(dated)) return dated;
      if (!this.looksLikeClanId(master.leaders.default)) return master.leaders.default;
    }

    const template = DAIMYOS.find(x => x.id === clanId);
    if (template && !this.looksLikeClanId(template.name)) return template.name;
    if (master?.family && !this.looksLikeClanId(master.family)) {
      return String(master.family).replace(/軍$/, '');
    }
    return '大名';
  },

  // 人名には「公」。家名・朝廷名（河内源氏、平安朝廷など）には付けない。
  // 「源義家」のように名が「家」で終わる人物は人名として扱う。,

  savedDaimyoLabel(data, name) {
    const clanId = data?.playerClanId;
    const labels = new Set();
    const master = (window.CLAN_MASTER_DATA || CLAN_MASTER || {})[clanId];
    if (master?.family) labels.add(String(master.family));
    const scens = (window.SCENARIOS_DATA && window.SCENARIOS_DATA.length > 0) ? window.SCENARIOS_DATA : (SCENARIOS || []);
    const scen = scens.find(s => String(s.id) === String(data?.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    if (playable?.clan) labels.add(playable.clan);
    if (labels.has(name) || /(氏|朝廷|幕府|政府|衆|党)$/.test(name || '')) return name;
    return `${name}公`;
  },

  // 自動セーブデータの確認と再開UI,

  checkResumeSaveData() {
    const raw = localStorage.getItem('sengoku_save_data');
    const banner = document.getElementById('resumeSaveBanner');
    const summary = document.getElementById('resumeSaveSummary');
    const resumeBtn = document.getElementById('resumeSaveBtn');

    if (!raw || !banner) return;

    try {
      const data = JSON.parse(raw);
      const provs = data.provincesDelta || data.provinces || [];
      const myProvs = provs.filter(p => p.ownerId === data.playerClanId);
      const daimyoLabel = this.savedDaimyoLabel(data, this.savedDaimyoName(data));
      const seasonName = ['春', '夏', '秋', '冬'][data.seasonIdx || 0];

      if (summary) {
        summary.textContent = `${data.year}年 ${seasonName} / ${daimyoLabel} (支配: ${myProvs.length}国 / 兵力: ${myProvs.reduce((a,c)=>a+(c.troops || 0),0).toLocaleString()}人)`;
      }

      banner.style.display = 'flex';
      if (resumeBtn) {
        resumeBtn.onclick = () => {
          this.loadGameData(data);
          document.getElementById('startModal')?.classList.add('hidden');
        };
      }
    } catch (e) {
      console.warn('Invalid save data:', e);
    }
  },

  // シナリオ切替,

  renderStartModal() {
    this.updateDiffBadge();
    document.querySelectorAll('.diff-option-btn[data-diff]').forEach(b => {
      b.classList.toggle('selected', b.dataset.diff === this.currentDifficulty);
    });

    // 多重登録防止: イベントリスナーは親コンテナへのイベントデリゲーションで初回のみ登録
    if (!this._startModalDelegated) {
      this._startModalDelegated = true;

      const modal = document.getElementById('startModal');
      if (modal) {
        modal.addEventListener('click', (e) => {
          // 1. 時代タブ
          const tab = e.target.closest('.era-tab-btn');
          if (tab) {
            document.querySelectorAll('.era-tab-btn').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const targetEra = tab.dataset.era;
            document.querySelectorAll('.scenario-btn').forEach(btn => {
              btn.style.display = (targetEra === 'all' || btn.dataset.era === targetEra) ? '' : 'none';
            });
            if (this.audio && this.audio.playHyoshigi) {
              this.audio.playHyoshigi();
            }
            return;
          }

          // 2. シナリオ選択ボタン
          const scenBtn = e.target.closest('.scenario-btn');
          if (scenBtn && scenBtn.dataset.scenId) {
            this.switchScenario(scenBtn.dataset.scenId);
            if (this.audio && this.audio.playHyoshigi) {
              this.audio.playHyoshigi();
            }
            return;
          }

          // 3. 難易度選択ボタン
          const diffBtn = e.target.closest('.diff-option-btn[data-diff]');
          if (diffBtn) {
            document.querySelectorAll('.diff-option-btn[data-diff]').forEach(b => b.classList.remove('selected'));
            diffBtn.classList.add('selected');
            this.currentDifficulty = diffBtn.dataset.diff;
            this.updateDiffBadge();
            if (this.audio && this.audio.playHyoshigi) {
              this.audio.playHyoshigi();
            }
            return;
          }

          // 4. ゲーム開始ボタン (AudioContext を確実に resume)
          const startBtn = e.target.closest('#startGameBtn');
          if (startBtn) {
            if (this.music) {
              this.music.init();
              if (this.music.ctx && this.music.ctx.state === 'suspended') {
                this.music.ctx.resume().catch(() => {});
              }
            }
            this.startGame();
            return;
          }
        });
      }

      // 大名詳細ポップアップ内のデリゲーション
      const popup = document.getElementById('daimyoPopup');
      if (popup) {
        popup.addEventListener('click', (e) => {
          if (e.target.closest('#daimyoPopupStartBtn')) {
            popup.classList.add('hidden');
            if (this.music) {
              this.music.init();
              if (this.music.ctx && this.music.ctx.state === 'suspended') {
                this.music.ctx.resume().catch(() => {});
              }
            }
            this.startGame();
          } else if (e.target.closest('#daimyoPopupCloseBtn') || e.target.closest('#daimyoPopupCancelBtn') || e.target === popup) {
            popup.classList.add('hidden');
          }
        });
      }
    }

    this.switchScenario(this.currentScenarioId);
  },

  // 要望対応: シナリオに領国を持つすべての勢力をプレイ可能大名として網羅,

  renderDaimyoGrid(playables, defaultClanId) {
    const grid = document.getElementById('daimyoGrid');
    if (!grid) return;
    grid.innerHTML = '';

    grid.style.maxHeight = '480px';
    grid.style.overflowY = 'auto';
    grid.style.overflowX = 'hidden';
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(152px, 1fr))';
    grid.style.gap = '6px';
    grid.style.padding = '4px 6px';
    grid.style.boxSizing = 'border-box';

    let initialSelectedDaimyo = null;

    playables.forEach(d => {
      const isSelected = d.id === defaultClanId;
      if (isSelected || (!initialSelectedDaimyo && !defaultClanId)) {
        this.playerClanId = d.id;
        this.playerDaimyo = d;
        initialSelectedDaimyo = d;
      }

      const card = document.createElement('div');
      card.className = `daimyo-card ${isSelected ? 'selected' : ''}`;
      card.dataset.id = d.id;
      card.style.cursor = 'pointer';

      // 能力値・性格の取得
      const ability = getClanAbility(d.id);
      const personLabel = ability.personality === 'aggressive' ? '攻勢型 ⚔️'
                        : ability.personality === 'domestic'   ? '内政型 🌾'
                        : 'バランス型 ⚖️';
      const personColor = ability.personality === 'aggressive' ? '#ff6b6b'
                        : ability.personality === 'domestic'   ? '#2ecc71'
                        : '#3498db';
      const provCount = d.provCount || (d.myProvinces ? d.myProvinces.length : 1);
      const kamonId = this.getClanKamonId(d.id);

      card.title = `${d.clan} 当主: ${d.name}\n支配: ${provCount}国\n(クリックで戦略解説・出陣)`;
      card.innerHTML = `
        <div class="daimyo-name">
          <div class="daimyo-name-wrap">
            <svg style="width:18px; height:18px; vertical-align:middle; flex-shrink:0; margin-top:1px;">
              <use href="#${kamonId}"></use>
            </svg>
            <span class="daimyo-name-text" title="${d.name}">${d.name}</span>
          </div>
          <span class="daimyo-prov-badge">${provCount}国</span>
        </div>
        <div class="daimyo-clan-row">
          <span class="daimyo-clan-name" title="${d.clan}">${d.clan}</span>
          <span style="color:${personColor}; font-size: 10.5pt; background:rgba(0,0,0,0.6); padding:1px 4px; border-radius:2px; border:1px solid ${personColor}; flex-shrink:0;">${d.difficulty}</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size: 11.5pt; background:rgba(0,0,0,0.35); padding:1px 4px; border-radius:2px;">
          <span style="color:#ffaaaa;">武<strong>${ability.military}</strong></span>
          <span style="color:#aaffaa;">内<strong>${ability.politics}</strong></span>
          <span style="color:#aaaaff;">知<strong>${ability.stratagem}</strong></span>
        </div>
      `;

      // シングルクリックで各大名の詳細解説ダイアログを展開
      card.addEventListener('click', () => {
        document.querySelectorAll('.daimyo-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.playerClanId = d.id;
        this.playerDaimyo = d;
        this.gold = d.gold;
        this.rice = d.rice;

        const badge = document.getElementById('selectedDaimyoBadge');
        if (badge) {
          badge.textContent = `選択中: ${d.name} (${d.clan}・支配${provCount}国)`;
        }

        this.audio.playHyoshigi();
        this.showDaimyoPopup(d);
      });

      grid.appendChild(card);
    });

    const defaultCard = grid.querySelector(`.daimyo-card[data-id="${defaultClanId}"]`) || grid.querySelector('.daimyo-card');
    if (defaultCard) {
      document.querySelectorAll('.daimyo-card').forEach(c => c.classList.remove('selected'));
      defaultCard.classList.add('selected');
      // 北から並べたので、おすすめ大名がグリッドの下にあっても見えるところまで送る（ページ自体は動かさない）
      const top = defaultCard.offsetTop - grid.offsetTop;
      if (top > grid.clientHeight - defaultCard.offsetHeight) grid.scrollTop = Math.max(0, top - 8);
      else grid.scrollTop = 0;
      const dData = playables.find(d => d.id === defaultCard.dataset.id) || playables[0];
      if (dData) {
        this.playerClanId = dData.id;
        this.playerDaimyo = dData;
        this.gold = dData.gold;
        this.rice = dData.rice;

        const provCount = dData.provCount || (dData.myProvinces ? dData.myProvinces.length : 1);
        const badge = document.getElementById('selectedDaimyoBadge');
        if (badge) {
          badge.textContent = `選択中: ${dData.name} (${dData.clan}・支配${provCount}国)`;
        }
      }
    }
  },

  showDaimyoPopup(d) {
    const popup = document.getElementById('daimyoPopup');
    if (!popup) return;

    this.playerClanId = d.id;
    this.playerDaimyo = d;
    this.gold = d.gold;
    this.rice = d.rice;

    const ability = getClanAbility(d.id);
    const kamonId = this.getClanKamonId(d.id);
    const provCount = d.provCount || (d.myProvinces ? d.myProvinces.length : 1);
    const personLabel = ability.personality === 'aggressive' ? '攻勢型 ⚔️'
                      : ability.personality === 'domestic'   ? '内政型 🌾'
                      : 'バランス型 ⚖️';
    const personColor = ability.personality === 'aggressive' ? '#ff6b6b'
                      : ability.personality === 'domestic'   ? '#2ecc71'
                      : '#3498db';

    // シナリオ情報の取得 (IDまたは年で柔軟に検索)
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId) || String(s.year) === String(this.currentScenarioId)) || SCENARIOS[0];
    const scenTitle = scen ? `${scen.year}年 ${scen.title}` : '戦国天下統一伝';

    // シナリオ固有の解説文を取得（大名の歴史的位置づけ）
    const scenDesc = (scen && scen.clanDescs && scen.clanDescs[d.id]) || d.desc || '天下布武の志を抱き、乱世に覇を唱えんとする当主。';

    const useEl = document.getElementById('popupKamonUse');
    if (useEl) useEl.setAttribute('href', `#${kamonId}`);

    const nameEl = document.getElementById('popupDaimyoName');
    if (nameEl) nameEl.textContent = d.name || '不明';

    const clanEl = document.getElementById('popupClanName');
    if (clanEl) clanEl.textContent = d.clan || '';

    const scenContextEl = document.getElementById('popupScenarioContext');
    if (scenContextEl) scenContextEl.textContent = `❖ ${scenTitle} ❖`;

    const diffEl = document.getElementById('popupDifficulty');
    if (diffEl) {
      diffEl.textContent = d.difficulty || '中級';
      diffEl.style.borderColor = d.difficulty === '初級' ? '#2ecc71' : d.difficulty === '中級' ? '#f39c12' : '#e74c3c';
      diffEl.style.color = d.difficulty === '初級' ? '#a9dfbf' : d.difficulty === '中級' ? '#f8c471' : '#ff9999';
    }

    const totalProvs = this.provinces.length || (window.PROVINCES_DATA ? window.PROVINCES_DATA.length : 71);
    const provEl = document.getElementById('popupProvCount');
    if (provEl) provEl.textContent = `支配: ${provCount}国 (天下統一まで${totalProvs - provCount}国)`;

    const milEl = document.getElementById('popupMilitary');
    if (milEl) milEl.textContent = ability.military || 60;

    const polEl = document.getElementById('popupPolitics');
    if (polEl) polEl.textContent = ability.politics || 60;

    const strEl = document.getElementById('popupStratagem');
    if (strEl) strEl.textContent = ability.stratagem || 55;

    const persEl = document.getElementById('popupPersonality');
    if (persEl) persEl.innerHTML = `<span style="color:${personColor}; border:1px solid ${personColor}; padding:3px 12px; border-radius:4px; font-size:12pt; font-weight:bold;">【${personLabel}】</span>`;

    const goldEl = document.getElementById('popupGold');
    if (goldEl) goldEl.textContent = (d.gold || 400).toLocaleString() + ' 貫';

    const riceEl = document.getElementById('popupRice');
    if (riceEl) riceEl.textContent = (d.rice || 600).toLocaleString() + ' 石';

    const descEl = document.getElementById('popupDesc');
    if (descEl) descEl.textContent = scenDesc;

    const tacEl = document.getElementById('popupTactic');
    if (tacEl) tacEl.innerHTML = `<strong>⚡ 奥義「${d.tactic || '全軍奮戦'}」</strong> ${d.tacticDesc || '全軍の力を結集して戦う！'}`;

    const startBtn = document.getElementById('daimyoPopupStartBtn');
    if (startBtn) {
      startBtn.innerHTML = `⚔️ 【${d.name}（${d.clan}）】で天下統一へ出陣！`;
    }

    // 周辺の出来事・近隣勢力動向 ＆ 戦略解説図 (SVG) の生成
    this.renderDaimyoStrategyBriefing(d, scen, ability);

    popup.classList.remove('hidden');
  },

  renderDaimyoStrategyBriefing(d, scen, ability) {
    const myProvs = d.myProvinces || [d.startProvId];
    const startProvId = d.startProvId || myProvs[0];
    const provList = this.provinces.length > 0 ? this.provinces : (window.PROVINCES_DATA || []);
    const homeProv = provList.find(p => p.id === startProvId);
    const homeProvName = homeProv ? homeProv.name : startProvId;
    const homeCastleName = (scen.castles && scen.castles[startProvId]) || (homeProv ? homeProv.castle : `${homeProvName}城`);

    const homeCastleLabel = document.getElementById('popupHomeCastleName');
    if (homeCastleLabel) homeCastleLabel.textContent = `本拠: ${homeProvName}国 (${homeCastleName})`;

    // 隣接する領国と他家勢力の抽出
    const neighborProvIds = new Set();
    myProvs.forEach(pId => {
      const p = provList.find(x => x.id === pId);
      if (p && p.neighbors) {
        p.neighbors.forEach(nId => {
          if (!myProvs.includes(nId)) {
            neighborProvIds.add(nId);
          }
        });
      }
    });

    const neighborClansMap = new Map();
    neighborProvIds.forEach(nId => {
      const ownerClanId = (scen.owners && scen.owners[nId]) || 'independent';
      const nProv = provList.find(x => x.id === nId);
      const nProvName = nProv ? nProv.name : nId;
      const nCastle = (scen.castles && scen.castles[nId]) || (nProv ? nProv.castle : `${nProvName}城`);

      if (!neighborClansMap.has(ownerClanId)) {
        const rivalPlayable = scen.playables ? scen.playables.find(x => x.id === ownerClanId) : null;
        const rivalProfile = window.CLAN_MASTER_DATA ? window.CLAN_MASTER_DATA[ownerClanId] : null;
        const rivalName = rivalPlayable ? rivalPlayable.name : (rivalProfile?.family || ownerClanId);
        const rivalClan = rivalPlayable ? rivalPlayable.clan : (rivalProfile?.family || ownerClanId);
        const rivalKamon = this.getClanKamonId(ownerClanId);
        neighborClansMap.set(ownerClanId, {
          clanId: ownerClanId,
          name: rivalName,
          clan: rivalClan,
          kamonId: rivalKamon,
          provinces: [],
          castles: []
        });
      }
      const entry = neighborClansMap.get(ownerClanId);
      entry.provinces.push(nProvName);
      entry.castles.push(nCastle);
    });

    const neighborList = Array.from(neighborClansMap.values());

    // 周辺の出来事・近隣勢力動向テキストの生成
    const surroundingEl = document.getElementById('popupSurroundingEvents');
    if (surroundingEl) {
      if (neighborList.length === 0) {
        surroundingEl.innerHTML = `周囲に直接隣接する他家はなく、領内の治世と国力増強に専念できる稀有な情勢です。まずは内政で兵糧と軍資金を蓄えましょう。`;
      } else {
        const rivalDescParts = neighborList.slice(0, 3).map(r => {
          return `<strong style="color:var(--gold-bright);">${r.clan}</strong>（${r.name} / ${r.provinces.slice(0, 2).join('・')}）`;
        });
        surroundingEl.innerHTML = `
          本拠【${homeProvName}国】の周辺には、${rivalDescParts.join('、および')}などの群雄が隣接しています。<br>
          ${scen.title}の動乱を受け、諸大名は領国拡大を狙って一触即発の睨み合いを続けています。隣接国への侵攻路を慎重に吟味し、敵の防備が薄い隙を突くことが覇道への要衝となります。
        `;
      }
    }

    // 戦略解説図 (SVG) の動的生成
    const diagContainer = document.getElementById('popupStrategyDiagram');
    if (diagContainer) {
      const playerKamon = this.getClanKamonId(d.id);
      const keyNeighbors = neighborList.slice(0, 3);
      const px = 95, py = 85;

      const nCoords = keyNeighbors.length === 1 ? [
        { x: 355, y: 85, stance: '攻略目標', color: '#ffd700', marker: 'arrowGold' }
      ] : keyNeighbors.length === 2 ? [
        { x: 355, y: 46, stance: '攻略推奨', color: '#ffd700', marker: 'arrowGold' },
        { x: 355, y: 124, stance: '侵攻警戒', color: '#ff6b6b', marker: 'arrowRed' }
      ] : [
        { x: 355, y: 35, stance: '攻略推奨', color: '#ffd700', marker: 'arrowGold' },
        { x: 365, y: 85, stance: '係争敵対', color: '#f39c12', marker: 'arrowGold' },
        { x: 355, y: 135, stance: '侵攻警戒', color: '#ff6b6b', marker: 'arrowRed' }
      ];

      let svgContent = `
        <svg viewBox="0 0 460 170" width="100%" height="100%" style="display:block;">
          <defs>
            <linearGradient id="pCardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#3d281a"/>
              <stop offset="100%" stop-color="#1c120b"/>
            </linearGradient>
            <linearGradient id="eCardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#381515"/>
              <stop offset="100%" stop-color="#1a0808"/>
            </linearGradient>
            <marker id="arrowGold" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ffd700" />
            </marker>
            <marker id="arrowRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ff6b6b" />
            </marker>
          </defs>

          <!-- 背景羅針盤グリッド線 -->
          <line x1="20" y1="85" x2="440" y2="85" stroke="rgba(212,175,55,0.12)" stroke-dasharray="3,3"/>
          <circle cx="95" cy="85" r="70" fill="none" stroke="rgba(212,175,55,0.1)" stroke-dasharray="2,4"/>
      `;

      // 矢印・相関線の描画
      keyNeighbors.forEach((nbr, i) => {
        const coord = nCoords[i];
        const isGold = coord.marker === 'arrowGold';
        svgContent += `
          <path d="M ${px + 52} ${py} Q ${(px + coord.x)/2} ${(py + coord.y)/2} ${coord.x - 52} ${coord.y}"
                fill="none" stroke="${coord.color}" stroke-width="2.2" stroke-dasharray="${isGold ? 'none' : '4,3'}"
                marker-end="url(#${coord.marker})"/>
          <text x="${(px + coord.x)/2 - 8}" y="${(py + coord.y)/2 - 5}" font-size="11" fill="${coord.color}" font-weight="bold" text-anchor="middle">
            ${coord.stance}
          </text>
        `;
      });

      // 貴家本拠ノード (左)
      svgContent += `
        <g transform="translate(${px - 50}, ${py - 35})">
          <rect x="0" y="0" width="102" height="70" rx="8" fill="url(#pCardGrad)" stroke="#ffd700" stroke-width="2" filter="drop-shadow(0 0 6px rgba(255,215,0,0.4))"/>
          <svg x="6" y="15" width="40" height="40"><use href="#${playerKamon}"/></svg>
          <text x="50" y="24" font-size="12" font-weight="bold" fill="#fff">${d.name.substring(0, 4)}</text>
          <text x="50" y="38" font-size="11" fill="#e59866">${d.clan.substring(0, 5)}</text>
          <rect x="48" y="44" width="48" height="16" rx="3" fill="rgba(212,175,55,0.25)"/>
          <text x="72" y="56" font-size="11" fill="#ffd700" text-anchor="middle" font-weight="bold">【貴家】</text>
        </g>
      `;

      // 周辺勢力ノード (右)
      if (keyNeighbors.length === 0) {
        svgContent += `
          <g transform="translate(290, 60)">
            <rect x="0" y="0" width="130" height="50" rx="6" fill="rgba(0,0,0,0.5)" stroke="#664422"/>
            <text x="65" y="30" font-size="12" fill="#aaa" text-anchor="middle">直接隣接する他家なし</text>
          </g>
        `;
      } else {
        keyNeighbors.forEach((nbr, i) => {
          const coord = nCoords[i];
          svgContent += `
            <g transform="translate(${coord.x - 50}, ${coord.y - 24})">
              <rect x="0" y="0" width="102" height="48" rx="6" fill="url(#eCardGrad)" stroke="${coord.color}" stroke-width="1.5"/>
              <svg x="5" y="7" width="34" height="34"><use href="#${nbr.kamonId}"/></svg>
              <text x="42" y="19" font-size="11" font-weight="bold" fill="#fff">${nbr.name.substring(0, 4)}</text>
              <text x="42" y="33" font-size="11" fill="#bbb">${nbr.provinces[0] ? nbr.provinces[0].substring(0, 4) : '隣国'}</text>
            </g>
          `;
        });
      }

      svgContent += `</svg>`;
      diagContainer.innerHTML = svgContent;
    }

    // 初手攻略方針ガイダンスの動的生成
    const adviceEl = document.getElementById('popupStrategyAdvice');
    if (adviceEl) {
      const topTarget = neighborList[0] ? `隣接する【${neighborList[0].provinces[0] || '隣国'}（${neighborList[0].clan}）】` : '近隣の隣接国';
      if (ability.personality === 'aggressive') {
        adviceEl.innerHTML = `🎯 <strong>初手攻略方針:</strong> 武勇に優れる貴家は電撃戦が得意です。まずは兵力を前線へ集結し、${topTarget}への進撃路を開いて城郭を速やかに攻め落としましょう。`;
      } else if (ability.personality === 'domestic') {
        adviceEl.innerHTML = `🎯 <strong>初手攻略方針:</strong> 内政に長ける貴家は富国強兵が王道です。初期資金と米を活かして本拠地の商業・石高を開墾し、十分な兵站を築いてから${topTarget}へ侵攻しましょう。`;
      } else {
        adviceEl.innerHTML = `🎯 <strong>初手攻略方針:</strong> 攻守の調和に優れた貴家は臨機応変の軍略が鍵です。前線城の防備を固めつつ隣国の動向を睨み、隙を見て${topTarget}へ進出を図りましょう。`;
      }
    }
  },

  showOfficerDetailModal(offOrId) {
    if (!offOrId) return;
    const targetId = typeof offOrId === 'string' ? ((window.OFFICER_ID_ALIASES && window.OFFICER_ID_ALIASES[offOrId]) || offOrId) : null;
    const off = typeof offOrId === 'string'
      ? (this.activeOfficers || []).find(o => o.id === targetId || o.id === offOrId) || (this.officers || []).find(o => o.id === targetId || o.id === offOrId) || (window.OFFICERS_MASTER || []).find(o => o.id === targetId || o.id === offOrId) || { name: offOrId }
      : offOrId;

    let modal = document.getElementById('officerDetailModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'officerDetailModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.78); z-index:100005; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    const assignedProv = off.assignedProvId ? this.provinces.find(x => x.id === off.assignedProvId) : null;
    const isMyClan = off.clanId === this.playerClanId;
    const isRonin = off.clanId === 'ronin';
    const clanName = isRonin ? '浪人 (未仕官)' : this.getClanFamilyName(off.clanId);
    const detailClanText = isRonin ? clanName : (off.isDaimyo ? `${clanName} (当主)` : `${clanName} 配下`);
    const age = this.year - (off.birthYear || 1530);
    const comment = this.getOfficerComment(off);

    let roleBadge = '';
    if (off.isDaimyo) {
      roleBadge = '<span style="background:#b7950b; color:#fff; padding:3px 12px; border-radius:4px; font-size:12pt; font-weight:bold;">👑 当主</span>';
    } else if (assignedProv) {
      roleBadge = `<span style="background:#27ae60; color:#fff; padding:3px 12px; border-radius:4px; font-size:12pt;">🏯 ${assignedProv.name}城主</span>`;
    } else if (isRonin) {
      roleBadge = '<span style="background:#7f8c8d; color:#fff; padding:3px 12px; border-radius:4px; font-size:12pt;">流浪の士</span>';
    } else {
      roleBadge = '<span style="background:#2980b9; color:#fff; padding:3px 12px; border-radius:4px; font-size:12pt;">待機中</span>';
    }

    modal.innerHTML = `
      <div style="background:#1c130d; border:2px solid var(--gold); border-radius:8px; width:92vw; max-width:660px; max-height:88vh; display:flex; flex-direction:column; box-shadow:0 0 50px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif; animation:modalPopIn 0.18s ease-out;">
        <!-- ヘッダー -->
        <div style="padding:14px 22px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:15pt; color:var(--gold-bright); font-weight:bold;">❖ 武将詳細・名将列伝 ❖</span>
          </div>
          <button id="closeOfficerDetailBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 6px;">✕</button>
        </div>

        <!-- 本文スクロール領域 -->
        <div style="padding:20px 24px; overflow-y:auto; flex:1;">
          <!-- 武将名 & 身分 & 所属 -->
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:14px; border-bottom:1px solid #4a3b2c; padding-bottom:10px;">
            <div style="display:flex; align-items:center; gap:12px;">
              <span id="officerDetailName" style="font-size:19pt; font-weight:bold; color:#ffffff; letter-spacing:1px;">${off.name}</span>
              ${roleBadge}
            </div>
            <div style="font-size:12pt;">
              <span style="color:#aaa;">所属: </span>
              <strong style="color:${isRonin ? '#bdc3c7' : (isMyClan ? '#2ecc71' : 'var(--gold)')}; font-size:12.5pt;">${detailClanText}</strong>
            </div>
          </div>

          <!-- 生没年 & 所在・旧国名 & 特技 -->
          <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:10px; margin-bottom:18px; background:rgba(0,0,0,0.35); padding:10px 14px; border-radius:5px; border:1px solid #3d2d20;">
            <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap; font-size:12pt; color:#ccc;">
              <div>
                生没年: <strong style="color:#ffffff;">${off.birthYear || '?'}年 〜 ${off.deathYear || '?'}年</strong>
                <span style="color:#aaa; margin-left:6px;">(現在 ${age}歳)</span>
              </div>
              <div>
                所在: <strong style="color:var(--gold-bright);">${this.getOfficerLocationInfo(off).provName}国</strong>
                <span style="color:#aaa; font-size:11pt; margin-left:2px;">(${this.getOfficerLocationInfo(off).label})</span>
              </div>
            </div>
            <div style="font-size:12pt;">
              <span style="color:#ffeaa7; background:rgba(183,149,11,0.25); border:1px solid #b7950b; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:12pt;">
                特技: ${off.skill || '名将の資質'}
              </span>
            </div>
          </div>

          <!-- 能力値カード -->
          <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:20px; text-align:center;">
            <div style="background:rgba(231,76,60,0.14); border:1px solid #c0392b; padding:10px 8px; border-radius:6px;">
              <div style="font-size:12pt; color:#ff7675; font-weight:bold;">⚔️ 武勇</div>
              <div style="font-size:19pt; font-weight:bold; color:#ff7675; margin-top:3px;">${off.military}</div>
            </div>
            <div style="background:rgba(52,152,219,0.14); border:1px solid #2980b9; padding:10px 8px; border-radius:6px;">
              <div style="font-size:12pt; color:#74b9ff; font-weight:bold;">🌾 内政</div>
              <div style="font-size:19pt; font-weight:bold; color:#74b9ff; margin-top:3px;">${off.politic || off.politics}</div>
            </div>
            <div style="background:rgba(46,204,113,0.14); border:1px solid #27ae60; padding:10px 8px; border-radius:6px;">
              <div style="font-size:12pt; color:#55efc4; font-weight:bold;">📜 知略</div>
              <div style="font-size:19pt; font-weight:bold; color:#55efc4; margin-top:3px;">${off.intel || off.stratagem}</div>
            </div>
          </div>

          <!-- 人物列伝本文 -->
          <div>
            <div style="font-size:13pt; color:var(--gold); font-weight:bold; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
              <span>📖</span><span>人物列伝・歴史事績</span>
            </div>
            <div style="background:rgba(0,0,0,0.5); border:1px solid #5a4638; border-radius:6px; padding:16px 18px; font-size:13pt; color:#f0e6d2; line-height:1.85; letter-spacing:0.4px; word-break:break-all;">
              ${off.lore ? this.cleanOfficerLore(off.lore) : '（歴史の波間に埋もれし伝記。記録された詳細な事績はありません）'}
            </div>
          </div>
        </div>

        <!-- フッター -->
        <div style="padding:12px 24px; border-top:1px solid #443322; background:rgba(0,0,0,0.35); display:flex; justify-content:flex-end;">
          <button id="closeOfficerDetailBtnBottom" style="background:#555; color:#fff; border:none; padding:7px 24px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:0.15s;">閉じる</button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    this.audio.playHyoshigi();

    const closeModal = () => { modal.style.display = 'none'; };
    document.getElementById('closeOfficerDetailBtn')?.addEventListener('click', closeModal);
    document.getElementById('closeOfficerDetailBtnBottom')?.addEventListener('click', closeModal);

    // モーダル背景クリックで閉じる
    modal.onclick = (e) => {
      if (e.target === modal) closeModal();
    };
  },

  // 城主任命モーダル（表形式・ソート対応・幅広ダイアログ・文字サイズ12pt以上）,

  openAppointGovernorModal(provId) {
    const p = this.provinces.find(x => x.id === provId);
    if (!p || p.ownerId !== this.playerClanId) return;

    let modal = document.getElementById('governorAppointModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'governorAppointModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    let sortKey = 'role'; // 'role', 'name', 'age', 'military', 'politic', 'intel', 'comment'
    let sortOrder = 'desc'; // 'asc' or 'desc'
    let searchQuery = '';

    const render = () => {
      // 自家の全武将（現在生存中の武将）
      const myOfficers = (this.activeOfficers || this.officers || []).filter(o => o.clanId === this.playerClanId && !o.isDead);
      const currentGov = p.governorId ? myOfficers.find(o => o.id === p.governorId) : null;

      let list = [...myOfficers];

      if (searchQuery) {
        const q = searchQuery.trim().toLowerCase();
        list = list.filter(o => {
          const comment = this.getOfficerComment(o).toLowerCase();
          return (o.name && o.name.toLowerCase().includes(q)) || comment.includes(q);
        });
      }

      // ソート処理
      list.sort((a, b) => {
        let diff = 0;
        if (sortKey === 'role') {
          // 当主(3) > 現職城主(2.5) > 他城主(2) > 待機中(1)
          const getRoleScore = (off) => {
            if (off.isDaimyo) return 3;
            if (off.id === p.governorId) return 2.5;
            if (off.assignedProvId) return 2;
            return 1;
          };
          diff = getRoleScore(a) - getRoleScore(b);
          if (diff === 0) diff = (a.military || 0) - (b.military || 0);
        } else if (sortKey === 'name') {
          diff = (a.name || '').localeCompare(b.name || '', 'ja');
        } else if (sortKey === 'age') {
          const ageA = this.year - (a.birthYear || 1530);
          const ageB = this.year - (b.birthYear || 1530);
          diff = ageA - ageB;
        } else if (sortKey === 'military') {
          diff = (a.military || 0) - (b.military || 0);
        } else if (sortKey === 'politic') {
          diff = (a.politic || 0) - (b.politic || 0);
        } else if (sortKey === 'base') {
          const getBaseName = (off) => {
            if (off.assignedProvId) {
              const pr = this.provinces.find(x => x.id === off.assignedProvId);
              return pr ? pr.name : '';
            }
            if (off.isDaimyo) {
              const home = this.getDaimyoHomeProvince(off);
              return home ? home.name : '';
            }
            return '';
          };
          diff = getBaseName(a).localeCompare(getBaseName(b), 'ja');
        } else if (sortKey === 'intel') {
          diff = (a.intel || 0) - (b.intel || 0);
        } else if (sortKey === 'comment') {
          diff = this.getOfficerComment(a).localeCompare(this.getOfficerComment(b), 'ja');
        }
        return sortOrder === 'desc' ? -diff : diff;
      });

      const getSortIcon = (key) => {
        if (sortKey !== key) return '<span style="color:#776655; font-size:11pt; margin-left:4px;">↕</span>';
        return sortOrder === 'asc' 
          ? '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▲</span>' 
          : '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▼</span>';
      };

      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:95vw; max-width:1180px; height:88vh; display:flex; flex-direction:column; box-shadow:0 0 45px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <!-- ヘッダー -->
          <div style="padding:12px 22px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">❖ ${p.name}国 (${p.castleName || p.castle}) 城代・城主任命 ❖</h3>
              <span style="font-size:12pt; color:#ccc;">武将行をクリックすると直ちに城主任命。各列ヘッダークリックで並び替え。城主不在時は城代が統治（能力${Math.round((p.jodaiRatio || 0.55)*100)}%）。</span>
            </div>
            <button id="closeGovModalBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 8px;">✕</button>
          </div>
          
          <!-- 現在の統治状況バー & 検索 -->
          <div style="padding:10px 20px; background:rgba(0,0,0,0.35); border-bottom:1px dashed #5a4638; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px;">
            <div style="display:flex; align-items:center; gap:14px;">
              <div>
                <span style="color:#aaa; font-size:12pt;">現在の統治: </span>
                ${currentGov ? (currentGov.isDaimyo ? `<strong style="color:var(--gold-bright); font-size:13pt;">👑 本拠親政: ${currentGov.name}</strong> <span style="font-size:12pt; color:#ddd;">(武${currentGov.military} 内${currentGov.politic} 謀${currentGov.intel})</span>` : `<strong style="color:#2ecc71; font-size:13pt;">🏯 城主: ${currentGov.name}</strong> <span style="font-size:12pt; color:#ddd;">(武${currentGov.military} 内${currentGov.politic} 謀${currentGov.intel})</span>`) : `<strong style="color:#e67e22; font-size:13pt;">🏯 ${this.getEffectiveStats(p.id).vacantBadge || '城代統治'}</strong>`}
              </div>
              ${currentGov ? `<button id="btnDismissGov" style="background:#78281f; color:#fff; border:1px solid #c0392b; padding:5px 14px; border-radius:4px; cursor:pointer; font-size:12pt; transition:0.2s;">城代に戻す (城主解任)</button>` : ''}
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12pt; color:#aaa;">検索:</span>
              <input id="inputGovSearch" type="text" placeholder="武将名・特技..." value="${searchQuery}" style="background:#22160d; color:#fff; border:1px solid #775533; padding:5px 10px; border-radius:4px; font-size:12pt; width:180px;">
            </div>
          </div>

          <!-- テーブル一覧コンテナ -->
          <div style="flex:1; overflow-y:auto; padding:0 20px;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; border-bottom:2px solid #775533; z-index:10; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
                  <th class="sortable-gov-th" data-key="name" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:160px; font-size:12pt;">名前 ${getSortIcon('name')}</th>
                  <th class="sortable-gov-th" data-key="role" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:110px; text-align:center; font-size:12pt;">身分・配置 ${getSortIcon('role')}</th>
                  <th class="sortable-gov-th" data-key="base" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:135px; text-align:center; font-size:12pt;">拠点 ${getSortIcon('base')}</th>
                  <th class="sortable-gov-th" data-key="age" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:80px; text-align:center; font-size:12pt;">年齢 ${getSortIcon('age')}</th>
                  <th class="sortable-gov-th" data-key="military" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">武勇 ${getSortIcon('military')}</th>
                  <th class="sortable-gov-th" data-key="politic" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">内政 ${getSortIcon('politic')}</th>
                  <th class="sortable-gov-th" data-key="intel" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">知略 ${getSortIcon('intel')}</th>
                  <th style="padding:11px 12px; color:var(--gold); width:125px; text-align:center; font-size:12pt;">任命操作</th>
                </tr>
              </thead>
              <tbody>
                ${list.length === 0 ? `
                  <tr>
                    <td colspan="8" style="text-align:center; padding:30px; color:#888; font-size:12pt;">該当する武将は見つかりませんでした。</td>
                  </tr>
                ` : ''}
                ${list.map((off, idx) => {
                  const isAssignedHere = off.id === p.governorId;
                  const assignedProv = off.assignedProvId ? this.provinces.find(x => x.id === off.assignedProvId) : null;
                  const age = this.year - (off.birthYear || 1530);

                  let roleBadge = '';
                  if (off.isDaimyo) {
                    roleBadge = '<span style="background:#b7950b; color:#fff; padding:2px 8px; border-radius:3px; font-weight:bold; font-size:12pt;">👑 当主</span>';
                  } else if (isAssignedHere) {
                    roleBadge = '<span style="background:#27ae60; color:#fff; padding:2px 8px; border-radius:3px; font-weight:bold; font-size:12pt;">🏯 当国城主</span>';
                  } else if (assignedProv) {
                    roleBadge = '<span style="background:#5d6d7e; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt; font-weight:bold;">🏯 城主</span>';
                  } else {
                    roleBadge = '<span style="background:#2980b9; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt;">待機中</span>';
                  }

                  let baseDisplay = '-';
                  if (assignedProv) {
                    baseDisplay = `<span style="color:#2ecc71; font-weight:bold;">${assignedProv.name}</span><span style="color:#aaa; font-size:11pt; margin-left:3px;">(${assignedProv.castleName || assignedProv.castle})</span>`;
                  } else if (off.isDaimyo) {
                    const capProv = this.getDaimyoHomeProvince(off);
                    baseDisplay = capProv 
                      ? `<span style="color:var(--gold-bright); font-weight:bold;">${capProv.name}</span><span style="color:#aaa; font-size:11pt; margin-left:3px;">(居城)</span>` 
                      : `<span style="color:#888;">所領なし</span>`;
                  } else {
                    baseDisplay = '<span style="color:#5dade2;">本国待機</span>';
                  }

                  const rowBg = isAssignedHere 
                    ? 'rgba(39, 174, 96, 0.16)' 
                    : (idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.18)');

                  return `
                    <tr class="officer-table-row" data-off-id="${off.id}" title="${isAssignedHere ? '現在任命中' : `クリックして${off.name}を城主任命`}" style="background:${rowBg}; border-bottom:1px solid #3d2d20; cursor:pointer; font-size:12pt; transition:background 0.15s;" onmouseover="this.style.background='rgba(215, 175, 100, 0.12)'" onmouseout="this.style.background='${rowBg}'">
                      <td style="padding:10px 12px; font-weight:bold; color:#ffffff; white-space:nowrap; font-size:12.5pt;">
                        ${off.name}
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap;">
                        ${roleBadge}
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap; font-size:12pt;">
                        ${baseDisplay}
                      </td>
                      <td style="padding:10px 10px; text-align:center; color:#ddd; white-space:nowrap; font-size:12pt;">
                        ${age}歳
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#ff6b6b; font-size:12.5pt;">${off.military}</b>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#5dade2; font-size:12.5pt;">${off.politic}</b>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#a3e4d7; font-size:12.5pt;">${off.intel}</b>
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap;">
                        ${isAssignedHere ? `
                          <span style="color:#2ecc71; font-weight:bold; font-size:12pt;">任命中</span>
                        ` : `
                          <button class="btn-select-gov" data-off-id="${off.id}" style="background:#1b4f72; color:#fff; border:1px solid #3498db; padding:5px 12px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:all 0.15s;">城主任命</button>
                        `}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- フッター -->
          <div style="padding:12px 20px; border-top:1px solid #443322; background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12pt; color:#aaa;">表示中: ${list.length}名 (現在年: ${this.year}年) 💡武将行をクリックで直ちに城主任命</span>
            <div style="display:flex; gap:8px;">
              <button id="openBatchGovFromSingle" style="background:#1b4f72; color:#fff; border:1px solid #3498db; padding:7px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">城主を一括任命</button>
              <button id="closeGovModalBtnBottom" style="background:#555; color:#fff; border:none; padding:7px 22px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">閉じる</button>
            </div>
          </div>
        </div>
      `;

      modal.style.display = 'flex';

      const closeModal = () => { modal.style.display = 'none'; };
      document.getElementById('closeGovModalBtn')?.addEventListener('click', closeModal);
      document.getElementById('closeGovModalBtnBottom')?.addEventListener('click', closeModal);
      document.getElementById('openBatchGovFromSingle')?.addEventListener('click', () => {
        closeModal();
        this.openBatchGovernorModal();
      });

      // 解任ボタン
      document.getElementById('btnDismissGov')?.addEventListener('click', () => {
        if (currentGov) {
          currentGov.assignedProvId = null;
        }
        p.governorId = null;
        const isCap = this.isCapitalProvince(p.id, p.ownerId);
        if (isCap) {
          this.log(`【城主解任】${p.name}の城主を解任し、大名本拠地親政（能力100%発揮）としました。`);
        } else {
          this.log(`【城主解任】${p.name}の城主を解任し、城代統治（大名能力の${Math.round((p.jodaiRatio || 0.55)*100)}%発揮）としました。`);
        }
        this.audio.playHyoshigi();
        closeModal();
        this.updateUI({ provId: p.id });
      });

      // ヘッダークリックソート
      modal.querySelectorAll('.sortable-gov-th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (sortKey === key) {
            sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
          } else {
            sortKey = key;
            sortOrder = (key === 'name' ? 'asc' : 'desc');
          }
          render();
        });
      });

      // 武将を城主任命する共通処理
      const appointOfficer = (offId) => {
        const newGov = myOfficers.find(o => o.id === offId);
        if (!newGov) return;
        if (newGov.id === p.governorId) {
          closeModal();
          return;
        }
        this.commitGovernorAppointment(p.id, offId);
        closeModal();
        this.updateUI({ provId: p.id });
      };

      // 行クリックで直接その武将を城主任命（列伝は表示しない）
      modal.querySelectorAll('.officer-table-row').forEach(row => {
        row.addEventListener('click', (e) => {
          const offId = row.dataset.offId;
          appointOfficer(offId);
        });
      });

      // 検索入力
      const searchInp = document.getElementById('inputGovSearch');
      if (searchInp) {
        const applySearch = (value) => {
          searchQuery = value;
          render();
          const newInp = document.getElementById('inputGovSearch');
          if (newInp) {
            newInp.focus();
            newInp.selectionStart = newInp.selectionEnd = newInp.value.length;
          }
        };
        searchInp.addEventListener('input', (e) => {
          if (e.isComposing || e.inputType === 'insertCompositionText') return;
          applySearch(e.target.value);
        });
        searchInp.addEventListener('compositionend', (e) => {
          applySearch(e.target.value);
        });
      }

      // 任命ボタン（行クリックと同一の任命処理を実行）
      modal.querySelectorAll('.btn-select-gov').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const offId = e.currentTarget.dataset.offId;
          appointOfficer(offId);
        });
      });
    };

    render();
  },

  // 城主一人を任命する。silent のときはログと音を出さない（一括任命用）,

  openBatchGovernorModal() {
    const mine = (this.provinces || []).filter(p => p.ownerId === this.playerClanId);
    if (mine.length === 0) {
      this.showOrderResult('⚠ 領国なし', '城主を任命できる自領がありません。', '#e67e22');
      return;
    }

    let modal = document.getElementById('batchGovernorModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'batchGovernorModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:100000; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    const officers = () => (this.activeOfficers || []).filter(o => o.clanId === this.playerClanId && !o.isDead);
    const draft = new Map();
    mine.forEach(p => draft.set(p.id, p.governorId || ''));

    const officerScore = (o) => (Number(o.politic) || 0) * 2 + (Number(o.intel) || 0) + (Number(o.military) || 0);

    const fillVacant = () => {
      const used = new Set();
      mine.forEach(p => {
        const id = draft.get(p.id);
        if (id) used.add(id);
      });

      let pool = officers().filter(o => !o.isDaimyo && !used.has(o.id));
      const vacant = mine.filter(p => !draft.get(p.id) && !this.isCapitalProvince(p.id, this.playerClanId));
      const remainingVacant = [];
      vacant.forEach(p => {
        const homeOfficers = pool.filter(o => o.defaultProv === p.id);
        if (homeOfficers.length > 0) {
          homeOfficers.sort((a, b) => officerScore(b) - officerScore(a));
          const best = homeOfficers[0];
          draft.set(p.id, best.id);
          used.add(best.id);
          pool = pool.filter(o => o.id !== best.id);
        } else {
          remainingVacant.push(p);
        }
      });

      const combat = (o) => (Number(o.military) || 0) * 2 + (Number(o.intel) || 0) + (Number(o.politic) || 0);
      const civil = (o) => (Number(o.politic) || 0) * 2 + (Number(o.intel) || 0) + (Number(o.military) || 0);
      const fronts = remainingVacant.filter(p => this.isClanFrontline(p))
        .sort((a, b) => this.frontlineWeight(b) - this.frontlineWeight(a));
      const rears = remainingVacant.filter(p => !this.isClanFrontline(p));
      pool.sort((a, b) => combat(b) - combat(a));
      fronts.forEach(p => {
        const next = pool.shift();
        if (!next) return;
        draft.set(p.id, next.id);
        used.add(next.id);
      });
      pool.sort((a, b) => civil(b) - civil(a));
      rears.forEach(p => {
        const next = pool.shift();
        if (!next) return;
        draft.set(p.id, next.id);
        used.add(next.id);
      });
    };

    mine.forEach(p => {
      if (!draft.get(p.id) && !this.isCapitalProvince(p.id, this.playerClanId)) {
        const used = new Set([...draft.values()].filter(Boolean));
        const homeOff = officers().find(o => !o.isDaimyo && !used.has(o.id) && o.defaultProv === p.id);
        if (homeOff) draft.set(p.id, homeOff.id);
      }
    });

    const render = () => {
      const offs = officers();
      const rows = mine.map(p => {
        const selected = draft.get(p.id) || '';
        const isCap = this.isCapitalProvince(p.id, this.playerClanId);
        const options = [`<option value="">城代のまま</option>`].concat(offs.map(o => {
          const age = this.year - (o.birthYear || 1530);
          const isHome = o.defaultProv === p.id;
          const homeBadge = isHome ? '★ゆかりの国 ' : '';
          const role = o.isDaimyo ? '当主' : (o.assignedProvId && o.assignedProvId !== p.id ? '他城' : '待機');
          return `<option value="${o.id}" ${selected === o.id ? 'selected' : ''}>${homeBadge}${o.name}（${role}・${age}歳 武${o.military} 内${o.politic} 謀${o.intel}）</option>`;
        })).join('');
        return `
          <tr style="border-bottom:1px solid #3d2d20;">
            <td style="padding:8px 10px; color:#fff; font-weight:bold; white-space:nowrap;">${this.getProvinceJapaneseName(p.id)} <span style="color:#aaa; font-weight:normal; font-size:11pt;">${p.castleName || p.castle || ''}</span> ${isCap ? '<span style="color:var(--gold-bright); font-size:11pt;">本拠</span>' : ''}</td>
            <td style="padding:8px 10px;">
              <select class="batch-gov-select" data-prov-id="${p.id}" style="width:100%; background:#22160d; color:#fff; border:1px solid #775533; padding:6px 8px; border-radius:4px; font-size:12pt;">
                ${options}
              </select>
            </td>
          </tr>`;
      }).join('');

      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:95vw; max-width:920px; height:86vh; display:flex; flex-direction:column; color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <div style="padding:12px 20px; border-bottom:1px solid #5a4638; display:flex; justify-content:space-between; align-items:center; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%);">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">❖ 城主一括任命 ❖</h3>
              <span style="font-size:12pt; color:#ccc;">各国の城主を選んで一度に任命します。自動任命はゆかりの地を優先し、強い武将を前線の城へ、残りの待機武将も空いた城へ配ります。本拠は対象外です。</span>
            </div>
            <button id="closeBatchGovBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer;">✕</button>
          </div>
          <div style="flex:1; overflow-y:auto; padding:8px 16px;">
            <table style="width:100%; border-collapse:collapse; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; color:var(--gold);">
                  <th style="text-align:left; padding:8px 10px; width:34%;">領国</th>
                  <th style="text-align:left; padding:8px 10px;">城主</th>
                </tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>
          </div>
          <div style="padding:12px 16px; border-top:1px solid #443322; display:flex; justify-content:space-between; gap:8px; flex-wrap:wrap;">
            <button id="batchGovAutoFill" style="background:#1b4f72; color:#fff; border:1px solid #3498db; padding:8px 14px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">空き城を自動任命</button>
            <div style="display:flex; gap:8px;">
              <button id="batchGovApply" style="background:linear-gradient(180deg, #d4af37, #b7950b); color:#111; border:none; padding:8px 18px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">この内容で一括任命</button>
              <button id="closeBatchGovBtnBottom" style="background:#555; color:#fff; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; font-size:12pt;">閉じる</button>
            </div>
          </div>
        </div>`;

      const close = () => { modal.style.display = 'none'; };
      document.getElementById('closeBatchGovBtn')?.addEventListener('click', close);
      document.getElementById('closeBatchGovBtnBottom')?.addEventListener('click', close);
      modal.onclick = (e) => { if (e.target === modal) close(); };

      modal.querySelectorAll('.batch-gov-select').forEach(sel => {
        sel.addEventListener('change', () => {
          const provId = sel.dataset.provId;
          const val = sel.value;
          if (val) {
            mine.forEach(other => {
              if (other.id !== provId && draft.get(other.id) === val) draft.set(other.id, '');
            });
          }
          draft.set(provId, val);
          render();
        });
      });

      document.getElementById('batchGovAutoFill')?.addEventListener('click', () => {
        fillVacant();
        render();
      });

      document.getElementById('batchGovApply')?.addEventListener('click', () => {
        const daimyo = offs.find(o => o.isDaimyo);
        const ordered = mine.slice().sort((a, b) => {
          const aD = draft.get(a.id) && daimyo && draft.get(a.id) === daimyo.id ? 1 : 0;
          const bD = draft.get(b.id) && daimyo && draft.get(b.id) === daimyo.id ? 1 : 0;
          return aD - bD;
        });
        let changed = 0;
        ordered.forEach(p => {
          const want = draft.get(p.id) || '';
          if (!want) {
            if (this.clearCastleGovernor(p.id, { silent: true })) changed++;
          } else if (this.commitGovernorAppointment(p.id, want, { silent: true })) {
            changed++;
          }
        });
        this.log(`【城主一括任命】${changed}件の城主任命を更新しました。`, 'important');
        this.audio.playTaiko();
        this.showOrderResult('🏯 城主一括任命', `${changed}件の任命を更新しました`, '#2ecc71');
        const listOpen = document.getElementById('provinceListModal')?.style.display === 'flex';
        close();
        if (this.selectedProvId) this.updateUI({ provId: this.selectedProvId });
        if (listOpen) this.openProvinceListModal();
      });
    };

    render();
    modal.style.display = 'flex';
    this.audio.playHyoshigi();
  },

  // 武将一覧モーダル（表形式・ソート対応・幅広ダイアログ・文字サイズ12pt以上）,

  openOfficerListModal() {
    this.reconcileDaimyoWithMap();
    let modal = document.getElementById('officerListModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'officerListModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    let currentTab = 'my'; // 'my', 'all', or 'ronin'
    let sortKey = 'role'; // 'role', 'name', 'clan', 'age', 'military', 'politic', 'intel', 'comment'
    let sortOrder = 'desc'; // 'asc' or 'desc'
    let searchQuery = '';

    const render = () => {
      const allActive = (this.activeOfficers || this.officers || []).filter(o => !o.isDead);
      const myActive = allActive.filter(o => o.clanId === this.playerClanId);
      const roninActive = allActive.filter(o => o.clanId === 'ronin');
      
      let list = currentTab === 'my' ? [...myActive] : (currentTab === 'ronin' ? [...roninActive] : [...allActive]);

      if (searchQuery) {
        const q = searchQuery.trim().toLowerCase();
        list = list.filter(o => {
          const comment = this.getOfficerComment(o).toLowerCase();
          const clanName = `${this.getClanDisplayName(o.clanId) || ''} ${this.getClanFamilyName(o.clanId) || ''}`.toLowerCase();
          return (o.name && o.name.toLowerCase().includes(q)) || 
                 comment.includes(q) || 
                 clanName.includes(q);
        });
      }

      // ソート処理
      list.sort((a, b) => {
        let diff = 0;
        if (sortKey === 'role') {
          // 当主(3) > 城代(2) > 待機中(1) > 浪人(0)
          const getRoleScore = (off) => {
            if (off.isDaimyo) return 3;
            if (off.assignedProvId) return 2;
            if (off.clanId === 'ronin') return 0;
            return 1;
          };
          diff = getRoleScore(a) - getRoleScore(b);
          if (diff === 0) diff = (a.military || 0) - (b.military || 0);
        } else if (sortKey === 'base') {
          diff = this.provinceGeoRank(this.officerBaseProvinceId(a)) - this.provinceGeoRank(this.officerBaseProvinceId(b));
          if (diff === 0) diff = (a.name || '').localeCompare(b.name || '', 'ja');
        } else if (sortKey === 'name') {
          diff = (a.name || '').localeCompare(b.name || '', 'ja');
        } else if (sortKey === 'clan') {
          const clanA = a.clanId === 'ronin' ? '浪人' : (this.getClanDisplayName(a.clanId) || '');
          const clanB = b.clanId === 'ronin' ? '浪人' : (this.getClanDisplayName(b.clanId) || '');
          diff = clanA.localeCompare(clanB, 'ja');
        } else if (sortKey === 'age') {
          const ageA = this.year - (a.birthYear || 1530);
          const ageB = this.year - (b.birthYear || 1530);
          diff = ageA - ageB;
        } else if (sortKey === 'military') {
          diff = (a.military || 0) - (b.military || 0);
        } else if (sortKey === 'politic') {
          diff = (a.politic || 0) - (b.politic || 0);
        } else if (sortKey === 'intel') {
          diff = (a.intel || 0) - (b.intel || 0);
        } else if (sortKey === 'comment') {
          diff = this.getOfficerComment(a).localeCompare(this.getOfficerComment(b), 'ja');
        }
        return sortOrder === 'desc' ? -diff : diff;
      });

      const getSortIcon = (key) => {
        if (sortKey !== key) return '<span style="color:#776655; font-size:11pt; margin-left:4px;">↕</span>';
        return sortOrder === 'asc' 
          ? '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▲</span>' 
          : '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▼</span>';
      };

      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:95vw; max-width:1180px; height:88vh; display:flex; flex-direction:column; box-shadow:0 0 45px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <!-- ヘッダー -->
          <div style="padding:12px 22px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">❖ 参陣武将録・名将一覧 ❖</h3>
              <span style="font-size:12pt; color:#ccc;">自軍および天下に名轟く武将・浪人の身分・拠点・能力を閲覧できます。浪人は直接登用も可能です。</span>
            </div>
            <button id="closeOfficerModalBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 8px;">✕</button>
          </div>

          <!-- コントロールバー（タブ、検索） -->
          <div style="padding:10px 20px; background:rgba(0,0,0,0.35); border-bottom:1px dashed #5a4638; display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center;">
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <button id="tabMyOfficers" style="background:${currentTab === 'my' ? '#922b21' : '#2b1d14'}; color:#fff; border:1px solid ${currentTab === 'my' ? '#c0392b' : '#664422'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:0.2s;">
                我が軍の武将 (${myActive.length}名)
              </button>
              <button id="tabRoninOfficers" style="background:${currentTab === 'ronin' ? '#b7950b' : '#2b1d14'}; color:${currentTab === 'ronin' ? '#fff' : '#f1c40f'}; border:1px solid ${currentTab === 'ronin' ? '#d4af37' : '#886622'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:0.2s;">
                🤝 浪人・未仕官 (${roninActive.length}名)
              </button>
              <button id="tabAllOfficers" style="background:${currentTab === 'all' ? '#922b21' : '#2b1d14'}; color:#fff; border:1px solid ${currentTab === 'all' ? '#c0392b' : '#664422'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:0.2s;">
                天下の武将 (${allActive.length}名)
              </button>
            </div>

            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12pt; color:#aaa;">検索:</span>
              <input id="inputOfficerSearch" type="text" placeholder="武将名・所属..." value="${searchQuery}" style="background:#22160d; color:#fff; border:1px solid #775533; padding:5px 10px; border-radius:4px; font-size:12pt; width:190px;">
            </div>
          </div>

          <!-- 武将テーブル一覧 -->
          <div style="flex:1; overflow-y:auto; padding:0 20px;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; border-bottom:2px solid #775533; z-index:10; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
                  <th class="sortable-off-th" data-key="name" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:140px; font-size:12pt;">名前 ${getSortIcon('name')}</th>
                  <th class="sortable-off-th" data-key="role" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:110px; text-align:center; font-size:12pt;">身分・配置 ${getSortIcon('role')}</th>
                  <th class="sortable-off-th" data-key="base" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:135px; text-align:center; font-size:12pt;">拠点 ${getSortIcon('base')}</th>
                  <th class="sortable-off-th" data-key="clan" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:130px; font-size:12pt;">所属 ${getSortIcon('clan')}</th>
                  <th class="sortable-off-th" data-key="age" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:150px; text-align:center; font-size:12pt;">年齢・生没年 ${getSortIcon('age')}</th>
                  <th class="sortable-off-th" data-key="military" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:80px; text-align:center; font-size:12pt;">武勇 ${getSortIcon('military')}</th>
                  <th class="sortable-off-th" data-key="politic" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:80px; text-align:center; font-size:12pt;">内政 ${getSortIcon('politic')}</th>
                  <th class="sortable-off-th" data-key="intel" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:80px; text-align:center; font-size:12pt;">知略 ${getSortIcon('intel')}</th>
                  <th style="padding:11px 10px; color:var(--gold); width:100px; text-align:center; font-size:12pt;">登用</th>
                </tr>
              </thead>
              <tbody>
                ${list.length === 0 ? `
                  <tr>
                    <td colspan="9" style="text-align:center; padding:30px; color:#888; font-size:12pt;">該当する武将は見つかりませんでした。</td>
                  </tr>
                ` : ''}
                ${list.map((off, idx) => {
                  const assignedProv = off.assignedProvId ? this.provinces.find(x => x.id === off.assignedProvId) : null;
                  const isMyClan = off.clanId === this.playerClanId;
                  const isRonin = off.clanId === 'ronin';
                  const homeProv = off.isDaimyo ? this.getDaimyoHomeProvince(off) : null;
                  const isMapDaimyo = !!homeProv;
                  const clanName = isRonin ? '浪人 (未仕官)' : this.getClanFamilyName(off.clanId);
                  const clanAffiliation = isRonin ? clanName : (isMapDaimyo ? `${clanName} (当主)` : `${clanName} 配下`);
                  const age = this.year - (off.birthYear || 1530);

                  let roleBadge = '';
                  if (isMapDaimyo) {
                    roleBadge = '<span style="background:#b7950b; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt; font-weight:bold;">👑 当主</span>';
                  } else if (assignedProv) {
                    roleBadge = '<span style="background:#27ae60; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt; font-weight:bold;">🏯 城主</span>';
                  } else if (isRonin) {
                    roleBadge = '<span style="background:#7f8c8d; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt;">浪人</span>';
                  } else {
                    roleBadge = '<span style="background:#2980b9; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt;">待機中</span>';
                  }

                  // 拠点
                  let baseDisplay = '-';
                  if (assignedProv) {
                    baseDisplay = `<span style="color:#2ecc71; font-weight:bold;">${assignedProv.name}</span><span style="color:#aaa; font-size:11pt; margin-left:3px;">(${assignedProv.castleName || assignedProv.castle})</span>`;
                  } else if (isMapDaimyo) {
                    baseDisplay = `<span style="color:var(--gold-bright); font-weight:bold;">${homeProv.name}</span><span style="color:#aaa; font-size:11pt; margin-left:3px;">(居城)</span>`;
                  } else if (isRonin) {
                    const defProvName = off.defaultProv ? this.getProvinceJapaneseName(off.defaultProv) : '';
                    const isDefProvMine = off.defaultProv && this.provinces.some(p => p.id === off.defaultProv && p.ownerId === this.playerClanId);
                    baseDisplay = defProvName 
                      ? `<span style="color:${isDefProvMine ? '#2ecc71' : '#bdc3c7'}; font-weight:${isDefProvMine ? 'bold' : 'normal'};">${defProvName}</span><span style="color:#888; font-size:11pt; margin-left:3px;">(${isDefProvMine ? '自領内' : '流浪'})</span>` 
                      : '<span style="color:#888;">諸国流浪</span>';
                  } else {
                    const capProv = this.getDaimyoHomeProvince(off);
                    baseDisplay = capProv 
                      ? `<span style="color:#5dade2;">${capProv.name}</span><span style="color:#888; font-size:11pt; margin-left:3px;">(待機)</span>` 
                      : '<span style="color:#888;">本国待機</span>';
                  }

                  const rowBg = isMapDaimyo 
                    ? 'rgba(183, 149, 11, 0.12)' 
                    : (idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.18)');

                  const roninReach = isRonin ? this.getRoninServiceReach(off, this.playerClanId) : null;
                  const farNote = roninReach && roninReach.dist > 1
                    ? `<div style="font-size:10pt; color:${roninReach.lacksHeir ? '#f5b041' : '#85c1e9'}; margin-top:2px;">${roninReach.lacksHeir ? '遠国・跡継ぎ不在で上昇' : '遠国・登用可'}</div>`
                    : '';
                  const recruitBtn = isRonin
                    ? (roninReach.reachable
                      ? `<button class="btn-recruit-ronin-row" data-off-id="${off.id}" style="background:linear-gradient(180deg, #d4af37, #b7950b); color:#111; border:none; padding:3px 10px; border-radius:3px; font-weight:bold; font-size:11.5pt; cursor:pointer; box-shadow:0 1px 3px rgba(0,0,0,0.5);">🤝 登用</button>${farNote}`
                      : `<span style="color:#888; font-size:11.5pt;" title="所在が分からず登用できません">所在不明</span>`)
                    : (isMyClan ? '<span style="color:#2ecc71; font-size:11.5pt;">自軍配下</span>' : '<span style="color:#777; font-size:11.5pt;">他家所属</span>');

                  return `
                    <tr class="officer-table-row" data-off-id="${off.id}" title="クリックで人物列伝を表示" style="background:${rowBg}; border-bottom:1px solid #3d2d20; cursor:pointer; font-size:12pt; transition:background 0.15s;" onmouseover="this.style.background='rgba(215, 175, 100, 0.12)'" onmouseout="this.style.background='${rowBg}'">
                      <td style="padding:10px 12px; font-weight:bold; color:#ffffff; white-space:nowrap; font-size:12.5pt; text-decoration:none; border-bottom:none;">
                        ${off.name}
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap;">
                        ${roleBadge}
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap; font-size:12pt;">
                        ${baseDisplay}
                      </td>
                      <td style="padding:10px 12px; white-space:nowrap;">
                        <span style="background:${isRonin ? 'rgba(127, 140, 141, 0.25)' : (isMyClan ? 'rgba(46, 204, 113, 0.2)' : 'rgba(255, 255, 255, 0.05)')}; color:${isRonin ? '#bdc3c7' : (isMyClan ? '#2ecc71' : '#e0d8c3')}; padding:3px 8px; border-radius:3px; border:1px solid ${isRonin ? '#7f8c8d' : (isMyClan ? '#27ae60' : '#5a4638')}; font-size:12pt;">
                          ${clanAffiliation}
                        </span>
                      </td>
                      <td style="padding:10px 12px; text-align:center; color:#ddd; white-space:nowrap; font-size:12pt;">
                        <strong style="color:#ffffff; font-size:12.5pt;">${age}歳</strong>
                        <span style="color:#aaa; font-size:12pt; margin-left:4px;">(${off.birthYear}〜${off.deathYear})</span>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#ff6b6b; font-size:12.5pt;">${off.military}</b>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#5dade2; font-size:12.5pt;">${off.politic}</b>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#a3e4d7; font-size:12.5pt;">${off.intel}</b>
                      </td>
                      <td style="padding:10px 8px; text-align:center; white-space:nowrap;">
                        ${recruitBtn}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- フッター -->
          <div style="padding:12px 20px; border-top:1px solid #443322; background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12pt; color:#aaa;">表示中: ${list.length}名 (現在年: ${this.year}年) 💡行クリックで人物列伝を表示 ｜ 遠国も登用可（遠いほど成功率は低下）。跡継ぎ不在時は確率が上がり、仕官も来ます</span>
            <button id="closeOfficerModalBtnBottom" style="background:#555; color:#fff; border:none; padding:7px 14px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">閉</button>
          </div>
        </div>
      `;

      modal.style.display = 'flex';

      const closeModal = () => { modal.style.display = 'none'; };
      document.getElementById('closeOfficerModalBtn')?.addEventListener('click', closeModal);
      document.getElementById('closeOfficerModalBtnBottom')?.addEventListener('click', closeModal);

      document.getElementById('tabMyOfficers')?.addEventListener('click', () => { currentTab = 'my'; render(); });
      document.getElementById('tabRoninOfficers')?.addEventListener('click', () => { currentTab = 'ronin'; render(); });
      document.getElementById('tabAllOfficers')?.addEventListener('click', () => { currentTab = 'all'; render(); });

      // 浪人の直接登用ボタン
      modal.querySelectorAll('.btn-recruit-ronin-row').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const offId = btn.dataset.offId;
          this.recruitRonin(offId, () => {
            render();
          });
        });
      });

      // ヘッダークリックソート
      modal.querySelectorAll('.sortable-off-th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (sortKey === key) {
            sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
          } else {
            sortKey = key;
            sortOrder = (key === 'name' || key === 'clan' || key === 'base' ? 'asc' : 'desc');
          }
          render();
        });
      });

      // 行クリックで武将詳細・列伝モーダル展開
      modal.querySelectorAll('.officer-table-row').forEach(row => {
        row.addEventListener('click', (e) => {
          if (e.target.closest('button')) return;
          const offId = row.dataset.offId;
          const off = list.find(o => o.id === offId) 
                   || (this.activeOfficers || []).find(o => o.id === offId)
                   || (window.OFFICERS_MASTER || []).find(o => o.id === offId);
          if (off) {
            this.showOfficerDetailModal(off);
          }
        });
      });

      const searchInput = document.getElementById('inputOfficerSearch');
      if (searchInput) {
        const applySearch = (value) => {
          searchQuery = value;
          render();
          const newInp = document.getElementById('inputOfficerSearch');
          if (newInp) {
            newInp.focus();
            newInp.selectionStart = newInp.selectionEnd = newInp.value.length;
          }
        };
        searchInput.addEventListener('input', (e) => {
          if (e.isComposing || e.inputType === 'insertCompositionText') return;
          applySearch(e.target.value);
        });
        searchInput.addEventListener('compositionend', (e) => {
          applySearch(e.target.value);
        });
      }
    };

    render();
    this.audio.playHyoshigi();
  },

  // 領国一覧モーダル（武将一覧と同じ表形式・ソート・検索）,

  openProvinceListModal() {
    if (this.isAutoPlay) this.stopAutoPlay('領国一覧表示のため');

    let modal = document.getElementById('provinceListModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'provinceListModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    let currentTab = 'my'; // 'my', 'all', or 'blank'
    let sortKey = 'castle';
    let sortOrder = 'asc';
    let searchQuery = '';
    const geoIndex = (row) => this.provinceGeoRank(row.p && row.p.id);
    const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));

    const formatManKoku = (n) => {
      const v = Number(n) || 0;
      if (v >= 10000) {
        const man = v / 10000;
        const text = man >= 100 ? String(Math.round(man)) : (Math.round(man * 10) / 10).toFixed(1).replace(/\.0$/, '');
        return `${text}万石`;
      }
      return `${v.toLocaleString('ja-JP')}石`;
    };

    const render = () => {
      const allProvs = this.provinces || [];
      const myProvs = allProvs.filter(p => p.ownerId === this.playerClanId);
      const blankProvs = allProvs.filter(p => !p.ownerId);
      let source = currentTab === 'my' ? myProvs : (currentTab === 'blank' ? blankProvs : allProvs);

      const castleOf = (p) => (this.currentScenario && this.currentScenario.castles && this.currentScenario.castles[p.id]) || p.castleName || p.castle || '居城';

      let rows = source.map(p => {
        const isBlank = !p.ownerId;
        const isMine = p.ownerId === this.playerClanId;
        const eff = isBlank ? null : this.getEffectiveStats(p.id);
        const castle = castleOf(p);
        const ownerName = isBlank ? '空白地' : (this.getClanFamilyName(p.ownerId) || '無所属');
        let govName = isBlank ? '国人・土豪' : (eff?.name || '城代');
        let roleRank = 0;
        if (!isBlank && eff?.isCapital && eff?.isDaimyo) roleRank = 3;
        else if (!isBlank && eff?.governor) roleRank = 2;
        else if (!isBlank) roleRank = 1;
        const officer = (!isBlank && eff && !eff.isJodai && eff.governor) ? eff.governor : null;
        let military = isBlank ? null : Number(eff?.military ?? 0);
        let politics = isBlank ? null : Number(eff?.politics ?? 0);
        let stratagem = isBlank ? null : Number(eff?.stratagem ?? 0);
        return {
          p,
          isBlank,
          isMine,
          eff,
          castle,
          region: p.region || '諸国',
          ownerName,
          govName,
          roleRank,
          officer,
          military,
          politics,
          stratagem,
          kokudaka: Number(p.kokudaka) || 0,
          troops: Number(p.troops) || 0,
          defense: Number(p.defense) || 0,
          commerce: Number(p.commerce) || 0,
          morale: Number(p.morale) || 0,
          order: Number(p.order !== undefined ? p.order : 85) || 0,
          specialty: p.specialty || ''
        };
      });

      if (searchQuery) {
        const q = searchQuery.trim().toLowerCase();
        rows = rows.filter(r => {
          const policy = r.isBlank ? '' : this.getGovernModeName(r.p.governance);
          const blob = `${r.p.name || ''} ${r.castle} ${r.region} ${r.ownerName} ${r.govName} ${r.specialty} ${policy}`.toLowerCase();
          return blob.includes(q);
        });
      }

      rows.sort((a, b) => {
        let diff = 0;
        if (sortKey === 'name') diff = (a.p.name || '').localeCompare(b.p.name || '', 'ja');
        else if (sortKey === 'castle' || sortKey === 'region') diff = geoIndex(a) - geoIndex(b);

        else if (sortKey === 'owner') diff = a.ownerName.localeCompare(b.ownerName, 'ja');
        else if (sortKey === 'governor') {
          diff = a.roleRank - b.roleRank;
          if (diff === 0) diff = a.govName.localeCompare(b.govName, 'ja');
        } else if (sortKey === 'military') diff = (a.military ?? -1) - (b.military ?? -1);
        else if (sortKey === 'politics') diff = (a.politics ?? -1) - (b.politics ?? -1);
        else if (sortKey === 'stratagem') diff = (a.stratagem ?? -1) - (b.stratagem ?? -1);
        else if (sortKey === 'kokudaka') diff = a.kokudaka - b.kokudaka;
        else if (sortKey === 'troops') diff = a.troops - b.troops;
        else if (sortKey === 'defense') diff = a.defense - b.defense;
        else if (sortKey === 'commerce') diff = a.commerce - b.commerce;
        else if (sortKey === 'morale') diff = a.morale - b.morale;
        else if (sortKey === 'order') diff = a.order - b.order;
        const tie = (a.p.name || '').localeCompare(b.p.name || '', 'ja');
        const primary = sortOrder === 'desc' ? -diff : diff;
        return primary || tie;
      });

      const getSortIcon = (key) => {
        if (sortKey !== key) return '<span style="color:#776655; font-size:11pt; margin-left:4px;">↕</span>';
        return sortOrder === 'asc'
          ? '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▲</span>'
          : '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▼</span>';
      };

      const th = (key, label, extra) => `<th class="sortable-prov-th" data-key="${key}" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; font-size:12pt; white-space:nowrap; ${extra || ''}">${label} ${getSortIcon(key)}</th>`;

      const governorCell = (r, roleBadge) => `<td style="padding:8px 8px; white-space:nowrap;">${roleBadge}<b style="margin-left:6px; color:#fff;">${esc(r.govName)}</b></td>`;

      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:96vw; max-width:1560px; height:88vh; display:flex; flex-direction:column; box-shadow:0 0 45px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <div style="padding:12px 22px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">❖ 領国録・城主と石高 ❖</h3>
              <span style="font-size:12pt; color:#ccc;">城主と武勇・内政・智謀、兵力や表高を一覧できます。城主・当主の行をクリックすると、その武将の概要と列伝が開きます。城代や空白地の行は、地図でその領国を選びます。</span>
            </div>
            <button id="closeProvinceModalBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 8px;">✕</button>
          </div>

          <div style="padding:10px 20px; background:rgba(0,0,0,0.35); border-bottom:1px dashed #5a4638; display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center;">
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <button id="tabMyProvinces" style="background:${currentTab === 'my' ? '#922b21' : '#2b1d14'}; color:#fff; border:1px solid ${currentTab === 'my' ? '#c0392b' : '#664422'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">
                我が領国 (${myProvs.length}国)
              </button>
              <button id="tabAllProvinces" style="background:${currentTab === 'all' ? '#922b21' : '#2b1d14'}; color:#fff; border:1px solid ${currentTab === 'all' ? '#c0392b' : '#664422'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">
                天下の領国 (${allProvs.length}国)
              </button>
              <button id="tabBlankProvinces" style="background:${currentTab === 'blank' ? '#7f8c8d' : '#2b1d14'}; color:${currentTab === 'blank' ? '#fff' : '#bdc3c7'}; border:1px solid ${currentTab === 'blank' ? '#bdc3c7' : '#664422'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">
                空白地 (${blankProvs.length}国)
              </button>
              <button id="provListOpenBatchGov" title="自領の城主をまとめて任命" style="background:linear-gradient(180deg, #d4af37, #b7950b); color:#111; border:none; padding:6px 14px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">城主一括任命</button>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12pt; color:#aaa;">検索:</span>
              <input id="inputProvinceSearch" type="text" placeholder="国名・城・城主・領主..." value="${esc(searchQuery)}" style="background:#22160d; color:#fff; border:1px solid #775533; padding:5px 10px; border-radius:4px; font-size:12pt; width:210px;">
            </div>
          </div>

          <div id="provinceListScroll" style="flex:1; overflow:auto; padding:0 12px 0 20px;">
            <table style="width:max-content; min-width:100%; border-collapse:collapse; text-align:left; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; border-bottom:2px solid #775533; z-index:10; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
                  ${th('name', '国名', '')}
                  ${th('castle', '城', 'min-width:14em;')}
                  ${th('region', '地方', 'text-align:center;')}
                  ${th('owner', '領主', '')}
                  ${th('governor', '城主', 'min-width:11em;')}
                  ${th('military', '武勇', 'text-align:center;')}
                  ${th('politics', '内政', 'text-align:center;')}
                  ${th('stratagem', '智謀', 'text-align:center;')}
                  ${th('troops', '兵力', 'text-align:right;')}
                  ${th('defense', '防御', 'text-align:center;')}
                  ${th('morale', '士気', 'text-align:center;')}
                  ${th('kokudaka', '表高', 'text-align:right;')}
                  ${th('commerce', '商業', 'text-align:right;')}
                  ${th('order', '治安度', 'text-align:center;')}
                </tr>
              </thead>
              <tbody>
                ${rows.length === 0 ? `
                  <tr>
                    <td colspan="14" style="text-align:center; padding:30px; color:#888; font-size:12pt;">該当する領国は見つかりませんでした。</td>
                  </tr>
                ` : rows.map((r, idx) => {
                  const eff = r.eff;
                  let roleBadge = '';
                  if (r.isBlank) {
                    roleBadge = '<span style="background:#7f8c8d; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt;">空白</span>';
                  } else if (eff && eff.isCapital && eff.isDaimyo) {
                    roleBadge = '<span style="background:#b7950b; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt; font-weight:bold;">👑 本拠</span>';
                  } else if (eff && eff.governor) {
                    roleBadge = '<span style="background:#27ae60; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt; font-weight:bold;">🏯 城主</span>';
                  } else {
                    const rawBadge = String(eff?.vacantBadge || '城代');
                    const badgeText = rawBadge.startsWith('城代統治') ? '城代統治' : rawBadge;
                    const badge = esc(badgeText);
                    roleBadge = `<span style="background:#d35400; color:#fff; padding:2px 8px; border-radius:3px; font-size:12pt; font-weight:bold;">${badge}</span>`;
                  }
                  const statCell = (value, color) => value == null
                    ? '<td style="padding:10px 8px; text-align:center; white-space:nowrap; color:#777;">—</td>'
                    : `<td style="padding:10px 8px; text-align:center; white-space:nowrap;"><b style="color:${color}; font-size:12.5pt;">${value}</b></td>`;
                  const isSelected = r.p.id === this.selectedProvId;
                  const rowBg = isSelected
                    ? 'rgba(215, 175, 100, 0.22)'
                    : (r.isMine && eff && eff.isCapital
                      ? 'rgba(183, 149, 11, 0.12)'
                      : (r.isBlank
                        ? 'rgba(127, 140, 141, 0.08)'
                        : (idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.18)')));
                  const ownerStyle = r.isBlank
                    ? 'background:rgba(127,140,141,0.25); color:#bdc3c7; border:1px solid #7f8c8d;'
                    : (r.isMine
                      ? 'background:rgba(46,204,113,0.2); color:#2ecc71; border:1px solid #27ae60;'
                      : 'background:rgba(255,255,255,0.05); color:#e0d8c3; border:1px solid #5a4638;');
                  const rowTitle = r.officer ? 'クリックで武将の概要と列伝を表示' : 'クリックで地図上の領国を選択';
                  return `
                    <tr class="province-table-row" role="button" tabindex="0" data-prov-id="${esc(r.p.id)}" data-off-id="${esc(r.officer ? r.officer.id : '')}" title="${rowTitle}" style="background:${rowBg}; border-bottom:1px solid #3d2d20; cursor:pointer; font-size:12pt;" onmouseover="this.style.background='rgba(215, 175, 100, 0.12)'" onmouseout="this.style.background='${rowBg}'">
                      <td style="padding:10px 8px; font-weight:bold; color:#fff; white-space:nowrap; font-size:12.5pt;">${esc(r.p.name)}</td>
                      <td style="padding:10px 8px; color:#f5eedc; white-space:nowrap; min-width:14em;" title="${esc(r.specialty)}">${esc(r.castle)}</td>
                      <td style="padding:10px 8px; text-align:center; white-space:nowrap; color:#ccc;">${esc(r.region)}</td>
                      <td style="padding:10px 10px; white-space:nowrap;">
                        <span style="${ownerStyle} padding:3px 8px; border-radius:3px; font-size:12pt;">${esc(r.ownerName)}</span>
                      </td>
                      ${governorCell(r, roleBadge)}
                      ${statCell(r.military, '#ff6b6b')}
                      ${statCell(r.politics, '#5dade2')}
                      ${statCell(r.stratagem, '#a3e4d7')}
                      <td style="padding:10px 10px; text-align:right; white-space:nowrap;">${r.troops.toLocaleString('ja-JP')}<span style="color:#aaa; font-size:11pt;"> 人</span></td>
                      <td style="padding:10px 8px; text-align:center; white-space:nowrap;">${r.defense}</td>
                      <td style="padding:10px 8px; text-align:center; white-space:nowrap;">${r.morale}</td>
                      <td style="padding:10px 10px; text-align:right; white-space:nowrap;"><b style="color:#ffd700; font-size:12.5pt;">${formatManKoku(r.kokudaka)}</b></td>
                      <td style="padding:10px 10px; text-align:right; white-space:nowrap;">${r.commerce.toLocaleString('ja-JP')}<span style="color:#aaa; font-size:11pt;"> 貫</span></td>
                      <td style="padding:10px 8px; text-align:center; white-space:nowrap;">${r.order}%</td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <div style="padding:12px 20px; border-top:1px solid #443322; background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center; gap:12px;">
            <span style="font-size:12pt; color:#aaa;">表示中: ${rows.length}国 (現在年: ${this.year}年) ｜ 城主・当主の行は列伝 ｜ 城代・空白地の行は地図を選択</span>
            <button id="closeProvinceModalBtnBottom" style="background:#555; color:#fff; border:none; padding:7px 14px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; white-space:nowrap;">閉</button>
          </div>
        </div>
      `;

      modal.style.display = 'flex';

      const closeModal = () => { modal.style.display = 'none'; };
      document.getElementById('closeProvinceModalBtn')?.addEventListener('click', closeModal);
      document.getElementById('closeProvinceModalBtnBottom')?.addEventListener('click', closeModal);

      document.getElementById('tabMyProvinces')?.addEventListener('click', () => { currentTab = 'my'; render(); });
      document.getElementById('tabAllProvinces')?.addEventListener('click', () => { currentTab = 'all'; render(); });
      document.getElementById('tabBlankProvinces')?.addEventListener('click', () => { currentTab = 'blank'; render(); });
      document.getElementById('provListOpenBatchGov')?.addEventListener('click', () => this.openBatchGovernorModal());

      modal.querySelectorAll('.sortable-prov-th').forEach(el => {
        el.addEventListener('click', () => {
          const key = el.dataset.key;
          if (sortKey === key) {
            sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
          } else {
            sortKey = key;
            sortOrder = (key === 'name' || key === 'castle' || key === 'region' || key === 'owner') ? 'asc' : 'desc';
          }
          render();
        });
      });

      modal.querySelectorAll('.province-table-row').forEach(row => {
        row.addEventListener('click', () => {
          const offId = row.dataset.offId;
          if (offId) {
            const off = (this.activeOfficers || []).find(o => o.id === offId)
              || (this.officers || []).find(o => o.id === offId)
              || (window.OFFICERS_MASTER || []).find(o => o.id === offId);
            if (off) {
              this.showOfficerDetailModal(off);
              return;
            }
          }
          const provId = row.dataset.provId;
          if (!provId) return;
          closeModal();
          this.selectProvince(provId);
        });
      });

      const searchInput = document.getElementById('inputProvinceSearch');
      if (searchInput) {
        const applySearch = (value) => {
          searchQuery = value;
          render();
          const newInp = document.getElementById('inputProvinceSearch');
          if (newInp) {
            newInp.focus();
            newInp.selectionStart = newInp.selectionEnd = newInp.value.length;
          }
        };
        searchInput.addEventListener('input', (e) => {
          if (e.isComposing || e.inputType === 'insertCompositionText') return;
          applySearch(e.target.value);
        });
        searchInput.addEventListener('compositionend', (e) => {
          applySearch(e.target.value);
        });
      }
    };

    render();
    this.audio.playHyoshigi();
  },

  // ============================================================================
  // 勢力一覧 ＆ 外交・同盟関係モーダル（表形式・ソート対応・同盟締結＆破棄対応）
  // ============================================================================,

  openFactionListModal() {
    let modal = document.getElementById('factionListModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'factionListModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    let sortKey = 'provCount'; // 'clan', 'leader', 'base', 'provCount', 'totalRice', 'totalTroops', 'officerCount', 'diplomacy'
    let sortOrder = 'desc'; // 'asc' or 'desc'
    let searchQuery = '';

    const render = () => {
      // 地図上に存在する全大名勢力ID（領国を持つ大名）
      const activeClanIds = [...new Set((this.provinces || []).map(p => p.ownerId).filter(Boolean))];

      // 各大名家の統計情報を集計
      let factions = activeClanIds.map(clanId => {
        const clanName = this.getClanFamilyName(clanId);
        const daimyoName = this.getDaimyoLeaderName(clanId);
        const provs = (this.provinces || []).filter(p => p.ownerId === clanId);
        const provCount = provs.length;
        const totalRice = provs.reduce((sum, p) => sum + (Number(p.rice) || 0), 0);
        const totalTroops = provs.reduce((sum, p) => sum + (Number(p.troops) || 0), 0);
        const officers = (this.activeOfficers || this.officers || []).filter(o => o.clanId === clanId && !o.isDead);
        const officerCount = officers.length;

        // 本拠地城
        const capId = (window.CLAN_CAPITAL_PROVINCES && window.CLAN_CAPITAL_PROVINCES[clanId]);
        const capProv = capId ? this.provinces.find(p => p.id === capId && p.ownerId === clanId) : null;
        const mainProv = capProv || provs[0];
        const capitalDisplay = mainProv ? `${mainProv.name} (${mainProv.castleName || mainProv.castle || '居城'})` : '-';

        // 同盟国一覧
        const allies = this.getAllies(clanId);

        // プレイヤーとの関係
        const isPlayer = (clanId === this.playerClanId);
        const isAlliedWithPlayer = this.isAllied(this.playerClanId, clanId);

        return {
          clanId,
          clanName,
          daimyoName,
          provinces: provs,
          provCount,
          totalRice,
          totalTroops,
          officerCount,
          capitalDisplay,
          allies,
          isPlayer,
          isAlliedWithPlayer
        };
      });

      // 検索フィルター
      if (searchQuery) {
        const q = searchQuery.trim().toLowerCase();
        factions = factions.filter(f => 
          f.clanName.toLowerCase().includes(q) ||
          f.daimyoName.toLowerCase().includes(q) ||
          f.capitalDisplay.toLowerCase().includes(q) ||
          f.allies.some(aId => `${this.getClanFamilyName(aId)} ${this.getDaimyoLeaderName(aId)}`.toLowerCase().includes(q))
        );
      }

      // ソート処理
      factions.sort((a, b) => {
        let diff = 0;
        if (sortKey === 'clan') {
          diff = a.clanName.localeCompare(b.clanName, 'ja');
        } else if (sortKey === 'leader') {
          diff = a.daimyoName.localeCompare(b.daimyoName, 'ja');
        } else if (sortKey === 'base') {
          diff = a.capitalDisplay.localeCompare(b.capitalDisplay, 'ja');
        } else if (sortKey === 'provCount') {
          diff = a.provCount - b.provCount;
        } else if (sortKey === 'totalRice') {
          diff = a.totalRice - b.totalRice;
        } else if (sortKey === 'totalTroops') {
          diff = a.totalTroops - b.totalTroops;
        } else if (sortKey === 'officerCount') {
          diff = a.officerCount - b.officerCount;
        } else if (sortKey === 'diplomacy') {
          const getDipScore = (f) => f.isPlayer ? 3 : (f.isAlliedWithPlayer ? 2 : 1);
          diff = getDipScore(a) - getDipScore(b);
        }
        return sortOrder === 'desc' ? -diff : diff;
      });

      const getSortIcon = (key) => {
        if (sortKey !== key) return '<span style="color:#776655; font-size:11pt; margin-left:4px;">↕</span>';
        return sortOrder === 'asc' 
          ? '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▲</span>' 
          : '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▼</span>';
      };

      const myAllies = this.getAllies(this.playerClanId);
      const myDaimyoName = this.playerDaimyo?.name || this.getDaimyoLeaderName(this.playerClanId);
      const myClanName = this.getClanFamilyName(this.playerClanId);

      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:95vw; max-width:1580px; height:88vh; display:flex; flex-direction:column; box-shadow:0 0 45px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <!-- ヘッダー -->
          <div style="padding:12px 22px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">❖ 天下大名勢力録・外交指南 ❖</h3>
              <span style="font-size:12pt; color:#ccc;">天下諸大名の支配領国、総石高、総兵力、武将数および外交同盟関係を閲覧できます。他大名との同盟締結・破棄が可能です。</span>
            </div>
            <button id="closeFactionModalBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 8px;">✕</button>
          </div>

          <!-- コントロールバー（自軍状況、検索） -->
          <div style="padding:10px 20px; background:rgba(0,0,0,0.35); border-bottom:1px dashed #5a4638; display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center;">
            <div style="display:flex; flex-wrap:wrap; align-items:center; gap:12px; font-size:12pt;">
              <span style="background:rgba(212,175,55,0.15); border:1px solid var(--gold); padding:4px 12px; border-radius:4px;">
                👑 貴家: <strong style="color:var(--gold-bright);">${myClanName}</strong> (${myDaimyoName}公)
              </span>
              <span style="background:rgba(0,0,0,0.4); border:1px solid #555; padding:4px 10px; border-radius:4px;">
                ⚡ 行動力: <strong style="color:#5dade2;">${this.ap} AP</strong>
              </span>
              <span style="background:rgba(0,0,0,0.4); border:1px solid #555; padding:4px 10px; border-radius:4px;">
                💰 軍資金: <strong style="color:#ffd700;">${this.gold.toLocaleString()} 両</strong>
              </span>
              <span style="background:rgba(46,204,113,0.15); border:1px solid #27ae60; padding:4px 10px; border-radius:4px;">
                🤝 同盟国: <strong style="color:#2ecc71;">${myAllies.length} 家</strong>
              </span>
            </div>

            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12pt; color:#aaa;">勢力検索:</span>
              <input id="inputFactionSearch" type="text" placeholder="大名家・当主・本拠..." value="${searchQuery}" style="background:#22160d; color:#fff; border:1px solid #775533; padding:5px 10px; border-radius:4px; font-size:12pt; width:200px;">
            </div>
          </div>

          <!-- 勢力テーブル一覧 -->
          <div style="flex:1; overflow-y:auto; padding:0 20px;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; border-bottom:2px solid #775533; z-index:10; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
                  <th class="sortable-fac-th" data-key="clan" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:260px; min-width:260px; white-space:nowrap; font-size:12pt;">大名家 ${getSortIcon('clan')}</th>
                  <th class="sortable-fac-th" data-key="leader" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:130px; font-size:12pt;">当主 ${getSortIcon('leader')}</th>
                  <th class="sortable-fac-th" data-key="base" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:360px; min-width:360px; white-space:nowrap; font-size:12pt;">本拠地 (居城) ${getSortIcon('base')}</th>
                  <th class="sortable-fac-th" data-key="provCount" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:95px; text-align:center; font-size:12pt;">領国数 ${getSortIcon('provCount')}</th>
                  <th class="sortable-fac-th" data-key="totalRice" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:110px; text-align:right; font-size:12pt;">総石高 ${getSortIcon('totalRice')}</th>
                  <th class="sortable-fac-th" data-key="totalTroops" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:110px; text-align:right; font-size:12pt;">総兵力 ${getSortIcon('totalTroops')}</th>
                  <th class="sortable-fac-th" data-key="officerCount" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">武将数 ${getSortIcon('officerCount')}</th>
                  <th class="sortable-fac-th" data-key="allies" style="padding:11px 12px; color:var(--gold); user-select:none; width:200px; font-size:12pt;">同盟国</th>
                  <th class="sortable-fac-th" data-key="diplomacy" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:170px; text-align:center; font-size:12pt;">外交・同盟 ${getSortIcon('diplomacy')}</th>
                </tr>
              </thead>
              <tbody>
                ${factions.length === 0 ? `
                  <tr>
                    <td colspan="9" style="text-align:center; padding:30px; color:#888; font-size:12pt;">該当する勢力は見つかりませんでした。</td>
                  </tr>
                ` : ''}
                ${factions.map(f => {
                  const provNames = f.provinces.map(p => p.name).join('、');
                  const isPlayer = f.isPlayer;
                  const isAllied = f.isAlliedWithPlayer;

                  let rowBg = 'transparent';
                  let borderLeft = 'none';
                  if (isPlayer) {
                    rowBg = 'rgba(212,175,55,0.12)';
                    borderLeft = '4px solid var(--gold)';
                  } else if (isAllied) {
                    rowBg = 'rgba(46,204,113,0.08)';
                    borderLeft = '4px solid #2ecc71';
                  }

                  // 同盟国タグ一覧
                  let alliesTagsHtml = '<span style="color:#777;">なし</span>';
                  if (f.allies && f.allies.length > 0) {
                    alliesTagsHtml = f.allies.map(aId => {
                      const aName = this.getClanFamilyName(aId);
                      const isMy = (aId === this.playerClanId);
                      const left = this.getAllianceRemainingSeasons(f.clanId, aId);
                      const remain = left >= 0 ? ` 残${left}季` : '';
                      return `<span style="display:inline-block; margin:2px 3px; padding:2px 7px; border-radius:3px; font-size:11pt; background:${isMy ? 'rgba(212,175,55,0.25)' : 'rgba(46,204,113,0.2)'}; border:1px solid ${isMy ? 'var(--gold)' : '#27ae60'}; color:${isMy ? 'var(--gold-bright)' : '#2ecc71'}; font-weight:${isMy ? 'bold' : 'normal'};" title="同盟の残り期間">🤝 ${aName}${remain}</span>`;
                    }).join('');
                  }

                  // 外交行動ボタン
                  let actionHtml = '';
                  if (isPlayer) {
                    actionHtml = '<span style="background:#b7950b; color:#fff; padding:3px 12px; border-radius:4px; font-weight:bold; font-size:11pt; display:inline-block;">👑 貴家</span>';
                  } else if (isAllied) {
                    actionHtml = `
                      <div style="display:flex; justify-content:center; align-items:center; gap:6px;">
                        <span style="background:#27ae60; color:#fff; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:11pt;">🤝 盟友</span>
                        <button class="btn-break-alliance-row" data-clan-id="${f.clanId}" style="background:#922b21; color:#fff; border:1px solid #c0392b; padding:3px 8px; border-radius:4px; cursor:pointer; font-size:11pt; transition:0.2s;" title="同盟を破棄し手切れとします (AP 1消費)">破棄</button>
                      </div>
                    `;
                  } else {
                    actionHtml = `
                      <div style="display:flex; justify-content:center; align-items:center; gap:6px;">
                        <span style="background:#555; color:#ddd; padding:3px 8px; border-radius:4px; font-size:11pt;">敵対</span>
                        <button class="btn-form-alliance-row" data-clan-id="${f.clanId}" style="background:linear-gradient(180deg, #27ae60, #1e8449); color:#fff; border:1px solid #2ecc71; padding:3px 10px; border-radius:4px; cursor:pointer; font-size:11pt; font-weight:bold; transition:0.2s;" title="使者を派遣して同盟を結びます (金500両・AP 1消費)">同盟</button>
                      </div>
                    `;
                  }

                  return `
                    <tr style="border-bottom:1px solid #3d2b1f; background:${rowBg}; border-left:${borderLeft}; transition:background 0.2s;" onmouseover="this.style.backgroundColor='rgba(255,255,255,0.06)'" onmouseout="this.style.backgroundColor='${rowBg}'">
                      <td style="padding:10px 12px; font-weight:bold; color:${isPlayer ? 'var(--gold-bright)' : '#fff'}; white-space:nowrap;">
                        ${isPlayer ? '★ ' : ''}${f.clanName}
                      </td>
                      <td style="padding:10px 12px; color:var(--gold-bright); font-weight:bold;">
                        ${f.daimyoName}
                      </td>
                      <td style="padding:10px 12px; color:#ddd; white-space:nowrap;">
                        ${f.capitalDisplay}
                      </td>
                      <td style="padding:10px 10px; text-align:center;" title="支配領国: ${provNames}">
                        <span style="font-weight:bold; color:${f.provCount >= 5 ? '#e74c3c' : (f.provCount >= 3 ? '#e67e22' : '#fff')};">${f.provCount}</span> ヶ国
                      </td>
                      <td style="padding:10px 10px; text-align:right; color:#2ecc71; font-weight:bold;">
                        ${f.totalRice.toLocaleString()} 石
                      </td>
                      <td style="padding:10px 10px; text-align:right; color:#f39c12; font-weight:bold;">
                        ${f.totalTroops.toLocaleString()} 人
                      </td>
                      <td style="padding:10px 10px; text-align:center; color:#ccc;">
                        ${f.officerCount} 名
                      </td>
                      <td style="padding:10px 12px;">
                        ${alliesTagsHtml}
                      </td>
                      <td style="padding:10px 12px; text-align:center;">
                        ${actionHtml}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- フッター -->
          <div style="padding:12px 20px; border-top:1px solid #443322; background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:12pt; color:#aaa;">
              現存大名: <strong style="color:#fff;">${factions.length}</strong> 家 ｜ 貴家の同盟国: <strong style="color:#2ecc71;">${myAllies.length}</strong> 家
              <span style="margin-left:14px; color:#bbb; font-size:11pt;">💡【同盟効果】相互攻撃不可・防衛戦での援軍（二年＝八季で解消。滅亡した大名は一覧から消える。締結: 金500両・AP 1点）</span>
            </div>
            <div>
              <button id="closeFactionModalBtnBottom" style="background:#555; color:#fff; border:none; padding:7px 22px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">閉</button>
            </div>
          </div>
        </div>
      `;

      modal.style.display = 'flex';

      const closeModal = () => { modal.style.display = 'none'; };
      document.getElementById('closeFactionModalBtn')?.addEventListener('click', closeModal);
      document.getElementById('closeFactionModalBtnBottom')?.addEventListener('click', closeModal);

      // 同盟締結ボタン
      modal.querySelectorAll('.btn-form-alliance-row').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const targetClanId = btn.dataset.clanId;
          this.formAlliance(targetClanId, () => render());
        });
      });

      // 同盟破棄ボタン
      modal.querySelectorAll('.btn-break-alliance-row').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const targetClanId = btn.dataset.clanId;
          this.breakAlliance(targetClanId, () => render());
        });
      });

      // ヘッダークリックソート
      modal.querySelectorAll('.sortable-fac-th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (sortKey === key) {
            sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
          } else {
            sortKey = key;
            sortOrder = (key === 'clan' || key === 'leader' || key === 'base' ? 'asc' : 'desc');
          }
          render();
        });
      });

      // 検索フィルター入力
      const searchInput = document.getElementById('inputFactionSearch');
      if (searchInput) {
        const applySearch = (value) => {
          searchQuery = value;
          render();
          const newInp = document.getElementById('inputFactionSearch');
          if (newInp) {
            newInp.focus();
            newInp.selectionStart = newInp.selectionEnd = newInp.value.length;
          }
        };
        searchInput.addEventListener('input', (e) => {
          if (e.isComposing || e.inputType === 'insertCompositionText') return;
          applySearch(e.target.value);
        });
        searchInput.addEventListener('compositionend', (e) => {
          applySearch(e.target.value);
        });
      }
    };

    render();
    this.audio?.playHyoshigi();
  },

  // ============================================================================
  // 浪人登用（単体実行処理）
  // ============================================================================
  async recruitRonin(officerId, callback = null) {
    const off = (this.activeOfficers || []).find(o => o.id === officerId && !o.isDead);
    if (!off || off.clanId !== 'ronin') {
      if (window.Swal) {
        Swal.fire({
          icon: 'info',
          title: '登用不可',
          text: '該当の浪人は現在仕官可能な状態ではありません。',
          background: '#1c130d',
          color: '#f5eedc'
        });
      }
      return;
    }

    // 所在国情報（遠国も登用可。遠いほど成功率は下がり、跡継ぎ不在なら上がる）
    const defProvName = off.defaultProv ? this.getProvinceJapaneseName(off.defaultProv) : '諸国';
    const reach = this.calcPlayerRoninRecruitRate(off);
    const isDefProvMine = reach.dist === 0;
    const isNeighbor = reach.dist === 1;
    const age = this.year - (off.birthYear || 1530);
    const rate = reach.rate;
    const reachBadge = isDefProvMine
      ? { bg: 'rgba(46,204,113,0.3)', border: '#27ae60', color: '#2ecc71', text: `🏯 流浪国（自領） (${defProvName})` }
      : isNeighbor
        ? { bg: 'rgba(230,126,34,0.3)', border: '#e67e22', color: '#f5b041', text: `隣国より仕官 (${defProvName})` }
        : { bg: 'rgba(52,152,219,0.28)', border: '#2980b9', color: '#85c1e9', text: `遠国より仕官・可 (${defProvName})` };
    const rateNote = !reach.reachable
      ? ''
      : isDefProvMine
        ? (reach.lacksHeir ? '（流浪国・跡継ぎ不在ボーナス）' : '（流浪国ボーナス）')
        : isNeighbor
          ? (reach.lacksHeir ? '（隣国・跡継ぎ不在で上昇）' : '（隣国のため成功率低下）')
          : (reach.lacksHeir ? '（遠国だが跡継ぎ不在のため成功率上昇）' : '（遠国・登用可。遠いため成功率低下）');

    if (!reach.reachable) {
      if (window.Swal) {
        Swal.fire({
          icon: 'info',
          title: '所在不明のため登用できず',
          html: `<div style="font-size:12pt; color:#f5eedc; line-height:1.7;">${off.name}の流浪先が判らず、使者を送れません。</div>`,
          confirmButtonText: '承知した',
          confirmButtonColor: '#7f8c8d',
          background: '#1c130d',
          color: '#f5eedc'
        });
      }
      return;
    }

    if (this.ap <= 0) {
      this.showOrderResult('⚠ 軍令権不足', '今季の軍令権(AP)が不足しています。「次季へ進む」で回復してください。', '#e67e22');
      return;
    }

    if (this.gold < 40) {
      this.showOrderResult('⚠ 資金不足', `浪人登用には支度金40貫が必要です（現在: ${this.gold}貫）。`, '#e74c3c');
      return;
    }

    // 確認ダイアログ
    let proceed = true;
    if (window.Swal) {
      const confirmRes = await Swal.fire({
        title: `❖ 浪人登用使者の派遣 ❖`,
        html: `
          <div style="text-align:left; font-size:12pt; color:#f5eedc; font-family:'Noto Serif JP',serif; line-height:1.6;">
            <div style="border-bottom:1px solid #5a4638; padding-bottom:8px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <span style="font-size:16pt; font-weight:bold; color:var(--gold-bright);">${off.name}</span>
                <span style="font-size:11.5pt; color:#ccc; margin-left:6px;">(${age}歳)</span>
              </div>
              <div>
                <span style="background:${reachBadge.bg}; border:1px solid ${reachBadge.border}; color:${reachBadge.color}; padding:2px 8px; border-radius:3px; font-size:11pt;">
                  ${reachBadge.text}
                </span>
              </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; text-align:center; margin-bottom:12px;">
              <div style="background:rgba(231,76,60,0.2); border:1px solid #c0392b; padding:4px; border-radius:4px;">
                <div style="font-size:10pt; color:#ff7675;">⚔️ 武勇</div>
                <div style="font-size:14pt; font-weight:bold; color:#ff7675;">${off.military}</div>
              </div>
              <div style="background:rgba(52,152,219,0.2); border:1px solid #2980b9; padding:4px; border-radius:4px;">
                <div style="font-size:10pt; color:#74b9ff;">🌾 内政</div>
                <div style="font-size:14pt; font-weight:bold; color:#74b9ff;">${off.politic}</div>
              </div>
              <div style="background:rgba(46,204,113,0.2); border:1px solid #27ae60; padding:4px; border-radius:4px;">
                <div style="font-size:10pt; color:#55efc4;">📜 知略</div>
                <div style="font-size:14pt; font-weight:bold; color:#55efc4;">${off.intel}</div>
              </div>
            </div>
            <div style="background:rgba(0,0,0,0.4); padding:8px 10px; border-radius:4px; margin-bottom:12px; font-size:11.5pt; color:#ddd; line-height:1.5;">
              <strong>【列伝】</strong> ${this.cleanOfficerLore(off.lore) || '天下に名を響かせる士。'}
            </div>
            <div style="background:rgba(212,175,55,0.12); border:1px solid var(--gold); border-radius:4px; padding:8px 10px; font-size:11.5pt;">
              💰 登用費用: <strong>金40貫</strong> ｜ 📜 軍令権: <strong>1消費</strong><br>
              🎯 登用成功見込み: <strong style="color:var(--gold-bright); font-size:13pt;">${rate}%</strong> ${rateNote}
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonText: '🤝 使者を派遣して登用する',
        confirmButtonColor: '#27ae60',
        cancelButtonText: '見送る',
        cancelButtonColor: '#7f8c8d',
        background: '#1c130d',
        color: '#f5eedc'
      });
      proceed = confirmRes.isConfirmed;
    }

    if (!proceed) return;

    // 行動力消費
    this.ap -= 1;
    this.updateStatusHeader();

    const isSuccess = (Math.random() * 100) < rate;

    if (isSuccess) {
      this.gold -= 40;
      off.clanId = this.playerClanId;
      off.isDaimyo = false;
      off.assignedProvId = null;

      this.log(`🤝【浪人登用成功】「殿の器量、天下一に候！我が命、貴家に捧げましょう！」${off.name}公が我が軍の配下に加わりました！`, 'important');
      try { this.audio.playGrandFanfare?.(); } catch(e) {}
      this.appointHistoricalHomeGovernors(this.playerClanId);

      if (window.Swal) {
        await Swal.fire({
          icon: 'success',
          title: '登用成功！',
          html: `
            <div style="font-size:13pt; color:#2ecc71; font-weight:bold; margin-bottom:8px; font-family:'Noto Serif JP',serif;">「我が忠義、生涯殿に捧げましょう！」</div>
            <div style="font-size:12pt; color:#f5eedc;">名将・<strong>${off.name}</strong>公が我が軍の配下武将に加わりました！<br>直ちに城主への任命や軍事・内政に登用可能です。</div>
          `,
          confirmButtonText: '大儀であった',
          confirmButtonColor: '#27ae60',
          background: '#1c130d',
          color: '#f5eedc'
        });
      }
    } else {
      // 失敗時は使者手当として金20貫のみ消費
      this.gold -= 20;
      this.log(`🍂【登用不首尾】使者を派遣するも、${off.name}は「今はまだ仕官の時ではない」と仕官を固辞しました（支度金20貫を返還）。`);
      try { this.audio.playHyoshigi?.(); } catch(e) {}

      if (window.Swal) {
        await Swal.fire({
          icon: 'warning',
          title: '登用不首尾……',
          html: `
            <div style="font-size:13pt; color:#e67e22; font-weight:bold; margin-bottom:8px; font-family:'Noto Serif JP',serif;">「今はまだ機が熟さぬ……」</div>
            <div style="font-size:12pt; color:#f5eedc;">${off.name}は仕官を固辞し、立ち去りました。<br>（支度金20貫を返還。次期以降も再登用可能です）</div>
          `,
          confirmButtonText: 'やむを得ぬ',
          confirmButtonColor: '#7f8c8d',
          background: '#1c130d',
          color: '#f5eedc'
        });
      }
    }

    this.updateUI(); // 選択中の国パネルも updateUI 内で再描画
    if (callback) callback();
  },

  // ============================================================================
  // 諸国人材登用・浪人招聘モーダル
  // ============================================================================,

  openRecruitRoninModal(targetRoninId = null) {
    if (this.isAutoPlay) this.stopAutoPlay('登用画面表示のため');
    if (targetRoninId) {
      this.recruitRonin(targetRoninId);
      return;
    }

    let modal = document.getElementById('recruitRoninModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'recruitRoninModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    let currentFilter = 'all'; // 'all' or 'myProv'
    let sortKey = 'military'; // 'military', 'politic', 'intel', 'age', 'name', 'prov'
    let sortOrder = 'desc';
    let searchQuery = '';

    const render = () => {
      const ronins = (this.activeOfficers || []).filter(o => o.clanId === 'ronin' && !o.isDead);
      const myProvIds = this.provinces.filter(p => p.ownerId === this.playerClanId).map(p => p.id);
      
      let list = ronins.filter(r => {
        if (currentFilter === 'myProv') {
          return r.defaultProv && myProvIds.includes(r.defaultProv);
        }
        return true;
      });

      if (searchQuery) {
        const q = searchQuery.trim().toLowerCase();
        list = list.filter(o => {
          const comment = this.getOfficerComment(o).toLowerCase();
          const defProvName = (o.defaultProv ? this.getProvinceJapaneseName(o.defaultProv) : '').toLowerCase();
          return (o.name && o.name.toLowerCase().includes(q)) || 
                 comment.includes(q) || 
                 defProvName.includes(q);
        });
      }

      // ソート処理
      list.sort((a, b) => {
        let diff = 0;
        if (sortKey === 'military') diff = (a.military || 0) - (b.military || 0);
        else if (sortKey === 'politic') diff = (a.politic || 0) - (b.politic || 0);
        else if (sortKey === 'intel') diff = (a.intel || 0) - (b.intel || 0);
        else if (sortKey === 'age') {
          const ageA = this.year - (a.birthYear || 1530);
          const ageB = this.year - (b.birthYear || 1530);
          diff = ageA - ageB;
        } else if (sortKey === 'name') {
          diff = (a.name || '').localeCompare(b.name || '', 'ja');
        } else if (sortKey === 'prov') {
          const provA = a.defaultProv ? this.getProvinceJapaneseName(a.defaultProv) : '';
          const provB = b.defaultProv ? this.getProvinceJapaneseName(b.defaultProv) : '';
          diff = provA.localeCompare(provB, 'ja');
        }
        return sortOrder === 'desc' ? -diff : diff;
      });

      const myProvCount = ronins.filter(r => r.defaultProv && myProvIds.includes(r.defaultProv)).length;

      const getSortIcon = (key) => {
        if (sortKey !== key) return '<span style="color:#776655; font-size:11pt; margin-left:4px;">↕</span>';
        return sortOrder === 'asc' 
          ? '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▲</span>' 
          : '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▼</span>';
      };

      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:95vw; max-width:1180px; height:88vh; display:flex; flex-direction:column; box-shadow:0 0 45px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <!-- ヘッダー -->
          <div style="padding:12px 22px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">❖ 人材登用・浪人招聘所 ❖</h3>
              <span style="font-size:12pt; color:#ccc;">遠国の浪人も登用できます。遠いほど成功率は下がり、跡継ぎがいないときは上がります（令状: 1 ｜ 支度金: 金40貫）。</span>
            </div>
            <button id="closeRecruitModalBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 8px;">✕</button>
          </div>

          <!-- コントロールバー -->
          <div style="padding:10px 20px; background:rgba(0,0,0,0.35); border-bottom:1px dashed #5a4638; display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center;">
            <div style="display:flex; gap:8px;">
              <button id="filterAllRonin" style="background:${currentFilter === 'all' ? '#b7950b' : '#2b1d14'}; color:${currentFilter === 'all' ? '#fff' : '#f1c40f'}; border:1px solid ${currentFilter === 'all' ? '#d4af37' : '#886622'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:0.2s;">
                全国の浪人 (${ronins.length}名)
              </button>
              <button id="filterMyProvRonin" style="background:${currentFilter === 'myProv' ? '#27ae60' : '#2b1d14'}; color:${currentFilter === 'myProv' ? '#fff' : '#a9dfbf'}; border:1px solid ${currentFilter === 'myProv' ? '#2ecc71' : '#1e8449'}; padding:6px 16px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold; transition:0.2s;">
                🏯 自領内滞在 (${myProvCount}名) ★成功率上昇
              </button>
            </div>

            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12pt; color:#aaa;">検索:</span>
              <input id="inputRecruitSearch" type="text" placeholder="武将名・流浪地..." value="${searchQuery}" style="background:#22160d; color:#fff; border:1px solid #775533; padding:5px 10px; border-radius:4px; font-size:12pt; width:190px;">
            </div>
          </div>

          <!-- 浪人テーブル一覧 -->
          <div style="flex:1; overflow-y:auto; padding:0 20px;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; border-bottom:2px solid #775533; z-index:10; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
                  <th class="sortable-rec-th" data-key="name" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:150px; font-size:12pt;">名前 ${getSortIcon('name')}</th>
                  <th class="sortable-rec-th" data-key="prov" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:140px; text-align:center; font-size:12pt;">滞在国 ${getSortIcon('prov')}</th>
                  <th class="sortable-rec-th" data-key="age" style="padding:11px 12px; color:var(--gold); cursor:pointer; user-select:none; width:130px; text-align:center; font-size:12pt;">年齢 ${getSortIcon('age')}</th>
                  <th class="sortable-rec-th" data-key="military" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">武勇 ${getSortIcon('military')}</th>
                  <th class="sortable-rec-th" data-key="politic" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">内政 ${getSortIcon('politic')}</th>
                  <th class="sortable-rec-th" data-key="intel" style="padding:11px 10px; color:var(--gold); cursor:pointer; user-select:none; width:85px; text-align:center; font-size:12pt;">知略 ${getSortIcon('intel')}</th>
                  <th style="padding:11px 10px; color:var(--gold); width:130px; text-align:center; font-size:12pt;">登用工作</th>
                </tr>
              </thead>
              <tbody>
                ${list.length === 0 ? `
                  <tr>
                    <td colspan="7" style="text-align:center; padding:35px; color:#888; font-size:12pt;">該当する浪人は見つかりませんでした。</td>
                  </tr>
                ` : ''}
                ${list.map((off, idx) => {
                  const reach = this.getRoninServiceReach(off, this.playerClanId);
                  const isMine = reach.dist === 0;
                  const isNeighbor = reach.dist === 1;
                  const defProvName = off.defaultProv ? this.getProvinceJapaneseName(off.defaultProv) : '諸国';
                  const age = this.year - (off.birthYear || 1530);
                  const rowBg = idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.18)';
                  const stayLabel = isMine ? '(流浪国)' : (isNeighbor ? '(隣国)' : (reach.reachable ? '(遠国・可)' : '(所在不明)'));
                  const stayColor = isMine ? '#2ecc71' : (isNeighbor ? '#f5b041' : '#85c1e9');
                  const stayBorder = isMine ? '#27ae60' : (isNeighbor ? '#e67e22' : '#2980b9');
                  const stayBg = isMine ? 'rgba(46,204,113,0.25)' : (isNeighbor ? 'rgba(230,126,34,0.22)' : 'rgba(52,152,219,0.22)');
                  const farNote = !isMine && !isNeighbor && reach.reachable
                    ? `<div style="font-size:10pt; color:${reach.lacksHeir ? '#f5b041' : '#85c1e9'}; margin-top:2px;">${reach.lacksHeir ? '跡継ぎ不在で上昇' : '登用可'}</div>`
                    : '';
                  const recruitCell = reach.reachable
                    ? `<button class="btn-do-recruit" data-off-id="${off.id}" style="background:linear-gradient(180deg, #d4af37, #b7950b); color:#111; border:none; padding:4px 14px; border-radius:4px; font-weight:bold; font-size:12pt; cursor:pointer; box-shadow:0 1px 4px rgba(0,0,0,0.5);">🤝 登用</button>${farNote}`
                    : `<span style="color:#888; font-size:11.5pt;" title="所在が分からず登用できません">所在不明</span>`;

                  return `
                    <tr class="recruit-table-row" data-off-id="${off.id}" style="background:${rowBg}; border-bottom:1px solid #3d2d20; cursor:pointer; font-size:12pt; transition:background 0.15s;" onmouseover="this.style.background='rgba(215, 175, 100, 0.12)'" onmouseout="this.style.background='${rowBg}'">
                      <td style="padding:10px 12px; font-weight:bold; color:#ffffff; white-space:nowrap; font-size:12.5pt;">
                        ${off.name}
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap;">
                        <span style="background:${stayBg}; color:${stayColor}; border:1px solid ${stayBorder}; padding:2px 8px; border-radius:3px; font-size:11.5pt;">
                          ${defProvName} ${stayLabel}
                        </span>
                      </td>
                      <td style="padding:10px 12px; text-align:center; color:#ddd; white-space:nowrap; font-size:12pt;">
                        <strong style="color:#ffffff; font-size:12.5pt;">${age}歳</strong>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#ff6b6b; font-size:12.5pt;">${off.military}</b>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#5dade2; font-size:12.5pt;">${off.politic}</b>
                      </td>
                      <td style="padding:10px 10px; text-align:center; white-space:nowrap;">
                        <b style="color:#a3e4d7; font-size:12.5pt;">${off.intel}</b>
                      </td>
                      <td style="padding:10px 8px; text-align:center; white-space:nowrap;">
                        ${recruitCell}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- フッター -->
          <div style="padding:12px 20px; border-top:1px solid #443322; background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12pt; color:#aaa;">表示中: ${list.length}名 ｜ 遠国も登用可 ｜ 流浪国は上昇、隣国・遠国は低下。跡継ぎ不在時は確率が上がり仕官も来ます</span>
            <button id="closeRecruitModalBtnBottom" style="background:#555; color:#fff; border:none; padding:7px 22px; border-radius:4px; cursor:pointer; font-size:12pt; font-weight:bold;">閉じる</button>
          </div>
        </div>
      `;

      modal.style.display = 'flex';

      const closeModal = () => { modal.style.display = 'none'; };
      document.getElementById('closeRecruitModalBtn')?.addEventListener('click', closeModal);
      document.getElementById('closeRecruitModalBtnBottom')?.addEventListener('click', closeModal);

      document.getElementById('filterAllRonin')?.addEventListener('click', () => { currentFilter = 'all'; render(); });
      document.getElementById('filterMyProvRonin')?.addEventListener('click', () => { currentFilter = 'myProv'; render(); });

      // ヘッダークリックソート
      modal.querySelectorAll('.sortable-rec-th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (sortKey === key) {
            sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
          } else {
            sortKey = key;
            sortOrder = (key === 'name' || key === 'prov' ? 'asc' : 'desc');
          }
          render();
        });
      });

      // 行クリックで列伝モーダル
      modal.querySelectorAll('.recruit-table-row').forEach(row => {
        row.addEventListener('click', (e) => {
          if (e.target.closest('button')) return;
          const offId = row.dataset.offId;
          const off = (this.activeOfficers || []).find(o => o.id === offId);
          if (off) this.showOfficerDetailModal(off);
        });
      });

      // 登用ボタンクリック
      modal.querySelectorAll('.btn-do-recruit').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const offId = btn.dataset.offId;
          this.recruitRonin(offId, () => {
            render();
          });
        });
      });

      const searchInput = document.getElementById('inputRecruitSearch');
      if (searchInput) {
        const applySearch = (value) => {
          searchQuery = value;
          render();
          const newInp = document.getElementById('inputRecruitSearch');
          if (newInp) {
            newInp.focus();
            newInp.selectionStart = newInp.selectionEnd = newInp.value.length;
          }
        };
        searchInput.addEventListener('input', (e) => {
          if (e.isComposing || e.inputType === 'insertCompositionText') return;
          applySearch(e.target.value);
        });
        searchInput.addEventListener('compositionend', (e) => {
          applySearch(e.target.value);
        });
      }
    };

    render();
    this.audio.playHyoshigi();
  },

  // 氏名から苗字を取る（豊臣・羽柴・長宗我部など複数文字を優先）,

  openProvinceOfficersModal(provId) {
    if (this.isAutoPlay) this.stopAutoPlay('武将一覧表示のため');

    const p = (this.provinces || []).find(x => x.id === provId);
    if (!p) return;

    let modal = document.getElementById('provinceOfficersModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'provinceOfficersModal';
      modal.className = 'custom-modal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    let sortKey = 'role'; // 'role', 'name', 'clan', 'age', 'military', 'politic', 'intel', 'comment'
    let sortOrder = 'desc';
    let searchQuery = '';

    const curCastle = (this.currentScenario && this.currentScenario.castles && this.currentScenario.castles[p.id]) || p.castleName || p.castle || '居城';
    const isMine = p.ownerId === this.playerClanId;
    const isBlank = !p.ownerId;
    const ownerName = isBlank ? '空白地 (領主不在)' : this.getClanDisplayName(p.ownerId);

    const closeModal = () => {
      if (modal) {
        modal.style.display = 'none';
        modal.innerHTML = '';
      }
      document.removeEventListener('keydown', handleKeyDown);
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') closeModal();
    };
    document.addEventListener('keydown', handleKeyDown);

    const render = () => {
      const provOfficers = this.getOfficersInProvince(p.id);

      let list = [...provOfficers];

      if (searchQuery) {
        const q = searchQuery.trim().toLowerCase();
        list = list.filter(o => {
          const comment = this.getOfficerComment(o).toLowerCase();
          const clanName = (o.clanId === 'ronin' ? '浪人' : `${this.getClanDisplayName(o.clanId) || ''} ${this.getClanFamilyName(o.clanId) || ''}`).toLowerCase();
          return (o.name && o.name.toLowerCase().includes(q)) || comment.includes(q) || clanName.includes(q);
        });
      }

      // ソート処理
      list.sort((a, b) => {
        let diff = 0;
        if (sortKey === 'role') {
          // 当主(3) > 城主(2) > 配下(1) > 浪人(0)
          const getRoleScore = (off) => {
            if (off.isDaimyo) return 3;
            if (off.id === p.governorId || off.assignedProvId === p.id) return 2;
            if (off.clanId === 'ronin') return 0;
            return 1;
          };
          diff = getRoleScore(a) - getRoleScore(b);
          if (diff === 0) diff = (a.military || 0) - (b.military || 0);
        } else if (sortKey === 'name') {
          diff = (a.name || '').localeCompare(b.name || '', 'ja');
        } else if (sortKey === 'clan') {
          const clanA = a.clanId === 'ronin' ? '浪人' : (this.getClanDisplayName(a.clanId) || '');
          const clanB = b.clanId === 'ronin' ? '浪人' : (this.getClanDisplayName(b.clanId) || '');
          diff = clanA.localeCompare(clanB, 'ja');
        } else if (sortKey === 'age') {
          const ageA = this.year - (a.birthYear || 1530);
          const ageB = this.year - (b.birthYear || 1530);
          diff = ageA - ageB;
        } else if (sortKey === 'military') {
          diff = (a.military || 0) - (b.military || 0);
        } else if (sortKey === 'politic') {
          diff = (a.politic || 0) - (b.politic || 0);
        } else if (sortKey === 'intel') {
          diff = (a.intel || 0) - (b.intel || 0);
        } else if (sortKey === 'comment') {
          diff = this.getOfficerComment(a).localeCompare(this.getOfficerComment(b), 'ja');
        }
        return sortOrder === 'desc' ? -diff : diff;
      });

      const getSortIcon = (key) => {
        if (sortKey !== key) return '<span style="color:#776655; font-size:11pt; margin-left:4px;">↕</span>';
        return sortOrder === 'asc' 
          ? '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▲</span>' 
          : '<span style="color:var(--gold-bright); font-size:12pt; margin-left:4px;">▼</span>';
      };

      modal.style.display = 'flex';
      modal.innerHTML = `
        <div style="background:#1b140e; border:2px solid var(--gold); border-radius:8px; width:95vw; max-width:1080px; max-height:88vh; display:flex; flex-direction:column; box-shadow:0 0 45px rgba(0,0,0,0.95); color:#f5eedc; font-family:'Noto Serif JP',serif;">
          <!-- ヘッダー -->
          <div style="padding:12px 20px; border-bottom:1px solid #5a4638; background:linear-gradient(180deg, #2b1d14 0%, #1a110a 100%); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h3 style="margin:0; font-size:15pt; color:var(--gold-bright);">
                🏯【${p.name}】在国武将一覧
                <span style="font-size:12.5pt; color:#ccc; font-weight:normal; margin-left:8px;">(城郭: ${curCastle})</span>
              </h3>
              <div style="font-size:11.5pt; color:#aaa; margin-top:2px;">
                支配: <strong style="color:${isMine ? 'var(--gold)' : (isBlank ? '#bdc3c7' : '#e0d8c3')}">${ownerName}</strong> 
                ｜ 滞在武将: <strong style="color:var(--gold-bright);">${provOfficers.length} 名</strong>
                <span style="color:#888; margin-left:8px;">※武将をクリックすると列伝・詳細を確認できます</span>
              </div>
            </div>
            <button id="closeProvOfficersModalBtn" style="background:transparent; border:none; color:#ddd; font-size:20pt; cursor:pointer; padding:0 8px; line-height:1;">✕</button>
          </div>

          <!-- 検索バー ＆ アクション -->
          <div style="padding:8px 20px; background:rgba(0,0,0,0.35); border-bottom:1px dashed #5a4638; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-size:12pt; color:#ccc;">
              ${isMine ? `
                <button id="btnProvOfficersAppoint" style="background:linear-gradient(180deg, #b7950b, #967208); color:#fff; border:1px solid #d4af37; padding:4px 12px; border-radius:3px; cursor:pointer; font-size:11.5pt; font-weight:bold;">
                  🏯 城主を交代・任命
                </button>
              ` : ''}
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:11.5pt; color:#aaa;">検索:</span>
              <input id="inputProvOfficerSearch" type="text" placeholder="武将名・所属..." value="${searchQuery}" style="background:#22160d; color:#fff; border:1px solid #775533; padding:4px 8px; border-radius:4px; font-size:11.5pt; width:180px;">
            </div>
          </div>

          <!-- 武将テーブル一覧 -->
          <div style="flex:1; overflow-y:auto; padding:0 20px;">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12pt;">
              <thead>
                <tr style="position:sticky; top:0; background:#261a12; border-bottom:2px solid #775533; z-index:10; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
                  <th class="sortable-prov-th" data-key="name" style="padding:10px 12px; color:var(--gold); cursor:pointer; user-select:none; width:140px;">名前 ${getSortIcon('name')}</th>
                  <th class="sortable-prov-th" data-key="role" style="padding:10px 12px; color:var(--gold); cursor:pointer; user-select:none; width:170px; min-width:170px; white-space:nowrap; text-align:center;">身分・役職 ${getSortIcon('role')}</th>
                  <th class="sortable-prov-th" data-key="clan" style="padding:10px 12px; color:var(--gold); cursor:pointer; user-select:none; width:120px;">所属 ${getSortIcon('clan')}</th>
                  <th class="sortable-prov-th" data-key="age" style="padding:10px 12px; color:var(--gold); cursor:pointer; user-select:none; width:220px; min-width:220px; white-space:nowrap; text-align:center;">年齢・生没年 ${getSortIcon('age')}</th>
                  <th class="sortable-prov-th" data-key="military" style="padding:10px 10px; color:var(--gold); cursor:pointer; user-select:none; width:70px; text-align:center;">武勇 ${getSortIcon('military')}</th>
                  <th class="sortable-prov-th" data-key="politic" style="padding:10px 10px; color:var(--gold); cursor:pointer; user-select:none; width:70px; text-align:center;">内政 ${getSortIcon('politic')}</th>
                  <th class="sortable-prov-th" data-key="intel" style="padding:10px 10px; color:var(--gold); cursor:pointer; user-select:none; width:70px; text-align:center;">知略 ${getSortIcon('intel')}</th>
                  <th style="padding:10px 12px; color:var(--gold);">略歴・特徴</th>
                </tr>
              </thead>
              <tbody>
                ${list.length === 0 ? `
                  <tr>
                    <td colspan="8" style="text-align:center; padding:40px 20px; color:#aaa;">
                      <div style="font-size:28pt; margin-bottom:8px;">🏯</div>
                      <div style="font-size:13pt; color:#e0d8c3; font-weight:bold; margin-bottom:6px;">
                        ${provOfficers.length === 0 ? '現在、この国に滞在している武将はいません。' : '条件に合致する武将が見つかりませんでした。'}
                      </div>
                      <div style="font-size:11.5pt; color:#888;">
                        ${provOfficers.length === 0 
                          ? (isBlank ? '領主不在の空白地です。' : (isMine ? '※「城主を交代・任命」ボタンから家臣を城主に任命できます。' : '※城代と守備隊が防備にあたっています。')) 
                          : '検索条件を変更してください。'}
                      </div>
                    </td>
                  </tr>
                ` : ''}
                ${list.map((off, idx) => {
                  const isGov = off.id === p.governorId || off.assignedProvId === p.id;
                  const isDaimyo = off.isDaimyo;
                  const isRonin = off.clanId === 'ronin';
                  const clanName = isRonin ? '浪人 (未仕官)' : (this.getClanDisplayName(off.clanId) || this.getClanFamilyName(off.clanId));
                  const age = this.year - (off.birthYear || 1530);
                  const comment = this.getOfficerComment(off);

                  const roleBadgeBase = 'display:inline-block; white-space:nowrap; padding:2px 8px; border-radius:3px; font-size:11pt;';
                  let roleBadge = '';
                  if (isDaimyo) {
                    roleBadge = `<span style="${roleBadgeBase} background:#b7950b; color:#fff; font-weight:bold;">👑 当主</span>`;
                  } else if (isGov) {
                    roleBadge = `<span style="${roleBadgeBase} background:#27ae60; color:#fff; font-weight:bold;">🏯 城主</span>`;
                  } else if (isRonin) {
                    roleBadge = `<span style="${roleBadgeBase} background:#7f8c8d; color:#fff;">🤝 浪人</span>`;
                  } else {
                    roleBadge = `<span style="${roleBadgeBase} background:#2980b9; color:#fff;">⚔️ 配下待機</span>`;
                  }

                  const rowBg = isDaimyo 
                    ? 'rgba(183, 149, 11, 0.12)' 
                    : (isGov ? 'rgba(39, 174, 96, 0.08)' : (idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.18)'));

                  return `
                    <tr class="prov-officer-table-row" data-off-id="${off.id}" style="border-bottom:1px solid #3d2d20; background:${rowBg}; cursor:pointer; transition:background 0.15s;" onmouseover="this.style.background='rgba(212,175,55,0.18)'" onmouseout="this.style.background='${rowBg}'">
                      <td style="padding:10px 12px; font-weight:bold; color:#fff;">
                        ${off.name}
                        ${off.isDaimyo ? ' <span style="color:var(--gold-bright); font-size:10.5pt;">★</span>' : ''}
                      </td>
                      <td style="padding:10px 12px; text-align:center; white-space:nowrap;">${roleBadge}</td>
                      <td style="padding:10px 12px; color:#d5dbdb;">${clanName}</td>
                      <td style="padding:10px 12px; text-align:center; color:#ccc; white-space:nowrap;">
                        ${age}歳
                        <span style="font-size:10.5pt; color:#888;">(${off.birthYear || '?'}〜${off.deathYear || '?'})</span>
                      </td>
                      <td style="padding:10px 10px; text-align:center; font-weight:bold; color:#ff6b6b;">${off.military || 0}</td>
                      <td style="padding:10px 10px; text-align:center; font-weight:bold; color:#5dade2;">${off.politic || 0}</td>
                      <td style="padding:10px 10px; text-align:center; font-weight:bold; color:#a3e4d7;">${off.intel || 0}</td>
                      <td style="padding:10px 12px; font-size:11pt; color:#c8b9ab; max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${comment}">
                        ${comment}
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- フッター -->
          <div style="padding:10px 20px; border-top:1px solid #5a4638; background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:11.5pt; color:#888;">
              行をクリックすると列伝・能力の詳細が開きます。
            </div>
            <button id="btnProvOfficersCloseFooter" style="background:#555; color:#fff; border:none; padding:6px 20px; border-radius:4px; cursor:pointer; font-size:11.5pt; font-weight:bold;">
              閉じる
            </button>
          </div>
        </div>
      `;

      // イベントリスナー
      modal.onclick = (e) => {
        if (e.target === modal) closeModal();
      };
      document.getElementById('closeProvOfficersModalBtn')?.addEventListener('click', closeModal);
      document.getElementById('btnProvOfficersCloseFooter')?.addEventListener('click', closeModal);

      document.getElementById('btnProvOfficersAppoint')?.addEventListener('click', () => {
        closeModal();
        this.openAppointGovernorModal(p.id);
      });

      // ソート
      modal.querySelectorAll('.sortable-prov-th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (sortKey === key) {
            sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
          } else {
            sortKey = key;
            sortOrder = (key === 'name' || key === 'clan' ? 'asc' : 'desc');
          }
          render();
        });
      });

      // 検索
      const searchInp = document.getElementById('inputProvOfficerSearch');
      if (searchInp) {
        const applySearch = (value) => {
          searchQuery = value;
          render();
          const newInp = document.getElementById('inputProvOfficerSearch');
          if (newInp) {
            newInp.focus();
            newInp.selectionStart = newInp.selectionEnd = newInp.value.length;
          }
        };
        searchInp.addEventListener('input', (e) => {
          if (e.isComposing || e.inputType === 'insertCompositionText') return;
          applySearch(e.target.value);
        });
        searchInp.addEventListener('compositionend', (e) => {
          applySearch(e.target.value);
        });
      }

      // 列伝表示（行クリック）
      modal.querySelectorAll('.prov-officer-table-row').forEach(row => {
        row.addEventListener('click', () => {
          const offId = row.dataset.offId;
          const off = (this.activeOfficers || []).find(o => o.id === offId) 
                   || (window.OFFICERS_MASTER || []).find(o => o.id === offId);
          if (off) this.showOfficerDetailModal(off);
        });
      });
    };

    render();
  },

  // 領国の選択と詳細表示,

  selectProvince(provId) {
    // diplomacy perspective: 他勢力領をクリックしたら視点を切替
    if (this.mapHeatMode === 'diplomacy') {
      const clicked = (this.provinces || []).find(x => x.id === provId);
      if (clicked && clicked.ownerId) {
        this.mapPerspectiveClanId = clicked.ownerId;
      }
    }
    this.selectedProvId = provId;
    const p = this.provinces.find(x => x.id === provId);
    if (!p) return;

    // 自国領土の全最前面押し出し・大名カラー輪郭ハイライト・選択中タイル最前面化を実行
    this.updateMapDisplay();

    const badge = document.getElementById('selectedProvBadge');
    if (badge) {
      const curCastle = (this.currentScenario && this.currentScenario.castles && this.currentScenario.castles[p.id]) || p.castleName || p.castle || '居城';
      badge.textContent = `${p.name} (${curCastle})`;
      badge.style.color = p.ownerId === this.playerClanId ? 'var(--gold-bright)' : '#e0d8c3';
    }

    const isMine = p.ownerId === this.playerClanId;
    const ownerName = this.getClanDisplayName(p.ownerId);

    const detailBox = document.getElementById('provDetailBox');
    if (detailBox) {
      const isBlank = !p.ownerId;
      const provOfficers = this.getOfficersInProvince(p.id);
      const ownerAb = isBlank ? null : getClanAbility(p.ownerId);
      const abStr = ownerAb ? `武${ownerAb.military} 内${ownerAb.politics} 謀${ownerAb.stratagem}` : '';
      const effStats = this.getEffectiveStats(p.id);

      let governorBadge = '';
      if (isBlank) {
        governorBadge = `
          <div style="margin:2px 0; background:rgba(127,140,141,0.15); border:1px solid #7f8c8d; border-radius:3px; padding:3px 8px; display:flex; justify-content:space-between; align-items:center; font-size:12pt; color:#bdc3c7;">
            <span style="font-weight:bold; color:#f5eedc;">🏕️ 領主不在（国人・土豪が自治中）</span>
            <span style="font-size:11pt; color:#ffd700;">※出陣・進軍で無血領有可能</span>
          </div>
        `;
      } else if (effStats.isCapital && effStats.isDaimyo) {
        governorBadge = `
          <div style="margin:2px 0; background:rgba(212,175,55,0.12); border:1px solid #b7950b; border-radius:3px; padding:2px 6px; display:flex; justify-content:space-between; align-items:center; font-size:12pt; white-space:nowrap; overflow:hidden;">
            <div style="display:flex; align-items:center; gap:5px; overflow:hidden;">
              <span style="color:var(--gold-bright); font-weight:bold;">👑 本拠親政: ${effStats.name}</span>
              <span style="color:#f5eedc; font-size:12pt;">武<b style="color:#ff6b6b;">${effStats.military}</b> 内<b style="color:#5dade2;">${effStats.politics}</b> 謀<b style="color:#a3e4d7;">${effStats.stratagem}</b></span>
            </div>
            ${isMine ? `<button id="btnAppointGovernor" style="background:#b7950b; color:#fff; border:none; padding:1px 6px; border-radius:2px; cursor:pointer; font-size:12pt; font-weight:bold; white-space:nowrap;">交代</button>` : ''}
          </div>
        `;
      } else if (effStats.governor) {
        governorBadge = `
          <div style="margin:2px 0; background:rgba(39,174,96,0.12); border:1px solid #27ae60; border-radius:3px; padding:2px 6px; display:flex; justify-content:space-between; align-items:center; font-size:12pt; white-space:nowrap; overflow:hidden;">
            <div style="display:flex; align-items:center; gap:5px; overflow:hidden;">
              <span style="color:#2ecc71; font-weight:bold;">🏯 城主: ${effStats.name}</span>
              
              <span style="color:#d5dbdb; font-size:12pt;">武<b style="color:#ff6b6b;">${effStats.military}</b> 内<b style="color:#5dade2;">${effStats.politics}</b> 謀<b style="color:#a3e4d7;">${effStats.stratagem}</b></span>
            </div>
            ${isMine ? `<button id="btnAppointGovernor" style="background:#34495e; color:#fff; border:1px solid #7f8c8d; padding:1px 6px; border-radius:2px; cursor:pointer; font-size:12pt; white-space:nowrap;">交代</button>` : ''}
          </div>
        `;
      } else {
        governorBadge = `
          <div style="margin:2px 0; background:rgba(230,126,34,0.12); border:1px solid #d35400; border-radius:3px; padding:2px 6px; display:flex; justify-content:space-between; align-items:center; font-size:12pt; white-space:nowrap; overflow:hidden;">
            <div style="display:flex; align-items:center; gap:5px; overflow:hidden;">
              <span style="color:#f39c12; font-weight:bold;">🏯 ${effStats.vacantBadge || '城代統治'}</span>
              <span style="color:#f5eedc; font-size:12pt;">武<b style="color:#ff6b6b;">${effStats.military}</b> 内<b style="color:#5dade2;">${effStats.politics}</b> 謀<b style="color:#a3e4d7;">${effStats.stratagem}</b></span>
            </div>
            ${isMine ? `<button id="btnAppointGovernor" style="background:#2980b9; color:#fff; border:1px solid #5dade2; padding:1px 6px; border-radius:2px; cursor:pointer; font-size:12pt; font-weight:bold; white-space:nowrap;">任命</button>` : ''}
          </div>
        `;
      }

      detailBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; flex-wrap:wrap; gap:2px 6px;">
          <div style="display:flex; align-items:baseline; gap:5px; flex-wrap:wrap;">
            ${isBlank ? `
              <span style="font-size: 12pt;">状態: <strong style="color:#bdc3c7; font-size:12.5pt;">空白地</strong> <span style="font-size: 11.5pt; color:#aaa;">(領主不在・無所属)</span></span>
            ` : `
              <span style="font-size: 12pt;">領主: <strong style="color:var(--gold); font-size:12.5pt;">${ownerName}</strong> <span style="font-size: 12pt; color:#ccc;">(${this.getClanFamilyName(p.ownerId)})</span></span>
            `}
            ${abStr ? `<span style="font-size: 12pt; color:#f9e79f; font-weight:bold; background:rgba(0,0,0,0.45); padding:1px 6px; border-radius:3px; border:1px solid #7d6608; white-space:nowrap; letter-spacing:0.5px;">${abStr}</span>` : ''}
          </div>
          <button id="btnViewProvOfficers" class="btn-view-prov-officers" style="background:linear-gradient(180deg, #3d2c1d, #22160d); color:var(--gold-bright); border:1px solid #8e6d3a; border-radius:3px; padding:2px 8px; font-size:11.5pt; font-weight:bold; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 1px 3px rgba(0,0,0,0.5); white-space:nowrap; transition:all 0.15s ease;" title="${p.name}の在国武将を一覧表示">
            <span>👥 武将一覧</span>
            <span style="background:rgba(212,175,55,0.25); color:#ffd700; border-radius:8px; padding:0 5px; font-size:10.5pt; border:1px solid rgba(212,175,55,0.4);">${provOfficers.length}</span>
          </button>
        </div>
        ${governorBadge}
        <div class="prov-detail-grid">
          <div class="prov-stat-row"><span>駐留兵力</span><span class="val">${p.troops.toLocaleString()} 人</span></div>
          <div class="prov-stat-row"><span>城郭防御</span><span class="val">${p.defense} / 100</span></div>
          <div class="prov-stat-row"><span>石高 (糧)</span><span class="val">${p.rice} 石</span></div>
          <div class="prov-stat-row"><span>商業 (金)</span><span class="val">${p.commerce} 貫</span></div>
          <div class="prov-stat-row"><span>軍勢士気</span><span class="val">${p.morale}</span></div>
          <div class="prov-stat-row"><span>治安度</span><span class="val">${p.order !== undefined ? p.order : 85}%</span></div>
        </div>
        ${isMine ? `
          <div style="margin-top:2px; background:rgba(0,0,0,0.35); padding:2px 6px; border-radius:3px; border:1px solid #553e2a; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size: 12pt; color:var(--gold-bright); white-space:nowrap;">統治方針:</span>
            <select id="singleProvGovernSelect" style="background:#1c130d; color:#fff; border:1px solid #775533; padding:1px 4px; border-radius:3px; font-family:inherit; font-size: 12pt; height:24px;">
              <option value="direct" ${p.governance === 'direct' ? 'selected' : ''}>👑 直轄（手動指揮）</option>
              <option value="military" ${p.governance === 'military' ? 'selected' : ''}>⚔️ 軍事進攻型</option>
              <option value="domestic" ${p.governance === 'domestic' ? 'selected' : ''}>🌾 内政型</option>
              <option value="balanced" ${p.governance === 'balanced' ? 'selected' : ''}>⚖️ 均衡型</option>
              <option value="logistics" ${p.governance === 'logistics' ? 'selected' : ''}>🚚 兵站輸送</option>
            </select>
          </div>
        ` : ''}
        ${p.castleLore ? `<div style="margin-top:2px; font-size: 12pt; color:#c8b9ab; line-height:1.3; border-top:1px dashed #553e2a; padding-top:2px;">🏯 ${p.castleLore}</div>` : ''}
      `;

      if (isMine) {
        document.getElementById('btnAppointGovernor')?.addEventListener('click', () => {
          this.openAppointGovernorModal(p.id);
        });
        document.getElementById('singleProvGovernSelect')?.addEventListener('change', (e) => {
          p.governance = e.target.value;
          this.log(`【統治方針】${p.name}の方針を「${this.getGovernModeName(p.governance)}」に変更しました。`);
          this.showOrderResult('📋 統治方針 変更', `${p.name}の方針を「${this.getGovernModeName(p.governance)}」に変更`, '#ffd700');
        });
      }

      document.getElementById('btnViewProvOfficers')?.addEventListener('click', () => {
        this.openProvinceOfficersModal(p.id);
      });
    }

    this.updateCommandButtons();
  },

  updateCommandButtons() {
    const p = this.provinces.find(x => x.id === this.selectedProvId);
    const isMine = p && p.ownerId === this.playerClanId;
    const hasAp = this.ap > 0;

    const cmdAttack = document.getElementById('cmdAttack');
    const cmdDomestic = document.getElementById('cmdDomestic');
    const cmdMilitary = document.getElementById('cmdMilitary');
    const cmdStratagem = document.getElementById('cmdStratagem');
    const cmdTransfer = document.getElementById('cmdTransfer');
    const cmdRecruit = document.getElementById('cmdRecruit');

    // ボタンのdisabled属性を解除し、常にクリックを受け付けて親切に処理・ガイドする
    [cmdAttack, cmdDomestic, cmdMilitary, cmdStratagem, cmdTransfer, cmdRecruit].forEach(btn => {
      btn?.removeAttribute('disabled');
    });

    if (cmdAttack) {
      const canAttack = isMine ? (p.neighbors || []).some(nId => {
        const n = this.provinces.find(x => x.id === nId);
        return n && n.ownerId !== this.playerClanId;
      }) && p.troops >= 1000 && this.rice >= 80 : true;
      cmdAttack.style.opacity = (canAttack && hasAp) ? '1' : '0.75';
    }

    if (cmdDomestic) {
      cmdDomestic.style.opacity = (this.gold >= 40 && hasAp) ? '1' : '0.75';
    }

    if (cmdMilitary) {
      const sel = this.provinces.find(x => x.id === this.selectedProvId);
      const needGold = sel && sel.ownerId === this.playerClanId ? this.getMilitaryGoldCost(sel) : 50;
      cmdMilitary.style.opacity = (this.gold >= needGold && hasAp) ? '1' : '0.75';
    }

    if (cmdStratagem) {
      cmdStratagem.style.opacity = (this.gold >= 40 && hasAp) ? '1' : '0.75';
    }

    if (cmdTransfer) {
      cmdTransfer.style.opacity = (isMine && p.troops >= 1000 && hasAp) ? '1' : '0.75';
    }

    if (cmdRecruit) {
      cmdRecruit.style.opacity = (this.gold >= 40 && hasAp) ? '1' : '0.75';
    }
  },

  // ============================================================================
  // 領国一括委任モーダル
  // ============================================================================,

  openGovernModal() {
    const modal = document.getElementById('governModal');
    if (!modal) return;
    this.renderGovernTable();
    modal.classList.remove('hidden');
    this.audio.playHyoshigi();
  },

  renderGovernTable() {
    const tbody = document.getElementById('governProvTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    myProvs.forEach(p => {
      const isFrontier = this.isProvinceFrontier(p);
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid #3a2a1a';

      tr.innerHTML = `
        <td style="padding:6px 10px;"><input type="checkbox" class="govern-select-cb" data-prov-id="${p.id}" style="accent-color:var(--gold);"></td>
        <td style="padding:6px 10px; font-weight:bold; color:#fff;">${p.name} <span style="font-size: 12pt; color:#aaa;">(${p.castleName || p.castle || "居城"})</span></td>
        <td style="padding:6px 10px;">${isFrontier ? '<span style="color:#ff8888;">前線</span>' : '<span style="color:#a9dfbf;">後方</span>'}</td>
        <td style="padding:6px 10px; color:#ffaaaa;">${p.troops.toLocaleString()} 人</td>
        <td style="padding:6px 10px; color:#ffd700;">${p.rice} / ${p.commerce}</td>
        <td style="padding:6px 10px;">
          <select class="govern-row-select" data-prov-id="${p.id}" style="background:#1a110a; color:#fff; border:1px solid #664422; padding:3px 6px; border-radius:3px; font-size: 12pt;">
            <option value="direct" ${p.governance === 'direct' ? 'selected' : ''}>👑 直轄</option>
            <option value="military" ${p.governance === 'military' ? 'selected' : ''}>⚔️ 軍事進攻型（自動攻略）</option>
            <option value="domestic" ${p.governance === 'domestic' ? 'selected' : ''}>🌾 内政型</option>
            <option value="balanced" ${p.governance === 'balanced' ? 'selected' : ''}>⚖️ 均衡型</option>
            <option value="logistics" ${p.governance === 'logistics' ? 'selected' : ''}>🚚 兵站輸送</option>
          </select>
        </td>
      `;

      tr.querySelector('.govern-row-select')?.addEventListener('change', (e) => {
        p.governance = e.target.value;
      });

      tbody.appendChild(tr);
    });
  },

  openTransferModal() {
    const p = this.provinces.find(x => x.id === this.selectedProvId);
    if (!p) return;

    const modal = document.getElementById('transferModal');
    const srcName = document.getElementById('transferSrcName');
    const maxTroops = document.getElementById('transferMaxTroops');
    const dstSelect = document.getElementById('transferDstSelect');
    const range = document.getElementById('transferTroopRange');
    const countLabel = document.getElementById('transferTroopCount');
    const remainLabel = document.getElementById('transferRemainTroops');

    if (!modal || !dstSelect || !range) return;

    srcName.textContent = `${p.name} (${p.castleName || p.castle || "居城"})`;
    maxTroops.textContent = p.troops.toLocaleString();

    dstSelect.innerHTML = '';
    (p.neighbors || []).forEach(nId => {
      const target = this.provinces.find(x => x.id === nId);
      if (target && target.ownerId === this.playerClanId) {
        const opt = document.createElement('option');
        opt.value = target.id;
        opt.textContent = `${target.name} (${target.castleName || target.castle || "居城"} / 現駐留: ${target.troops.toLocaleString()}人)`;
        dstSelect.appendChild(opt);
      }
    });

    const maxTransfer = Math.max(0, p.troops - 500);
    range.min = 100;
    range.max = maxTransfer;
    range.value = Math.min(1000, maxTransfer);

    const updateLabels = () => {
      const val = parseInt(range.value, 10) || 0;
      countLabel.textContent = val.toLocaleString();
      remainLabel.textContent = (p.troops - val).toLocaleString();
    };

    range.oninput = updateLabels;
    updateLabels();

    modal.classList.remove('hidden');
    this.audio.playHyoshigi();
  },

  openDeployModal() {
    let p = this.provinces.find(x => x.id === this.selectedProvId);
    let target = null;

    if (p && p.ownerId !== this.playerClanId) {
      // 同盟国への攻撃を禁止
      if (this.isAllied(this.playerClanId, p.ownerId)) {
        this.showOrderResult('⚠ 同盟関係', `${p.name}を領有する${this.getClanFamilyName(p.ownerId)}とは同盟関係にあります。同盟国を攻撃することはできません。`, '#e67e22');
        return;
      }
      // 敵国を選択中に出陣を押した場合：その敵国に隣接する自国領土（兵力1000以上）を探索
      target = p;
      const friendlyNeighbors = (p.neighbors || [])
        .map(nId => this.provinces.find(x => x.id === nId))
        .filter(x => x && x.ownerId === this.playerClanId && x.troops >= 1000);
      if (friendlyNeighbors.length === 0) {
        this.showOrderResult('⚠ 出陣不可', `${target.name}に隣接する貴家の領国で出陣可能な兵力(1,000人以上)を持つ城がありません。`, '#e74c3c');
        return;
      }
      p = friendlyNeighbors.sort((a, b) => b.troops - a.troops)[0];
      this.selectedProvId = p.id;
    } else {
      if (!p || p.ownerId !== this.playerClanId) {
        const myProvs = this.provinces.filter(x => x.ownerId === this.playerClanId && x.troops >= 1000);
        if (myProvs.length > 0) {
          p = myProvs[0];
          this.selectProvince(p.id);
        }
      }
      if (!p || p.troops < 1000) {
        this.showOrderResult('⚠ 出陣不可', '出陣には駐留兵力1,000人以上が必要です。自国領国を選択してください。', '#e74c3c');
        return;
      }
    }

    const modal = document.getElementById('deployModal');
    const srcName = document.getElementById('deploySrcName');
    const maxTroops = document.getElementById('deployMaxTroops');
    const dstSelect = document.getElementById('deployDstSelect');
    const range = document.getElementById('deployTroopRange');
    const countLabel = document.getElementById('deployTroopCount');
    const remainLabel = document.getElementById('deployRemainTroops');
    const riceCostLabel = document.getElementById('deployRiceCost');

    if (!modal || !dstSelect || !range) return;

    srcName.textContent = `${p.name} (${p.castleName || p.castle || "居城"})`;
    maxTroops.textContent = p.troops.toLocaleString();

    dstSelect.innerHTML = '';
    (p.neighbors || []).forEach(nId => {
      const neighbor = this.provinces.find(x => x.id === nId);
      // 同盟国を攻撃対象から除外
      if (neighbor && neighbor.ownerId !== this.playerClanId && !this.isAllied(this.playerClanId, neighbor.ownerId)) {
        const isTargetBlank = !neighbor.ownerId;
        const opt = document.createElement('option');
        opt.value = neighbor.id;
        if (isTargetBlank) {
          opt.textContent = `【空白地】${neighbor.name} (${neighbor.castleName || neighbor.castle || "城"} / 土豪兵: ${neighbor.troops.toLocaleString()}人 / ⚔️無血進駐可能)`;
        } else {
          opt.textContent = `${neighbor.name} (${neighbor.castleName || neighbor.castle || "居城"} / 敵兵: ${neighbor.troops.toLocaleString()}人 / 城防: ${neighbor.defense})`;
        }
        if (target && neighbor.id === target.id) {
          opt.selected = true;
        }
        dstSelect.appendChild(opt);
      }
    });

    if (dstSelect.options.length === 0) {
      this.showOrderResult('⚠ 出陣不可', `${p.name}に隣接する敵国がありません（同盟国または自国領）。前線の領国を選択してください。`, '#e74c3c');
      return;
    }

    const maxDeploy = Math.max(500, p.troops - 500);
    range.min = 500;
    range.max = maxDeploy;
    range.value = Math.min(3000, maxDeploy);

    const updateLabels = () => {
      const val = parseInt(range.value, 10) || 500;
      const riceCost = Math.round(val * 0.08);
      countLabel.textContent = val.toLocaleString();
      remainLabel.textContent = (p.troops - val).toLocaleString();
      riceCostLabel.textContent = riceCost.toLocaleString();
    };

    range.oninput = updateLabels;
    updateLabels();

    this._deployPredictedEnemyForm = null;
    this._deployPredictedFor = null;
    this.refreshDeployFormationIntel();
    dstSelect.onchange = () => {
      this._deployPredictedEnemyForm = null;
      this._deployPredictedFor = null;
      this.refreshDeployFormationIntel();
    };

    modal.classList.remove('hidden');
    try { this.audio.playHoragai?.(); } catch(e) {}
  },

  startEndingRoll(isShogunRoute = false) {
    const rollModal = document.getElementById('endingRollModal');
    if (!rollModal) return;

    // オーケストラBGM演奏開始！
    this.music.playTrack('victory');
    triggerCelebrationConfetti();

    // 桜吹雪Canvasアニメーション開始
    this.initEndingSakura();

    // 背景に大名の家紋透かしを設定
    const kamonContainer = document.getElementById('endingKamonBackdrop');
    if (kamonContainer && this.playerClanId) {
      kamonContainer.innerHTML = `
        <svg viewBox="0 0 100 100" style="width:100%; height:100%; filter: drop-shadow(0 0 20px rgba(255,215,0,0.4));">
          <use href="#kamon-${this.playerClanId}"></use>
        </svg>
      `;
    }

    // エンドロールのコンテンツ生成
    const clanName = this.playerDaimyo?.clan || '武家';
    const daimyoName = this.playerDaimyo?.name || '当主';
    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
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

    const titlePrefix = isShogunRoute ? '朝廷勅許・征夷大将軍就任' : '日本全五拾州完全平定';
    const titleMain = isShogunRoute ? `${clanName}幕府 開府創世録` : '天下統一・不滅の大覇業録';

    // 天下静謐の大綱（泰平の法制・仁政）
    const peaceEdicts = [
      { title: '兵農分離・万民安堵', desc: '武士は武と徳を修めて治安を護り、農民は耕作に専念する盤石の秩序を確立。' },
      { title: '五街道整備・楽市楽座', desc: '関所を撤廃し諸国の交易を奨励。街道と宿場町が賑わい、豊かな文化が花開く。' },
      { title: '武家諸法度・信義の天下', desc: '私闘や横暴を厳禁とし、公明正大なる法治と信義に基づく泰平の政道を敷く。' },
      { title: '四海静謐・治水開墾', desc: '大河川の治水と新田開発を全国で推進し、飢饉なき豊かな美田を後世へ遺す。' }
    ];

    const edictsHtml = peaceEdicts.map(e => `
      <div style="background:rgba(212,175,55,0.08); border:1px solid #775533; border-radius:6px; padding:14px 18px; text-align:left;">
        <div style="font-size:12.5pt; color:#ffd700; font-weight:bold; margin-bottom:6px;">❖ ${e.title}</div>
        <div style="font-size: 12pt; color:#e0d8c3; line-height:1.7;">${e.desc}</div>
      </div>
    `).join('');

    const contentEl = document.getElementById('endingRollContent');
    if (contentEl) {
      contentEl.innerHTML = `
        <!-- 題字 -->
        <div style="margin-bottom: 70px;">
          <div style="font-size: 14pt; color: #d4af37; letter-spacing: 8px; margin-bottom: 12px;">❖ ${titlePrefix} ❖</div>
          <div style="font-size: 32pt; font-weight: bold; color: #fff; text-shadow: 0 0 30px rgba(255,215,0,0.9); letter-spacing: 6px; margin-bottom: 16px;">
            ${titleMain}
          </div>
          <div style="font-size: 22pt; color: #ffd700; font-weight: bold;">
            初代征夷大将軍 ${daimyoName}
          </div>
          <div style="font-size: 13pt; color: #aaa; margin-top: 8px;">
            ${clanName} 宗家
          </div>
        </div>

        <!-- 第一幕：大平定の記録 -->
        <div style="margin-bottom: 80px; padding: 24px; border-top: 1px solid #664422; border-bottom: 1px solid #664422; background: rgba(0,0,0,0.4); border-radius: 8px;">
          <div style="font-size: 15pt; color: #ffd700; font-weight: bold; margin-bottom: 14px; letter-spacing: 4px;">
            【第一幕：天下統一の軌跡】
          </div>
          <p style="font-size: 12.5pt; color: #eee; max-width: 680px; margin: 0 auto 16px auto; line-height: 2.2; text-indent: 1.5em;">
            時に西暦${this.year}年 ${this.seasonNames[this.seasonIdx]}。百余年にわたり幾多の英傑が夢見ながらも果たすことの叶わなかった天下静謐の誓いが、ここに結実せり。
            北の蝦夷松前から南の薩摩大隅に至るまで、戦禍の煙はことごとく消え去り、日の本全土に満開の桜と民の歓喜が満ち溢れた。
          </p>
          <div style="font-size: 12pt; color: #ffdd88; margin-top: 10px;">
            激闘戦歴: ${this.stats.battlesWon}勝 (${this.stats.battlesFought}戦) ｜ 領有州国: ${myProvs.length}州 ｜ 軍勢総員: ${myProvs.reduce((acc, p) => acc + p.troops, 0).toLocaleString()}名
          </div>
        </div>

        <!-- 第二幕：幕府施政大綱 -->
        <div style="margin-bottom: 90px;">
          <div style="font-size: 15pt; color: #ffd700; font-weight: bold; margin-bottom: 16px; letter-spacing: 4px;">
            【第二幕：武門棟梁・新政の柱石】
          </div>
          <div style="font-size: 18pt; color: #fff; font-weight: bold; margin-bottom: 8px;">
            ${ep.regime}
          </div>
          <div style="font-size: 12pt; color: #bbb; margin-bottom: 24px;">
            政庁本拠：${ep.capital}
          </div>
          <div style="max-width: 700px; margin: 0 auto; text-align: left; background: rgba(212,175,55,0.06); border: 1px solid #775533; border-radius: 8px; padding: 20px 28px; line-height: 2.2;">
            <div style="margin-bottom: 12px;"><strong style="color:#ffd700;">一、法治と道義：</strong> ${ep.pillar1}</div>
            <div style="margin-bottom: 12px;"><strong style="color:#ffd700;">一、産業と民生：</strong> ${ep.pillar2}</div>
            <div><strong style="color:#ffd700;">一、秩序と泰平：</strong> ${ep.pillar3}</div>
          </div>
        </div>

        <!-- 第三幕：その後の幕府と日本の歴史（百年の変遷）★最重要 -->
        <div style="margin-bottom: 100px; padding: 30px 20px; border-top: 2px solid #ffd700; border-bottom: 2px solid #ffd700; background: radial-gradient(circle, rgba(40,20,10,0.6) 0%, rgba(0,0,0,0.85) 100%); border-radius: 8px;">
          <div style="font-size: 18pt; color: #ffd700; font-weight: bold; margin-bottom: 20px; letter-spacing: 6px; text-shadow: 0 0 15px rgba(255,215,0,0.7);">
            【第三幕：この幕府が紡いだ「その後の日本」】
          </div>
          <div style="font-size: 13pt; color: #dcd0c0; margin-bottom: 30px; font-style: italic;">
            〜 乱世を越えて、時代はどのように受け継がれたのか 〜
          </div>

          <div style="max-width: 720px; margin: 0 auto; text-align: left; line-height: 2.3; font-size: 12pt;">
            <div style="margin-bottom: 28px; background: rgba(0,0,0,0.4); padding: 16px 20px; border-left: 4px solid #ffd700; border-radius: 0 6px 6px 0;">
              <div style="font-size: 13pt; color: #ffd700; font-weight: bold; margin-bottom: 6px;">
                ❖ 統一後十年【礎の時代】
              </div>
              <div style="color: #f7f1e3; text-indent: 1em;">
                ${ep.future10}
              </div>
            </div>

            <div style="margin-bottom: 28px; background: rgba(0,0,0,0.4); padding: 16px 20px; border-left: 4px solid #e67e22; border-radius: 0 6px 6px 0;">
              <div style="font-size: 13pt; color: #ffaa55; font-weight: bold; margin-bottom: 6px;">
                ❖ 統一後五十年【黄金期と文化の爛熟】
              </div>
              <div style="color: #f7f1e3; text-indent: 1em;">
                ${ep.future50}
              </div>
            </div>

            <div style="margin-bottom: 28px; background: rgba(0,0,0,0.4); padding: 16px 20px; border-left: 4px solid #2ecc71; border-radius: 0 6px 6px 0;">
              <div style="font-size: 13pt; color: #a9dfbf; font-weight: bold; margin-bottom: 6px;">
                ❖ 統一後百年〜近代へ【悠久の泰平と世界への飛躍】
              </div>
              <div style="color: #f7f1e3; text-indent: 1em;">
                ${ep.future100}
              </div>
            </div>

            <div style="margin-top: 36px; padding: 20px 24px; border: 1px dashed #ffd700; border-radius: 8px; background: rgba(255,215,0,0.05); text-align: center;">
              <div style="font-size: 12pt; color: #aaa; margin-bottom: 6px;">後世の歴史家が記す言葉</div>
              <div style="font-size: 13pt; color: #ffd700; font-style: italic; line-height: 2.1;">
                ${ep.historianQuote}
              </div>
            </div>
          </div>
        </div>

        <!-- 第四幕：天下静謐の誓い・諸国万民の安堵 -->
        <div style="margin-bottom: 90px;">
          <div style="font-size: 15pt; color: #ffd700; font-weight: bold; margin-bottom: 20px; letter-spacing: 4px;">
            【第四幕：天下静謐の誓い・諸国万民の安堵】
          </div>
          <p style="font-size: 12pt; color: #eee; max-width: 680px; margin: 0 auto 24px auto; line-height: 2.2;">
            百余年に及ぶ争乱の火はことごとく消え去り、日の本全土に真の静謐が訪れり。<br>
            刀を鍬に持ち替え美田を拓く民の歓喜が山河を満たし、<br>
            貴家の敷きし仁政と大義は、未来永劫にわたり泰平を護る礎となった。
          </p>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; max-width: 760px; margin: 0 auto; text-align: center;">
            ${edictsHtml}
          </div>
        </div>

        <!-- 終幕：悠久の祈りとフィナーレ -->
        <div style="margin-top: 100px; margin-bottom: 120px;">
          <div style="font-size: 20pt; color: #ffd700; font-style: italic; letter-spacing: 4px; line-height: 2.4; margin-bottom: 30px;">
            「もののふの 捧げし至誠は 豊秋の実りとなり<br>
            民の笑顔は 悠久の泰平の光となる」
          </div>

          <div style="font-size: 34pt; font-weight: bold; color: #fff; letter-spacing: 12px; margin: 40px 0; text-shadow: 0 0 40px rgba(255,215,0,1);">
            完
          </div>

          <div style="font-size: 14pt; color: #d4af37; letter-spacing: 6px; margin-bottom: 40px;">
            〜 天下泰平 ・ 日の本の黎明 〜
          </div>

          <button id="endingCloseFinalBtn" style="padding: 12px 36px; font-size: 14pt; font-weight: bold; background: linear-gradient(180deg, #ffd700 0%, #b8860b 100%); color: #111; border: 2px solid #fff; border-radius: 30px; cursor: pointer; box-shadow: 0 0 30px rgba(255,215,0,0.8); font-family: inherit;">
            ❖ 統一の記録・詳細へ進む ❖
          </button>
        </div>
      `;

      document.getElementById('endingCloseFinalBtn')?.addEventListener('click', () => {
        this.closeEndingRoll();
      });
    }

    // 表示開始
    rollModal.classList.remove('hidden');

    // スクロール開始
    this.startEndingScroll();
  },

  startEndingScroll() {
    const container = document.getElementById('endingRollContainer');
    if (!container) return;

    this.endingScrollSpeed = 0.75; // 基本速度 (px/frame)
    this.endingIsPaused = false;
    container.scrollTop = 0;

    const scrollLoop = () => {
      if (document.getElementById('endingRollModal')?.classList.contains('hidden')) return;

      if (!this.endingIsPaused && container) {
        container.scrollTop += this.endingScrollSpeed;
      }

      this._rollAnimId = requestAnimationFrame(scrollLoop);
    };

    if (this._rollAnimId) cancelAnimationFrame(this._rollAnimId);
    this._rollAnimId = requestAnimationFrame(scrollLoop);

    // コントロールボタンのイベント
    const pauseBtn = document.getElementById('endingPauseBtn');
    if (pauseBtn) {
      pauseBtn.onclick = () => {
        this.endingIsPaused = !this.endingIsPaused;
        pauseBtn.textContent = this.endingIsPaused ? '▶ 再開' : '⏸ 一時停止';
      };
    }

    const speedBtn = document.getElementById('endingSpeedBtn');
    if (speedBtn) {
      speedBtn.onclick = () => {
        if (this.endingScrollSpeed <= 0.8) {
          this.endingScrollSpeed = 1.6;
          speedBtn.textContent = '⏩ 速度: 2.0x';
        } else if (this.endingScrollSpeed <= 1.8) {
          this.endingScrollSpeed = 3.2;
          speedBtn.textContent = '⏩ 速度: 4.0x';
        } else {
          this.endingScrollSpeed = 0.75;
          speedBtn.textContent = '⏩ 速度: 1.0x';
        }
      };
    }

    const skipBtn = document.getElementById('endingSkipBtn');
    if (skipBtn) {
      skipBtn.onclick = () => this.closeEndingRoll();
    }
  },

  updateDiffBadge() {
    const badge = document.getElementById('diffBadgeDisplay');
    if (!badge) return;
    const diff = this.currentDifficulty || 'normal';
    const config = {
      easy:   { text: '【初級】', color: '#2ecc71', border: '#27ae60', bg: 'rgba(46,204,113,0.25)' },
      normal: { text: '【中級】', color: '#f39c12', border: '#d68910', bg: 'rgba(243,156,18,0.25)' },
      hard:   { text: '【上級】', color: '#e67e22', border: '#d35400', bg: 'rgba(230,126,34,0.25)' },
      hell:   { text: '【修羅】', color: '#ff6666', border: '#aa3333', bg: 'rgba(100,20,20,0.4)' }
    };
    const c = config[diff] || config.normal;
    badge.textContent = c.text;
    badge.style.color = c.color;
    badge.style.borderColor = c.border;
    badge.style.background = c.bg;
  },

  // ============================================================================
  // ヘッダー・ステータス更新
  // ============================================================================,

  updateStatusHeader() {
    this.updateDiffBadge();
    const seasonDisp = document.getElementById('seasonDisplay');
    if (seasonDisp) {
      seasonDisp.innerHTML = `<i data-lucide="calendar" style="width:16px; height:16px;"></i><span>${this.year}年 ${this.seasonNames[this.seasonIdx]}</span>`;
      if (window.lucide) lucide.createIcons();
    }

    const weatherDisp = document.getElementById('weatherDisplay');
    if (weatherDisp) weatherDisp.textContent = `🌤️ 天候: ${this.currentWeather}`;

    const daimyoEl = document.getElementById('statDaimyo');
    const livingPlayerDaimyo = (this.activeOfficers || []).find(o => o.clanId === this.playerClanId && o.isDaimyo && !o.isDead);
    if (livingPlayerDaimyo && this.playerDaimyo && livingPlayerDaimyo.name && this.playerDaimyo.name !== livingPlayerDaimyo.name) {
      this.playerDaimyo.name = livingPlayerDaimyo.name;
      this.playerDaimyo.officerId = livingPlayerDaimyo.id;
    }
    if (daimyoEl && this.playerDaimyo) daimyoEl.textContent = this.playerDaimyo.name;

    const ability = getClanAbility(this.playerClanId);
    const personLabel = ability.personality === 'aggressive' ? '攻勢型'
                      : ability.personality === 'domestic'   ? '内政型'
                      : 'バランス型';
    const personColor = ability.personality === 'aggressive' ? '#ff8888'
                      : ability.personality === 'domestic'   ? '#88ff88'
                      : '#88ccff';
    const personBg = ability.personality === 'aggressive' ? 'rgba(255,107,107,0.18)'
                   : ability.personality === 'domestic'   ? 'rgba(46,204,113,0.18)'
                   : 'rgba(52,152,219,0.18)';

    const clanEl = document.getElementById('statClan');
    const dynamicClan = this.getClanFamilyName(this.playerClanId);
    if (clanEl) clanEl.textContent = dynamicClan;
    if (this.playerDaimyo) this.playerDaimyo.clan = dynamicClan;

    const badgeEl = document.getElementById('statPersonalityBadge');
    if (badgeEl) {
      badgeEl.textContent = personLabel;
      badgeEl.style.color = personColor;
      badgeEl.style.background = personBg;
      badgeEl.style.borderColor = personColor;
    }

    const milEl = document.getElementById('statMil');
    if (milEl) milEl.textContent = ability.military ?? 70;
    const polEl = document.getElementById('statPol');
    if (polEl) polEl.textContent = ability.politics ?? 70;
    const stratEl = document.getElementById('statStrat');
    if (stratEl) stratEl.textContent = ability.stratagem ?? 70;

    const goldEl = document.getElementById('statGold');
    if (goldEl) goldEl.textContent = this.gold.toLocaleString();

    const riceEl = document.getElementById('statRice');
    if (riceEl) riceEl.textContent = this.rice.toLocaleString();

    const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
    const totalCount = this.provinces.length;
    const provsEl = document.getElementById('statProvinces');
    if (provsEl) provsEl.textContent = `${myProvs.length} / ${totalCount} 国`;

    const progEl = document.getElementById('statProgression');
    if (progEl) progEl.textContent = `天下統一まで ${totalCount - myProvs.length}国`;

    const prob = Math.min(100, Math.round((myProvs.length / totalCount) * 100));
    const probEl = document.getElementById('statProbability');
    if (probEl) probEl.textContent = `${prob}%`;
    const probBar = document.getElementById('statProbBar');
    if (probBar) probBar.style.width = `${prob}%`;

    let totalTroops = 0;
    myProvs.forEach(p => totalTroops += p.troops);
    const troopsEl = document.getElementById('statTroops');
    if (troopsEl) troopsEl.textContent = totalTroops.toLocaleString();

    const apEl = document.getElementById('statAp');
    if (apEl) apEl.textContent = `${this.ap} / ${this.maxAp}`;

    const apTokens = document.getElementById('apTokensContainer');
    if (apTokens) {
      apTokens.innerHTML = '';
      for (let i = 0; i < this.maxAp; i++) {
        const t = document.createElement('div');
        t.className = `ap-token ${i < this.ap ? 'active' : ''}`;
        apTokens.appendChild(t);
      }
    }

    if (window.lucide && typeof lucide.createIcons === 'function') {
      lucide.createIcons();
    }

    const headKamon = document.getElementById('headerKamonSvg');
    if (headKamon && this.playerClanId) {
      headKamon.innerHTML = `<use href="#${this.getClanKamonId(this.playerClanId)}" x="0" y="0" width="32" height="32"/>`;
    }
  },

  // 大名家・家紋に即した鮮明なハイライト輪郭カラーの取得,

  log(msg, type = '') {
    const logBox = document.getElementById('gameLog');
    if (logBox) {
      logBox.innerHTML = '';
      const div = document.createElement('div');
      div.className = `log-entry ${type}`;
      div.textContent = msg;
      logBox.appendChild(div);
    }
    const fullList = document.getElementById('chronicleFullList');
    if (fullList) {
      const div = document.createElement('div');
      div.className = `log-entry ${type}`;
      div.textContent = `${this.year}年 ${this.seasonNames[this.seasonIdx]}: ${msg}`;
      fullList.insertBefore(div, fullList.firstChild);
    }
  },

  // ============================================================================
  // UIイベントバインディング
  // ============================================================================,

  initUI() {
    // 戦況年代記モーダル開閉
    const openChronicle = () => {
      document.getElementById('chronicleModal')?.classList.remove('hidden');
      this.audio.playHyoshigi();
    };
    document.getElementById('headerChronicleWrap')?.addEventListener('click', openChronicle);
    document.getElementById('closeChronicleModalBtn')?.addEventListener('click', () => {
      document.getElementById('chronicleModal')?.classList.add('hidden');
    });
    document.getElementById('closeChronicleModalBtn2')?.addEventListener('click', () => {
      document.getElementById('chronicleModal')?.classList.add('hidden');
    });

    // 厳選5大コマンドボタン
    document.getElementById('cmdDomestic')?.addEventListener('click', () => this.executeDomestic());
    document.getElementById('cmdMilitary')?.addEventListener('click', () => this.executeMilitary());
    document.getElementById('cmdStratagem')?.addEventListener('click', () => this.executeStratagem());
    document.getElementById('cmdRecruit')?.addEventListener('click', () => this.openRecruitRoninModal());
    document.getElementById('cmdAttack')?.addEventListener('click', () => this.openDeployModal());
    document.getElementById('cmdTransfer')?.addEventListener('click', () => this.openTransferModal());
    document.getElementById('nextTurnBtn')?.addEventListener('click', () => {
      if (this.isAutoPlay) {
        this.stopAutoPlay('手動停止');
      }
      this.nextSeason();
    });

    // オートプレーモード設定
    document.getElementById('autoPlayToggleBtn')?.addEventListener('click', () => {
      this.toggleAutoPlay();
    });
    const autoSpeedSlider = document.getElementById('autoPlaySpeedSlider');
    if (autoSpeedSlider) {
      autoSpeedSlider.addEventListener('input', (e) => {
        this.updateAutoPlaySpeed(e.target.value);
      });
    }

    // 出陣モーダル
    document.getElementById('deployCancelBtn')?.addEventListener('click', () => {
      document.getElementById('deployModal')?.classList.add('hidden');
    });
    document.getElementById('deployConfirmBtn')?.addEventListener('click', () => this.confirmDeploy());

    // 陣形選択
    document.querySelectorAll('#formationOptionGroup .diff-option-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#formationOptionGroup .diff-option-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this.selectedFormationKey = btn.dataset.form;
        this.refreshDeployFormationIntel();
      });
    });

    // 地図ヒートマップ切替
    document.querySelectorAll('#mapHeatFilter .map-heat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.setMapHeatMode(btn.dataset.heat);
      });
    });

    // 兵力移動モーダル
    document.getElementById('transferCancelBtn')?.addEventListener('click', () => {
      document.getElementById('transferModal')?.classList.add('hidden');
    });
    document.getElementById('transferConfirmBtn')?.addEventListener('click', () => this.confirmTransfer());

    // 合戦行動ボタン (一騎討ち廃止)
    document.getElementById('bCmdAssault')?.addEventListener('click', () => this.handleBattleAction('assault'));
    document.getElementById('bCmdShoot')?.addEventListener('click', () => this.handleBattleAction('shoot'));
    document.getElementById('bCmdDefend')?.addEventListener('click', () => this.handleBattleAction('defend'));
    document.getElementById('bCmdTactic')?.addEventListener('click', () => this.handleBattleAction('tactic'));
    document.getElementById('bCmdRetreat')?.addEventListener('click', () => this.handleBattleAction('retreat'));

    // 攻城戦行動ボタン (完全強化)
    document.getElementById('siegeBtnAssault')?.addEventListener('click', () => this.handleSiegeAction('assault'));
    document.getElementById('siegeBtnShoot')?.addEventListener('click', () => this.handleSiegeAction('shoot'));
    document.getElementById('siegeBtnSurround')?.addEventListener('click', () => this.handleSiegeAction('surround'));
    document.getElementById('siegeBtnPersuade')?.addEventListener('click', () => this.handleSiegeAction('persuade'));
    document.getElementById('siegeBtnRetreat')?.addEventListener('click', () => this.handleSiegeAction('retreat'));

    // 勢力一覧モーダル
    document.getElementById('factionListModalBtn')?.addEventListener('click', () => this.openFactionListModal());

    // 領国一覧モーダル
    document.getElementById('provinceListModalBtn')?.addEventListener('click', () => this.openProvinceListModal());

    // 武将一覧モーダル
    document.getElementById('officerListModalBtn')?.addEventListener('click', () => this.openOfficerListModal());

    // 領国一括委任モーダル
    document.getElementById('governModalBtn')?.addEventListener('click', () => this.openGovernModal());
    document.getElementById('closeGovernModalBtn')?.addEventListener('click', () => {
      document.getElementById('governModal')?.classList.add('hidden');
      if (this.selectedProvId) this.selectProvince(this.selectedProvId);
    });

    // 委任プリセット
    document.getElementById('btnPresetDomestic')?.addEventListener('click', () => this.applyPresetGovernance('rear_domestic'));
    document.getElementById('btnPresetLogistics')?.addEventListener('click', () => this.applyPresetGovernance('rear_logistics'));
    document.getElementById('btnPresetMilitary')?.addEventListener('click', () => this.applyPresetGovernance('front_military'));
    document.getElementById('btnPresetDirect')?.addEventListener('click', () => this.applyPresetGovernance('all_direct'));

    // 委任一括適用
    document.getElementById('applyDirectBatch')?.addEventListener('click', () => this.applyBatchGovernance('direct'));
    document.getElementById('applyMilitaryBatch')?.addEventListener('click', () => this.applyBatchGovernance('military'));
    document.getElementById('applyDomesticBatch')?.addEventListener('click', () => this.applyBatchGovernance('domestic'));
    document.getElementById('applyBalancedBatch')?.addEventListener('click', () => this.applyBatchGovernance('balanced'));
    document.getElementById('applyLogisticsBatch')?.addEventListener('click', () => this.applyBatchGovernance('logistics'));

    // 全選択チェックボックス
    document.getElementById('selectAllProvsCheckbox')?.addEventListener('change', (e) => {
      document.querySelectorAll('.govern-select-cb').forEach(cb => cb.checked = e.target.checked);
    });

    // 征夷大将軍宣下モーダルボタン
    document.getElementById('shogunAcceptEndingBtn')?.addEventListener('click', () => {
      document.getElementById('shogunModal')?.classList.add('hidden');
      this.shogunAppointed = true;
      this.triggerVictory(true); // 将軍就任エンディング
    });
    document.getElementById('shogunContinueConquestBtn')?.addEventListener('click', () => {
      document.getElementById('shogunModal')?.classList.add('hidden');
      this.shogunAppointed = true;
      this.audio.playHoragai();
      this.log('👑【征夷大将軍宣下】朝廷より征夷大将軍に任ぜられました！残る群雄を平定し全土完全統一へ進軍します！', 'important');
      Swal.fire({
        icon: 'success',
        title: '👑 征夷大将軍 拝命！',
        text: '大将軍の武威を轟かせ、残る群雄を平定し日本全五拾州の完全統一へ邁進します！',
        background: '#241710',
        color: '#ffd700'
      });
      this.updateUI();
    });

    // 天下統一・エンドロール再鑑賞ボタン
    document.getElementById('victoryWatchRollBtn')?.addEventListener('click', () => {
      document.getElementById('victoryModal')?.classList.add('hidden');
      this.startEndingRoll(this._isShogunRoute);
    });

    // 天下統一・滅亡再戦ボタン
    document.getElementById('victoryRestartBtn')?.addEventListener('click', () => location.reload());
    document.getElementById('defeatRestartBtn')?.addEventListener('click', () => location.reload());

    // ヘッダー音量・BGM制御
    document.getElementById('bgmToggleBtn')?.addEventListener('click', () => {
      this.music.toggleBgm();
      const badge = document.getElementById('bgmTitleBadge');
      if (badge) {
        badge.textContent = this.music.isBgmMuted ? '🔇 BGM: 停止' : `🎵 ${this.music.tracks[this.music.currentTrack]?.name || '和風BGM'}`;
      }
    });

    document.getElementById('soundToggleBtn')?.addEventListener('click', () => {
      this.music.init();
      const isMuted = this.music.toggleMute();
      document.getElementById('soundText').textContent = isMuted ? '音: OFF' : '音: ON';
      document.getElementById('soundIcon').textContent = isMuted ? '🔇' : '🔊';

      const slider = document.getElementById('volumeSlider');
      if (slider && !isMuted && parseFloat(slider.value) === 0) {
        slider.value = 0.7;
        this.music.setVolume(0.7);
      }
    });

    document.getElementById('volumeSlider')?.addEventListener('input', (e) => {
      this.music.init();
      const val = parseFloat(e.target.value);
      if (this.music.isMuted && val > 0) {
        this.music.isMuted = false;
        document.getElementById('soundText').textContent = '音: ON';
        document.getElementById('soundIcon').textContent = '🔊';
      }
      this.music.setVolume(val);
      if (val === 0) {
        document.getElementById('soundText').textContent = '音: OFF';
        document.getElementById('soundIcon').textContent = '🔇';
      } else if (!this.music.isMuted) {
        document.getElementById('soundText').textContent = '音: ON';
        document.getElementById('soundIcon').textContent = '🔊';
      }
    });

    // セーブ・ロード
    document.getElementById('saveGameBtn')?.addEventListener('click', () => {
      this.autoSave(true);
      Swal.fire({ icon: 'success', title: '戦況記録完了', text: '天下の戦況をブラウザに記録しました。次回起動時に再開できます。', background: '#241710', color: '#fff' });
    });

    document.getElementById('loadGameBtn')?.addEventListener('click', () => {
      const raw = localStorage.getItem('sengoku_save_data');
      if (!raw) {
        Swal.fire({ icon: 'info', title: '記録なし', text: '保存された戦況データがありません。', background: '#241710', color: '#fff' });
        return;
      }
      try {
        const data = JSON.parse(raw);
        this.loadGameData(data);
      } catch (e) {
        Swal.fire({ icon: 'error', title: '読込失敗', text: 'データの復元に失敗しました。', background: '#241710', color: '#fff' });
      }
    });

    // 菅野よう子風 戦国管弦楽 響宴録 UI初期化
    this.initMusicJukeboxUI();
  },


  // ============================================================================
  // 戦国管弦楽 響宴録 (ジュークボックス・サウンドテスト) UI制御
  // ============================================================================,

  initMusicJukeboxUI() {
    const modal = document.getElementById('musicJukeboxModal');
    if (!modal) return;

    // 開く関数
    const openJukebox = () => {
      this.music.init();
      modal.classList.remove('hidden');
      this.updateJukeboxDisplay();
      try { this.audio.playDecision?.(); } catch(e) {}
    };

    // 閉じる関数
    const closeJukebox = () => {
      modal.classList.add('hidden');
      try { this.audio.playCancel?.(); } catch(e) {}
    };

    document.getElementById('openJukeboxBtn')?.addEventListener('click', openJukebox);
    document.getElementById('bgmToggleBtn')?.addEventListener('click', openJukebox);
    document.getElementById('closeJukeboxBtn')?.addEventListener('click', closeJukebox);
    document.getElementById('closeJukeboxBtn2')?.addEventListener('click', closeJukebox);

    // コントロールボタン
    document.getElementById('jbPrevBtn')?.addEventListener('click', () => {
      this.music.playPrevTrack();
      this.updateJukeboxDisplay();
      try { this.audio.playDecision?.(); } catch(e) {}
    });

    document.getElementById('jbNextBtn')?.addEventListener('click', () => {
      this.music.playNextTrack();
      this.updateJukeboxDisplay();
      try { this.audio.playDecision?.(); } catch(e) {}
    });

    document.getElementById('jbPlayPauseBtn')?.addEventListener('click', () => {
      this.music.toggleBgm();
      this.updateJukeboxDisplay();
    });

    // スライダー連動
    document.getElementById('jbMasterVol')?.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      this.music.setVolume(val);
      const mainSlider = document.getElementById('volumeSlider');
      if (mainSlider) mainSlider.value = val;
    });

    document.getElementById('jbBgmVol')?.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      this.music.setBgmVolume(val);
    });

    document.getElementById('jbSeVol')?.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      this.music.setSeVolume(val);
    });

    // 大名専用曲優先チェックボックス
    const daimyoCb = document.getElementById('jbDaimyoModeCheck');
    if (daimyoCb) {
      daimyoCb.checked = this.music.daimyoBgmEnabled;
      daimyoCb.addEventListener('change', (e) => {
        this.music.daimyoBgmEnabled = e.target.checked;
        if (!this.inBattle) {
          this.music.playTrack(this.getSeasonTrackKey(), true);
          this.updateJukeboxDisplay();
        }
      });
    }

    // 4大カテゴリ別 楽曲選曲リストの生成
    this.renderJukeboxTrackList();

    // SE試聴グリッドの生成
    this.renderJukeboxSeGrid();
  },

  renderJukeboxTrackList() {
    const container = document.getElementById('jbTrackListContainer');
    if (!container) return;
    container.innerHTML = '';

    const categories = [
      {
        title: '🌸【四季・天下創世の情景】',
        tracks: ['op', 'spring', 'summer', 'autumn', 'winter']
      },
      {
        title: '🏯【英傑大名 専用交響詩】',
        tracks: ['oda', 'takeda', 'uesugi', 'date', 'mori_choso', 'shimazu', 'hojo']
      },
      {
        title: '⚔️【合戦・決戦・激突】',
        tracks: ['battle', 'battle_intense', 'siege', 'march', 'advantage', 'crisis']
      },
      {
        title: '📜【歴史・天下泰平・鎮魂】',
        tracks: ['event', 'shogun', 'tea', 'diplomacy', 'victory', 'tragedy']
      }
    ];

    categories.forEach(cat => {
      const group = document.createElement('div');
      group.className = 'jb-category-group';

      const titleEl = document.createElement('div');
      titleEl.className = 'jb-category-title';
      titleEl.textContent = cat.title;
      group.appendChild(titleEl);

      const grid = document.createElement('div');
      grid.className = 'jb-track-grid';

      cat.tracks.forEach(trackId => {
        const trk = this.music.tracks[trackId];
        if (!trk) return;

        const card = document.createElement('div');
        card.className = `jb-track-card ${this.music.currentTrack === trackId ? 'active' : ''}`;
        card.dataset.trackId = trackId;

        card.innerHTML = `
          <div class="jb-track-card-info">
            <div class="jb-track-card-name">🎵 ${trk.name}</div>
            <div class="jb-track-card-genre">${trk.genre || ''}</div>
          </div>
          <span style="font-size: 10pt; color: var(--gold-bright);">▶ 演奏</span>
        `;

        card.addEventListener('click', () => {
          this.music.playTrack(trackId, true);
          this.updateJukeboxDisplay();
          try { this.audio.playDecision?.(); } catch(e) {}
        });

        grid.appendChild(card);
      });

      group.appendChild(grid);
      container.appendChild(group);
    });
  },

  renderJukeboxSeGrid() {
    const grid = document.getElementById('jbSeGrid');
    if (!grid) return;
    grid.innerHTML = '';

    const seItems = [
      { label: '📯 陣中法螺貝', action: () => this.audio.playHoragai?.(1.0) },
      { label: '🎺 祝賀ファンファーレ', action: () => this.audio.playFanfare?.() },
      { label: '👑 大将軍特大凱歌', action: () => this.audio.playGrandFanfare?.() },
      { label: '🥁 能楽小鼓', action: () => this.audio.playTsuzumiSound?.() },
      { label: '🥁 地鳴り大太鼓', action: () => this.audio.playWadaikoSound?.() },
      { label: '🥁 締太鼓連打', action: () => this.audio.playTaiko?.(1.2) },
      { label: '⚔️ 抜刀・白刃火花', action: () => this.audio.playSword?.() },
      { label: '💥 火縄銃隊一斉射', action: () => this.audio.playTeppo?.() },
      { label: '🏹 弓矢隊斉射', action: () => this.audio.playArrow?.() },
      { label: '🐎 騎馬隊突撃', action: () => this.audio.playCavalry?.() },
      { label: '💰 小判チャリン', action: () => this.audio.playCoin?.() },
      { label: '💧 茶室・水琴窟', action: () => this.audio.playTea?.() },
      { label: '🔔 大銅鑼・梵鐘', action: () => this.audio.playDoraSound?.() },
      { label: '⚡ 運命の劇的ヒット', action: () => this.audio.playEventNotice?.() },
      { label: '🎌 勝鬨・全軍凱歌', action: () => this.audio.playKachi?.() },
      { label: '🏆 官位昇叙ハープ', action: () => this.audio.playRankUp?.() },
      { label: '🪵 拍子木', action: () => this.audio.playHyoshigi?.() },
      { label: '⛩️ 神楽鈴', action: () => this.audio.playSuzu?.() }
    ];

    seItems.forEach(item => {
      const btn = document.createElement('button');
      btn.className = 'jb-se-btn';
      btn.textContent = item.label;
      btn.addEventListener('click', () => {
        try { item.action(); } catch(e) {}
      });
      grid.appendChild(btn);
    });
  },

  updateJukeboxDisplay() {
    const curTrk = this.music.getCurrentTrackInfo();
    if (!curTrk) return;

    // 現在曲のタイトル・ジャンル・解説
    const titleEl = document.getElementById('jbTrackTitle');
    const genreEl = document.getElementById('jbTrackGenre');
    const descEl = document.getElementById('jbTrackDesc');
    const playPauseBtn = document.getElementById('jbPlayPauseBtn');
    const eqVis = document.getElementById('jbEqVisualizer');
    const badge = document.getElementById('bgmTitleBadge');

    if (titleEl) titleEl.textContent = curTrk.name;
    if (genreEl) genreEl.textContent = curTrk.genre || '';
    if (descEl) descEl.textContent = curTrk.desc || '';

    if (playPauseBtn) {
      playPauseBtn.textContent = this.music.isBgmMuted ? '▶ 再生' : '⏸ 停止';
    }

    if (eqVis) {
      if (this.music.isBgmMuted) {
        eqVis.classList.add('paused');
      } else {
        eqVis.classList.remove('paused');
      }
    }

    if (badge) {
      badge.textContent = this.music.isBgmMuted ? '🔇 BGM: 停止' : `🎵 ${curTrk.name}`;
    }

    // カードの active クラス更新
    document.querySelectorAll('.jb-track-card').forEach(card => {
      if (card.dataset.trackId === this.music.currentTrack) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  },

  // ============================================================================
  // 四季折々の日本美・季節＆天候パーティクルビジュアル (Canvas)
  // ============================================================================,

  showHonnoujiSuccessorSelectModal(ev) {
    const options = (ev && ev.successorOptions) || (window.HONNOUJI_SUCCESSION_DATA || {}).successorOptions || [];

    let modal = document.getElementById('honnoujiSuccessorModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'honnoujiSuccessorModal';
      modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.88); z-index:99999; display:flex; justify-content:center; align-items:center;';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div style="background:#19120c; border:2px solid #e74c3c; border-radius:8px; width:92%; max-width:760px; max-height:88vh; display:flex; flex-direction:column; box-shadow:0 0 40px rgba(231,76,60,0.6); color:#f5eedc; font-family:'Noto Serif JP',serif;">
        <div style="padding:14px 20px; border-bottom:1px solid #78281f; background:linear-gradient(180deg, #3a1510 0%, #1c0a08 100%);">
          <h2 style="margin:0; font-size:16pt; color:#ff6b6b; text-align:center;">❖ 天下動乱・後継勢力の選択 ❖</h2>
          <p style="margin:6px 0 0 0; font-size:11pt; color:#e0d8c3; text-align:center; line-height:1.4;">
            織田信長公の落命により、織田帝国は瞬く間に分裂いたしました。<br>
            以後の乱世を生き抜くため、貴殿が率いる後継勢力を選定してください。
          </p>
          ${this.autoPlayPausedForEvent ? '<p class="event-auto-pause-note" style="margin:8px 0 0 0; font-size:11pt; color:#f5b041; text-align:center;">⏸ オート進行を一時停止しています。後継を選ぶと再開します。</p>' : ''}
        </div>
        <div style="flex:1; overflow-y:auto; padding:16px 20px; display:flex; flex-direction:column; gap:12px;">
          ${options.map(opt => {
            const ab = getClanAbility(opt.clanId) || { military: 75, politics: 75, stratagem: 75 };
            const provCount = this.provinces.filter(p => p.ownerId === opt.clanId).length;
            return `
              <div style="background:rgba(255,255,255,0.04); border:1px solid #5a4638; border-radius:6px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center; gap:12px;">
                <div style="flex:1;">
                  <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:4px;">
                    <strong style="font-size:13pt; color:var(--gold-bright);">${opt.name}</strong>
                    <span style="font-size:10.5pt; color:#e67e22; font-weight:bold;">${opt.title}</span>
                    <span style="font-size:10pt; color:#aaa;">支配領国: ${provCount}カ国</span>
                  </div>
                  <div style="font-size:10.5pt; color:#ccc; margin-bottom:4px;">${opt.desc}</div>
                  <div style="font-size:10pt; color:#f9e79f;">
                    能力: 武勇${ab.military} / 内政${ab.politics} / 知略${ab.stratagem}
                  </div>
                </div>
                <div>
                  <button class="btn-choose-successor" data-clan-id="${opt.clanId}" style="background:#922b21; color:#fff; border:1px solid #e74c3c; padding:8px 16px; border-radius:4px; cursor:pointer; font-size:11.5pt; font-weight:bold; white-space:nowrap; transition:0.2s;">この勢力を率いる</button>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;

    modal.style.display = 'flex';

    modal.querySelectorAll('.btn-choose-successor').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const clanId = e.currentTarget.dataset.clanId;
        const chosen = options.find(o => o.clanId === clanId);
        modal.style.display = 'none';

        this.executeHonnoujiSuccession(clanId);
        this.audio.playTaiko();
        this.audio.playFanfare();
        this.music.playTrack(this.getSeasonTrackKey());

        if (this.autoPlayPausedForEvent || this.isAutoPlay) {
          this.log(`【天下動乱】${chosen.name}が立ち上がり、後継勢力として覇業を開始しました！`, 'important');
          this.updateUI();
          const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
          if (myProvs.length > 0) this.selectProvince(myProvs[0].id);
          this.continueAfterHistoricalEvent();
          return;
        }

        Swal.fire({
          title: `❖ 新当主 就任 ❖`,
          html: `
            <div style="text-align:center; padding:10px; font-family:'Noto Serif JP',serif;">
              <p style="font-size:14pt; color:#ffd700; margin-bottom:12px;"><strong>【${chosen.name} 公、天下取りへ名乗りを上げる！】</strong></p>
              <p style="font-size:11.5pt; color:#fff; line-height:1.6;">
                信長公の遺志を継ぎ、あるいは新たな武門の天下を築くため、${chosen.name}公が立ち上がりました！<br>
                山崎・賤ヶ岳の激戦を制し、天下統一を成し遂げてください！
              </p>
            </div>
          `,
          background: '#1c130d',
          color: '#f5eedc',
          confirmButtonText: 'いざ、出陣！',
          confirmButtonColor: '#922b21'
        }).then(() => {
          this.log(`【天下動乱】${chosen.name}が立ち上がり、後継勢力として覇業を開始しました！`, 'important');
          this.updateUI();
          const myProvs = this.provinces.filter(p => p.ownerId === this.playerClanId);
          if (myProvs.length > 0) {
            this.selectProvince(myProvs[0].id);
          }
          this.continueAfterHistoricalEvent();
        });
      });
    });
  },

  showHistoricalEvent(ev) {
    this.sealRebellionPair(ev.id);
    const choices = typeof ev.choices === 'function' ? ev.choices(this) : (ev.choices || []);
    if (this.isAutoPlay) this.pauseAutoPlayForEvent();

    const modal = document.getElementById('historyEventModal');
    if (!modal) {
      const choice = choices.find(c => c.isHistorical) || choices[0];
      if (choice) this.applyHistoricalChoice(ev, choice);
      else this.continueAfterHistoricalEvent();
      return;
    }

    this.audio.playHoragai();
    setTimeout(() => this.audio.playTaiko(1.6), 400);

    const titleEl = document.getElementById('eventTitle');
    const badgeEl = document.getElementById('eventSeasonBadge');
    const subTitleEl = document.getElementById('eventSubTitle');
    const narrativeEl = document.getElementById('eventNarrative');
    const container = document.getElementById('eventChoicesContainer');

    if (titleEl) titleEl.textContent = ev.title;
    if (badgeEl) badgeEl.textContent = `${this.year}年 ${this.seasonNames[this.seasonIdx]}`;
    if (subTitleEl) subTitleEl.textContent = ev.subTitle;
    if (narrativeEl) narrativeEl.textContent = typeof ev.narrative === 'function' ? ev.narrative(this) : ev.narrative;

    if (container) {
      container.innerHTML = '';

      choices.forEach((c, idx) => {
        const card = document.createElement('div');
        card.className = `event-choice-card ${c.isHistorical ? 'historical' : 'if-route'}`;
        card.innerHTML = `
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <span style="font-size: 12pt; font-weight:bold; color:${c.isHistorical ? '#5dade2' : '#f39c12'}; background:rgba(0,0,0,0.5); padding:2px 8px; border-radius:3px;">
                ${c.isHistorical ? '📜 史実の決断' : '⚡ 歴史改変IFルート'}
              </span>
              <span style="font-size: 12pt; color:#aaa;">選択肢 ${idx + 1}</span>
            </div>
            <div style="font-size: 12pt; font-weight:bold; color:#fff; line-height:1.4; margin-bottom:6px;">
              ${c.text}
            </div>
            <div style="font-size: 12pt; color:#ddd; line-height:1.45;">
              <div style="color:#ffd700; margin-bottom:2px;">この選択の効果</div>
              ${c.desc}
              ${this.choiceEffectHtml(c, ev)}
            </div>
          </div>
          <button class="turn-btn" style="margin:8px 0 0 0; padding:6px 12px; font-size: 12pt; background:${c.isHistorical ? 'linear-gradient(180deg, #2980b9, #1b4f72)' : 'linear-gradient(180deg, #d35400, #962d00)'};">
            この決断を断行する
          </button>
        `;

        card.addEventListener('click', () => {
          if (this._eventDecidedId === ev.id) return;
          this._eventDecidedId = ev.id;
          this.applyHistoricalChoice(ev, c);
        });

        container.appendChild(card);
      });
    }

    this._eventDecidedId = null;
    modal.classList.remove('hidden');
  }

  /**
   * 選択イベントの史実ルートで、リンク先データイベントの領地変更が落ちないのを補う。
   * 選択側が既に ownerId を書き換えている／反乱・本能寺専用処理がある場合は触らない。
   */

};
