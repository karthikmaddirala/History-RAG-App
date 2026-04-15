// Syncs chrome.history to the backend. Runs on install, on each new visit,
// and on a 30-min alarm as a safety-net.

const BACKEND = "http://localhost:8000";
const BATCH_SIZE = 100;
const SYNC_ALARM = "history-sync";

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create(SYNC_ALARM, { periodInMinutes: 30 });
  syncHistory(Date.now() - 30 * 24 * 3600 * 1000); // backfill last 30 days
});

chrome.alarms.onAlarm.addListener(a => {
  if (a.name === SYNC_ALARM) incrementalSync();
});

chrome.history.onVisited.addListener(async item => {
  await postBatch([toEntry(item)]);
});

chrome.action.onClicked.addListener(tab => {
  chrome.sidePanel.open({ tabId: tab.id });
});

async function incrementalSync() {
  const { lastSync = Date.now() - 24 * 3600 * 1000 } =
    await chrome.storage.local.get("lastSync");
  await syncHistory(lastSync);
}

async function syncHistory(startTime) {
  const items = await chrome.history.search({
    text: "", startTime, maxResults: 10000
  });
  for (let i = 0; i < items.length; i += BATCH_SIZE) {
    await postBatch(items.slice(i, i + BATCH_SIZE).map(toEntry));
  }
  await chrome.storage.local.set({ lastSync: Date.now() });
}

function toEntry(h) {
  return {
    url: h.url,
    title: h.title || "",
    visit_time: Math.floor((h.lastVisitTime || Date.now()) / 1000),
    visit_count: h.visitCount || 1
  };
}

async function postBatch(entries) {
  if (!entries.length) return;
  try {
    await fetch(`${BACKEND}/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entries })
    });
  } catch (e) {
    console.error("ingest failed", e);
  }
}
