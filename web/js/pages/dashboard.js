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
  let cpuModel = "CPU";
  let cpuMax = 0;
  let coresText = "";
  let memSpecText = "";
  let osText = "";
  let lastDown = 0, lastUp = 0, lastPing = null;

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

      // 系统详情卡：CPU 型号 + 最高频率（睿频，探测失败则用实时值）
      const freqMhz = cpuMax || p.cpu_freq_mhz;
      document.getElementById("dCpu").textContent =
        (freqMhz ? cpuModel + " " + (freqMhz / 1000).toFixed(1) + " GHz" : cpuModel);
      // 核心：静态 + CPU 使用率（如 "10核 / 16线程 25%"）
      document.getElementById("dCores").textContent =
        (coresText ? coresText + "  " : "") + Math.round(p.cpu) + "%";
      // 内存：规格 + 使用率（如 "DDR4 16G 3800MHz 58%"）
      document.getElementById("dMem").textContent =
        (memSpecText ? memSpecText + "  " : "") + Math.round(p.mem) + "%";
      lastDown = p.net_down;
      lastUp = p.net_up;
      updateNet();
    } catch (e) {
      /* 忽略单次失败 */
    }
  }

  /* 系统信息行 */
  function updateUptimeOs() {
    const el = document.getElementById("dUptimeOs");
    if (!el) return;
    el.textContent = osText || "--";
  }

  /* 网络行：↓下行 ↑上行 延迟 */
  function updateNet() {
    const el = document.getElementById("dNet");
    if (!el) return;
    el.textContent =
      "↓" + API.fmtSpeed(lastDown) +
      "  ↑" + API.fmtSpeed(lastUp) +
      (lastPing != null ? "  " + lastPing + "ms" : "");
  }

  async function refreshPing() {
    try {
      const r = await API.ping();
      if (r && r.ms != null) {
        document.getElementById("hpPing").textContent = r.ms + " ms";
        lastPing = r.ms;
        updateNet();
      }
    } catch (e) { /* ignore */ }
  }

  /* 简化 CPU 型号："12th Gen Intel(R) Core(TM) i5-12600KF" → "i5-12600KF" */
  function shortCpu(m) {
    if (!m) return "CPU";
    const re = /(i[3-9]-\d{4,5}[A-Za-z]*|Ryzen\s?\d+\s?\w+\s?\d*[A-Za-z]*|i[3-9]\s?\d{4,5}[A-Za-z]*)/i;
    const mm = String(m).match(re);
    if (mm) return mm[1].replace(/\s+/g, " ");
    const parts = String(m).split(" ").filter(Boolean);
    return parts.length > 1 ? parts.slice(-2).join(" ") : m;
  }

  /* 一次性加载静态系统信息（睿频未就绪时延迟重试） */
  let staticRetry = null;

  async function loadStatic() {
    try {
      const s = await API.getSysinfo();
      if (!s) return;
      cpuModel = shortCpu(s.cpu_model);
      cpuMax = s.cpu_max_mhz || 0;
      coresText = (s.cpu_cores || "?") + "核 / " + (s.cpu_threads || "?") + "线程";
      memSpecText = s.mem_spec || "";
      osText = s.os || "--";
      document.getElementById("dGpu").textContent = s.gpu || "--";
      updateUptimeOs();
      // 全分区用量："C: 64 GB / 117 GB · D: 230 GB / 1024 GB"
      if (s.disks && s.disks.length) {
        document.getElementById("dDiskUse").textContent = s.disks
          .map((d) => `${d.mount.replace(":\\", "")} ${UI.gb(d.used)} / ${UI.gb(d.total)}`)
          .join("  ·  ");
      }
      // 睿频探测未完成时 8 秒后重试
      if (!cpuMax) {
        clearTimeout(staticRetry);
        staticRetry = setTimeout(loadStatic, 8000);
      }
    } catch (e) { /* ignore */ }
  }

  /* 天气显示（hero 右侧），失败 60 秒后自动重试 */
  let weatherTimer = null;

  async function loadWeather() {
    try {
      const w = await API.getWeather();
      const el = document.getElementById("heroWeather");
      if (el && w) {
        const parts = [w.city, w.temp != null ? w.temp + "°" : "--", w.desc];
        el.textContent = parts.filter(Boolean).join(" · ");
      }
      if (!w || w.temp == null) {
        // 降级结果：稍后重试
        clearTimeout(weatherTimer);
        weatherTimer = setTimeout(loadWeather, 60000);
      }
    } catch (e) {
      clearTimeout(weatherTimer);
      weatherTimer = setTimeout(loadWeather, 60000);
    }
  }

  function init() {
    document.getElementById("heroGreet").textContent = greet();
    document.getElementById("heroQuote").textContent =
      "「" + QUOTES[Math.floor(Math.random() * QUOTES.length)] + "」";
    tickClock();
    refreshPerf();
    refreshPing();
    loadStatic();
    loadWeather();

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
    clearTimeout(weatherTimer);
    weatherTimer = null;
    clearTimeout(staticRetry);
    staticRetry = null;
  }

  return { init, destroy };
})();
