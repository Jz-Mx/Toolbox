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
  let uptimeText = "";
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
      uptimeText = UI.dur(p.uptime);
      updateUptimeOs();
    } catch (e) {
      /* 忽略单次失败 */
    }
  }

  /* 系统信息行：系统版本 · 启动时间 */
  function updateUptimeOs() {
    const el = document.getElementById("dUptimeOs");
    if (!el) return;
    el.textContent = [osText, uptimeText ? "启动 " + uptimeText : ""].filter(Boolean).join(" · ");
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
      document.getElementById("dGpu").textContent = String(s.gpu || "--").split(" / ")[0];
      updateUptimeOs();
      // 全分区用量："C: 64 GB / 117 GB · D: 230 GB / 1024 GB"
      if (s.disks && s.disks.length) {
        document.getElementById("dDiskUse").textContent = s.disks
          .map((d) => `${d.mount.replace(":\\", "")} ${UI.gb(d.used)} / ${UI.gb(d.total)}`)
          .join("  ·  ");
      }
      // 分区文字未超过系统信息时：分区与系统信息互换（分区提前）
      const dUse = document.getElementById("dDiskUse");
      const dSys = document.getElementById("dUptimeOs");
      if (dUse && dSys && dUse.textContent.length > 0 && dUse.textContent.length <= osText.length) {
        const a = dUse.closest(".d-item");
        const b = dSys.closest(".d-item");
        if (a && b && a !== b) {
          b.parentElement.insertBefore(a, b);
        }
      }
      // 睿频探测未完成时 8 秒后重试
      if (!cpuMax) {
        clearTimeout(staticRetry);
        staticRetry = setTimeout(loadStatic, 8000);
      }
    } catch (e) { /* ignore */ }
  }

  /* 天气图标（苹果 SF Symbols 风格线条 SVG） */
  const W_ICONS = {
    sun: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M18.7 5.3l-1.8 1.8M7.1 16.9l-1.8 1.8"/></svg>',
    sunCloud: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="3.2"/><path d="M8 2.5V4.5M8 11.5v2M2.5 8H4.5M11.5 8h2M4 4l1.4 1.4M10.6 10.6L12 12"/><path d="M17 19H8.5a3.5 3.5 0 01.3-7 5 5 0 019.6 1.2A2.8 2.8 0 0117 19z"/></svg>',
    cloud: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H8a4 4 0 01-.4-8A5.5 5.5 0 0118.9 12 3.2 3.2 0 0117.5 19z"/></svg>',
    fog: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 15H8a4 4 0 01-.4-8A5.5 5.5 0 0118.9 8"/><path d="M3 18h12M5 21h10"/></svg>',
    rain: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 15H8a4 4 0 01-.4-8A5.5 5.5 0 0118.9 8 3.2 3.2 0 0117.5 15z"/><path d="M9 19l-1 2.5M13.5 19l-1 2.5M18 19l-1 2.5"/></svg>',
    snow: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 15H8a4 4 0 01-.4-8A5.5 5.5 0 0118.9 8 3.2 3.2 0 0117.5 15z"/><path d="M11 19v3M11 20.5l-1.5-1M11 20.5l1.5-1M15.5 19v3M15.5 20.5l-1.5-1M15.5 20.5l1.5-1"/></svg>',
    storm: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 15H8a4 4 0 01-.4-8A5.5 5.5 0 0118.9 8 3.2 3.2 0 0117.5 15z"/><path d="M12.5 16l-2.5 4.5h3l-1.5 3.5"/></svg>',
  };

  function weatherIcon(code) {
    if (code === 0) return W_ICONS.sun;
    if (code === 1 || code === 2) return W_ICONS.sunCloud;
    if (code === 3 || code == null) return W_ICONS.cloud;
    if (code >= 45 && code <= 48) return W_ICONS.fog;
    if (code >= 51 && code <= 67) return W_ICONS.rain;
    if (code >= 71 && code <= 77) return W_ICONS.snow;
    if (code >= 80 && code <= 82) return W_ICONS.rain;
    if (code >= 85 && code <= 86) return W_ICONS.snow;
    if (code >= 95) return W_ICONS.storm;
    return W_ICONS.cloud;
  }

  /* 天气显示（hero 右侧，失败 60 秒后自动重试） */
  let weatherTimer = null;

  async function loadWeather() {
    try {
      const w = await API.getWeather();
      const el = document.getElementById("heroWeather");
      if (el && w) {
        const parts = [w.city, w.temp != null ? w.temp + "°" : "--", w.desc];
        el.innerHTML = weatherIcon(w.code) + '<span class="hw-text">' + parts.filter(Boolean).join(" · ") + "</span>";
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

  /* 每日提问：高中数学题（含答案），答对点亮星星；双击重置；0 点自动换题 */
  const DAILY_QUESTIONS = [
    { q: "求函数 f(x) = x² - 4x + 3 的最小值。", a: ["-1"] },
    { q: "已知 sinα = 3/5（α 为锐角），求 cosα 的值。", a: ["4/5", "0.8"] },
    { q: "等差数列 {aₙ} 中 a₁=2，d=3，求 a₁₀。", a: ["29"] },
    { q: "等比数列 {bₙ} 中 b₁=1，q=2，求前 6 项和。", a: ["63"] },
    { q: "解不等式 x² - 5x + 6 < 0。", a: ["2<x<3", "（2,3）", "(2,3)", "2到3", "2<x 且 x<3"] },
    { q: "求直线 y = 2x + 1 与 x 轴的交点坐标。", a: ["-0.5", "-1/2", "(-0.5,0)", "（-0.5,0）"] },
    { q: "圆 x² + y² = 25 上点 (3,4) 处切线斜率。", a: ["-3/4", "-0.75"] },
    { q: "已知向量 a=(1,2)，b=(3,-1)，求 a·b。", a: ["1"] },
    { q: "函数 y = 2sin(x + π/6) 的最小正周期？", a: ["2π", "2pi", "6.28"] },
    { q: "求 log₂8 + log₃9 的值。", a: ["5"] },
    { q: "从 5 名同学中选 2 名，有多少种选法？", a: ["10"] },
    { q: "掷骰子两次，点数之和为 7 的概率？", a: ["1/6", "6/36", "0.1667", "0.17"] },
    { q: "已知 f(x) = x³ - 3x，求 f'(x)。", a: ["3x²-3", "3x^2-3", "3x2-3"] },
    { q: "双曲线 x²/9 - y²/16 = 1 的渐近线方程？", a: ["y=±4x/3", "4x/3", "y=4x/3"] },
    { q: "求 ∫₀¹ 3x² dx 的值。", a: ["1"] },
    { q: "△ABC 中 a=3，b=4，∠C=90°，求 c。", a: ["5"] },
    { q: "tanθ = 2，求 (sinθ+cosθ)/(sinθ-cosθ)。", a: ["3"] },
    { q: "函数 f(x) = x³ - 3x + 1 的单调递减区间？", a: ["(-1,1)", "（-1,1）", "-1<x<1", "(-1, 1)"] },
    { q: "排列数 A₅³ 等于多少？", a: ["60"] },
    { q: "求椭圆 x²/25 + y²/9 = 1 的焦距。", a: ["8"] },
    { q: "log₁₀100 + log₁₀1000 等于多少？", a: ["5"] },
    { q: "已知复数 z = 2 + 3i，求 |z|。", a: ["√13", "sqrt13", "3.61", "3.6"] },
    { q: "抛物线 y² = 8x 的焦点坐标是？", a: ["(2,0)", "（2,0）", "2"] },
    { q: "求函数 y = 1/(x² + 1) 的最大值。", a: ["1"] },
  ];

  function normAns(s) {
    return String(s).toLowerCase()
      .replace(/[，。、（）()]/g, " ")
      .replace(/×/g, "*").replace(/÷/g, "/").replace(/－/g, "-")
      .replace(/π/g, "pi").replace(/√/g, "sqrt")
      .replace(/\s+/g, "");
  }

  function checkAnswer(input, answers) {
    const n = normAns(input);
    if (!n) return false;
    for (const a of answers) {
      const na = normAns(a);
      if (na === n) return true;
      const f1 = parseFloat(n), f2 = parseFloat(na);
      if (!isNaN(f1) && !isNaN(f2) && Math.abs(f1 - f2) < 0.05) return true;
    }
    return false;
  }

  const DAILY_KEY = "talent_daily";

  function dailyState() {
    try { return JSON.parse(localStorage.getItem(DAILY_KEY)) || {}; }
    catch (e) { return {}; }
  }
  function dailySave(st) {
    try { localStorage.setItem(DAILY_KEY, JSON.stringify(st)); } catch (e) { /* ignore */ }
  }

  function todayStr() {
    return new Date().toISOString().slice(0, 10);
  }

  function pickIdx(dateStr, offset) {
    let seed = 0;
    for (const ch of dateStr) seed = (seed * 31 + ch.charCodeAt(0)) % 100000;
    return (seed + offset) % DAILY_QUESTIONS.length;
  }

  function renderDaily(st) {
    const el = document.getElementById("dailyQ");
    const btn = document.getElementById("dailyCheck");
    if (!el || !btn) return;
    el.textContent = DAILY_QUESTIONS[st.idx].q;
    btn.classList.toggle("done", !!st.done);
    if (st.done) {
      btn.style.animation = "none";
      void btn.offsetWidth;
      btn.style.animation = "";
    }
  }

  function loadDaily() {
    const btn = document.getElementById("dailyCheck");
    const input = document.getElementById("dailyInput");
    if (!btn || !input) return;

    const today = todayStr();
    let st = dailyState();
    if (st.date !== today) {
      st = { date: today, idx: pickIdx(today, 0), done: false };
      dailySave(st);
    }
    renderDaily(st);

    if (btn.dataset.bound) return;
    btn.dataset.bound = "1";

    // 发送答案：答对点亮星星（Q弹动画）
    const submit = () => {
      const val = input.value.trim();
      if (!val) return;
      const cur = dailyState();
      if (cur.date !== todayStr() || cur.done) { input.value = ""; return; }
      if (checkAnswer(val, DAILY_QUESTIONS[cur.idx].a)) {
        cur.done = true;
        dailySave(cur);
        renderDaily(cur);
        UI.toast("答对啦！星星已点亮 ✦");
      } else {
        UI.toast("再想想哦，答案好像不对～");
      }
      input.value = "";
    };
    document.getElementById("dailySend").addEventListener("click", submit);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") submit(); });

    // 双击星星：重置题目（换一道 + 未点亮）
    btn.addEventListener("dblclick", () => {
      const today = todayStr();
      const stNow = dailyState();
      const resetIdx = pickIdx(today, (stNow.idx || 0) + 1);
      dailySave({ date: today, idx: resetIdx, done: false });
      renderDaily({ date: today, idx: resetIdx, done: false });
      UI.toast("已重置题目");
    });

    // 每天 0 点自动刷新
    setInterval(() => {
      const stNow = dailyState();
      if (stNow.date !== todayStr()) {
        const t = todayStr();
        dailySave({ date: t, idx: pickIdx(t, 0), done: false });
        renderDaily({ date: t, idx: pickIdx(t, 0), done: false });
      }
    }, 60000);
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
    loadDaily();

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
