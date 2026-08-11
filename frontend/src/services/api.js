const API_BASE = "/api/v1";

/**
 * Send a search query to the semantic search API.
 * @param {string} query - The user's free-text description.
 * @returns {Promise<{results: Array<{id: number, quote: string, author: string}>}>}
 */
export async function searchQuotes(query) {
    const response = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Search failed" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

/**
 * Send a philosophical query to the debate API.
 * @param {string} query - The user's question.
 * @returns {Promise<{success: boolean, essay: string, sources: Array<{id: number, quote: string, author: string}>}>}
 */
export async function debateQuotes(query) {
    const response = await fetch(`${API_BASE}/debate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Debate failed" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}
