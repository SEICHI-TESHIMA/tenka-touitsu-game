/**
 * @file js/render/MapRenderer.js - SVGマップ描画・ズーム・天候Canvasエフェクト
 * 戦国天下統一伝 ES6モジュール
 * @typedef {import('../types.js').Province} Province
 * @typedef {import('../types.js').PlayableDaimyo} PlayableDaimyo
 * @typedef {import('../types.js').Scenario} Scenario
 */

// モジュール間安全参照ヘルパー
var SCENARIOS = (typeof window !== 'undefined' && (window.SCENARIOS || window.SCENARIOS_DATA)) || [];

export class MapRenderer {
  constructor(game) {
    this.game = game;
  }
}

export const MapRendererMethods = {
  provinceCenterXY(prov) {
    if (!prov) return null;
    let cx = Number(prov.cx), cy = Number(prov.cy);
    if (!Number.isFinite(cx) || !Number.isFinite(cy)) {
      const base = (window.PROVINCES_DATA || []).find(p => p.id === prov.id);
      cx = Number(base && base.cx); cy = Number(base && base.cy);
    }
    return (Number.isFinite(cx) && Number.isFinite(cy)) ? { x: cx, y: cy } : null;
  },

  /** 領国群の重心に最も近い国 */

  provinceLatitude(provId) {
    const lat = (window.PROVINCE_LATITUDE || {})[provId];
    if (Number.isFinite(Number(lat))) return Number(lat);
    const rank = this.provinceGeoRank(provId);
    return rank >= 10000 ? 0 : 42 - rank * 0.14;
  },

  // 天皇・親王・上皇は支城の城代にしない。本拠の当主に選ばれたときだけ居城に座る。,

  initSvgMap() {
    if (typeof window.loadKamonSymbols === 'function') {
      window.loadKamonSymbols();
    }
    // 【修正1】CSSによる立体的な傾き（3D変形）を強制的に無効化する
    const svgMap = document.getElementById('sengokuMapSvg');
    if (svgMap) {
      svgMap.style.setProperty('transform', 'none', 'important');
    }
    const mapWrapper = document.getElementById('mapWrapper');
    if (mapWrapper) {
      mapWrapper.style.setProperty('perspective', 'none', 'important');
      mapWrapper.style.setProperty('transform', 'none', 'important');
    }

    const roadsGroup = document.getElementById('mapRoadsGroup');
    const provGroup = document.getElementById('mapProvincesGroup');
    const markGroup = document.getElementById('mapMarkersGroup');
    if (!provGroup) return;

    if (roadsGroup) roadsGroup.innerHTML = '';
    if (provGroup) provGroup.innerHTML = '';
    if (markGroup) markGroup.innerHTML = '';

    // 街道・航路ラインの描画
    const drawnPairs = new Set();
    this.provinces.forEach(p => {
      (p.neighbors || []).forEach(nId => {
        const key = [p.id, nId].sort().join('-');
        if (!drawnPairs.has(key)) {
          drawnPairs.add(key);
          const target = this.provinces.find(x => x.id === nId);
          if (target && p.cx !== undefined && target.cx !== undefined) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', p.cx);
            line.setAttribute('y1', p.cy);
            line.setAttribute('x2', target.cx);
            line.setAttribute('y2', target.cy);
            line.setAttribute('stroke', 'rgba(180, 140, 70, 0.45)');
            line.setAttribute('stroke-width', '1.5');
            line.setAttribute('stroke-dasharray', '3,3');
            roadsGroup.appendChild(line);
          }
        }
      });
    });

    // 50領国ポリゴン & 家紋バッジの描画
    this.provinces.forEach(p => {
      const isMine = p.ownerId === this.playerClanId;
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('id', `path-${p.id}`);
      path.setAttribute('class', `prov-path ${isMine ? 'player-prov' : 'enemy-prov'}`);
      path.setAttribute('d', p.svgPath || p.d);
      path.setAttribute('fill', this.getProvinceColor(p));

      path.addEventListener('click', (e) => {
        e.stopPropagation();
        this.selectProvince(p.id);
        this.audio.playHyoshigi();
      });

      provGroup.appendChild(path);

      // 家紋バッジ（各領国の中心点に配置）
      if (p.cx !== undefined && p.cy !== undefined) {
        const badgeG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        badgeG.setAttribute('id', `badge-${p.id}`);
        badgeG.setAttribute('class', `prov-badge-group ${isMine ? 'player-badge' : ''}`);
        if (!p.ownerId) {
          badgeG.style.display = 'none'; // ユーザー要件: 空白地は家紋非表示
        }

        // 家紋バッジ (16pxでさらに小型化・過密解消)
        const badgeSize = 16;
        const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        use.setAttribute('id', `kamon-use-${p.id}`);
        use.setAttribute('href', p.ownerId ? `#${this.getClanKamonId(p.ownerId)}` : '');
        use.setAttribute('x', p.cx - badgeSize / 2);
        use.setAttribute('y', p.cy - badgeSize / 2);
        use.setAttribute('width', badgeSize);
        use.setAttribute('height', badgeSize);
        if (!p.ownerId) {
          use.style.display = 'none';
        }

        badgeG.appendChild(use);
        markGroup.appendChild(badgeG);
      }
    });

    // パン・ズーム
    const wrapper = document.getElementById('mapWrapper');
    const panLayer = document.getElementById('mapPanZoomLayer');
    if (wrapper && panLayer && !this.mapGestureBound) {
      // シナリオを切り替えて地図を描き直しても、ドラッグ操作が二重にならないようにする
      this.mapGestureBound = true;
      wrapper.addEventListener('mousedown', (e) => {
        this.isMapDragging = true;
        this.dragStartX = e.clientX - this.mapPanX;
        this.dragStartY = e.clientY - this.mapPanY;
      });

      window.addEventListener('mousemove', (e) => {
        if (!this.isMapDragging) return;
        this.mapPanX = e.clientX - this.dragStartX;
        this.mapPanY = e.clientY - this.dragStartY;
        this.applyPanZoom();
      });

      window.addEventListener('mouseup', () => {
        this.isMapDragging = false;
      });

      // スマホ：地図上のドラッグは上下左右とも地図を動かす。2本指で拡大縮小
      const touchDistance = (a, b) => Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      const mapZoomLimit = () => (window.matchMedia('(max-width: 768px)').matches ? 5 : 3.5);

      wrapper.addEventListener('touchstart', (e) => {
        if (e.target.closest('.map-ctrl-btn')) return;
        if (e.touches.length === 1) {
          const t = e.touches[0];
          this.touchStartX = t.clientX;
          this.touchStartY = t.clientY;
          this.dragStartX = t.clientX - this.mapPanX;
          this.dragStartY = t.clientY - this.mapPanY;
          this.isMapTouchPanning = false;
          this.mapPinching = false;
          return;
        }
        if (e.touches.length === 2) {
          this.mapPinching = true;
          this.pinchStartDist = touchDistance(e.touches[0], e.touches[1]);
          this.pinchStartScale = this.mapScale;
          this.isMapTouchPanning = true;
          this.mapSuppressClick = true;
        }
      }, { passive: true });

      wrapper.addEventListener('touchmove', (e) => {
        if (e.target.closest('.map-ctrl-btn') && !this.mapPinching && !this.isMapTouchPanning) return;
        if (e.touches.length === 2 && this.mapPinching) {
          e.preventDefault();
          const dist = touchDistance(e.touches[0], e.touches[1]);
          if (!this.pinchStartDist) return;
          const rect = wrapper.getBoundingClientRect();
          const cx = (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left;
          const cy = (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top;
          const oldScale = this.mapScale || 1;
          const nextScale = Math.min(mapZoomLimit(), Math.max(0.65, this.pinchStartScale * (dist / this.pinchStartDist)));
          this.mapPanX = cx - (cx - this.mapPanX) * (nextScale / oldScale);
          this.mapPanY = cy - (cy - this.mapPanY) * (nextScale / oldScale);
          this.mapScale = nextScale;
          this.applyPanZoom();
          this.mapSuppressClick = true;
          return;
        }
        if (e.touches.length !== 1 || this.mapPinching) return;
        const t = e.touches[0];
        const dx = t.clientX - this.touchStartX;
        const dy = t.clientY - this.touchStartY;
        if (!this.isMapTouchPanning) {
          if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
          this.isMapTouchPanning = true;
        }
        e.preventDefault();
        this.mapPanX = t.clientX - this.dragStartX;
        this.mapPanY = t.clientY - this.dragStartY;
        this.applyPanZoom();
        this.mapSuppressClick = true;
      }, { passive: false });

      wrapper.addEventListener('touchend', (e) => {
        if (e.touches.length === 1) {
          const t = e.touches[0];
          this.touchStartX = t.clientX;
          this.touchStartY = t.clientY;
          this.dragStartX = t.clientX - this.mapPanX;
          this.dragStartY = t.clientY - this.mapPanY;
          this.mapPinching = false;
          this.isMapTouchPanning = false;
          return;
        }
        if (e.touches.length === 0) {
          this.isMapTouchPanning = false;
          this.mapPinching = false;
        }
      });

      // 地図を動かした直後のタップで領国が選ばれないようにする
      wrapper.addEventListener('click', (e) => {
        if (!this.mapSuppressClick) return;
        this.mapSuppressClick = false;
        e.preventDefault();
        e.stopPropagation();
      }, true);

      wrapper.addEventListener('wheel', (e) => {
        e.preventDefault();
        const rect = wrapper.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        // ホイールズームを細かく滑らかに調整できるように設定 (約5%刻みの微細ズーム)
        const zoomFactor = e.deltaY < 0 ? 1.05 : 0.952;
        const oldScale = this.mapScale;
        const newScale = Math.min(mapZoomLimit(), Math.max(0.65, oldScale * zoomFactor));
        this.mapPanX = mouseX - (mouseX - this.mapPanX) * (newScale / oldScale);
        this.mapPanY = mouseY - (mouseY - this.mapPanY) * (newScale / oldScale);
        this.mapScale = newScale;
        this.applyPanZoom();
      }, { passive: false });

      document.getElementById('mapZoomInBtn')?.addEventListener('click', () => {
        this.mapScale = Math.min(mapZoomLimit(), this.mapScale * 1.2);
        this.applyPanZoom();
      });
      document.getElementById('mapZoomOutBtn')?.addEventListener('click', () => {
        this.mapScale = Math.max(0.65, this.mapScale * 0.83);
        this.applyPanZoom();
      });
      document.getElementById('mapResetBtn')?.addEventListener('click', () => {
        this.mapScale = 1.0;
        this.mapPanX = 0;
        this.mapPanY = 0;
        this.applyPanZoom();
      });
    }
  },

  applyPanZoom() {
    const panLayer = document.getElementById('mapPanZoomLayer');
    if (panLayer) {
      panLayer.setAttribute('transform', `translate(${this.mapPanX}, ${this.mapPanY}) scale(${this.mapScale})`);
    }
  },


  // ============================================================================
  // 陣形三すくみ・地形補正・軍師予測
  // ============================================================================,

  initEndingSakura() {
    const canvas = document.getElementById('endingSakuraCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const petals = [];
    const petalCount = 70;

    for (let i = 0; i < petalCount; i++) {
      petals.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 7 + 5,
        speedX: Math.random() * 1.5 - 0.5,
        speedY: Math.random() * 1.2 + 0.8,
        angle: Math.random() * Math.PI * 2,
        angularSpeed: Math.random() * 0.03 - 0.015,
        color: Math.random() > 0.3 ? 'rgba(255, 192, 203, 0.75)' : 'rgba(255, 215, 0, 0.65)'
      });
    }

    const animate = () => {
      if (document.getElementById('endingRollModal')?.classList.contains('hidden')) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      petals.forEach(p => {
        p.x += p.speedX;
        p.y += p.speedY;
        p.angle += p.angularSpeed;

        if (p.y > canvas.height + 20) {
          p.y = -20;
          p.x = Math.random() * canvas.width;
        }
        if (p.x > canvas.width + 20) p.x = -20;
        if (p.x < -20) p.x = canvas.width + 20;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle);
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.ellipse(0, 0, p.size, p.size * 0.55, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      this._sakuraAnimId = requestAnimationFrame(animate);
    };

    if (this._sakuraAnimId) cancelAnimationFrame(this._sakuraAnimId);
    this._sakuraAnimId = requestAnimationFrame(animate);
  },

  getClanHighlightColor(clanId) {
    if (!clanId) return '#ffd700';

    const CLAN_THEME_COLORS = {
      oda: '#ff4444',        // 織田: 鮮紅
      toyotomi: '#ffd700',   // 豊臣: 黄金
      tokugawa: '#2ecc71',   // 徳川: 葵緑
      takeda: '#e74c3c',     // 武田: 茜紅
      uesugi: '#3498db',     // 上杉: 毘沙門天の蒼天
      hojo: '#f39c12',       // 北条: 黄金山吹
      mori: '#1abc9c',       // 毛利: 厳島翡翠
      date: '#a569bd',       // 伊達: 雅紫
      shimazu: '#5dade2',    // 島津: 薩摩碧
      chosokabe: '#27ae60',  // 長宗我部: 土佐若竹
      sanada: '#ff3333',     // 真田: 六文銭赤備え
      imagawa: '#3498db',    // 今川: 駿河碧
      azai: '#58d68d',       // 浅井: 近江若草
      rokkaku: '#bb8fce',    // 六角: 近江源氏藤紫
      kyogoku: '#48c9b0',    // 京極: 水浅葱
      asakura: '#af7ac5',    // 朝倉: 一乗谷紫
      miyoshi: '#16a085',    // 三好: 阿波碧海
      otomo: '#e74c3c',      // 大友: 豊後紅
      ryuzoji: '#2980b9',    // 龍造寺: 肥前群青
      amago: '#f39c12',      // 尼子: 出雲月白金
      saito: '#f1c40f',      // 斎藤: 美濃金
      satake: '#27ae60',     // 佐竹: 常陸常盤緑
      nanbu: '#9b59b6',      // 南部: 南部紫
      ashikaga: '#f1c40f',   // 足利将軍家: 室町黄金
      minamoto: '#3498db',   // 源氏: 白藍
      taira: '#e74c3c',      // 平家: 赤旗紅
      chotei: '#ffd700',     // 朝廷・公家: 平安雅金
      masakado: '#ff4500',   // 平将門: 新皇の猛火
      sumitomo: '#00bcd4',   // 藤原純友: 瀬戸内碧青
      satsuma: '#5dade2',    // 薩摩藩: 薩摩碧
      choshu: '#1abc9c',     // 長州藩: 萩碧
      aizu: '#e74c3c',       // 会津藩: 赤誠紅
      bakufu: '#f1c40f'      // 幕府: 徳川葵金
    };

    if (CLAN_THEME_COLORS[clanId]) {
      return CLAN_THEME_COLORS[clanId];
    }

    // シナリオまたはCLAN_HISTORICAL_PROFILESの色
    const scen = SCENARIOS.find(s => String(s.id) === String(this.currentScenarioId) || String(s.year) === String(this.currentScenarioId));
    const playable = scen?.playables?.find(x => x.id === clanId);
    let c = playable?.color;
    if (!c) {
      const master = (window.CLAN_MASTER_DATA || {})[clanId];
      if (master && master.color) c = master.color;
    }

    if (c) {
      return this.brightenHexColor(c, 35);
    }
    return '#ffd700';
  },

  // カラーの明度引き上げヘルパー,

  updateMapDisplay() {
    const highlightColor = this.getClanHighlightColor(this.playerClanId);
    const glowColor = this.getClanGlowColor(this.playerClanId, 0.75);

    // CSSカスタムプロパティを更新して全体のスタイルと同期
    document.documentElement.style.setProperty('--player-clan-color', highlightColor);
    document.documentElement.style.setProperty('--player-clan-glow', glowColor);

    const provGroup = document.getElementById('mapProvincesGroup');
    const markGroup = document.getElementById('mapMarkersGroup');
    this._heatRangeCache = null;

    // 1. 各タイルの色・クラス・インラインスタイルの設定
    this.provinces.forEach(p => {
      const isMine = p.ownerId === this.playerClanId;
      const isSelected = p.id === this.selectedProvId;
      const path = document.getElementById(`path-${p.id}`);

      if (path) {
        path.setAttribute('fill', this.getProvinceColor(p));
        path.classList.toggle('player-prov', isMine);
        path.classList.toggle('enemy-prov', !isMine);
        path.classList.toggle('selected', isSelected);

        if (isMine) {
          // 自国領土：大名・家紋に即した鮮明な輪郭（見づらい光彩は一切なし）
          // 選択時は登録領国色をはっきり明るくした輪郭にする（塗りとの差が分かる程度）
          path.style.stroke = isSelected
            ? this.brightenHexColor(this.getRegisteredProvinceColor(p), 50)
            : highlightColor;
          // 自国領土の輪郭線は少し小さく(1.3px)、国を選んだ時はもう少し太く(3.2px)際立たせる
          path.style.strokeWidth = isSelected ? '3.2px' : '1.3px';
          path.style.filter = 'none';
        } else {
          if (!isSelected) {
            path.style.stroke = '';
            path.style.strokeWidth = '';
            path.style.filter = 'none';
          } else {
            // 他国偵察選択時：登録領国色をはっきり明るくした実線(3.0px)
            path.style.stroke = this.brightenHexColor(this.getRegisteredProvinceColor(p), 50);
            path.style.strokeWidth = '3.0px';
            path.style.filter = 'none';
          }
        }
      }

      const badge = document.getElementById(`badge-${p.id}`);
      if (badge) {
        badge.classList.toggle('player-badge', isMine);
        badge.style.display = p.ownerId ? '' : 'none'; // ユーザー要件: 空白地は家紋非表示
      }
      const use = document.getElementById(`kamon-use-${p.id}`);
      if (use) {
        if (!p.ownerId) {
          use.setAttribute('href', '');
          use.style.display = 'none';
        } else {
          use.setAttribute('href', `#${this.getClanKamonId(p.ownerId)}`);
          use.style.display = '';
        }
      }
    });

    // 2. 自国領土のタイルを全て最前面に押し出す（他国タイルの下に輪郭が隠れるのを完全防止）
    if (provGroup) {
      this.provinces.forEach(p => {
        if (p.ownerId === this.playerClanId && p.id !== this.selectedProvId) {
          const path = document.getElementById(`path-${p.id}`);
          if (path && path.parentNode === provGroup) {
            provGroup.appendChild(path);
          }
        }
      });
      // 選択中の自国/敵国タイルはさらに最前面へ
      if (this.selectedProvId) {
        const selPath = document.getElementById(`path-${this.selectedProvId}`);
        if (selPath && selPath.parentNode === provGroup) {
          provGroup.appendChild(selPath);
        }
      }
    }

    // 3. 自国家紋バッジも最前面に押し出す
    if (markGroup) {
      this.provinces.forEach(p => {
        if (p.ownerId === this.playerClanId && p.id !== this.selectedProvId) {
          const badge = document.getElementById(`badge-${p.id}`);
          if (badge && badge.parentNode === markGroup) {
            markGroup.appendChild(badge);
          }
        }
      });
      if (this.selectedProvId) {
        const selBadge = document.getElementById(`badge-${this.selectedProvId}`);
        if (selBadge && selBadge.parentNode === markGroup) {
          markGroup.appendChild(selBadge);
        }
      }
    }
  },

  initSeasonCanvas() {
    this.seasonCanvas = document.getElementById('seasonCanvas');
    if (!this.seasonCanvas) return;
    this.seasonCtx = this.seasonCanvas.getContext('2d');
    this.seasonParticles = [];

    const resize = () => {
      const parent = this.seasonCanvas.parentElement;
      if (parent) {
        this.seasonCanvas.width = parent.clientWidth;
        this.seasonCanvas.height = parent.clientHeight;
      }
    };
    resize();
    window.addEventListener('resize', resize);

    this.initSeasonParticles();
    this.startSeasonAnimationLoop();
  },

  startSeasonAnimationLoop() {
    const render = () => {
      if (!this.seasonCanvas || !this.seasonCtx) return;
      const ctx = this.seasonCtx;
      const w = this.seasonCanvas.width;
      const h = this.seasonCanvas.height;
      if (w === 0 || h === 0) {
        requestAnimationFrame(render);
        return;
      }
      ctx.clearRect(0, 0, w, h);

      const s = this.seasonIdx; // 0:春, 1:夏, 2:秋, 3:冬
      const isRain = this.currentWeather === '恵みの雨' || this.currentWeather === '豪雨';
      const isBlizzard = this.currentWeather === '吹雪' || this.currentWeather === '大雪';

      // 1. 雨天描画
      if (isRain) {
        ctx.strokeStyle = this.currentWeather === '豪雨' ? 'rgba(160, 200, 240, 0.4)' : 'rgba(180, 220, 255, 0.25)';
        ctx.lineWidth = this.currentWeather === '豪雨' ? 1.6 : 1.0;
        ctx.beginPath();
        for (let i = 0; i < 40; i++) {
          const rx = (Math.sin(i * 77 + Date.now() * 0.002) * 0.5 + 0.5) * w;
          const ry = ((Date.now() * 0.7 + i * 33) % h);
          ctx.moveTo(rx, ry);
          ctx.lineTo(rx - 6, ry + 16);
        }
        ctx.stroke();
      }

      // 2. 季節パーティクル描画
      this.seasonParticles.forEach(p => {
        p.angle += p.rotSpeed;
        p.flip += p.flipSpeed;

        if (s === 0) {
          // 春：桜の花びら
          p.y += p.speedY * 0.85;
          p.x += Math.sin(p.angle) * 1.2 + 0.5;
          if (p.y > h + 10) { p.y = -10; p.x = Math.random() * w; }
          if (p.x > w + 10) p.x = -10;

          ctx.save();
          ctx.translate(p.x, p.y);
          ctx.rotate(p.angle);
          ctx.scale(Math.cos(p.flip), 1);
          ctx.fillStyle = `rgba(255, 182, 193, ${p.opacity})`;
          ctx.beginPath();
          ctx.ellipse(0, 0, p.size, p.size * 1.6, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } else if (s === 1) {
          // 夏：陽光・木漏れ日の輝き
          p.y -= p.speedY * 0.5;
          p.x += Math.cos(p.angle) * 0.4;
          if (p.y < -10) { p.y = h + 10; p.x = Math.random() * w; }

          ctx.save();
          ctx.beginPath();
          const radGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 2);
          radGrad.addColorStop(0, `rgba(255, 235, 140, ${p.opacity * 0.7})`);
          radGrad.addColorStop(1, 'rgba(255, 235, 140, 0)');
          ctx.fillStyle = radGrad;
          ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } else if (s === 2) {
          // 秋：紅葉（赤・橙・黄金）
          p.y += p.speedY * 1.05;
          p.x += Math.sin(p.angle) * 1.5;
          if (p.y > h + 10) { p.y = -10; p.x = Math.random() * w; }
          if (p.x > w + 10) p.x = -10;

          ctx.save();
          ctx.translate(p.x, p.y);
          ctx.rotate(p.angle);
          ctx.scale(Math.cos(p.flip), 1);
          const col = (p.size > 5.5) ? 'rgba(215, 60, 30,' : 'rgba(235, 160, 25,';
          ctx.fillStyle = `${col} ${p.opacity})`;
          ctx.beginPath();
          ctx.arc(0, 0, p.size * 1.1, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } else if (s === 3) {
          // 冬：雪
          const wind = isBlizzard ? 3.0 : 0.3;
          p.y += (isBlizzard ? p.speedY * 2.0 : p.speedY * 0.75);
          p.x += Math.sin(p.angle) * 0.7 + wind;
          if (p.y > h + 10) { p.y = -10; p.x = Math.random() * w; }
          if (p.x > w + 10) p.x = -10;

          ctx.save();
          ctx.beginPath();
          ctx.fillStyle = `rgba(240, 245, 255, ${p.opacity * 0.85})`;
          ctx.arc(p.x, p.y, isBlizzard ? p.size * 0.8 : p.size * 0.9, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
      });

      requestAnimationFrame(render);
    };

    requestAnimationFrame(render);
  },

  // ============================================================================
  // 歴史劇的動乱・重大決断イベント (IF展開システム)
  // ============================================================================,

};
