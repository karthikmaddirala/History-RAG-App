const BACKEND = "http://localhost:8000";

function switchTab(which) {
  for (const t of ["chat", "search"]) {
    document.getElementById(`tab-${t}`).classList.toggle("active", t === which);
    document.getElementById(`pane-${t}`).classList.toggle("active", t === which);
  }
}
document.getElementById("tab-chat").onclick = () => switchTab("chat");
document.getElementById("tab-search").onclick = () => switchTab("search");

const input = document.getElementById("chat-input");
const results = document.getElementById("results");

input.addEventListener("keydown", async e => {
  if (e.key !== "Enter" || !input.value.trim()) return;
  const query = input.value.trim();
  results.innerHTML = "<p>Searching...</p>";
  try {
    const res = await fetch(`${BACKEND}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    render(data.hits || []);
  } catch (err) {
    results.innerHTML = `<p style="color:red">Error: ${err.message}. Is the backend running?</p>`;
  }
});

function render(hits) {
  if (!hits.length) { results.innerHTML = "<p>No matches found.</p>"; return; }
  results.innerHTML = hits.map(h => {
    const m = h.metadata;
    const date = new Date(m.visit_time * 1000).toLocaleDateString();
    return `<div class="hit">
      <a href="${m.url}" target="_blank">${escapeHtml(m.title)}</a>
      <div class="meta">${m.domain} · ${date}</div>
    </div>`;
  }).join("");
}

function escapeHtml(s) {
  return (s || "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
