/* ═══════════════════════════════════════════
   监控页 · 实时折线图 + 系统信息
   ═══════════════════════════════════════════ */

const Monitor = (() => {
  const MAX = 90; // 保留 90 个采样点
  const series = {
    cpu: { data: [], color: "#8b5cf6", fill: "rgba(139,92,246,0.25)" },
    mem: { data: [], color: "#ec4899", fill: "rgba(236,72,153,0.25)" },
    net: { down: [], up: [], colorDown: "#22d3ee", colorUp: "#f472b6" },
  };

  let timer = null;
  let bootTime = null;

  function drawLine(canvas, arr, color, fillColor, maxVal, minVal = 0, reset = true) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (reset) {
      canvas.width = w * dpr;
      canvas.height = h * dpr;
    }
    const ctx = canvas.getContext("2d");
    if (reset) {
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      // 水平网格参考线（25% / 50% / 75%）
      ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 6]);
      for (let g = 1; g <= 3; g++) {
        const gy = (h * g) / 4;
        ctx.beginPath();
        ctx.moveTo(0, gy);
        ctx.lineTo(w, gy);
        ctx.stroke();
      }
      ctx.setLineDash([]);
    }

    const pad = 4;
    const range = (maxVal - minVal) || 1;
    const step = (w - pad * 2) / (MAX - 1);

    if (arr.length < 2) return;

    ctx.beginPath();
    arr.forEach((v, i) => {
      const x = pad + i * step;
      const y = h - pad - ((v - minVal) / range) * (h - pad * 2);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    if (fillColor) {
      const last = arr.length - 1;
      const xLast = pad + last * step;
      const xFirst = pad;
      ctx.lineTo(xLast, h - pad);
      ctx.lineTo(xFirst, h - pad);
      ctx.closePath();
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, fillColor);
      grad.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.beginPath();
      arr.forEach((v, i) => {
        const x = pad + i * step;
        const y = h - pad - ((v - minVal) / range) * (h - pad * 2);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.2;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.shadowColor = color;
    ctx.shadowBlur = 8;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  /* 动态 Y 轴范围：让曲线铺满图表高度（高度一致） */
  function autoRange(arr) {
    if (!arr.length) return { lo: 0, hi: 100 };
    const min = Math.min(...arr);
    const max = Math.max(...arr);
    let lo = Math.floor(min / 10) * 10;
    let hi = Math.ceil(max / 10) * 10;
    if (lo < 0) lo = 0;
    if (hi - lo < 10) hi = lo + 10;
    if (hi > 100) hi = 100;
    return { lo, hi };
  }

  function renderCharts() {
    // CPU / 内存各占一图，Y 轴动态范围使曲线高度一致
    const cpuR = autoRange(series.cpu.data);
    drawLine(document.getElementById("chartCpu"), series.cpu.data, series.cpu.color, series.cpu.fill, cpuR.hi, cpuR.lo, true);
    const memR = autoRange(series.mem.data);
    drawLine(document.getElementById("chartMem"), series.mem.data, series.mem.color, series.mem.fill, memR.hi, memR.lo, true);
    const maxNet = Math.max(...series.net.down, ...series.net.up, 1);
    const c = document.getElementById("chartNet");
    // 下行线（带填充），随后叠加上行线（不重置画布、不清屏）
    drawLine(c, series.net.down, series.net.colorDown, "rgba(34,211,238,0.18)", maxNet, 0, true);
    drawLine(c, series.net.up, series.net.colorUp, null, maxNet, 0, false);
  }

  async function sample() {
    try {
      const p = await API.getPerf();
      if (!p) return;

      series.cpu.data.push(p.cpu);
      if (series.cpu.data.length > MAX) series.cpu.data.shift();
      series.mem.data.push(p.mem);
      if (series.mem.data.length > MAX) series.mem.data.shift();
      series.net.down.push(p.net_down);
      if (series.net.down.length > MAX) series.net.down.shift();
      series.net.up.push(p.net_up);
      if (series.net.up.length > MAX) series.net.up.shift();

      document.getElementById("cpuNow").textContent = Math.round(p.cpu) + "%";
      document.getElementById("memNow").textContent = Math.round(p.mem) + "%";
      document.getElementById("netNow").textContent =
        "↓ " + API.fmtSpeed(p.net_down) + "  ↑ " + API.fmtSpeed(p.net_up);

      renderCharts();
    } catch (e) { /* ignore */ }
  }

  async function loadSysinfo() {
    try {
      const s = await API.getSysinfo();
      if (!s) return;
      bootTime = s.boot_time;

      const rows = [
        ["操作系统", s.os],
        ["CPU", s.cpu_name],
        ["核心 / 线程", s.cpu_cores + " 核 / " + s.cpu_threads + " 线程"],
        ["内存总量", API.fmtGB(s.mem_total)],
        ["显卡", s.gpu],
        ["主板", s.motherboard],
        ["BIOS", s.bios],
        ["主机名", s.hostname],
        ["开机时长", bootTime ? UI.dur(Date.now() / 1000 - bootTime) : "--"],
      ];
      document.getElementById("sysinfoBody").innerHTML = rows
        .map(([k, v]) => `<tr><td>${UI.esc(k)}</td><td>${UI.esc(v || "--")}</td></tr>`)
        .join("");

      const disks = (s.disks || []).map((d) => {
        const pct = Math.round((d.used / d.total) * 100);
        return `
          <div class="disk-item">
            <div class="disk-top"><span>${UI.esc(d.mount)}</span><b>${UI.gb(d.used)} / ${UI.gb(d.total)} · ${pct}%</b></div>
            <div class="bar"><div class="bar-fill" style="width:${pct}%;${pct > 90 ? 'background:linear-gradient(135deg,#f43f5e,#e11d48);' : ''}"></div></div>
          </div>`;
      });
      document.getElementById("diskList").innerHTML = disks.join("") || '<div class="proc-empty">未获取到磁盘信息</div>';
    } catch (e) { /* ignore */ }
  }

  function init() {
    series.cpu.data = [];
    series.mem.data = [];
    series.net.down = [];
    series.net.up = [];
    loadSysinfo();
    sample();
    clearInterval(timer);
    timer = setInterval(sample, 1000);
  }

  function destroy() {
    clearInterval(timer);
    timer = null;
  }

  return { init, destroy };
})();
