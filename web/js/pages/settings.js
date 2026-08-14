/* ═══════════════════════════════════════════
   设置页 · 个性化配色
   主题强调色 / 导航选中色：默认从背景图自动提取搭配色，可自定义并持久化
   ═══════════════════════════════════════════ */

const Settings = (() => {
  const KEY = "talent_theme";
  const PRESETS = ["#8b5cf6", "#ec4899", "#22d3ee", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#6366f1"];

  let accent = null;   // 主题强调色
  let navAccent = null; // 导航选中色
  let followNav = true; // 导航是否跟随强调色

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
            const sat = max - min;                 // 饱和度
            const bright = (max + min) / 2;        // 亮度
            if (bright < 40 || bright > 235) continue; // 排除过暗过亮
            const score = sat + bright * 0.08;     // 鲜艳优先
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

  /* 应用主题到 CSS 变量 */
  function apply(ac, nav, follow) {
    accent = normalize(ac);
    navAccent = normalize(nav);
    followNav = follow;
    const root = document.documentElement.style;
    root.setProperty("--accent", accent);
    root.setProperty("--accent2", `color-mix(in srgb, ${accent}, #ffffff 30%)`);
    root.setProperty("--nav-accent", follow ? accent : navAccent);
    try {
      localStorage.setItem(KEY, JSON.stringify({ accent, navAccent, followNav: follow }));
    } catch (e) { /* ignore */ }
  }

  /* 初始化：读持久化配置，无则从背景图提取 */
  async function init() {
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem(KEY));
    } catch (e) { /* ignore */ }

    if (saved && saved.accent) {
      apply(saved.accent, saved.navAccent || saved.accent, saved.followNav !== false);
    } else {
      const c = await extractFromBg();
      apply(c, c, true);
    }

    // 渲染设置控件
    renderPicker("accentPalette", "accentPick", accent);
    renderPicker("navPalette", "navPick", followNav ? accent : navAccent);

    const accentPick = document.getElementById("accentPick");
    const navPick = document.getElementById("navPick");
    if (accentPick.dataset.bound) return;
    accentPick.dataset.bound = "1";

    accentPick.addEventListener("input", () => {
      apply(accentPick.value, followNav ? accentPick.value : navAccent, followNav);
      renderPicker("accentPalette", "accentPick", accentPick.value);
      if (followNav) {
        document.getElementById("navPick").value = accentPick.value;
        renderPicker("navPalette", "navPick", accentPick.value);
      }
    });

    navPick.addEventListener("input", () => {
      followNav = false;
      apply(accent, navPick.value, false);
      renderPicker("navPalette", "navPick", navPick.value);
    });

    document.getElementById("btnAccentReset").addEventListener("click", async () => {
      const c = normalize(await extractFromBg());
      apply(c, followNav ? c : navAccent, followNav);
      document.getElementById("accentPick").value = c;
      renderPicker("accentPalette", "accentPick", c);
      if (followNav) {
        document.getElementById("navPick").value = c;
        renderPicker("navPalette", "navPick", c);
      }
      UI.toast("已恢复为背景搭配色");
    });

    document.getElementById("btnNavReset").addEventListener("click", () => {
      followNav = true;
      apply(accent, accent, true);
      document.getElementById("navPick").value = accent;
      renderPicker("navPalette", "navPick", accent);
      UI.toast("导航色已跟随强调色");
    });
  }

  /* 渲染色板并联动取色器 */
  function renderPicker(paletteId, pickId, current) {
    const palette = document.getElementById(paletteId);
    const pick = document.getElementById(pickId);
    if (!palette || !pick) return;
    const cur = normalize(current);
    palette.innerHTML = PRESETS.map((c) =>
      `<div class="swatch ${c === cur ? "sel" : ""}" data-c="${c}" style="background:${c}"></div>`).join("");
    pick.value = cur;

    palette.onclick = (e) => {
      const s = e.target.closest(".swatch");
      if (!s) return;
      pick.value = s.dataset.c;
      pick.dispatchEvent(new Event("input"));
    };
  }

  return { init, apply, extractFromBg };
})();
