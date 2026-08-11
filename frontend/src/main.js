import { searchQuotes } from "./services/api.js";

const queryInput = document.getElementById("query-input");
const searchBtn = document.getElementById("search-btn");
const loadingState = document.getElementById("loading-state");
const resultsSection = document.getElementById("results-section");
const resultsContainer = document.getElementById("results-container");
const resultsCount = document.getElementById("results-count");
const noResults = document.getElementById("no-results");
const errorState = document.getElementById("error-state");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const suggestionsEl = document.getElementById("suggestions");

const SUGGESTIONS = [
    "starting over after a failure",
    "the quiet before a big decision",
    "loving someone from far away",
    "why patience is not passivity",
];

SUGGESTIONS.forEach((text) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = text;
    btn.addEventListener("click", () => {
        queryInput.value = text;
        syncButton();
        handleSearch();
    });
    suggestionsEl.appendChild(btn);
});

function showState(state) {
    [loadingState, resultsSection, noResults, errorState, emptyState].forEach((el) =>
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

async function handleSearch() {
    const query = queryInput.value.trim();
    if (!query) return;

    searchBtn.disabled = true;
    searchBtn.textContent = "Reading…";
    showState(loadingState);

    try {
        const data = await searchQuotes(query);
        const results = data.results || [];

        if (results.length === 0) {
            showState(noResults);
            return;
        }

        resultsCount.textContent = `${results.length} passages`;
        resultsContainer.innerHTML = results.map(renderQuoteCard).join("");
        showState(resultsSection);
    } catch (err) {
        errorMessage.textContent = err.message || "Something went wrong. Please try again.";
        showState(errorState);
    } finally {
        searchBtn.textContent = "Find quotes";
        syncButton();
    }
}

searchBtn.addEventListener("click", handleSearch);
queryInput.addEventListener("input", syncButton);
queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSearch();
});

syncButton();
queryInput.focus();
