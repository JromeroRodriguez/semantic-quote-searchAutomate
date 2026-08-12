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

function formatNumber(n) {
    return n == null ? "—" : n.toLocaleString();
}

function renderReceipt(receipt) {
    return `
        <div class="receipt-grid">
            <div class="receipt-row"><span>Quotes processed</span><span>${formatNumber(receipt.quotes_processed)}</span></div>
            <div class="receipt-row"><span>Batches created</span><span>${formatNumber(receipt.batches_created)}</span></div>
            <div class="receipt-row"><span>Requests completed</span><span>${formatNumber(receipt.requests_completed)}</span></div>
            ${receipt.requests_failed > 0 ? `<div class="receipt-row error"><span>Requests failed</span><span>${formatNumber(receipt.requests_failed)}</span></div>` : ""}
            <hr>
            <div class="receipt-row"><span>Estimated input</span><span>${formatNumber(receipt.estimated_input_tokens)} tokens</span></div>
            <div class="receipt-row"><span>Actual input</span><span>${formatNumber(receipt.actual_input_tokens)} tokens</span></div>
            <div class="receipt-row"><span>Output</span><span>${formatNumber(receipt.actual_output_tokens)} tokens</span></div>
            <div class="receipt-row total"><span>Total</span><span>${formatNumber(receipt.total_tokens)} tokens</span></div>
            <div class="receipt-row muted"><span>Limit per request</span><span>${formatNumber(receipt.token_limit_per_request)} tokens</span></div>
        </div>
    `;
}

function renderBatchCard(batch) {
    return `
        <li class="batch-card">
            <div class="batch-header">
                <span class="batch-id">Batch ${batch.batch_id}</span>
                <span class="batch-count">${batch.quote_count} quotes</span>
            </div>
            <div class="batch-tokens">
                Est: ${formatNumber(batch.estimated_input_tokens)}
                ${batch.actual_input_tokens != null ? ` · Actual: ${formatNumber(batch.actual_input_tokens)}` : ""}
                ${batch.actual_output_tokens != null ? ` · Out: ${formatNumber(batch.actual_output_tokens)}` : ""}
            </div>
            <div class="batch-ids">IDs: ${batch.quote_ids.join(", ")}</div>
        </li>
    `;
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
        optimizerReceipt.innerHTML = renderReceipt(data.receipt);
        optimizerBatchesContainer.innerHTML = `<ol class="batch-list">${data.batches.map(renderBatchCard).join("")}</ol>`;
        showState(optimizerResultsSection);
    } catch (err) {
        errorMessage.textContent = err.message || "Optimizer failed. Please try again.";
        showState(errorState);
    } finally {
        optimizerRunBtn.textContent = "Run Optimizer";
        optimizerRunBtn.disabled = false;
    }
}

optimizerRunBtn.addEventListener("click", handleOptimizerRun);

setMode("search");
queryInput.focus();
