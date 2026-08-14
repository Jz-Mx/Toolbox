/* ═══════════════════════════════════════════
   首页 · 仪表盘
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

      UI.setRing("ringCpuFg", p.cpu, UI.pctColor(p.cpu));
      document.getElementById("cpuNum").textContent = Math.round(p.cpu);
      UI.setRing("ringMemFg", p.mem, UI.pctColor(p.mem));
      document.getElementById("memNum").textContent = Math.round(p.mem);

      document.getElementById("diskPct").textContent = Math.round(p.disk_pct) + "%";
      document.getElementById("diskBar").style.width = p.disk_pct + "%";
      document.getElementById("diskUsed").textContent = API.fmtGB(p.disk_used);
      document.getElementById("diskTotal").textContent = "共 " + API.fmtGB(p.disk_total);

      document.getElementById("netDown").textContent = API.fmtSpeed(p.net_down);
      document.getElementById("netUp").textContent = API.fmtSpeed(p.net_up);
      const total = p.net_down + p.net_up;
      if (lastNet === null || Math.abs(total - lastNet) > 512) {
        lastNet = total;
        document.getElementById("netSpeed").textContent = API.fmtSpeed(total);
      }

      // hero 参数行
      document.getElementById("hpCpu").textContent = Math.round(p.cpu) + "%";
      document.getElementById("hpMem").textContent = Math.round(p.mem) + "%";
      document.getElementById("hpDisk").textContent = Math.round(p.disk_pct) + "%";
      document.getElementById("hpNet").textContent = API.fmtSpeed(total);
    } catch (e) {
      /* 忽略单次失败 */
    }
  }

  async function refreshPing() {
    try {
      const r = await API.ping();
      const el = document.getElementById("netPing");
      if (el && r && r.ms != null) el.textContent = `延迟 ${r.ms} ms`;
    } catch (e) { /* ignore */ }
  }

  function init() {
    document.getElementById("heroGreet").textContent = greet();
    document.getElementById("heroQuote").textContent =
      "「" + QUOTES[Math.floor(Math.random() * QUOTES.length)] + "」";
    tickClock();
    refreshPerf();
    refreshPing();

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
