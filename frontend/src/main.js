import { searchQuotes, debateQuotes } from "./services/api.js";

const queryInput = document.getElementById("query-input");
const searchBtn = document.getElementById("search-btn");
const loadingState = document.getElementById("loading-state");
const resultsSection = document.getElementById("results-section");
const resultsContainer = document.getElementById("results-container");
const resultsCount = document.getElementById("results-count");

const debateResultsSection = document.getElementById("debate-results-section");
const debateEssayContainer = document.getElementById("debate-essay-container");
const debateSourcesContainer = document.getElementById("debate-sources-container");

const noResults = document.getElementById("no-results");
const errorState = document.getElementById("error-state");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const suggestionsEl = document.getElementById("suggestions");

const modeSearchBtn = document.getElementById("mode-search-btn");
const modeDebateBtn = document.getElementById("mode-debate-btn");
const heroSearch = document.getElementById("hero-search");
const heroDebate = document.getElementById("hero-debate");
const inputLabel = document.getElementById("input-label");
const actionHint = document.getElementById("action-hint");

let currentMode = "search"; // "search" or "debate"

const SEARCH_SUGGESTIONS = [
    "empezar de nuevo tras un fracaso",
    "la calma antes de una gran decisión",
    "amar a alguien desde la distancia",
    "por qué la paciencia no es pasividad",
];

const DEBATE_SUGGESTIONS = [
    "¿Es más importante el conocimiento o la imaginación?",
    "¿Puede existir la justicia sin misericordia?",
    "¿Cuál es el verdadero propósito del sufrimiento?",
    "¿Requiere la libertad independencia absoluta?",
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
    [resultsSection, debateResultsSection, noResults, errorState, emptyState, loadingState].forEach((el) =>
        el.classList.add("hidden")
    );

    if (mode === "search") {
        modeSearchBtn.classList.add("active");
        modeDebateBtn.classList.remove("active");
        heroSearch.classList.remove("hidden");
        heroDebate.classList.add("hidden");
        inputLabel.textContent = "Tu descripción";
        queryInput.placeholder = "Sigo dudando de una decisión que ya tomé…";
        searchBtn.textContent = "Buscar citas";
        actionHint.textContent = "Pulsa ⌘ / Ctrl + Enter para buscar";
    } else {
        modeDebateBtn.classList.add("active");
        modeSearchBtn.classList.remove("active");
        heroDebate.classList.remove("hidden");
        heroSearch.classList.add("hidden");
        inputLabel.textContent = "Pregunta filosófica";
        queryInput.placeholder = "¿Es más importante el conocimiento o la imaginación?";
        searchBtn.textContent = "Debatir";
        actionHint.textContent = "Pulsa ⌘ / Ctrl + Enter para debatir";
    }
    renderSuggestions();
    syncButton();
}

modeSearchBtn.addEventListener("click", () => setMode("search"));
modeDebateBtn.addEventListener("click", () => setMode("debate"));

function showState(state) {
    [loadingState, resultsSection, debateResultsSection, noResults, errorState, emptyState].forEach((el) =>
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
    searchBtn.textContent = currentMode === "search" ? "Leyendo…" : "Debatiendo…";
    showState(loadingState);

    try {
        if (currentMode === "search") {
            const data = await searchQuotes(query);
            const results = data.results || [];

            if (results.length === 0) {
                showState(noResults);
                return;
            }

            resultsCount.textContent = `${results.length} pasajes`;
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
        errorMessage.textContent = err.message || "Algo salió mal. Por favor, inténtalo de nuevo.";
        showState(errorState);
    } finally {
        searchBtn.textContent = currentMode === "search" ? "Buscar citas" : "Debatir";
        syncButton();
    }
}

searchBtn.addEventListener("click", handleSubmit);
queryInput.addEventListener("input", syncButton);
queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
});

setMode("search");
queryInput.focus();
