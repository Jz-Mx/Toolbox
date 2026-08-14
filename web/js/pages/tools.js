/* ═══════════════════════════════════════════
   工具页 · 内存清理 / 临时文件 / 进程 / 启动项
   ═══════════════════════════════════════════ */

const Tools = (() => {
  let scanResult = null;
  let meterTimer = null;

  /* ── 内存清理 ── */
  async function bindMemory() {
    const btn = document.getElementById("btnCleanMem");
    const meter = document.getElementById("memBefore");

    // 显示当前占用
    const updateMeter = async () => {
      try {
        const p = await API.getPerf();
        if (p) meter.textContent = Math.round(p.mem) + " %";
      } catch (e) { /* ignore */ }
    };
    const startMeter = () => {
      updateMeter();
      if (!meterTimer) meterTimer = setInterval(updateMeter, 3000);
    };

    if (btn.dataset.bound) {
      startMeter(); // 重新进入页面时恢复内存占用轮询
      return;
    }
    btn.dataset.bound = "1";
    const res = document.getElementById("memResult");

    startMeter();

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "清理中…";
      res.classList.remove("show", "err");
      try {
        const r = await API.cleanMemory();
        res.classList.add("show");
        res.textContent = `清理完成！释放约 ${r.freed.toFixed(1)}% 内存（${r.before.toFixed(0)}% → ${r.after.toFixed(0)}%）`;
        UI.toast("内存清理完成");
        updateMeter();
      } catch (e) {
        res.classList.add("show", "err");
        res.textContent = "清理失败：" + e.message;
      } finally {
        btn.disabled = false;
        btn.textContent = "开始清理";
      }
    });
  }

  /* ── 临时文件清理 ── */
  async function bindTemp() {
    const btnScan = document.getElementById("btnScanTemp");
    if (btnScan.dataset.bound) return; // 防止页面切换时重复绑定
    btnScan.dataset.bound = "1";
    const btnClean = document.getElementById("btnCleanTemp");
    const sizeEl = document.getElementById("tempSize");
    const res = document.getElementById("tempResult");

    btnScan.addEventListener("click", async () => {
      btnScan.disabled = true;
      btnScan.textContent = "扫描中…";
      sizeEl.textContent = "扫描中";
      res.classList.remove("show", "err");
      try {
        scanResult = await API.scanTemp();
        sizeEl.textContent = UI.gb(scanResult.size) + `（${scanResult.count} 个文件）`;
        btnClean.disabled = false;
        UI.toast("扫描完成，发现 " + scanResult.count + " 个临时文件");
      } catch (e) {
        sizeEl.textContent = "--";
        res.classList.add("show", "err");
        res.textContent = "扫描失败：" + e.message;
      } finally {
        btnScan.disabled = false;
        btnScan.textContent = "重新扫描";
      }
    });

    btnClean.addEventListener("click", async () => {
      if (!scanResult) return;
      if (!confirm(`确定要清理 ${scanResult.count} 个临时文件（${UI.gb(scanResult.size)}）吗？`)) return;
      btnClean.disabled = true;
      btnClean.textContent = "清理中…";
      res.classList.remove("show", "err");
      try {
        const r = await API.cleanTemp();
        res.classList.add("show");
        res.textContent = `清理完成！释放 ${UI.gb(r.freed)} 空间`;
        UI.toast("临时文件清理完成");
        scanResult = null;
        sizeEl.textContent = "--";
        btnClean.disabled = true;
        btnClean.textContent = "清理";
      } catch (e) {
        res.classList.add("show", "err");
        res.textContent = "清理失败：" + e.message;
        btnClean.disabled = false;
        btnClean.textContent = "清理";
      }
    });
  }

  /* ── 进程管理 ── */
  async function loadProcesses() {
    const list = document.getElementById("procList");
    list.innerHTML = '<div class="proc-empty">加载中…</div>';
    try {
      const procs = await API.getTopProcesses();
      if (!procs || !procs.length) {
        list.innerHTML = '<div class="proc-empty">暂无进程数据</div>';
        return;
      }
      list.innerHTML = procs.map((p) => `
        <div class="proc-item">
          <span class="p-name">${UI.esc(p.name)}</span>
          <span class="p-mem">CPU ${p.cpu.toFixed(1)}%</span>
          <span class="p-mem">${p.mem_mb.toFixed(0)} MB</span>
          <button class="p-kill" data-pid="${p.pid}" data-name="${UI.esc(p.name)}">结束</button>
        </div>`).join("");

      list.querySelectorAll(".p-kill").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const pid = btn.dataset.pid;
          const name = btn.dataset.name;
          if (!confirm(`确定要结束进程「${name}」吗？`)) return;
          try {
            const r = await API.killProcess(parseInt(pid, 10));
            UI.toast(r.ok ? `已结束 ${name}` : `无法结束 ${name}`);
            loadProcesses();
          } catch (e) {
            UI.toast("操作失败：" + e.message);
          }
        });
      });
    } catch (e) {
      list.innerHTML = `<div class="proc-empty">加载失败：${UI.esc(e.message)}</div>`;
    }
  }

  async function bindProcesses() {
    const btn = document.getElementById("btnRefreshProc");
    if (btn.dataset.bound) {
      loadProcesses(); // 桥接就绪后重进页面时刷新为真实数据
      return;
    }
    btn.dataset.bound = "1";
    btn.addEventListener("click", loadProcesses);
    loadProcesses();
  }

  /* ── 启动项 ── */
  async function loadStartup() {
    const list = document.getElementById("startupList");
    list.innerHTML = '<div class="proc-empty">加载中…</div>';
    try {
      const items = await API.getStartupItems();
      if (!items || !items.length) {
        list.innerHTML = '<div class="proc-empty">未发现启动项</div>';
        return;
      }
      list.innerHTML = items.map((it) => `
        <div class="proc-item">
          <span class="p-name">${UI.esc(it.name)}</span>
          <span class="p-mem" style="width:auto;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${UI.esc(it.source)}</span>
          <button class="p-kill" data-cmd="${UI.esc(it.command)}" style="background:rgba(34,211,238,0.18);color:#67e8f9;">复制</button>
        </div>`).join("");

      list.querySelectorAll(".p-kill").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const ok = await UI.copyText(btn.dataset.cmd);
          UI.toast(ok ? "路径已复制" : "复制失败");
        });
      });
    } catch (e) {
      list.innerHTML = `<div class="proc-empty">加载失败：${UI.esc(e.message)}</div>`;
    }
  }

  async function bindStartup() {
    const btn = document.getElementById("btnRefreshStartup");
    if (btn.dataset.bound) {
      loadStartup(); // 桥接就绪后重进页面时刷新为真实数据
      return;
    }
    btn.dataset.bound = "1";
    btn.addEventListener("click", loadStartup);
    loadStartup();
  }

  function init() {
    bindMemory();
    bindTemp();
    bindProcesses();
    bindStartup();
  }

  function destroy() {
    clearInterval(meterTimer);
    meterTimer = null;
  }

  return { init, destroy };
})();
