const statusEl = document.getElementById("status");
const ping = document.getElementById("ping");

function baseUrl() {
  const d = import.meta.env.VITE_LEXIE_BASE_URL;
  if (d && d.length) return d.replace(/\/$/, "");
  return "";
}

async function checkHealth() {
  statusEl.style.display = "block";
  const direct = baseUrl();
  const url = direct
    ? `${direct}/health`
    : "/__lexie/health";
  const t0 = performance.now();
  try {
    const res = await fetch(url, { method: "GET" });
    const t1 = performance.now();
    const text = await res.text();
    let body;
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
    const ms = Math.round(t1 - t0);
    statusEl.innerHTML = "";
    const title = res.ok
      ? `<p class="ok">HTTP ${res.status} — up (${ms} ms client round-trip, not full STT path)</p>`
      : `<p class="err">HTTP ${res.status}</p>`;
    statusEl.insertAdjacentHTML("beforeend", title);
    statusEl.insertAdjacentHTML("beforeend", "<pre></pre>");
    statusEl.querySelector("pre").textContent =
      typeof body === "string" ? body : JSON.stringify(body, null, 2);
  } catch (e) {
    statusEl.innerHTML = `<p class="err">Fetch failed: ${e.message}</p>
      <p style="color:#7b82a8;font-size:0.9rem">If CORS: use <code>npm run dev</code> + proxy, or add your origin in FastAPI <code>LEXIE_CORS_ORIGINS</code>.</p>`;
  }
}

ping.addEventListener("click", checkHealth);
checkHealth();
