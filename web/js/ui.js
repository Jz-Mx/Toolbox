/* ═══════════════════════════════════════════
   Talent 工具箱 · 通用 UI 工具
   ═══════════════════════════════════════════ */

const UI = (() => {
  let toastTimer = null;

  /* Toast 轻提示（Q弹入场） */
  function toast(msg, ms = 2200) {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), ms);
  }

  /* 数字格式化：GB */
  function gb(bytes) {
    if (bytes == null || isNaN(bytes)) return "--";
    const g = bytes / 1024 ** 3;
    return g >= 100 ? g.toFixed(0) + " GB" : g.toFixed(1) + " GB";
  }

  /* 秒 → 人类可读时长 */
  function dur(sec) {
    sec = Math.max(0, Math.floor(sec));
    const d = Math.floor(sec / 86400);
    const h = Math.floor((sec % 86400) / 3600);
    const m = Math.floor((sec % 3600) / 60);
    if (d > 0) return `${d} 天 ${h} 小时`;
    if (h > 0) return `${h} 小时 ${m} 分`;
    return `${m} 分 ${sec % 60} 秒`;
  }

  /* SVG 环形图进度（0-100） */
  function setRing(ringFgId, pct, color) {
    const el = document.getElementById(ringFgId);
    if (!el) return;
    const c = 2 * Math.PI * 40; // r=40
    el.style.strokeDasharray = c;
    el.style.strokeDashoffset = c * (1 - Math.min(100, Math.max(0, pct)) / 100);
    if (color) el.style.stroke = color;
  }

  /* 颜色渐变插值（用于环形图随占用变化） */
  function pctColor(pct) {
    const stops = [
      [34, 211, 238],   // 青
      [139, 92, 246],   // 紫
      [236, 72, 153],   // 粉
      [244, 63, 94],    // 红
    ];
    const t = Math.min(1, Math.max(0, pct / 100)) * (stops.length - 1);
    const i = Math.floor(t);
    const f = t - i;
    const a = stops[i], b = stops[Math.min(i + 1, stops.length - 1)];
    const rgb = a.map((v, k) => Math.round(v + (b[k] - v) * f));
    return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
  }

  /* 复制文本到剪贴板 */
  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        return true;
      } catch (e2) {
        return false;
      }
    }
  }

  /* 带小圆点的脉冲按钮（工具操作反馈） */
  function pulseBtn(btn, on) {
    if (!btn) return;
    btn.style.transition = "transform 0.35s cubic-bezier(0.34,1.56,0.64,1)";
    if (on) btn.style.transform = "scale(1.06)";
    else btn.style.transform = "scale(1)";
  }

  /* HTML 转义（进程名/路径等外部数据插入 innerHTML 前必须转义） */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  return { toast, gb, dur, setRing, pctColor, copyText, pulseBtn, esc };
})();
