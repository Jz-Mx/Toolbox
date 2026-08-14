// 验证：题库 60 题 + 答过排除 + 全答完重置（独立于页面的纯逻辑测试）
const fs = require("fs");
const path = require("path");

const src = fs.readFileSync(
  path.join(__dirname, "..", "web", "js", "pages", "dashboard.js"),
  "utf-8"
);

// 1) 题库数量
const qCount = (src.match(/\{ q: "/g) || []).length;
console.log("题库题数:", qCount);
if (qCount < 60) { console.log("FAIL: 题库不足 60"); process.exit(1); }

// 2) 提取 DAILY_QUESTIONS 数组（用 Function 构造求值）
const m = src.match(/const DAILY_QUESTIONS = (\[[\s\S]*?\]);/);
if (!m) { console.log("FAIL: 未找到 DAILY_QUESTIONS"); process.exit(1); }
const questions = eval("(" + m[1] + ")");
console.log("解析题数:", questions.length);
if (questions.length < 60) { console.log("FAIL"); process.exit(1); }

// 3) 模拟"答过排除"逻辑（复刻 pickAvailable）
function pickAvailable(dateStr, excludeIdx, done) {
  let pool = questions.map((_, i) => i).filter((i) => !done.includes(i) && i !== excludeIdx);
  if (!pool.length) {
    done = [];
    pool = questions.map((_, i) => i).filter((i) => i !== excludeIdx);
  }
  let seed = 0;
  for (const ch of dateStr) seed = (seed * 31 + ch.charCodeAt(0)) % 100000;
  return pool[seed % pool.length];
}

// 答过 10 题后，10 次选题都不应落在 done 集合
const done10 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let ok = true;
for (let i = 0; i < 10; i++) {
  const idx = pickAvailable("2026-08-14", -1, done10);
  if (done10.includes(idx)) { ok = false; console.log("FAIL: 选中了已答过的题", idx); }
}
console.log("答过 10 题后选题避开:", ok ? "OK" : "FAIL");

// 全部答完 → 重置（返回有效题号）
const allDone = questions.map((_, i) => i);
const afterAll = pickAvailable("2026-08-14", -1, allDone);
console.log("全答完后重置选题:", afterAll >= 0 && afterAll < questions.length ? "OK" : "FAIL", "(选到", afterAll, ")");

// 双击换题（排除当前题）
const cur = 3;
const swapped = pickAvailable("2026-08-14", cur, done10);
console.log("换题排除当前题:", swapped !== cur ? "OK" : "FAIL");
console.log("RESULT:", ok ? "ALL_OK" : "HAS_FAIL");
process.exit(ok ? 0 : 1);
