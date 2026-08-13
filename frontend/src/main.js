import { searchQuotes, debateQuotes, runOptimizer } from "./services/api.js";

const queryInput = document.getElementById("query-input");
const searchBtn = document.getElementById("search-btn");
const loadingState = document.getElementById("loading-state");
const resultsSection = document.getElementById("results-section");
const resultsContainer = document.getElementById("results-container");
const resultsCount = document.getElementById("results-count");

const debateResultsSection = document.getElementById("debate-results-section");
const debateEssayContainer = document.getElementById("debate-essay-container");
const debateSourcesContainer = document.getElementById("debate-sources-container");
const debateLoadingState = document.getElementById("debate-loading-state");

const noResults = document.getElementById("no-results");
const errorState = document.getElementById("error-state");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const suggestionsEl = document.getElementById("suggestions");

const modeSearchBtn = document.getElementById("mode-search-btn");
const modeDebateBtn = document.getElementById("mode-debate-btn");
const modeOptimizerBtn = document.getElementById("mode-optimizer-btn");
const heroSearch = document.getElementById("hero-search");
const heroDebate = document.getElementById("hero-debate");
const heroOptimizer = document.getElementById("hero-optimizer");
const inputLabel = document.getElementById("input-label");
const actionHint = document.getElementById("action-hint");

const optimizerPanel = document.getElementById("optimizer-panel");
const optimizerInput = document.getElementById("optimizer-input");
const optimizerRunBtn = document.getElementById("optimizer-run-btn");
const optimizerLoadingState = document.getElementById("optimizer-loading-state");
const optimizerResultsSection = document.getElementById("optimizer-results-section");
const optimizerReceipt = document.getElementById("optimizer-receipt");
const optimizerBatchesContainer = document.getElementById("optimizer-batches-container");
const optimizerMetrics = document.getElementById("optimizer-metrics");
const optimizerChart = document.getElementById("optimizer-chart");
const optimizerFilterInput = document.getElementById("optimizer-filter-input");
const optimizerExpandAllBtn = document.getElementById("optimizer-expand-all-btn");
const optimizerCollapseAllBtn = document.getElementById("optimizer-collapse-all-btn");
const optimizerCompareBtn = document.getElementById("optimizer-compare-btn");
const optimizerCompareContainer = document.getElementById("optimizer-compare-container");

let currentMode = "search"; // "search", "debate", or "optimizer"

const SEARCH_SUGGESTIONS = [
    "starting over after failure",
    "the calm before a major decision",
    "loving someone from a distance",
    "why patience is not passivity",
];

const DEBATE_SUGGESTIONS = [
    "Is knowledge more important than imagination?",
    "Can justice exist without mercy?",
    "What is the true purpose of suffering?",
    "Does freedom require absolute independence?",
];

function renderSuggestions() {
    suggestionsEl.innerHTML = "";
    const list = currentMode === "search" ? SEARCH_SUGGESTIONS : DEBATE_SUGGESTIONS;
    list.forEach((text) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = text;
        btn.addEventListener("click", () => {
            queryInput.value = text;
            syncButton();
            handleSubmit();
        });
        suggestionsEl.appendChild(btn);
    });
}

function setMode(mode) {
    currentMode = mode;
    [resultsSection, debateResultsSection, optimizerResultsSection, noResults, errorState,
     emptyState, loadingState, debateLoadingState, optimizerLoadingState, optimizerPanel,
     suggestionsEl].forEach((el) =>
        el.classList.add("hidden")
    );

    if (mode === "search") {
        modeSearchBtn.classList.add("active");
        modeDebateBtn.classList.remove("active");
        modeOptimizerBtn.classList.remove("active");
        heroSearch.classList.remove("hidden");
        heroDebate.classList.add("hidden");
        heroOptimizer.classList.add("hidden");
        inputLabel.textContent = "Your description";
        queryInput.placeholder = "I am still doubting a decision I already made…";
        searchBtn.textContent = "Search quotes";
        actionHint.textContent = "Press ⌘ / Ctrl + Enter to search";
        queryInput.parentElement.classList.remove("hidden");
        suggestionsEl.classList.remove("hidden");
    } else if (mode === "debate") {
        modeDebateBtn.classList.add("active");
        modeSearchBtn.classList.remove("active");
        modeOptimizerBtn.classList.remove("active");
        heroDebate.classList.remove("hidden");
        heroSearch.classList.add("hidden");
        heroOptimizer.classList.add("hidden");
        inputLabel.textContent = "Philosophical question";
        queryInput.placeholder = "Is knowledge more important than imagination?";
        searchBtn.textContent = "Debate";
        actionHint.textContent = "Press ⌘ / Ctrl + Enter to debate";
        queryInput.parentElement.classList.remove("hidden");
        suggestionsEl.classList.remove("hidden");
    } else {
        modeOptimizerBtn.classList.add("active");
        modeSearchBtn.classList.remove("active");
        modeDebateBtn.classList.remove("active");
        heroOptimizer.classList.remove("hidden");
        heroSearch.classList.add("hidden");
        heroDebate.classList.add("hidden");
        queryInput.parentElement.classList.add("hidden");
        optimizerPanel.classList.remove("hidden");
    }
    renderSuggestions();
    syncButton();
}

modeSearchBtn.addEventListener("click", () => setMode("search"));
modeDebateBtn.addEventListener("click", () => setMode("debate"));
modeOptimizerBtn.addEventListener("click", () => setMode("optimizer"));

function showState(state) {
    [loadingState, debateLoadingState, optimizerLoadingState, resultsSection, debateResultsSection,
     optimizerResultsSection, noResults, errorState, emptyState].forEach((el) =>
        el.classList.add("hidden")
    );
    state.classList.remove("hidden");
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (c) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[c]);
}

function renderQuoteCard(quote, index) {
    return `
        <li>
            <span class="num">${String(index + 1).padStart(2, "0")}</span>
            <div>
                <blockquote>${escapeHtml(quote.quote)}</blockquote>
                <cite>${escapeHtml(quote.author)}</cite>
            </div>
        </li>
    `;
}

function syncButton() {
    searchBtn.disabled = !queryInput.value.trim();
}

async function handleSubmit() {
    const query = queryInput.value.trim();
    if (!query) return;

    searchBtn.disabled = true;
    searchBtn.textContent = currentMode === "search" ? "Reading…" : "Generating…";
    
    // Show appropriate loading state based on mode
    if (currentMode === "search") {
        showState(loadingState);
    } else {
        showState(debateLoadingState);
    }

    try {
        if (currentMode === "search") {
            const data = await searchQuotes(query);
            const results = data.results || [];

            if (results.length === 0) {
                showState(noResults);
                return;
            }

            resultsCount.textContent = `${results.length} passages`;
            resultsContainer.innerHTML = results.map(renderQuoteCard).join("");
            showState(resultsSection);
        } else {
            const data = await debateQuotes(query);
            const essay = data.essay || "";
            const sources = data.sources || [];

            const paragraphs = essay.split("\n\n").map(p => `<p>${escapeHtml(p)}</p>`).join("");
            debateEssayContainer.innerHTML = paragraphs;
            debateSourcesContainer.innerHTML = sources.map(renderQuoteCard).join("");
            showState(debateResultsSection);
        }
    } catch (err) {
        errorMessage.textContent = err.message || "Something went wrong. Please try again.";
        showState(errorState);
    } finally {
        searchBtn.textContent = currentMode === "search" ? "Search quotes" : "Debate";
        syncButton();
    }
}

searchBtn.addEventListener("click", handleSubmit);
queryInput.addEventListener("input", syncButton);
queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
});

let lastOptimizerData = null;
let currentFilter = "";
const expandedBatches = new Set();

function formatNumber(n) {
    return n == null ? "—" : n.toLocaleString();
}

function renderReceipt(receipt) {
    return `
        <div class="receipt-grid">
            <div class="receipt-row"><span>Quotes processed</span><span>${formatNumber(receipt.quotes_processed)}</span></div>
            <div class="receipt-row"><span>Batches created</span><span>${formatNumber(receipt.batches_created)}</span></div>
            <hr>
            <div class="receipt-row total"><span>Total estimated tokens</span><span>${formatNumber(receipt.estimated_input_tokens)} tokens</span></div>
            <div class="receipt-row muted"><span>Limit per batch</span><span>${formatNumber(receipt.token_limit_per_request)} tokens</span></div>
        </div>
    `;
}

function renderPackingMetrics(data, limit) {
    const batches = data.batches || [];
    if (!batches.length) return "";
    const used = batches.reduce((sum, b) => sum + b.estimated_input_tokens, 0);
    const capacity = batches.length * limit;
    const efficiency = capacity > 0 ? Math.round((used / capacity) * 100) : 0;
    const wasted = batches.reduce((sum, b) => sum + Math.max(0, limit - b.estimated_input_tokens), 0);
    const oversized = batches.filter(b => b.estimated_input_tokens > limit).length;
    return `
        <div class="metrics-grid">
            <div class="metric"><span>Packing efficiency</span><b>${efficiency}%</b></div>
            <div class="metric"><span>Wasted tokens</span><b>${formatNumber(wasted)}</b></div>
            <div class="metric"><span>Oversized quotes</span><b>${oversized}</b></div>
            <div class="metric"><span>Requests needed</span><b>${formatNumber(batches.length)}</b></div>
        </div>
    `;
}

function renderChart(data, limit) {
    const batches = data.batches || [];
    if (!batches.length) return "";
    const bars = batches.map((b) => {
        const pct = limit > 0 ? (b.estimated_input_tokens / limit) * 100 : 0;
        const height = Math.max(3, Math.min(100, pct));
        const oversized = b.estimated_input_tokens > limit;
        return `
            <div class="chart-col" title="${formatNumber(b.estimated_input_tokens)} tokens (${Math.round(pct)}%)">
                <div class="chart-bar${oversized ? " oversized" : ""}" style="height: ${height}%"></div>
                <span class="chart-label">${b.batch_id}</span>
            </div>
        `;
    }).join("");
    return `<div class="chart-title">Token distribution per batch</div><div class="chart-bars">${bars}</div>`;
}

function buildCopyPrompt(batch) {
    const lines = (batch.quotes || [])
        .map((q, i) => `${i + 1}. "${q.quote}" — ${q.author}`)
        .join("\n");
    return `You are an expert literary and philosophical analyst. For each quote in the batch below, provide a concise thematic analysis, core meaning, and contextual interpretation:\n\n` +
        `Batch ${batch.batch_id} (${batch.quote_count} quotes):\n${lines}`;
}

async function copyText(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        const ok = document.execCommand("copy");
        ta.remove();
        return ok;
    }
}

function renderBatchCard(batch, limit, filter) {
    const filterLower = (filter || "").trim().toLowerCase();
    const quotes = (batch.quotes || []).filter((q) => {
        if (!filterLower) return true;
        return `${q.quote} ${q.author}`.toLowerCase().includes(filterLower);
    });
    if (filterLower && !quotes.length) return "";

    const pct = limit > 0 ? Math.round((batch.estimated_input_tokens / limit) * 100) : 0;
    const oversized = batch.estimated_input_tokens > limit;
    const quotesHtml = quotes.map(q => `
        <div class="batch-quote-item">
            <blockquote>"${escapeHtml(q.quote)}"</blockquote>
            <cite>— ${escapeHtml(q.author)} (ID: ${q.id})</cite>
        </div>
    `).join("");
    const expandedClass = expandedBatches.has(batch.batch_id) ? " expanded" : "";

    return `
        <li class="batch-card${expandedClass}" data-batch-id="${batch.batch_id}">
            <div class="batch-header">
                <span class="batch-id">Batch ${batch.batch_id}${oversized ? '<span class="badge-warn">oversized</span>' : ""} <span style="font-size: 0.75rem; color: var(--muted); font-family: var(--sans);">(${batch.quote_count} quotes)</span></span>
                <span class="batch-tokens">${formatNumber(batch.estimated_input_tokens)} / ${limit} tokens (${pct}%)</span>
            </div>
            <div class="batch-gauge"><div class="batch-gauge-fill${oversized ? " danger" : ""}" style="width: ${Math.min(100, pct)}%"></div></div>
            <div class="batch-actions">
                <button type="button" class="opt-tool-btn copy-prompt-btn" data-copy-batch="${batch.batch_id}">Copy Prompt</button>
            </div>
            <div class="batch-expand-hint">Click to inspect quotes ▼</div>
            <div class="batch-quotes-list">
                ${quotesHtml}
            </div>
        </li>
    `;
}

function renderBatches() {
    if (!lastOptimizerData) return;
    if (!lastOptimizerData.batches.length) {
        optimizerBatchesContainer.innerHTML = `<p class="muted" style="margin-top: 1rem;">No batches generated.</p>`;
        return;
    }
    const limit = lastOptimizerData.receipt.token_limit_per_request;
    const html = lastOptimizerData.batches.map(b => renderBatchCard(b, limit, currentFilter)).join("");
    optimizerBatchesContainer.innerHTML = html
        ? `<ol class="batch-list">${html}</ol>`
        : `<p class="muted" style="margin-top: 1rem;">No quotes match "${currentFilter}".</p>`;
}

async function handleOptimizerRun() {
    const maxTokens = parseInt(optimizerInput.value, 10);
    if (!maxTokens || maxTokens <= 0) {
        errorMessage.textContent = "Please enter a valid token budget.";
        showState(errorState);
        return;
    }

    optimizerRunBtn.disabled = true;
    optimizerRunBtn.textContent = "Running…";
    showState(optimizerLoadingState);

    try {
        const data = await runOptimizer(maxTokens);
        lastOptimizerData = data;
        expandedBatches.clear();
        currentFilter = "";
        optimizerFilterInput.value = "";
        optimizerCompareContainer.innerHTML = "";

        optimizerReceipt.innerHTML = renderReceipt(data.receipt);
        optimizerMetrics.innerHTML = renderPackingMetrics(data, maxTokens);
        const chartHtml = renderChart(data, maxTokens);
        optimizerChart.classList.toggle("hidden", !chartHtml);
        optimizerChart.innerHTML = chartHtml;
        renderBatches();
        showState(optimizerResultsSection);
    } catch (err) {
        errorMessage.textContent = err.message || "Optimizer failed. Please try again.";
        showState(errorState);
    } finally {
        optimizerRunBtn.textContent = "Run Optimizer";
        optimizerRunBtn.disabled = false;
    }
}

optimizerBatchesContainer.addEventListener("click", async (e) => {
    const copyBtn = e.target.closest("[data-copy-batch]");
    if (copyBtn) {
        const batchId = Number(copyBtn.dataset.copyBatch);
        const batch = (lastOptimizerData.batches || []).find(b => b.batch_id === batchId);
        if (!batch) return;
        const ok = await copyText(buildCopyPrompt(batch));
        copyBtn.textContent = ok ? "Copied!" : "Copy Prompt";
        if (ok) setTimeout(() => { copyBtn.textContent = "Copy Prompt"; }, 1500);
        return;
    }
    if (e.target.closest(".batch-quotes-list") || e.target.closest("button")) return;
    const card = e.target.closest(".batch-card");
    if (!card) return;
    const id = Number(card.dataset.batchId);
    if (expandedBatches.has(id)) {
        expandedBatches.delete(id);
    } else {
        expandedBatches.add(id);
    }
    card.classList.toggle("expanded");
});

optimizerFilterInput.addEventListener("input", () => {
    currentFilter = optimizerFilterInput.value;
    renderBatches();
});

optimizerExpandAllBtn.addEventListener("click", () => {
    (lastOptimizerData?.batches || []).forEach(b => expandedBatches.add(b.batch_id));
    renderBatches();
});

optimizerCollapseAllBtn.addEventListener("click", () => {
    expandedBatches.clear();
    renderBatches();
});

optimizerCompareBtn.addEventListener("click", async () => {
    optimizerCompareBtn.disabled = true;
    optimizerCompareContainer.innerHTML = `<p class="muted" style="margin: 1rem 0;">Running optimizer at 500, 1000, 2000…</p>`;
    try {
        const limits = [500, 1000, 2000];
        const results = await Promise.all(limits.map(l => runOptimizer(l)));
        const rows = results.map((r, i) => {
            const limit = limits[i];
            const used = (r.batches || []).reduce((sum, b) => sum + b.estimated_input_tokens, 0);
            const capacity = (r.batches.length || 1) * limit;
            const efficiency = capacity > 0 ? Math.round((used / capacity) * 100) : 0;
            return `
                <tr>
                    <td>${formatNumber(limit)}</td>
                    <td>${formatNumber(r.receipt.batches_created)}</td>
                    <td>${formatNumber(r.receipt.estimated_input_tokens)}</td>
                    <td>${efficiency}%</td>
                </tr>
            `;
        }).join("");
        optimizerCompareContainer.innerHTML = `
            <table class="compare-table">
                <thead><tr><th>Budget</th><th>Requests</th><th>Total tokens</th><th>Efficiency</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } catch (err) {
        optimizerCompareContainer.innerHTML = `<p class="error" style="margin: 1rem 0;">${escapeHtml(err.message || "Compare failed.")}</p>`;
    } finally {
        optimizerCompareBtn.disabled = false;
    }
});

document.getElementById("export-json-btn").addEventListener("click", () => {
    if (!lastOptimizerData) return;
    const blob = new Blob([JSON.stringify(lastOptimizerData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "optimizer-receipt-report.json";
    a.click();
    URL.revokeObjectURL(url);
});

optimizerRunBtn.addEventListener("click", handleOptimizerRun);

setMode("search");
queryInput.focus();
