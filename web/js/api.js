/* ═══════════════════════════════════════════
   Talent 工具箱 · API 桥接层
   - 桌面版（pywebview）：调用 Python 后端真实数据
   - 浏览器版（直接打开 index.html）：自动降级为模拟数据，方便预览
   注意：pywebview 6 的 window.pywebview 在页面脚本执行后才注入，
   因此必须等 pywebviewready 事件后再绑定原生桥接。
   ═══════════════════════════════════════════ */

const API = (() => {
  let native = null;

  const fmtGB = (bytes) => {
    if (bytes === null || bytes === undefined || isNaN(bytes)) return "--";
    const gb = bytes / (1024 ** 3);
    return gb >= 100 ? gb.toFixed(0) + " GB" : gb.toFixed(1) + " GB";
  };
  const fmtSpeed = (bps) => {
    if (bps === null || bps === undefined || isNaN(bps)) return "--";
    if (bps < 1024) return bps.toFixed(0) + " B/s";
    if (bps < 1024 * 1024) return (bps / 1024).toFixed(1) + " KB/s";
    if (bps < 1024 * 1024 * 1024) return (bps / 1024 / 1024).toFixed(2) + " MB/s";
    return (bps / 1024 / 1024 / 1024).toFixed(2) + " GB/s";
  };

  /* ── 浏览器演示模式：模拟数据 ── */
  const mock = {
    get_perf: async () => ({
      cpu: Math.round(18 + Math.random() * 42),
      mem: Math.round(45 + Math.random() * 25),
      disk_pct: 63,
      disk_used: 428.5 * 1024 ** 3,
      disk_total: 680 * 1024 ** 3,
      net_down: 2.4 * 1024 * 1024 + Math.random() * 1024 * 1024,
      net_up: 0.3 * 1024 * 1024 + Math.random() * 200 * 1024,
      uptime: 5.2 * 3600,
    }),
    get_sysinfo: async () => ({
      os: "Windows 11（演示模式）",
      cpu_name: "AMD Ryzen 7 5800X（演示）",
      cpu_cores: 8,
      cpu_threads: 16,
      mem_total: 32 * 1024 ** 3,
      gpu: "NVIDIA GeForce RTX 3070（演示）",
      motherboard: "ASUS ROG STRIX B550（演示）",
      bios: "American Megatrends 2407（演示）",
      hostname: "TALENT-PC",
      boot_time: Date.now() / 1000 - 5.2 * 3600,
      disks: [
        { mount: "C:", total: 680 * 1024 ** 3, used: 428.5 * 1024 ** 3 },
        { mount: "D:", total: 1024 * 1024 ** 3, used: 500 * 1024 ** 3 },
      ],
    }),
    clean_memory: async () => {
      const before = 60 + Math.random() * 15;
      const after = before - (5 + Math.random() * 8);
      return { before, after, freed: before - after };
    },
    scan_temp: async () => {
      const size = (0.5 + Math.random() * 2.5) * 1024 ** 3;
      const count = Math.round(800 + Math.random() * 5000);
      return { path: "C:\\Users\\Talent\\AppData\\Local\\Temp（演示）", size, count };
    },
    clean_temp: async () => ({
      freed: (0.4 + Math.random() * 2) * 1024 ** 3,
    }),
    get_top_processes: async () => [
      { pid: 1234, name: "chrome.exe", cpu: 6.5, mem_mb: 1520 },
      { pid: 5678, name: "Talent.exe", cpu: 3.2, mem_mb: 260 },
      { pid: 9012, name: "explorer.exe", cpu: 1.1, mem_mb: 180 },
    ],
    kill_process: async (pid) => ({ ok: true, name: "demo.exe" }),
    get_startup_items: async () => [
      { name: "OneDrive", command: "C:\\Users\\Talent\\AppData\\Local\\Microsoft\\OneDrive\\OneDrive.exe", source: "HKCU\\Run" },
      { name: "微信", command: "D:\\WeChat\\WeChat.exe -autorun", source: "HKCU\\Run" },
    ],
    ping: async () => ({ ms: Math.round(15 + Math.random() * 40) }),
  };

  /* 绑定原生桥接（pywebview 注入完成后调用） */
  function bind() {
    if (window.pywebview && window.pywebview.api) {
      native = window.pywebview.api;
      return true;
    }
    return false;
  }
  // 立即尝试一次（浏览器直接打开时为 false；pywebview 下由 pywebviewready 事件触发）
  bind();
  window.addEventListener("pywebviewready", () => {
    if (bind()) {
      console.log("[Talent] 已连接桌面后端");
      // 通知主程序重新初始化当前页面，切换到真实数据
      if (window.TalentOnBridgeReady) window.TalentOnBridgeReady();
    }
  });

  async function call(name, ...args) {
    try {
      if (native && typeof native[name] === "function") {
        return await native[name](...args);
      }
      const fn = mock[name];
      if (fn) return await fn(...args);
      throw new Error("API 不存在: " + name);
    } catch (e) {
      console.error("[API]", name, e);
      throw e;
    }
  }

  return {
    get hasNative() { return !!native; },
    bind,
    call,
    getPerf: () => call("get_perf"),
    getSysinfo: () => call("get_sysinfo"),
    cleanMemory: () => call("clean_memory"),
    scanTemp: () => call("scan_temp"),
    cleanTemp: () => call("clean_temp"),
    getTopProcesses: () => call("get_top_processes"),
    killProcess: (pid) => call("kill_process", pid),
    getStartupItems: () => call("get_startup_items"),
    ping: () => call("ping"),
    getWeather: () => call("get_weather"),
    log: (level, msg) => call("log", level, msg),
    moveTo: (x, y) => call("move_to", x, y),
    minimize: () => call("minimize"),
    close: () => call("close"),
    fmtGB,
    fmtSpeed,
  };
})();
