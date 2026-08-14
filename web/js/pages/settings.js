/* ═══════════════════════════════════════════
   外观设置 · 主题强调色（关于页小面板）
   默认从背景图自动提取搭配色，可自定义并持久化，导航选中色跟随强调色
   ═══════════════════════════════════════════ */

const Settings = (() => {
  const KEY = "talent_theme";
  const PRESETS = ["#8b5cf6", "#ec4899", "#22d3ee", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#6366f1"];

  let accent = "#8b5cf6";

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

  /* 应用主题到 CSS 变量 */
  function apply(ac) {
    accent = normalize(ac);
    const root = document.documentElement.style;
    root.setProperty("--accent", accent);
    root.setProperty("--accent2", `color-mix(in srgb, ${accent}, #ffffff 30%)`);
    root.setProperty("--nav-accent", accent);
    try {
      localStorage.setItem(KEY, JSON.stringify({ accent }));
    } catch (e) { /* ignore */ }
  }

  /* 初始化：读持久化配置，无则从背景图提取；渲染关于页外观面板 */
  async function init() {
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem(KEY));
    } catch (e) { /* ignore */ }

    if (saved && saved.accent) {
      apply(saved.accent);
    } else {
      apply(await extractFromBg());
    }

    renderPicker();

    const pick = document.getElementById("accentPick");
    const reset = document.getElementById("btnAccentReset");
    if (!pick || pick.dataset.bound) return;
    pick.dataset.bound = "1";

    pick.addEventListener("input", () => {
      apply(pick.value);
      renderPicker();
    });

    reset.addEventListener("click", async () => {
      const c = normalize(await extractFromBg());
      apply(c);
      renderPicker();
      UI.toast("已恢复为背景搭配色");
    });
  }

  /* 渲染关于页色板并联动取色器 */
  function renderPicker() {
    const palette = document.getElementById("accentPalette");
    const pick = document.getElementById("accentPick");
    if (!palette || !pick) return;
    const cur = accent;
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
