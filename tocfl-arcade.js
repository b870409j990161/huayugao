const MANIFEST_PATH = "./packs/generated/manifest.generated.json";
const STORAGE_PROGRESS = "tocfl-arcade-progress-v1";
const STORAGE_BUNDLES = "tocfl-arcade-custom-bundles-v1";
const PRACTICE_COUNT = 10;

const MODE_NAMES = {
  topic_mode: "Topic Practice",
  story_mode: "Story Quest",
  review_mode: "Review Rehab",
  mock_exam_mode: "Mock Exam",
  listening_mode: "Listening Mission",
  news_mode: "News Rewrite"
};

const els = {
  bankSummary: document.querySelector("#bank-summary"),
  statusText: document.querySelector("#status-text"),
  modeGrid: document.querySelector("#mode-grid"),
  bundleInput: document.querySelector("#bundle-input"),
  clearBundlesButton: document.querySelector("#clear-bundles-button"),
  resetProgressButton: document.querySelector("#reset-progress-button"),
  statModes: document.querySelector("#stat-modes"),
  statQuestions: document.querySelector("#stat-questions"),
  statSessions: document.querySelector("#stat-sessions"),
  statWrong: document.querySelector("#stat-wrong"),
  sessionTitle: document.querySelector("#session-title"),
  progressText: document.querySelector("#progress-text"),
  scoreText: document.querySelector("#score-text"),
  emptyState: document.querySelector("#empty-state"),
  questionCard: document.querySelector("#question-card"),
  resultCard: document.querySelector("#result-card"),
  resultTitle: document.querySelector("#result-title"),
  resultSummary: document.querySelector("#result-summary"),
  resultList: document.querySelector("#result-list"),
  modeChip: document.querySelector("#mode-chip"),
  itemChip: document.querySelector("#item-chip"),
  typeChip: document.querySelector("#type-chip"),
  stemContext: document.querySelector("#stem-context"),
  stemTitle: document.querySelector("#stem-title"),
  stemText: document.querySelector("#stem-text"),
  audioPanel: document.querySelector("#audio-panel"),
  audioScript: document.querySelector("#audio-script"),
  questionText: document.querySelector("#question-text"),
  optionsGrid: document.querySelector("#options-grid"),
  feedbackPanel: document.querySelector("#feedback-panel"),
  feedbackTitle: document.querySelector("#feedback-title"),
  feedbackExplanation: document.querySelector("#feedback-explanation"),
  auditPanel: document.querySelector("#audit-panel"),
  auditCopy: document.querySelector("#audit-copy"),
  submitButton: document.querySelector("#submit-button"),
  nextButton: document.querySelector("#next-button")
};

const state = {
  manifest: null,
  packsById: new Map(),
  groupedModes: new Map(),
  progress: loadProgress(),
  session: null,
  index: 0,
  selectedOptionKey: null,
  answers: [],
  resultCommitted: false
};

function createEmptyProgress() {
  return {
    sessionsCompleted: 0,
    totalCorrect: 0,
    totalAnswers: 0,
    wrongItems: {}
  };
}

function loadProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_PROGRESS);
    return raw ? { ...createEmptyProgress(), ...JSON.parse(raw) } : createEmptyProgress();
  } catch (error) {
    console.warn("Failed to load progress.", error);
    return createEmptyProgress();
  }
}

function saveProgress() {
  localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(state.progress));
}

function loadCustomBundles() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_BUNDLES) ?? "[]");
  } catch (error) {
    console.warn("Failed to load custom bundles.", error);
    return [];
  }
}

function saveCustomBundles(bundles) {
  localStorage.setItem(STORAGE_BUNDLES, JSON.stringify(bundles));
}

async function fetchJson(path) {
  const response = await fetch(path, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to load ${path} (${response.status})`);
  }
  return response.json();
}

function setStatus(text) {
  els.statusText.textContent = text;
}

function toggleHidden(element, shouldHide) {
  element.classList.toggle("hidden", shouldHide);
}

function shuffle(items) {
  const cloned = [...items];
  for (let i = cloned.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [cloned[i], cloned[j]] = [cloned[j], cloned[i]];
  }
  return cloned;
}

function updateStats() {
  const totalQuestions = [...state.groupedModes.values()].reduce(
    (sum, mode) => sum + (mode.tutorial?.meta.count ?? 0) + (mode.core?.meta.count ?? 0),
    0
  );
  els.statModes.textContent = String(state.groupedModes.size);
  els.statQuestions.textContent = String(totalQuestions);
  els.statSessions.textContent = String(state.progress.sessionsCompleted);
  els.statWrong.textContent = String(Object.keys(state.progress.wrongItems).length);
}

function summarizeLibrary() {
  const bundleCount = loadCustomBundles().length;
  const lines = [
    `${state.groupedModes.size} modes loaded`,
    `${bundleCount} imported bundle${bundleCount === 1 ? "" : "s"}`,
    `${Object.keys(state.progress.wrongItems).length} items in review queue`
  ];
  els.bankSummary.textContent = lines.join(" · ");
}

function buildGroups(manifest, inlinePacks) {
  const packsById = new Map();
  const groups = new Map();

  manifest.packs.forEach((meta) => {
    const pack = inlinePacks.get(meta.id);
    if (!pack) return;

    packsById.set(meta.id, pack);
    const existing =
      groups.get(meta.mode) ??
      {
        mode: meta.mode,
        label: MODE_NAMES[meta.mode] ?? meta.label ?? meta.mode,
        description: meta.description ?? "",
        tutorial: null,
        core: null,
        imported: false
      };

    if (meta.experience === "tutorial") {
      existing.tutorial = { meta, pack };
    } else {
      existing.core = { meta, pack };
    }

    if (meta.imported) {
      existing.imported = true;
    }

    groups.set(meta.mode, existing);
  });

  state.packsById = packsById;
  state.groupedModes = groups;
}

async function loadLibrary() {
  const baseManifest = await fetchJson(MANIFEST_PATH);
  const inlinePacks = new Map();

  for (const meta of baseManifest.packs) {
    inlinePacks.set(meta.id, await fetchJson(meta.file));
  }

  const customBundles = loadCustomBundles();
  const mergedManifest = {
    version: baseManifest.version,
    packs: [...baseManifest.packs]
  };

  customBundles.forEach((bundle, bundleIndex) => {
    (bundle.packs ?? []).forEach((pack, packIndex) => {
      const id = pack.packId ?? `custom-${bundleIndex}-${packIndex}`;
      inlinePacks.set(id, pack);
      mergedManifest.packs.push({
        id,
        mode: pack.mode,
        label: pack.label ?? MODE_NAMES[pack.mode] ?? pack.mode,
        experience: pack.experience ?? "core",
        itemType: pack.itemType ?? "mixed",
        count: Array.isArray(pack.items) ? pack.items.length : 0,
        description: pack.description ?? "Imported bundle",
        imported: true,
        file: null
      });
    });
  });

  state.manifest = mergedManifest;
  buildGroups(mergedManifest, inlinePacks);
  updateStats();
  summarizeLibrary();
  renderModeGrid();
}

function renderModeGrid() {
  els.modeGrid.replaceChildren();

  [...state.groupedModes.values()].forEach((group) => {
    const card = document.createElement("article");
    card.className = "mode-card";

    const title = document.createElement("h3");
    title.textContent = group.label;

    const description = document.createElement("p");
    description.className = "mode-meta";
    description.textContent = group.description;

    const counts = document.createElement("p");
    counts.className = "mode-meta";
    counts.textContent = `Tutorial ${group.tutorial?.meta.count ?? 0} · Core ${group.core?.meta.count ?? 0}${group.imported ? " · Imported update" : ""}`;

    const buttons = document.createElement("div");
    buttons.className = "button-row";

    const tutorialButton = document.createElement("button");
    tutorialButton.className = "primary-button";
    tutorialButton.type = "button";
    tutorialButton.textContent = "Tutorial";
    tutorialButton.disabled = !group.tutorial;
    tutorialButton.addEventListener("click", () => startPack(group.mode, "tutorial"));

    const practiceButton = document.createElement("button");
    practiceButton.className = "ghost-button";
    practiceButton.type = "button";
    practiceButton.textContent = "Practice";
    practiceButton.disabled = !group.core;
    practiceButton.addEventListener("click", () => startPack(group.mode, "core"));

    const reviewButton = document.createElement("button");
    reviewButton.className = "ghost-button";
    reviewButton.type = "button";
    reviewButton.textContent = "Review Wrong";
    reviewButton.addEventListener("click", () => startReview(group.mode));

    buttons.append(tutorialButton, practiceButton, reviewButton);
    card.append(title, description, counts, buttons);
    els.modeGrid.appendChild(card);
  });
}

function buildSession(modeKey, items, label) {
  state.session = { modeKey, label, items };
  state.index = 0;
  state.selectedOptionKey = null;
  state.answers = [];
  state.resultCommitted = false;
}

function getCurrentItem() {
  return state.session?.items[state.index] ?? null;
}

function updateSessionHeader() {
  const total = state.session?.items.length ?? 0;
  const current = total === 0 ? 0 : Math.min(state.index + 1, total);
  const correct = state.answers.filter((entry) => entry?.isCorrect).length;
  els.progressText.textContent = `${current} / ${total}`;
  els.scoreText.textContent = `${correct} correct`;
}

function renderAudit(item) {
  const notes = [];
  const quality = item.quality ?? {};
  notes.push(`fairness: ${quality.fairnessStatus ?? "unknown"}`);
  notes.push(`originality: ${quality.originalityStatus ?? "unknown"}`);
  notes.push(`logic: ${quality.logicStatus ?? "unknown"}`);

  (item.superLevelWordAudit ?? []).forEach((audit) => {
    notes.push(
      [
        `word ${audit.wordText}`,
        `level ${audit.detectedLevel}`,
        audit.replacementText ? `replace ${audit.replacementText}` : null,
        audit.keepReason ? `keep ${audit.keepReason}` : null
      ]
        .filter(Boolean)
        .join(" · ")
    );
  });

  toggleHidden(els.auditPanel, notes.length === 0);
  els.auditCopy.replaceChildren();
  notes.forEach((note) => {
    const p = document.createElement("p");
    p.textContent = note;
    els.auditCopy.appendChild(p);
  });
}

function createOptionButton(option, answerRecord) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "option-card";
  if (state.selectedOptionKey === option.optionKey) {
    button.classList.add("selected");
  }

  if (answerRecord) {
    if (option.optionKey === answerRecord.correctOptionKey) {
      button.classList.add("correct");
    } else if (option.optionKey === answerRecord.selectedOptionKey && !answerRecord.isCorrect) {
      button.classList.add("wrong");
    }
  }

  button.disabled = Boolean(answerRecord);
  button.innerHTML = `<span class="option-key">${option.optionKey}</span><span>${option.optionText}</span>`;
  button.addEventListener("click", () => {
    if (answerRecord) return;
    state.selectedOptionKey = option.optionKey;
    els.submitButton.disabled = false;
    renderCurrentItem();
  });
  return button;
}

function renderFeedback(item, answerRecord) {
  if (!answerRecord) {
    toggleHidden(els.feedbackPanel, true);
    return;
  }

  toggleHidden(els.feedbackPanel, false);
  els.feedbackTitle.textContent = answerRecord.isCorrect ? "Correct" : "Keep this one in review";
  els.feedbackTitle.className = `feedback-title ${answerRecord.isCorrect ? "correct" : "wrong"}`;
  els.feedbackExplanation.textContent = item.explanationText ?? "";
  renderAudit(item);
}

function renderCurrentItem() {
  const item = getCurrentItem();
  const answerRecord = state.answers[state.index];

  if (!item) return;

  toggleHidden(els.emptyState, true);
  toggleHidden(els.resultCard, true);
  toggleHidden(els.questionCard, false);

  els.sessionTitle.textContent = state.session.label;
  els.modeChip.textContent = MODE_NAMES[state.session.modeKey] ?? state.session.modeKey;
  els.itemChip.textContent = item.itemCode;
  els.typeChip.textContent = item.itemType;
  els.stemContext.textContent = item.stem?.contextSentence ?? "";
  els.stemTitle.textContent = item.stem?.title ?? "Stem";
  els.stemText.textContent = item.stem?.text ?? "";
  els.questionText.textContent = item.questionText ?? "";
  toggleHidden(els.audioPanel, item.itemType !== "listening");
  els.audioScript.textContent = item.audio?.ttsScript?.normal ?? "";

  els.optionsGrid.replaceChildren();
  (item.options ?? []).forEach((option) => {
    els.optionsGrid.appendChild(createOptionButton(option, answerRecord));
  });

  renderFeedback(item, answerRecord);
  els.submitButton.disabled = Boolean(answerRecord) || !state.selectedOptionKey;
  els.nextButton.disabled = !answerRecord;
  updateSessionHeader();
}

function commitSession() {
  if (state.resultCommitted) return;

  const correct = state.answers.filter((entry) => entry?.isCorrect).length;
  state.progress.sessionsCompleted += 1;
  state.progress.totalAnswers += state.answers.length;
  state.progress.totalCorrect += correct;

  state.answers.forEach((answer) => {
    if (!answer) return;
    if (answer.isCorrect) {
      delete state.progress.wrongItems[answer.itemCode];
      return;
    }

    state.progress.wrongItems[answer.itemCode] = {
      modeKey: state.session.modeKey,
      correctOptionKey: answer.correctOptionKey
    };
  });

  saveProgress();
  updateStats();
  summarizeLibrary();
  state.resultCommitted = true;
}

function renderResult() {
  commitSession();
  toggleHidden(els.questionCard, true);
  toggleHidden(els.resultCard, false);

  const total = state.answers.length;
  const correct = state.answers.filter((entry) => entry?.isCorrect).length;
  els.resultTitle.textContent = "Session Complete";
  els.resultSummary.textContent = `You answered ${correct} of ${total} correctly. Review Wrong is now available for any missed items.`;
  els.resultList.replaceChildren();

  state.answers.forEach((answer, index) => {
    const li = document.createElement("li");
    const item = state.session.items[index];
    li.textContent = `${answer.itemCode} · ${answer.isCorrect ? "correct" : `selected ${answer.selectedOptionKey}, answer ${answer.correctOptionKey}`} · ${item.questionText}`;
    els.resultList.appendChild(li);
  });

  updateSessionHeader();
}

function submitAnswer() {
  const item = getCurrentItem();
  if (!item || !state.selectedOptionKey) return;

  state.answers[state.index] = {
    itemCode: item.itemCode,
    selectedOptionKey: state.selectedOptionKey,
    correctOptionKey: item.answerOptionKey,
    isCorrect: state.selectedOptionKey === item.answerOptionKey
  };

  renderCurrentItem();
}

function goNext() {
  const total = state.session?.items.length ?? 0;
  if (state.index >= total - 1) {
    renderResult();
    return;
  }

  state.index += 1;
  state.selectedOptionKey = null;
  renderCurrentItem();
}

function findGroup(modeKey) {
  const group = state.groupedModes.get(modeKey);
  if (!group) {
    throw new Error(`Mode ${modeKey} not found.`);
  }
  return group;
}

function startPack(modeKey, experience) {
  const group = findGroup(modeKey);
  const bucket = experience === "tutorial" ? group.tutorial : group.core;
  if (!bucket) {
    throw new Error(`No ${experience} pack for ${modeKey}.`);
  }

  const sourceItems = bucket.pack.items ?? [];
  const items = experience === "tutorial" ? sourceItems.slice(0, 10) : shuffle(sourceItems).slice(0, PRACTICE_COUNT);
  buildSession(modeKey, items, `${group.label} · ${experience === "tutorial" ? "Tutorial" : "Practice"}`);
  setStatus(`Loaded ${items.length} items from ${group.label}.`);
  renderCurrentItem();
}

function startReview(modeKey) {
  const group = findGroup(modeKey);
  const coreItems = group.core?.pack.items ?? [];
  const wrongSet = new Set(
    Object.entries(state.progress.wrongItems)
      .filter(([, meta]) => meta.modeKey === modeKey)
      .map(([itemCode]) => itemCode)
  );

  if (!wrongSet.size) {
    setStatus(`No wrong answers queued for ${group.label}.`);
    return;
  }

  const reviewItems = coreItems.filter((item) => wrongSet.has(item.itemCode)).slice(0, PRACTICE_COUNT);
  buildSession(modeKey, reviewItems, `${group.label} · Review`);
  setStatus(`Loaded ${reviewItems.length} review items for ${group.label}.`);
  renderCurrentItem();
}

function resetProgress() {
  state.progress = createEmptyProgress();
  saveProgress();
  updateStats();
  summarizeLibrary();
  setStatus("Local progress reset.");
}

async function handleBundleUpload(event) {
  const [file] = event.target.files ?? [];
  if (!file) return;

  try {
    const raw = await file.text();
    const bundle = JSON.parse(raw);
    if (!Array.isArray(bundle.packs)) {
      throw new Error("Bundle must include a packs array.");
    }

    const bundles = loadCustomBundles();
    bundles.push(bundle);
    saveCustomBundles(bundles);
    await loadLibrary();
    setStatus(`Imported bundle: ${file.name}`);
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Failed to import bundle.");
  } finally {
    els.bundleInput.value = "";
  }
}

function clearBundles() {
  saveCustomBundles([]);
  loadLibrary()
    .then(() => setStatus("Imported bundles cleared."))
    .catch((error) => {
      console.error(error);
      setStatus("Failed to clear imported bundles.");
    });
}

function bindEvents() {
  els.bundleInput.addEventListener("change", handleBundleUpload);
  els.clearBundlesButton.addEventListener("click", clearBundles);
  els.resetProgressButton.addEventListener("click", resetProgress);
  els.submitButton.addEventListener("click", submitAnswer);
  els.nextButton.addEventListener("click", goNext);
}

async function initialize() {
  bindEvents();
  await loadLibrary();
  setStatus("Arcade ready. Start with Tutorial on any mode card.");
}

initialize().catch((error) => {
  console.error(error);
  setStatus("Arcade failed to initialize.");
});
