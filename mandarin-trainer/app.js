const state = {
  data: null,
  view: "grammar",
  level: "A2",
  mode: "learn",
  selectedId: null,
  answered: false,
};

const levelOptions = [
  ["all", "全部等級"],
  ["N1", "準備一級"],
  ["N2", "準備二級"],
  ["A1", "入門級"],
  ["A2", "基礎級"],
  ["B1", "進階級"],
  ["B2", "高階級"],
  ["C1", "流利級"],
  ["L1", "語法第1級"],
  ["L2", "語法第2級"],
  ["L3", "語法第3級"],
  ["L4", "語法第4級"],
  ["L5", "語法第5級"],
];

const els = {
  levelSelect: document.querySelector("#levelSelect"),
  modeSelect: document.querySelector("#modeSelect"),
  itemList: document.querySelector("#itemList"),
  studyCard: document.querySelector("#studyCard"),
  tabs: [...document.querySelectorAll(".tabs button")],
  todayCount: document.querySelector("#todayCount"),
  masteredCount: document.querySelector("#masteredCount"),
  accuracyCount: document.querySelector("#accuracyCount"),
  resetProgress: document.querySelector("#resetProgress"),
};

const storage = {
  get records() {
    return JSON.parse(localStorage.getItem("mandarinRecords") || "{}");
  },
  set records(value) {
    localStorage.setItem("mandarinRecords", JSON.stringify(value));
  },
  get events() {
    return JSON.parse(localStorage.getItem("mandarinEvents") || "[]");
  },
  set events(value) {
    localStorage.setItem("mandarinEvents", JSON.stringify(value.slice(-1000)));
  },
};

async function init() {
  state.data = await fetch("./assets/learning-data.json").then((res) => res.json());
  levelOptions.forEach(([value, label]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    els.levelSelect.append(option);
  });
  els.levelSelect.value = state.level;
  bindEvents();
  render();
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  }
}

function bindEvents() {
  els.levelSelect.addEventListener("change", (event) => {
    state.level = event.target.value;
    state.selectedId = null;
    render();
  });
  els.modeSelect.addEventListener("change", (event) => {
    state.mode = event.target.value;
    state.selectedId = null;
    render();
  });
  els.tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      state.view = tab.dataset.view;
      state.selectedId = null;
      render();
    });
  });
  els.resetProgress.addEventListener("click", () => {
    if (confirm("要清除這台裝置上的學習紀錄嗎？")) {
      localStorage.removeItem("mandarinRecords");
      localStorage.removeItem("mandarinEvents");
      render();
    }
  });
}

function datasetForView() {
  if (state.view === "vocab") return state.data.vocabulary;
  if (state.view === "grammar") return state.data.grammar;
  if (state.view === "tocfl") return state.data.tocfl;
  return [];
}

function filteredItems() {
  const items = datasetForView();
  if (state.level === "all" || state.view === "tocfl") return items;
  return items.filter((item) => item.level === state.level);
}

function reviewSort(items) {
  if (state.mode !== "review") return items;
  const records = storage.records;
  return [...items].sort((a, b) => {
    const ra = records[a.id]?.score || 0;
    const rb = records[b.id]?.score || 0;
    return ra - rb;
  });
}

function render() {
  els.tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === state.view));
  renderStats();

  if (state.view === "records") {
    els.itemList.innerHTML = "";
    renderRecords();
    return;
  }

  const items = reviewSort(filteredItems());
  if (!items.length) {
    els.itemList.innerHTML = "";
    els.studyCard.innerHTML = `<h2>這個等級暫無資料</h2><p class="prompt">請切換等級或功能。</p>`;
    return;
  }
  if (!state.selectedId || !items.some((item) => item.id === state.selectedId)) {
    state.selectedId = pickDefaultItem(items).id;
  }
  renderList(items);
  renderStudy(items.find((item) => item.id === state.selectedId) || items[0], items);
}

function pickDefaultItem(items) {
  if (state.mode === "practice") return items[Math.floor(Math.random() * items.length)];
  return items[0];
}

function renderList(items) {
  els.itemList.innerHTML = "";
  items.slice(0, 180).forEach((item) => {
    const button = document.createElement("button");
    button.className = `list-item ${item.id === state.selectedId ? "active" : ""}`;
    button.innerHTML = `<strong>${titleOf(item)}</strong><span>${subtitleOf(item)}</span>`;
    button.addEventListener("click", () => {
      state.selectedId = item.id;
      state.answered = false;
      render();
    });
    els.itemList.append(button);
  });
}

function renderStudy(item, pool) {
  state.answered = false;
  if (state.mode === "learn") renderLearn(item);
  if (state.mode === "review") renderReview(item, pool);
  if (state.mode === "practice") renderPractice(item, pool);
}

function renderLearn(item) {
  els.studyCard.innerHTML = `
    <h2>${titleOf(item)}</h2>
    <div class="tag-row">${tagsOf(item).map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
    <div class="prompt">${bodyOf(item)}</div>
    <div class="action-row">
      <button class="primary-button" data-action="known">已學會</button>
      <button class="ghost-button" data-action="next">下一題</button>
    </div>
  `;
  els.studyCard.querySelector("[data-action='known']").addEventListener("click", () => mark(item, true));
  els.studyCard.querySelector("[data-action='next']").addEventListener("click", nextItem);
}

function renderReview(item, pool) {
  const quiz = makeQuiz(item, pool);
  els.studyCard.innerHTML = quizTemplate(item, quiz, "複習這一題");
  bindAnswerButtons(item, quiz);
}

function renderPractice(item, pool) {
  const quiz = makeQuiz(item, pool);
  els.studyCard.innerHTML = quizTemplate(item, quiz, "依出題準則練習");
  bindAnswerButtons(item, quiz);
}

function quizTemplate(item, quiz, label) {
  return `
    <h2>${label}</h2>
    <div class="tag-row">${tagsOf(item).map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
    <div class="prompt">${quiz.question}</div>
    <div class="answers">
      ${quiz.options
        .map((option) => `<button class="answer-button" data-correct="${option === quiz.answer}">${option}</button>`)
        .join("")}
    </div>
    <div class="action-row">
      <button class="ghost-button" data-action="next">換一題</button>
    </div>
  `;
}

function bindAnswerButtons(item, quiz) {
  els.studyCard.querySelectorAll(".answer-button").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.answered) return;
      state.answered = true;
      const correct = button.dataset.correct === "true";
      button.classList.add(correct ? "correct" : "wrong");
      els.studyCard.querySelectorAll(".answer-button").forEach((option) => {
        if (option.textContent === quiz.answer) option.classList.add("correct");
      });
      mark(item, correct);
    });
  });
  els.studyCard.querySelector("[data-action='next']").addEventListener("click", nextItem);
}

function makeQuiz(item, pool) {
  if (state.view === "vocab") {
    return {
      question: `「${item.word}」的拼音是什麼？`,
      answer: item.pinyin || item.pos,
      options: shuffle([item.pinyin || item.pos, ...sample(pool, item, 3).map((x) => x.pinyin || x.pos)]),
    };
  }
  if (state.view === "grammar") {
    return {
      question: item.example ? `哪一個語法點最符合例句：「${item.example}」？` : `請選出語法點名稱。`,
      answer: item.name,
      options: shuffle([item.name, ...sample(pool, item, 3).map((x) => x.name)]),
    };
  }
  return {
    question: `${item.band} ${item.skill}：${item.description}`,
    answer: item.name,
    options: shuffle([item.name, ...sample(pool, item, 3).map((x) => x.name)]),
  };
}

function mark(item, correct) {
  const records = storage.records;
  const previous = records[item.id] || { score: 0, attempts: 0, correct: 0 };
  records[item.id] = {
    ...previous,
    title: titleOf(item),
    level: item.level || item.band,
    type: state.view,
    score: Math.max(0, previous.score + (correct ? 2 : -1)),
    attempts: previous.attempts + 1,
    correct: previous.correct + (correct ? 1 : 0),
    updatedAt: new Date().toISOString(),
  };
  storage.records = records;
  storage.events = [...storage.events, { id: item.id, correct, at: new Date().toISOString() }];
  renderStats();
}

function nextItem() {
  const items = reviewSort(filteredItems());
  if (!items.length) return;
  const current = items.findIndex((item) => item.id === state.selectedId);
  state.selectedId = state.mode === "practice" ? pickDefaultItem(items).id : items[(current + 1) % items.length].id;
  render();
}

function renderStats() {
  const records = Object.values(storage.records);
  const today = new Date().toISOString().slice(0, 10);
  const events = storage.events.filter((event) => event.at.slice(0, 10) === today);
  const attempts = records.reduce((sum, record) => sum + record.attempts, 0);
  const correct = records.reduce((sum, record) => sum + record.correct, 0);
  els.todayCount.textContent = events.length;
  els.masteredCount.textContent = records.filter((record) => record.score >= 4).length;
  els.accuracyCount.textContent = attempts ? `${Math.round((correct / attempts) * 100)}%` : "0%";
}

function renderRecords() {
  const records = Object.values(storage.records).sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  els.studyCard.innerHTML = `
    <h2>學習記錄</h2>
    <div class="tag-row">
      <span class="tag">本機保存</span>
      <span class="tag">${records.length} 個項目</span>
    </div>
    <table class="record-table">
      <thead><tr><th>項目</th><th>類型</th><th>正確率</th><th>熟練度</th></tr></thead>
      <tbody>
        ${records
          .slice(0, 80)
          .map((record) => {
            const rate = record.attempts ? Math.round((record.correct / record.attempts) * 100) : 0;
            return `<tr><td>${record.title}</td><td>${labelForType(record.type)}</td><td>${rate}%</td><td>${record.score}</td></tr>`;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

function titleOf(item) {
  return item.word || item.name || item.pattern;
}

function subtitleOf(item) {
  return item.pinyin || item.example || `${item.band || item.level} ${item.skill || ""}`;
}

function bodyOf(item) {
  if (state.view === "vocab") return `詞類：${item.pos || "未標示"}<br>拼音：${item.pinyin || "未標示"}<br>任務領域：${item.context}`;
  if (state.view === "grammar") return item.example ? `例句：${item.example}` : "請搭配教師例句或生成題庫補充使用情境。";
  if (state.view === "tocfl") return `${item.band} ${item.skill} ${item.part}<br>${item.description}`;
  return "";
}

function tagsOf(item) {
  return [item.levelName, item.level, item.context, item.pos, item.band, item.skill].filter(Boolean).slice(0, 4);
}

function labelForType(type) {
  return { vocab: "生詞", grammar: "語法", tocfl: "華測" }[type] || type;
}

function sample(pool, current, count) {
  return shuffle(pool.filter((item) => item.id !== current.id)).slice(0, count);
}

function shuffle(items) {
  return [...new Set(items.filter(Boolean))].sort(() => Math.random() - 0.5);
}

init();
