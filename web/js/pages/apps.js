/* ═══════════════════════════════════════════
   小玩意页 · 计算器 / 番茄钟 / 颜色 / 字符统计 / 待办
   ═══════════════════════════════════════════ */

const Apps = (() => {
  /* ── 计算器 ── */
  let calcExpr = "";
  let calcShown = false;

  function calcRender() {
    document.getElementById("calcScreen").textContent = calcExpr || "0";
  }

  function bindCalc() {
    const grid = document.getElementById("calcGrid");
    if (grid.dataset.bound) return; // 防止页面切换时重复绑定
    grid.dataset.bound = "1";
    const keys = [
      "C", "(", ")", "÷",
      "7", "8", "9", "×",
      "4", "5", "6", "-",
      "1", "2", "3", "+",
      "0", ".", "⌫", "=",
    ];
    grid.innerHTML = keys.map((k) => {
      let cls = "";
      if ("÷×-+".includes(k)) cls = "op";
      if (k === "=") cls = "eq";
      if (k === "C" || k === "⌫") cls = "clear";
      return `<button class="${cls}" data-k="${k}">${k}</button>`;
    }).join("");

    grid.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      const k = btn.dataset.k;

      if (k === "C") {
        calcExpr = "";
        calcShown = false;
      } else if (k === "⌫") {
        calcExpr = calcExpr.slice(0, -1);
      } else if (k === "=") {
        try {
          const expr = calcExpr
            .replace(/×/g, "*").replace(/÷/g, "/")
            .replace(/%/g, "/100");
          if (!/^[0-9+\-*/().\s]+$/.test(expr)) throw new Error("bad");
          let val = Function('"use strict";return (' + expr + ")")();
          if (typeof val !== "number" || !isFinite(val)) throw new Error("bad");
          calcExpr = String(Math.round(val * 1e10) / 1e10);
          calcShown = true;
        } catch (err) {
          calcExpr = "出错了！";
          calcShown = true;
        }
      } else {
        if (calcShown && /[0-9.]/.test(k)) {
          calcExpr = k; // 上次结果后输入数字，重新开始
        } else {
          calcExpr += k;
        }
        calcShown = false;
      }
      calcRender();
    });
  }

  /* ── 番茄钟 ── */
  let pomoLeft = 25 * 60;
  let pomoTotal = 25 * 60;
  let pomoTimer = null;
  let pomoRunning = false;
  let pomoEnded = false;

  function pomoRender() {
    const m = String(Math.floor(pomoLeft / 60)).padStart(2, "0");
    const s = String(pomoLeft % 60).padStart(2, "0");
    document.getElementById("pomoTime").textContent = `${m}:${s}`;
    const c = 2 * Math.PI * 84;
    const fg = document.getElementById("pomoFg");
    fg.style.strokeDasharray = c;
    fg.style.strokeDashoffset = c * (1 - pomoLeft / pomoTotal);
  }

  function pomoStop() {
    clearInterval(pomoTimer);
    pomoTimer = null;
    pomoRunning = false;
    document.getElementById("pomoStart").textContent = "继续";
    document.getElementById("pomoState").textContent = "已暂停";
  }

  function bindPomo() {
    const btnStart = document.getElementById("pomoStart");
    if (btnStart.dataset.bound) return; // 防止页面切换时重复绑定
    btnStart.dataset.bound = "1";
    const btnReset = document.getElementById("pomoReset");
    document.getElementById("pomoFg").style.stroke = "url(#pomoGrad)";
    pomoRender();

    // 给 SVG 注入渐变（因为 CSS 里 url 引用需要真实元素）
    const svg = document.querySelector(".pomo-ring");
    if (svg && !document.getElementById("pomoGrad")) {
      const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
      defs.innerHTML = `<linearGradient id="pomoGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#ec4899"/>
      </linearGradient>`;
      svg.prepend(defs);
    }

    btnStart.addEventListener("click", () => {
      if (pomoEnded) {
        pomoLeft = pomoTotal;
        pomoEnded = false;
      }
      if (pomoRunning) {
        pomoStop();
        return;
      }
      if (pomoLeft <= 0) pomoLeft = pomoTotal;
      pomoRunning = true;
      btnStart.textContent = "暂停";
      document.getElementById("pomoState").textContent = "专注中…";
      UI.toast("番茄钟开始，专注起来！");
      pomoTimer = setInterval(() => {
        pomoLeft--;
        pomoRender();
        if (pomoLeft <= 0) {
          clearInterval(pomoTimer);
          pomoTimer = null;
          pomoRunning = false;
          pomoEnded = true;
          btnStart.textContent = "再来一轮";
          document.getElementById("pomoState").textContent = "完成啦！休息一下吧";
          UI.toast("番茄钟完成！休息一下～");
        }
      }, 1000);
    });

    btnReset.addEventListener("click", () => {
      pomoStop();
      pomoLeft = pomoTotal;
      pomoEnded = false;
      btnStart.textContent = "开始";
      document.getElementById("pomoState").textContent = "准备开始";
      pomoRender();
    });

    document.querySelectorAll(".pomo-modes .mode").forEach((m) => {
      m.addEventListener("click", () => {
        document.querySelectorAll(".pomo-modes .mode").forEach((x) => x.classList.remove("active"));
        m.classList.add("active");
        pomoStop();
        pomoTotal = parseInt(m.dataset.min, 10) * 60;
        pomoLeft = pomoTotal;
        pomoEnded = false;
        btnStart.textContent = "开始";
        document.getElementById("pomoState").textContent = "准备开始";
        pomoRender();
      });
    });
  }

  /* ── 颜色工具 ── */
  const PALETTE = ["#8b5cf6", "#ec4899", "#22d3ee", "#f59e0b", "#10b981", "#ef4444",
    "#3b82f6", "#14b8a6", "#f97316", "#a855f7", "#84cc16", "#64748b"];

  function bindColor() {
    const pick = document.getElementById("colorPick");
    if (pick.dataset.bound) return; // 防止页面切换时重复绑定
    pick.dataset.bound = "1";
    const code = document.getElementById("colorCode");
    const palette = document.getElementById("palette");

    palette.innerHTML = PALETTE.map((c) =>
      `<div class="swatch" data-c="${c}" style="background:${c}"></div>`).join("");

    const apply = (c) => {
      pick.value = c;
      code.textContent = c;
      document.querySelectorAll(".palette .swatch").forEach((s) =>
        s.classList.toggle("sel", s.dataset.c.toLowerCase() === c.toLowerCase()));
    };

    pick.addEventListener("input", () => apply(pick.value));
    palette.addEventListener("click", (e) => {
      const s = e.target.closest(".swatch");
      if (s) apply(s.dataset.c);
    });

    document.getElementById("btnCopyColor").addEventListener("click", async () => {
      const ok = await UI.copyText(code.textContent);
      UI.toast(ok ? `已复制 ${code.textContent}` : "复制失败");
    });

    apply("#8b5cf6");
  }

  /* ── 字符统计 ── */
  function bindCount() {
    const area = document.getElementById("countArea");
    if (area.dataset.bound) return; // 防止页面切换时重复绑定
    area.dataset.bound = "1";
    const upd = () => {
      const v = area.value;
      const chars = v.replace(/\s/g, "");
      const lines = v ? v.split(/\r\n|\r|\n/).length : 0;
      document.getElementById("cChars").textContent = [...chars].length;
      document.getElementById("cAll").textContent = [...v].length;
      document.getElementById("cLines").textContent = lines;
    };
    area.addEventListener("input", upd);
  }

  /* ── 待办清单 ── */
  const TODO_KEY = "talent_todos";

  function todoLoad() {
    try { return JSON.parse(localStorage.getItem(TODO_KEY)) || []; }
    catch (e) { return []; }
  }
  function todoSave(list) {
    localStorage.setItem(TODO_KEY, JSON.stringify(list));
  }

  function todoRender(list) {
    const ul = document.getElementById("todoList");
    if (!list.length) {
      ul.innerHTML = '<li class="proc-empty" style="border:none;">还没有待办，添加一件吧～</li>';
      return;
    }
    ul.innerHTML = list.map((t, i) => `
      <li class="${t.done ? "done" : ""}">
        <button class="t-check" data-i="${i}">${t.done ? "✓" : ""}</button>
        <span class="t-text">${UI.esc(t.text)}</span>
        <button class="t-del" data-i="${i}">✕</button>
      </li>`).join("");
  }

  function bindTodo() {
    const input = document.getElementById("todoInput");
    if (input.dataset.bound) return; // 防止页面切换时重复绑定
    input.dataset.bound = "1";
    const addBtn = document.getElementById("btnTodoAdd");
    const ul = document.getElementById("todoList");
    const list = todoLoad();
    todoRender(list);

    const save = () => todoSave(list);

    const add = () => {
      const v = input.value.trim();
      if (!v) return;
      list.unshift({ text: v, done: false });
      input.value = "";
      save();
      todoRender(list);
      UI.toast("已添加待办");
    };
    addBtn.addEventListener("click", add);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") add(); });

    ul.addEventListener("click", (e) => {
      const check = e.target.closest(".t-check");
      const del = e.target.closest(".t-del");
      if (check) {
        const i = +check.dataset.i;
        list[i].done = !list[i].done;
        save();
        todoRender(list);
      } else if (del) {
        const i = +del.dataset.i;
        list.splice(i, 1);
        save();
        todoRender(list);
      }
    });
  }

  function init() {
    bindCalc();
    bindPomo();
    bindColor();
    bindCount();
    bindTodo();
  }

  return { init };
})();
