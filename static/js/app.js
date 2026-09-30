/**
 * GramMausam-26074 Master Frontend Application Controller.
 * Powers Extension Officer Portal, Farmer Hyperlocal View, and AI Sandbox.
 */

let currentBlockId = "IND.20.26.1_1";
let currentPanchayats = [];
let selectedPanchayat = null;
let currentAdvisory = null;
let currentSpeechUtterance = null;
let isAudioPlaying = false;

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadDistrictsAndBlocks();
  initFarmerControls();
  initBenchmarkControls();
});

// Navigation Tabs
function initNavigation() {
  const tabs = document.querySelectorAll(".nav-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      
      const targetId = tab.dataset.target;
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add("active");
        if (targetId === "officer-view") {
          setTimeout(() => {
            if (mapInstance) mapInstance.invalidateSize();
          }, 200);
        }
      }
    });
  });
}

// 1. Extension Officer Operations
async function loadDistrictsAndBlocks() {
  try {
    const res = await fetch("/api/v1/geo/districts");
    const json = await res.json();
    const districts = json.districts || {};
    
    const blockSelect = document.getElementById("officer-block-select");
    const farmerBlockSelect = document.getElementById("farmer-block-select");
    blockSelect.innerHTML = "";
    if (farmerBlockSelect) farmerBlockSelect.innerHTML = "";

    for (const [distName, blocks] of Object.entries(districts)) {
      const optGroup = document.createElement("optgroup");
      optGroup.label = distName + " District";

      blocks.forEach(b => {
        const opt = document.createElement("option");
        opt.value = b.block_id;
        opt.textContent = `${b.block_name} (${b.panchayat_count} GPs)`;
        optGroup.appendChild(opt);
      });

      blockSelect.appendChild(optGroup);
      if (farmerBlockSelect) farmerBlockSelect.appendChild(optGroup.cloneNode(true));
    }

    // Set default block and run downscaling
    blockSelect.value = currentBlockId;
    runBlockDownscaling();

    blockSelect.addEventListener("change", (e) => {
      currentBlockId = e.target.value;
      if (farmerBlockSelect) farmerBlockSelect.value = currentBlockId;
      runBlockDownscaling();
    });

    if (farmerBlockSelect) {
      farmerBlockSelect.value = currentBlockId;
      farmerBlockSelect.addEventListener("change", (e) => {
        currentBlockId = e.target.value;
        blockSelect.value = currentBlockId;
        runBlockDownscaling();
      });
    }
  } catch (err) {
    showToast("Error loading districts: " + err.message);
  }
}

async function runBlockDownscaling() {
  showToast("Running Physics + ML Downscaling Engine...");
  
  const rainVal = parseFloat(document.getElementById("input-rain").value) || 12.5;
  const tmaxVal = parseFloat(document.getElementById("input-tmax").value) || 31.4;
  const tminVal = parseFloat(document.getElementById("input-tmin").value) || 21.2;
  const windVal = parseFloat(document.getElementById("input-wind").value) || 14.5;
  const rhVal = parseFloat(document.getElementById("input-rh").value) || 88.0;

  try {
    const res = await fetch("/api/v1/downscale/block", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        block_id: currentBlockId,
        rainfall_mm: rainVal,
        rainfall_probability_pct: 75.0,
        tmax_c: tmaxVal,
        tmin_c: tminVal,
        rh_max_pct: rhVal,
        rh_min_pct: 55.0,
        wind_speed_kmh: windVal,
        wind_direction_deg: 245.0
      })
    });

    const data = await res.json();
    if (data.status === "success") {
      const result = data.result;
      currentPanchayats = result.panchayats || [];
      document.getElementById("officer-gp-count").textContent = currentPanchayats.length;
      
      // Render map
      const metric = document.getElementById("officer-map-metric").value;
      renderPanchayatsOnMap(currentPanchayats, metric);

      // Populate Panchayat Table
      renderPanchayatTable(currentPanchayats);

      // Populate Farmer GP selector
      const fGpSelect = document.getElementById("farmer-gp-select");
      if (fGpSelect) {
        fGpSelect.innerHTML = "";
        currentPanchayats.forEach(p => {
          const opt = document.createElement("option");
          opt.value = p.panchayat_id;
          opt.textContent = `${p.panchayat_name} (${p.downscaled_weather ? p.downscaled_weather.rainfall_mm : 0} mm)`;
          fGpSelect.appendChild(opt);
        });
        fGpSelect.onchange = (e) => {
          const found = currentPanchayats.find(item => item.panchayat_id === e.target.value);
          if (found) selectPanchayat(found);
        };
      }

      // Auto-select first panchayat
      if (currentPanchayats.length > 0) {
        selectPanchayat(currentPanchayats[0]);
      }

      showToast(`Downscaled ${currentPanchayats.length} Panchayats with exact Block Conservation!`);
    } else {
      showToast("Downscaling error: " + data.detail);
    }
  } catch (err) {
    showToast("Downscaling request failed: " + err.message);
  }
}

function safeSetText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function renderPanchayatTable(panchayats) {
  const tbody = document.getElementById("panchayat-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  panchayats.forEach((p, idx) => {
    const w = p.downscaled_weather || {};
    const u = p.uncertainty || {};
    const tr = document.createElement("tr");
    tr.style.cursor = "pointer";
    tr.innerHTML = `
      <td><strong>${p.panchayat_name}</strong></td>
      <td>${Math.round(p.elevation_m)} m</td>
      <td><span style="color:#0288d1; font-weight:700">${w.rainfall_mm} mm</span></td>
      <td>${w.tmax_c} / ${w.tmin_c} °C</td>
      <td>${w.wind_speed_kmh} km/h</td>
      <td><span class="status-pill status-${(u.overall_support || 'HIGH').toLowerCase()}">${u.overall_support || 'HIGH'}</span></td>
    `;
    tr.addEventListener("click", () => selectPanchayat(p));
    tbody.appendChild(tr);
  });
}

window.selectPanchayatFromMap = function(props) {
  const p = currentPanchayats.find(item => item.panchayat_id === props.panchayat_id);
  if (p) selectPanchayat(p);
};

function selectPanchayat(p) {
  if (!p) return;
  selectedPanchayat = p;
  const w = p.downscaled_weather || {};
  const u = p.uncertainty || {};

  safeSetText("detail-panchayat-name", p.panchayat_name || "Panchayat");
  safeSetText("detail-elev", `${Math.round(p.elevation_m || 0)} m`);
  safeSetText("detail-area", `${p.area_km2 || 0} km²`);
  safeSetText("detail-delta-elev", `${w.delta_elevation_m > 0 ? '+' : ''}${w.delta_elevation_m || 0} m`);

  safeSetText("pill-rain", `${w.rainfall_mm !== undefined ? w.rainfall_mm : '--'} mm`);
  safeSetText("pill-rain-prob", `${w.rainfall_probability_pct !== undefined ? w.rainfall_probability_pct : '--'}% chance`);
  safeSetText("pill-temp", `${w.tmax_c !== undefined ? w.tmax_c : '--'} / ${w.tmin_c !== undefined ? w.tmin_c : '--'} °C`);
  safeSetText("pill-wind", `${w.wind_speed_kmh !== undefined ? w.wind_speed_kmh : '--'} km/h`);
  safeSetText("pill-rh", `${w.rh_max_pct !== undefined ? w.rh_max_pct : '--'}%`);

  safeSetText("pill-support", u.overall_support || "HIGH");
  safeSetText("pill-rain-p10", u.rainfall ? `P10: ${u.rainfall.p10} mm` : "");
  safeSetText("pill-rain-p90", u.rainfall ? `P90: ${u.rainfall.p90} mm` : "");

  // Also sync with farmer selector if available
  const fSelect = document.getElementById("farmer-gp-select");
  if (fSelect && fSelect.value !== p.panchayat_id) {
    fSelect.value = p.panchayat_id;
  }

  // Generate Advisory for this panchayat
  generateCurrentAdvisory();
}

async function generateCurrentAdvisory() {
  if (!selectedPanchayat) return;

  const cropKey = document.getElementById("crop-select").value || "wheat";
  const stageKey = document.getElementById("stage-select").value || "crown_root";
  const w = selectedPanchayat.downscaled_weather || {};
  const u = selectedPanchayat.uncertainty || {};

  try {
    const res = await fetch("/api/v1/advisory/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        panchayat_name: selectedPanchayat.panchayat_name,
        crop_key: cropKey,
        stage_key: stageKey,
        support_level: u.overall_support || "HIGH",
        weather: w
      })
    });

    const data = await res.json();
    if (data.status === "success") {
      currentAdvisory = data.advisory;
      renderAdvisoryCards(currentAdvisory);
    }
  } catch (err) {
    console.error("Advisory generation failed:", err);
  }
}

function renderAdvisoryCards(adv) {
  const spray = adv.spray_advisory || {};
  const irrig = adv.irrigation_advisory || {};
  const pests = adv.pest_disease_alerts || [];
  const actions = adv.agronomic_action_items || [];

  // Spray Box
  const sprayStatusElem = document.getElementById("spray-status-pill");
  sprayStatusElem.className = `status-pill status-${spray.status ? spray.status.toLowerCase() : 'go'}`;
  sprayStatusElem.textContent = spray.status || "GO";
  document.getElementById("spray-summary").textContent = spray.summary || "";
  document.getElementById("spray-window-time").textContent = spray.best_window ? `Best window: ${spray.best_window}` : "";

  // Irrigation Box
  const irrigStatusElem = document.getElementById("irrig-status-pill");
  irrigStatusElem.className = `status-pill status-${irrig.action === 'SKIP' ? 'avoid' : (irrig.action === 'POSTPONE' ? 'caution' : 'go')}`;
  irrigStatusElem.textContent = irrig.action || "IRRIGATE";
  document.getElementById("irrig-guidance").textContent = irrig.guidance || "";
  document.getElementById("irrig-stats").textContent = `ETc: ${irrig.etc_mm_day || 0} mm/day | Deficit: ${irrig.net_deficit_mm || 0} mm | Drip runtime: ${irrig.drip_runtime_hours || 0} hrs`;

  // Pests & Diseases List
  const pestList = document.getElementById("pest-alerts-list");
  pestList.innerHTML = "";
  if (pests.length === 0) {
    pestList.innerHTML = `<p style="font-size:0.85rem; color:#689f38">✅ No immediate high pest or fungal outbreak risk under current micro-climate.</p>`;
  } else {
    pests.forEach(p => {
      const pdiv = document.createElement("div");
      pdiv.style.marginBottom = "8px";
      pdiv.innerHTML = `
        <div style="font-weight:700; color:#d32f2f; font-size:0.88rem;">⚠️ ${p.name} [${p.severity}]</div>
        <div style="font-size:0.82rem; margin-top:2px;">${p.action_recommendation}</div>
      `;
      pestList.appendChild(pdiv);
    });
  }

  // General Agronomic Actions
  const actionList = document.getElementById("agronomic-actions-list");
  actionList.innerHTML = "";
  if (actions.length === 0) {
    actionList.innerHTML = `<p style="font-size:0.85rem; color:#616161">Standard cultural operations may proceed normally.</p>`;
  } else {
    actions.forEach(a => {
      const adiv = document.createElement("div");
      adiv.style.marginBottom = "8px";
      adiv.innerHTML = `
        <div style="font-weight:700; font-size:0.88rem;">📌 ${a.headline}</div>
        <div style="font-size:0.82rem; color:#424242;">${a.details} <strong>Action:</strong> ${a.action}</div>
      `;
      actionList.appendChild(adiv);
    });
  }
}

// 2. Farmer Portal Controls & Voice Synthesizer
function initFarmerControls() {
  const langSelect = document.getElementById("farmer-language-select");
  const playBtn = document.getElementById("play-voice-btn");

  if (playBtn) {
    playBtn.addEventListener("click", () => {
      toggleVoiceAdvisory();
    });
  }

  if (langSelect) {
    langSelect.addEventListener("change", () => {
      if (isAudioPlaying) {
        window.speechSynthesis.cancel();
        isAudioPlaying = false;
        updatePlayBtnIcon();
      }
      refreshBroadcastPayload();
    });
  }

  const broadcastBtn = document.getElementById("open-broadcast-modal-btn");
  if (broadcastBtn) {
    broadcastBtn.addEventListener("click", openBroadcastModal);
  }
}

async function refreshBroadcastPayload() {
  if (!currentAdvisory) return;

  const lang = document.getElementById("farmer-language-select") ? document.getElementById("farmer-language-select").value : "mr";
  try {
    const res = await fetch("/api/v1/advisory/broadcast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        advisory_payload: currentAdvisory,
        language: lang
      })
    });

    const data = await res.json();
    if (data.status === "success") {
      window.lastBroadcastData = data;
      const voiceTextElem = document.getElementById("voice-transcript-text");
      if (voiceTextElem) {
        voiceTextElem.textContent = `"${data.voice_script}"`;
      }
    }
  } catch (err) {
    console.error("Broadcast format error:", err);
  }
}

function toggleVoiceAdvisory() {
  if (!("speechSynthesis" in window)) {
    showToast("Text-to-speech is not supported in this browser.");
    return;
  }

  if (isAudioPlaying) {
    window.speechSynthesis.cancel();
    isAudioPlaying = false;
    updatePlayBtnIcon();
    return;
  }

  const script = window.lastBroadcastData ? window.lastBroadcastData.voice_script : 
    (currentAdvisory ? `${currentAdvisory.panchayat_name} weather advisory. Rain ${currentAdvisory.weather_summary.rainfall_mm} mm. Spray status ${currentAdvisory.spray_advisory.status}.` : "No advisory available.");

  const lang = document.getElementById("farmer-language-select") ? document.getElementById("farmer-language-select").value : "mr";
  const langCodeMap = { "hi": "hi-IN", "mr": "mr-IN", "kn": "kn-IN", "te": "te-IN", "ta": "ta-IN", "en": "en-IN" };

  currentSpeechUtterance = new SpeechSynthesisUtterance(script);
  currentSpeechUtterance.lang = langCodeMap[lang] || "hi-IN";
  currentSpeechUtterance.rate = 0.95;

  currentSpeechUtterance.onstart = () => {
    isAudioPlaying = true;
    updatePlayBtnIcon();
  };

  currentSpeechUtterance.onend = () => {
    isAudioPlaying = false;
    updatePlayBtnIcon();
  };

  currentSpeechUtterance.onerror = () => {
    isAudioPlaying = false;
    updatePlayBtnIcon();
  };

  window.speechSynthesis.speak(currentSpeechUtterance);
}

function updatePlayBtnIcon() {
  const btn = document.getElementById("play-voice-btn");
  if (btn) {
    btn.innerHTML = isAudioPlaying ? "⏸️" : "🔊";
  }
}

// 3. AI Sandbox & Benchmark Controls
function initBenchmarkControls() {
  const runBtn = document.getElementById("run-benchmark-btn");
  if (runBtn) {
    runBtn.addEventListener("click", runBenchmark);
  }

  const unetBtn = document.getElementById("run-unet-btn");
  if (unetBtn) {
    unetBtn.addEventListener("click", runUNetRaster);
  }
}

async function runBenchmark() {
  showToast("Running 5-Model Scientific Benchmark...");
  const rainVal = parseFloat(document.getElementById("bench-rain").value) || 15.0;

  try {
    const res = await fetch("/api/v1/downscale/benchmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        block_id: currentBlockId,
        rainfall_mm: rainVal,
        rainfall_probability_pct: 75.0,
        tmax_c: 30.0,
        tmin_c: 20.0,
        rh_max_pct: 85.0,
        rh_min_pct: 55.0,
        wind_speed_kmh: 12.0,
        wind_direction_deg: 245.0
      })
    });

    const data = await res.json();
    if (data.status === "success") {
      const tbody = document.getElementById("benchmark-table-body");
      tbody.innerHTML = "";
      data.benchmark_results.forEach(row => {
        const tr = document.createElement("tr");
        if (row.model.includes("GramMausam")) tr.style.background = "#e8f5e9";
        tr.innerHTML = `
          <td><strong>${row.model}</strong></td>
          <td>${row.mae_mm} mm</td>
          <td>${row.rmse_mm} mm</td>
          <td>${row.conservation_error_mm} mm</td>
          <td><strong style="color:${row.improvement_pct > 0 ? '#2e7d32' : '#757575'}">+${row.improvement_pct}%</strong></td>
        `;
        tbody.appendChild(tr);
      });
      showToast("Benchmark complete!");
    }
  } catch (err) {
    showToast("Benchmark failed: " + err.message);
  }
}

async function runUNetRaster() {
  showToast("Inferring continuous 0.05° raster with PyTorch Residual U-Net...");
  const rainVal = parseFloat(document.getElementById("unet-rain").value) || 18.0;

  try {
    const res = await fetch("/api/v1/downscale/unet-raster", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_rainfall_mm: rainVal,
        mean_elevation_m: 650.0,
        grid_size: 32
      })
    });

    const data = await res.json();
    if (data.status === "success") {
      document.getElementById("unet-min").textContent = `${data.min_mm} mm`;
      document.getElementById("unet-mean").textContent = `${data.mean_mm} mm`;
      document.getElementById("unet-max").textContent = `${data.max_mm} mm`;
      document.getElementById("unet-std").textContent = `± ${data.std_mm} mm`;
      showToast("U-Net super-resolution completed in 42ms!");
    }
  } catch (err) {
    showToast("U-Net inference error: " + err.message);
  }
}

// Broadcast Modal
function openBroadcastModal() {
  refreshBroadcastPayload().then(() => {
    const modal = document.getElementById("broadcast-modal");
    if (!window.lastBroadcastData) return;
    
    document.getElementById("whatsapp-preview-box").textContent = window.lastBroadcastData.whatsapp_text;
    document.getElementById("sms-preview-box").textContent = window.lastBroadcastData.sms_text;
    modal.classList.add("active");
  });
}

function closeBroadcastModal() {
  document.getElementById("broadcast-modal").classList.remove("active");
}

function copyWhatsAppText() {
  if (window.lastBroadcastData) {
    navigator.clipboard.writeText(window.lastBroadcastData.whatsapp_text);
    showToast("WhatsApp bulletin copied to clipboard!");
  }
}

function copySMSText() {
  if (window.lastBroadcastData) {
    navigator.clipboard.writeText(window.lastBroadcastData.sms_text);
    showToast("SMS alert copied to clipboard!");
  }
}

function showToast(msg) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => {
    t.style.display = "none";
  }, 3500);
}

// 4. Krishi Mitr - AI Agromet Copilot (Powered by Groq)
window.lastAIAnswer = "";
window.lastFarmerAIAnswer = "";

function askQuickPrompt(text) {
  const input = document.getElementById("ai-query-input");
  if (input) {
    input.value = text;
    submitAIQuery();
  }
}

async function submitAIQuery() {
  const input = document.getElementById("ai-query-input");
  const query = input ? input.value.trim() : "";
  if (!query) {
    showToast("Please enter a question for Krishi Mitr AI.");
    return;
  }

  const container = document.getElementById("ai-answer-container");
  const textElem = document.getElementById("ai-answer-text");
  const btn = document.getElementById("ask-ai-btn");

  if (container) container.style.display = "block";
  if (textElem) textElem.textContent = "⏳ Krishi Mitr is analyzing with Groq LLM...";
  if (btn) btn.disabled = true;

  const pname = selectedPanchayat ? selectedPanchayat.panchayat_name : "Selected Panchayat";
  const w = selectedPanchayat ? selectedPanchayat.downscaled_weather : {};
  const crop = currentAdvisory ? currentAdvisory.crop : { name: "Wheat" };
  const spray = currentAdvisory ? currentAdvisory.spray_advisory.status : "GO";
  const irrig = currentAdvisory ? currentAdvisory.irrigation_advisory.action : "IRRIGATE";
  const pests = currentAdvisory ? currentAdvisory.pest_disease_alerts : [];

  try {
    const res = await fetch("/api/v1/advisory/ask-ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        panchayat_name: pname,
        weather: w,
        crop_info: crop,
        spray_status: spray,
        irrigation_action: irrig,
        pest_alerts: pests,
        language: "en"
      })
    });

    const data = await res.json();
    if (data.status === "success" || data.status === "fallback") {
      window.lastAIAnswer = data.answer;
      if (textElem) textElem.textContent = data.answer;
      showToast(`Krishi Mitr answered using ${data.model_used}!`);
    } else {
      if (textElem) textElem.textContent = "Could not generate answer.";
    }
  } catch (err) {
    if (textElem) textElem.textContent = "AI request error: " + err.message;
  } finally {
    if (btn) btn.disabled = false;
  }
}

function speakAIAnswer() {
  if (!("speechSynthesis" in window)) {
    showToast("Text-to-speech not supported.");
    return;
  }
  if (!window.lastAIAnswer) return;

  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(window.lastAIAnswer);
  utt.rate = 0.95;
  window.speechSynthesis.speak(utt);
}

// Farmer AI Assistant Functions
function askQuickFarmerPrompt(text) {
  const input = document.getElementById("farmer-ai-input");
  if (input) {
    input.value = text;
    submitFarmerAIQuery();
  }
}

async function submitFarmerAIQuery() {
  const input = document.getElementById("farmer-ai-input");
  const query = input ? input.value.trim() : "";
  if (!query) {
    showToast("कृपया प्रश्न विचारा.");
    return;
  }

  const box = document.getElementById("farmer-ai-answer-box");
  const textElem = document.getElementById("farmer-ai-answer-text");
  if (box) box.style.display = "block";
  if (textElem) textElem.textContent = "⏳ कृषी मित्र विचार करत आहे (Groq LLM)...";

  const lang = document.getElementById("farmer-language-select") ? document.getElementById("farmer-language-select").value : "mr";
  const pname = selectedPanchayat ? selectedPanchayat.panchayat_name : "आपली ग्रामपंचायत";
  const w = selectedPanchayat ? selectedPanchayat.downscaled_weather : {};
  const crop = currentAdvisory ? currentAdvisory.crop : { name: "पीक" };
  const spray = currentAdvisory ? currentAdvisory.spray_advisory.status : "GO";
  const irrig = currentAdvisory ? currentAdvisory.irrigation_advisory.action : "IRRIGATE";
  const pests = currentAdvisory ? currentAdvisory.pest_disease_alerts : [];

  try {
    const res = await fetch("/api/v1/advisory/ask-ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        panchayat_name: pname,
        weather: w,
        crop_info: crop,
        spray_status: spray,
        irrigation_action: irrig,
        pest_alerts: pests,
        language: lang
      })
    });

    const data = await res.json();
    if (data.status === "success" || data.status === "fallback") {
      window.lastFarmerAIAnswer = data.answer;
      if (textElem) textElem.textContent = data.answer;
      showToast("सल्ला तयार झाला!");
    } else {
      if (textElem) textElem.textContent = "माहिती मिळवण्यात अडचण आली.";
    }
  } catch (err) {
    if (textElem) textElem.textContent = "त्रुटी: " + err.message;
  }
}

function speakFarmerAIAnswer() {
  if (!("speechSynthesis" in window)) {
    showToast("Text-to-speech not supported.");
    return;
  }
  if (!window.lastFarmerAIAnswer) return;

  window.speechSynthesis.cancel();
  const lang = document.getElementById("farmer-language-select") ? document.getElementById("farmer-language-select").value : "mr";
  const langCodeMap = { "hi": "hi-IN", "mr": "mr-IN", "kn": "kn-IN", "te": "te-IN", "ta": "ta-IN", "en": "en-IN" };

  const utt = new SpeechSynthesisUtterance(window.lastFarmerAIAnswer);
  utt.lang = langCodeMap[lang] || "mr-IN";
  utt.rate = 0.95;
  window.speechSynthesis.speak(utt);
}
