/* ═══════════════════════════════════════════
   关于页 · 开发者信息
   ═══════════════════════════════════════════ */

const About = (() => {
  function init() {
    const qq = document.getElementById("qqText");
    if (qq.dataset.bound) return; // 防止页面切换/桥接就绪时重复绑定
    qq.dataset.bound = "1";
    qq.addEventListener("click", async (e) => {
      const ok = await UI.copyText(e.target.textContent.trim());
      UI.toast(ok ? "QQ 已复制" : "复制失败");
    });
    // data-copy 按钮：复制对应元素文本
    document.querySelectorAll("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const src = document.getElementById(btn.dataset.copy);
        if (!src) return;
        const ok = await UI.copyText(src.textContent.trim());
        UI.toast(ok ? `已复制 ${src.textContent.trim()}` : "复制失败");
      });
    });
  }
  return { init };
})();
