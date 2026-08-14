/* ═══════════════════════════════════════════
   外观设置 · 主题强调色 + 玻璃风格 + 背景模糊度（关于页面板）
   默认强调色从背景图自动提取，全部设置持久化
   ═══════════════════════════════════════════ */

const Settings = (() => {
  const KEY = "talent_theme";
  /* 24 色缩小色盘：彩色系 + 冷色 + 暖色 + 灰阶 */
  const PRESETS = [
    "#8b5cf6", "#a855f7", "#d946ef", "#ec4899", "#f43f5e", "#ef4444",
    "#f97316", "#f59e0b", "#facc15", "#84cc16", "#22c55e", "#10b981",
    "#14b8a6", "#06b6d4", "#22d3ee", "#0ea5e9", "#3b82f6", "#6366f1",
    "#818cf8", "#c084fc", "#e879f9", "#fb7185", "#94a3b8", "#64748b",
  ];

  /* 玻璃风格预设：blur / 背景透明度 / 饱和度 */
  const MODES = {
    frost: { blur: 32, bg: 0.055, sat: 130, label: "毛玻璃" },
    water: { blur: 16, bg: 0.03, sat: 170, label: "水玻璃" },
    matte: { blur: 46, bg: 0.09, sat: 100, label: "磨砂" },
  };

  let accent = "#8b5cf6";
  let mode = "frost";
  let blur = 32;

  /* 归一化为 hex（rgb() → #rrggbb） */
  function normalize(color) {
    if (!color) return "#8b5cf6";
    if (color.startsWith("#")) return color;
    const m = color.match(/(\d+),\s*(\d+),\s*(\d+)/);
    if (m) {
      return "#" + m.slice(1, 4).map((v) => (+v).toString(16).padStart(2, "0")).join("");
    }
    return "#8b5cf6";
  }

  /* 从背景图提取主色（取最鲜艳的代表色） */
  function extractFromBg() {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        try {
          const c = document.createElement("canvas");
          c.width = c.height = 16;
          const ctx = c.getContext("2d");
          ctx.drawImage(img, 0, 0, 16, 16);
          const d = ctx.getImageData(0, 0, 16, 16).data;
          let best = null, bestScore = -1;
          for (let i = 0; i < d.length; i += 4) {
            const r = d[i], g = d[i + 1], b = d[i + 2], a = d[i + 3];
            if (a < 128) continue;
            const max = Math.max(r, g, b), min = Math.min(r, g, b);
            const sat = max - min;
            const bright = (max + min) / 2;
            if (bright < 40 || bright > 235) continue;
            const score = sat + bright * 0.08;
            if (score > bestScore) { bestScore = score; best = [r, g, b]; }
          }
          resolve(best ? `rgb(${best[0]},${best[1]},${best[2]})` : "#8b5cf6");
        } catch (e) {
          resolve("#8b5cf6");
        }
      };
      img.onerror = () => resolve("#8b5cf6");
      img.src = "assets/bg.jpg";
    });
  }

  /* 应用全部主题到 CSS 变量 */
  function apply() {
    const m = MODES[mode];
    const blurPx = blur;
    const root = document.documentElement.style;
    root.setProperty("--accent", accent);
    root.setProperty("--accent2", `color-mix(in srgb, ${accent}, #ffffff 30%)`);
    root.setProperty("--nav-accent", accent);
    root.setProperty("--glass-blur", blurPx + "px");
    root.setProperty("--glass-bg", `rgba(255, 255, 255, ${m.bg})`);
    root.setProperty("--glass-sat", m.sat + "%");
    try {
      localStorage.setItem(KEY, JSON.stringify({ accent, mode, blur }));
    } catch (e) { /* ignore */ }
  }

  /* 初始化：读持久化配置，无则提取背景色；渲染外观面板 */
  async function init() {
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem(KEY));
    } catch (e) { /* ignore */ }

    if (saved && saved.accent) {
      accent = normalize(saved.accent);
      mode = MODES[saved.mode] ? saved.mode : "frost";
      blur = typeof saved.blur === "number" ? saved.blur : MODES[mode].blur;
    } else {
      accent = normalize(await extractFromBg());
      mode = "frost";
      blur = MODES.frost.blur;
    }
    apply();

    // 渲染控件
    renderAccent();
    renderModes();
    syncBlur();

    const toggle = document.getElementById("colorToggle");
    const pop = document.getElementById("colorPop");
    if (!toggle || toggle.dataset.bound) return;
    toggle.dataset.bound = "1";

    // 强调色按钮：点击展开/收起色盘
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      pop.hidden = !pop.hidden;
      toggle.classList.toggle("open", !pop.hidden);
    });
    document.addEventListener("click", (e) => {
      if (!pop.hidden && !pop.contains(e.target) && !toggle.contains(e.target)) {
        pop.hidden = true;
        toggle.classList.remove("open");
      }
    });

    const pick = document.getElementById("accentPick");
    pick.addEventListener("input", () => {
      accent = normalize(pick.value);
      apply();
      renderAccent();
    });

    const modesBox = document.getElementById("glassModes");
    modesBox.addEventListener("click", (e) => {
      const btn = e.target.closest(".mode");
      if (!btn || !MODES[btn.dataset.mode]) return;
      mode = btn.dataset.mode;
      blur = MODES[mode].blur;
      apply();
      renderModes();
      syncBlur();
    });

    const range = document.getElementById("glassBlur");
    range.addEventListener("input", () => {
      blur = parseInt(range.value, 10);
      apply();
      document.getElementById("glassBlurVal").textContent = blur + "px";
    });

    document.getElementById("btnAppearanceReset").addEventListener("click", async () => {
      accent = normalize(await extractFromBg());
      mode = "frost";
      blur = MODES.frost.blur;
      apply();
      renderAccent();
      renderModes();
      syncBlur();
      UI.toast("已恢复默认外观");
    });
  }

  /* 渲染色板（展开面板内）并同步色块按钮 */
  function renderAccent() {
    const palette = document.getElementById("accentPalette");
    const pick = document.getElementById("accentPick");
    const dot = document.getElementById("ctDot");
    if (!palette || !pick) return;
    palette.innerHTML = PRESETS.map((c) =>
      `<div class="swatch ${c === accent ? "sel" : ""}" data-c="${c}" style="background:${c}"></div>`).join("");
    pick.value = accent;
    if (dot) dot.style.background = accent;
    palette.onclick = (e) => {
      const s = e.target.closest(".swatch");
      if (!s) return;
      pick.value = s.dataset.c;
      pick.dispatchEvent(new Event("input"));
      // 选中后收起色盘
      const pop = document.getElementById("colorPop");
      const toggle = document.getElementById("colorToggle");
      if (pop) pop.hidden = true;
      if (toggle) toggle.classList.remove("open");
    };
  }

  /* 渲染玻璃风格按钮 */
  function renderModes() {
    const box = document.getElementById("glassModes");
    if (!box) return;
    box.querySelectorAll(".mode").forEach((b) => {
      b.classList.toggle("active", b.dataset.mode === mode);
    });
  }

  /* 同步模糊度滑块 */
  function syncBlur() {
    const range = document.getElementById("glassBlur");
    const val = document.getElementById("glassBlurVal");
    if (!range || !val) return;
    range.value = blur;
    val.textContent = blur + "px";
  }

  return { init, apply, extractFromBg };
})();
