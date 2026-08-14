/* ═══════════════════════════════════════════
   Talent 工具箱 · 主入口
   页面切换 / 标题栏 / 拖拽 / 背景装饰 / 错误上报
   ═══════════════════════════════════════════ */

(() => {
  const PAGES = {
    dashboard: Dashboard,
    monitor: Monitor,
    tools: Tools,
    apps: Apps,
    about: About,
    settings: Settings,
  };

  let current = "dashboard";
  const pageEls = document.querySelectorAll(".page");
  const navItems = document.querySelectorAll(".nav-item");

  /* ── 页面切换 ── */
  function switchPage(name) {
    if (!PAGES[name] || name === current) return;
    if (PAGES[current] && PAGES[current].destroy) PAGES[current].destroy();
    current = name;

    pageEls.forEach((el) => el.classList.remove("active"));
    document.getElementById("page-" + name).classList.add("active");
    navItems.forEach((n) => n.classList.toggle("active", n.dataset.page === name));
    document.querySelector(".main").scrollTop = 0;

    if (PAGES[name].init) PAGES[name].init();
  }

  navItems.forEach((n) => {
    n.addEventListener("click", () => switchPage(n.dataset.page));
  });
  document.querySelectorAll("[data-jump]").forEach((b) => {
    b.addEventListener("click", () => switchPage(b.dataset.jump));
  });

  /* ── 标题栏按钮 ── */
  document.getElementById("btnMin").addEventListener("click", () => {
    if (API.hasNative) API.minimize();
  });
  document.getElementById("btnClose").addEventListener("click", () => {
    if (API.hasNative) API.close();
    else window.close();
  });

  /* ── frameless 窗口拖拽 ── */
  (function bindDrag() {
    const area = document.getElementById("dragArea");
    if (!API.hasNative) return;

    let rafId = null;
    let startX = 0, startY = 0, winX = 0, winY = 0, dragging = false;

    area.addEventListener("mousedown", (e) => {
      if (e.button !== 0) return;
      dragging = true;
      startX = e.screenX;
      startY = e.screenY;
      winX = e.screenX - e.clientX;
      winY = e.screenY - e.clientY;
    });
    window.addEventListener("mousemove", (e) => {
      if (!dragging) return;
      if (rafId) return;
      rafId = requestAnimationFrame(() => {
        rafId = null;
        API.moveTo(winX + e.screenX - startX, winY + e.screenY - startY);
      });
    });
    window.addEventListener("mouseup", () => {
      dragging = false;
      if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    });
  })();

  /* ── 前端错误上报（桌面版写入日志文件，便于排查） ── */
  window.addEventListener("error", (e) => {
    if (API.hasNative) API.log("error", `[${e.message}] @ ${e.filename}:${e.lineno}`);
  });
  window.addEventListener("unhandledrejection", (e) => {
    if (API.hasNative) API.log("error", "unhandledrejection: " + String(e.reason));
  });

  /* ── 桥接就绪：重新初始化当前页，切换到真实数据源 ── */
  window.TalentOnBridgeReady = () => {
    if (PAGES[current] && PAGES[current].destroy) PAGES[current].destroy();
    if (PAGES[current] && PAGES[current].init) PAGES[current].init();
  };

  /* ── 启动：先应用主题，再初始化首页 ── */
  Settings.init().then(() => {
    Dashboard.init();
  });
})();
