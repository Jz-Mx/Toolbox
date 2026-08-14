/* ═══════════════════════════════════════════
   首页 · 仪表盘（简洁版：hero + 实时参数行）
   ═══════════════════════════════════════════ */

const Dashboard = (() => {
  const QUOTES = [
    "今天的风儿甚是喧嚣呢～",
    "不管多晚，都会有人等你回家。",
    "只要心怀梦想，哪里都是星辰大海。",
    "与其仰望星空，不如脚踏实地。",
    "所谓奇迹，不过是努力的另一个名字。",
    "世界很大，幸好有你。",
    "今天的你，也要元气满满哦！",
    "温柔的人，运气都不会太差。",
    "慢慢来，比较快。",
    "愿你被这个世界温柔以待。",
    "梦想还是要有的，万一实现了呢。",
    "每一次努力，都是幸运的伏笔。",
    "生活明朗，万物可爱。",
    "你认真起来的样子，闪闪发光。",
    "别怕，天塌下来有高个子顶着。",
    "所有的好运，都藏在你的努力里。",
    "保持热爱，奔赴山海。",
    "心之所向，素履以往。",
    "此心安处是吾乡。",
    "既然选择了远方，便只顾风雨兼程。",
  ];

  let perfTimer = null;
  let pingTimer = null;
  let lastNet = null;

  function greet() {
    const h = new Date().getHours();
    if (h < 5) return "夜深了，要注意休息哦";
    if (h < 9) return "早上好呀";
    if (h < 12) return "上午好";
    if (h < 14) return "中午好，吃饭了吗";
    if (h < 18) return "下午好";
    if (h < 22) return "晚上好";
    return "夜深了，要注意休息哦";
  }

  function tickClock() {
    const now = new Date();
    const p = (n) => String(n).padStart(2, "0");
    document.getElementById("heroClock").textContent =
      `${p(now.getHours())}:${p(now.getMinutes())}:${p(now.getSeconds())}`;
    const week = "日一二三四五六"[now.getDay()];
    document.getElementById("heroDate").textContent =
      `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 星期${week}`;
  }

  async function refreshPerf() {
    try {
      const p = await API.getPerf();
      if (!p) return;

      const total = p.net_down + p.net_up;
      if (lastNet === null || Math.abs(total - lastNet) > 512) {
        lastNet = total;
      }

      // hero 参数行
      document.getElementById("hpCpu").textContent = Math.round(p.cpu) + "%";
      document.getElementById("hpMem").textContent = Math.round(p.mem) + "%";
      document.getElementById("hpDisk").textContent = Math.round(p.disk_pct) + "%";
      document.getElementById("hpNet").textContent = API.fmtSpeed(total);

      // 系统详情卡
      document.getElementById("dCpu").textContent = Math.round(p.cpu) + "%";
      document.getElementById("dMem").textContent = Math.round(p.mem) + "%";
      document.getElementById("dMemUse").textContent =
        (p.mem_used != null ? UI.gb(p.mem_used) + " / " : "") + UI.gb(p.mem_total || 0);
      document.getElementById("dDisk").textContent = Math.round(p.disk_pct) + "%";
      document.getElementById("dDiskUse").textContent = UI.gb(p.disk_used) + " / " + UI.gb(p.disk_total);
      document.getElementById("dDown").textContent = API.fmtSpeed(p.net_down);
      document.getElementById("dUp").textContent = API.fmtSpeed(p.net_up);
      document.getElementById("dUptime").textContent = UI.dur(p.uptime);
    } catch (e) {
      /* 忽略单次失败 */
    }
  }

  async function refreshPing() {
    try {
      const r = await API.ping();
      if (r && r.ms != null) {
        document.getElementById("hpPing").textContent = r.ms + " ms";
        document.getElementById("dPing").textContent = r.ms + " ms";
      }
    } catch (e) { /* ignore */ }
  }

  /* 一次性加载静态系统信息 */
  async function loadStatic() {
    try {
      const s = await API.getSysinfo();
      if (!s) return;
      document.getElementById("dCores").textContent =
        (s.cpu_cores || "?") + " 核 / " + (s.cpu_threads || "?") + " 线程";
      document.getElementById("dOs").textContent = String(s.os || "--").replace(/^Windows-(\d+)-[\d.]+-SP\d+.*$/, "Windows $1");
      document.getElementById("dGpu").textContent = s.gpu || "--";
    } catch (e) { /* ignore */ }
  }

  function init() {
    document.getElementById("heroGreet").textContent = greet();
    document.getElementById("heroQuote").textContent =
      "「" + QUOTES[Math.floor(Math.random() * QUOTES.length)] + "」";
    tickClock();
    refreshPerf();
    refreshPing();
    loadStatic();

    clearInterval(perfTimer);
    perfTimer = setInterval(() => {
      tickClock();
      refreshPerf();
    }, 1000);
    clearInterval(pingTimer);
    pingTimer = setInterval(refreshPing, 10000);
  }

  function destroy() {
    clearInterval(perfTimer);
    perfTimer = null;
    clearInterval(pingTimer);
    pingTimer = null;
  }

  return { init, destroy };
})();
