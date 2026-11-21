// Azure AI Foundry Suite - Client Application
// Author: Arnav Sharma (Chandigarh University)
// AI-901 Industrial Internship Project

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initResponsibleAI();
  initModelAndNlpWorkloads();
  initExamEngine();
});

/* ----------------------------------------------------
   1. TAB NAVIGATION
---------------------------------------------------- */
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab-btn");
  const panes = document.querySelectorAll(".tab-pane");

  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      tabs.forEach(t => t.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

/* ----------------------------------------------------
   2. RESPONSIBLE AI (WEEK 1)
---------------------------------------------------- */
let predefinedScenarios = [];

async function initResponsibleAI() {
  const select = document.getElementById("predefinedScenarioSelect");
  const btnLoad = document.getElementById("btnLoadPredefinedScenario");
  const detailsBox = document.getElementById("predefinedDetailsBox");
  const btnAudit = document.getElementById("btnAuditScenario");
  const customInput = document.getElementById("customScenarioInput");

  try {
    const res = await fetch("/api/responsible-ai/scenarios");
    const data = await res.json();
    predefinedScenarios = data.scenarios || [];

    function updateDetails() {
      const selected = predefinedScenarios.find(s => s.id === select.value);
      if (selected && detailsBox) {
        detailsBox.innerHTML = `
          <strong>Domain:</strong> ${selected.domain}<br>
          <strong>Scenario:</strong> ${selected.description}<br>
          <strong>Primary Concerns:</strong> <span class="badge badge-warning">${selected.primary_risks.join(", ")}</span>
        `;
      }
    }

    if (select) {
      select.addEventListener("change", updateDetails);
      updateDetails();
    }

    if (btnLoad) {
      btnLoad.addEventListener("click", () => {
        const selected = predefinedScenarios.find(s => s.id === select.value);
        if (selected && customInput) {
          customInput.value = selected.description;
          runRaiAudit(selected.description);
        }
      });
    }
  } catch (err) {
    console.error("Failed to load predefined scenarios:", err);
  }

  if (btnAudit) {
    btnAudit.addEventListener("click", () => {
      const text = customInput ? customInput.value.trim() : "";
      if (!text) {
        alert("Please enter a scenario description or prompt to audit.");
        return;
      }
      runRaiAudit(text);
    });
  }
}

async function runRaiAudit(text) {
  const container = document.getElementById("raiAuditResultContainer");
  const scoreDisplay = document.getElementById("raiScoreDisplay");
  const statusText = document.getElementById("raiStatusText");
  const badgePill = document.getElementById("raiBadgePill");
  const principlesGrid = document.getElementById("raiPrincipleScoresGrid");
  const risksBox = document.getElementById("raiRisksBox");
  const remediationsBox = document.getElementById("raiRemediationsBox");

  try {
    const res = await fetch("/api/responsible-ai/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_text: text })
    });
    const result = await res.json();

    if (container) container.style.display = "block";
    if (scoreDisplay) scoreDisplay.textContent = `${result.overall_score}/100`;
    if (statusText) statusText.textContent = `Audit Assessment: ${result.status}`;
    
    const subtitle = document.getElementById("raiSubtitle");
    if (subtitle) {
      if (result.audit_engine) {
        subtitle.innerHTML = `<span style="color: var(--accent-cyan); font-weight: 600;"><i class="fa-solid fa-cloud-bolt"></i> Live LLM Audit Engine: ${result.audit_engine}</span>`;
      } else {
        subtitle.textContent = "Microsoft Responsible AI Standard v2 Scorecard";
      }
    }

    if (badgePill) {
      const colorClass = result.badge_color === "success" ? "badge-success" : (result.badge_color === "warning" ? "badge-warning" : "badge-danger");
      badgePill.innerHTML = `<span class="badge ${colorClass}">${result.status}</span>`;
    }

    // Principle breakdown
    if (principlesGrid) {
      principlesGrid.innerHTML = "";
      for (const [key, val] of Object.entries(result.principles_breakdown)) {
        const title = key.replace("_", " ").toUpperCase();
        const statColor = val.status === "Good" ? "var(--success)" : ((val.status === "Critical" || val.score <= 30) ? "var(--danger)" : "var(--warning)");
        principlesGrid.innerHTML += `
          <div style="background: var(--bg-card); padding: 0.8rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700;">
              <span>${title}</span>
              <span style="color: ${statColor};">${val.score}%</span>
            </div>
            <div style="background: var(--bg-secondary); height: 6px; border-radius: 3px; margin-top: 0.4rem; overflow:hidden;">
              <div style="width: ${val.score}%; background: ${statColor}; height: 100%;"></div>
            </div>
          </div>
        `;
      }
    }

    // Risks
    if (risksBox) {
      if (result.identified_risks && result.identified_risks.length > 0) {
        risksBox.innerHTML = `
          <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger); padding: 0.8rem; border-radius: var(--radius-sm); margin-bottom: 0.8rem;">
            <strong style="color: var(--danger); font-size: 0.85rem;"><i class="fa-solid fa-triangle-exclamation"></i> Identified Compliance Risks:</strong>
            <ul style="font-size: 0.82rem; margin-left: 1.2rem; margin-top: 0.3rem;">
              ${result.identified_risks.map(r => `<li>${r}</li>`).join("")}
            </ul>
          </div>
        `;
      } else {
        risksBox.innerHTML = `
          <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid var(--success); padding: 0.8rem; border-radius: var(--radius-sm); margin-bottom: 0.8rem;">
            <strong style="color: var(--success); font-size: 0.85rem;"><i class="fa-solid fa-circle-check"></i> No High-Risk Violations Flagged.</strong>
          </div>
        `;
      }
    }

    // Remediations
    if (remediationsBox) {
      remediationsBox.innerHTML = `
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 0.8rem; border-radius: var(--radius-sm);">
          <strong style="color: var(--accent-blue); font-size: 0.85rem;"><i class="fa-solid fa-clipboard-list"></i> Microsoft Responsible AI Remediation Actions:</strong>
          <ul style="font-size: 0.82rem; margin-left: 1.2rem; margin-top: 0.3rem; color: var(--text-secondary);">
            ${result.remediations.map(act => `<li>${act}</li>`).join("")}
          </ul>
        </div>
      `;
    }
  } catch (err) {
    console.error("Audit error:", err);
  }
}

/* ----------------------------------------------------
   3. MODELS & NLP WORKLOADS (WEEK 2)
---------------------------------------------------- */
function initModelAndNlpWorkloads() {
  const tokenInput = document.getElementById("tokenInputText");
  const charSpan = document.getElementById("tokenCharCount");
  const wordSpan = document.getElementById("tokenWordCount");
  const tokSpan = document.getElementById("tokenTokenCount");

  if (tokenInput) {
    tokenInput.addEventListener("input", async () => {
      const text = tokenInput.value;
      if (!text) {
        charSpan.textContent = "0";
        wordSpan.textContent = "0";
        tokSpan.textContent = "0";
        return;
      }
      try {
        const res = await fetch("/api/foundry/calculate-tokens", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });
        const data = await res.json();
        charSpan.textContent = data.character_count;
        wordSpan.textContent = data.word_count;
        tokSpan.textContent = data.estimated_tokens;
      } catch (e) {
        charSpan.textContent = text.length;
        wordSpan.textContent = text.split(/\s+/).filter(Boolean).length;
        tokSpan.textContent = Math.ceil(text.length / 4);
      }
    });
  }

  // Load Sample Agreement button
  const btnLoadContract = document.getElementById("btnLoadSampleContract");
  const nlpInput = document.getElementById("nlpInputText");
  if (btnLoadContract && nlpInput) {
    btnLoadContract.addEventListener("click", () => {
      nlpInput.value = `Contoso Global AI Platforms Inc. agrees to deliver managed cloud AI services through Microsoft Foundry to Chandigarh University. Provider warrants an overall availability uptime of 99.95% during each billing cycle. Model response latency for standard generative completion queries shall not exceed 850 milliseconds. All user data is encrypted in transit using TLS 1.3 and at rest using AES-256 bit keys. In high-stakes healthcare and credit scoring domains, human-in-the-loop verification is mandatory. Audit logs shall be preserved for 365 calendar days.`;
      runNlp();
    });
  }

  // Run NLP Analysis button
  const btnRunNlp = document.getElementById("btnRunNlpAnalysis");
  if (btnRunNlp) {
    btnRunNlp.addEventListener("click", runNlp);
  }
}

async function runNlp() {
  const nlpInput = document.getElementById("nlpInputText");
  const container = document.getElementById("nlpResultContainer");
  const text = nlpInput ? nlpInput.value.trim() : "";

  if (!text) {
    alert("Please enter text to analyze.");
    return;
  }

  try {
    const res = await fetch("/api/text-analysis/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();

    if (container) container.style.display = "block";

    const subtitle = document.getElementById("nlpEngineSubtitle");
    if (subtitle && data.engine) {
      subtitle.innerHTML = `<span style="color: var(--accent-cyan); font-weight: 600;"><i class="fa-solid fa-cloud-bolt"></i> Live Engine: ${data.engine}</span>`;
    }

    // Sentiment
    const sBadge = document.getElementById("nlpSentimentBadge");
    if (sBadge) {
      sBadge.textContent = data.sentiment.sentiment;
      sBadge.className = `badge badge-${data.sentiment.badge}`;
    }
    document.getElementById("nlpPolarityVal").textContent = data.sentiment.polarity;
    document.getElementById("nlpSubjectivityVal").textContent = data.sentiment.subjectivity;
    document.getElementById("nlpConfidenceVal").textContent = `${Math.round(data.sentiment.confidence * 100)}%`;

    // Entities
    const entitiesBox = document.getElementById("nlpEntitiesPills");
    if (entitiesBox) {
      entitiesBox.innerHTML = "";
      if (data.entities.length === 0) {
        entitiesBox.innerHTML = `<span style="font-size:0.8rem; color:var(--text-muted);">No named entities detected.</span>`;
      } else {
        data.entities.forEach(ent => {
          entitiesBox.innerHTML += `
            <span class="badge badge-purple" title="Confidence: ${Math.round(ent.confidence * 100)}%">
              <strong>${ent.text}</strong> [${ent.category}]
            </span>
          `;
        });
      }
    }

    // Keyphrases
    const kpBox = document.getElementById("nlpKeyphrasesPills");
    if (kpBox) {
      kpBox.innerHTML = "";
      data.keyphrases.forEach(kp => {
        kpBox.innerHTML += `
          <span class="badge badge-info">
            ${kp.phrase} <small>(${kp.frequency})</small>
          </span>
        `;
      });
    }

    // Summary
    document.getElementById("nlpCompressionRatio").textContent = data.summary.compression_ratio;
    document.getElementById("nlpSummaryText").textContent = data.summary.summary;

  } catch (err) {
    console.error("NLP analysis error:", err);
  }
}

/* ----------------------------------------------------
   4. FOUNDRY CHAT & AGENTS (WEEK 3)
---------------------------------------------------- */
let chatHistory = [];
let lastAssistantSpeech = "";

function initFoundryChat() {
  const tempSlider = document.getElementById("chatTempSlider");
  const tempLabel = document.getElementById("tempValLabel");
  const btnSend = document.getElementById("btnSendFoundryChat");
  const queryInput = document.getElementById("chatUserQueryInput");
  const btnSpeak = document.getElementById("btnSpeakLastResponse");

  if (tempSlider && tempLabel) {
    tempSlider.addEventListener("input", () => {
      tempLabel.textContent = tempSlider.value;
    });
  }

  if (btnSend && queryInput) {
    btnSend.addEventListener("click", () => sendChat());
    queryInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendChat();
    });
  }

  if (btnSpeak) {
    btnSpeak.addEventListener("click", () => {
      if (!lastAssistantSpeech) {
        alert("No assistant message to read aloud yet.");
        return;
      }
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(lastAssistantSpeech);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      } else {
        alert("Web Speech API not supported in this browser.");
      }
    });
  }
}

async function sendChat() {
  const queryInput = document.getElementById("chatUserQueryInput");
  const chatMessages = document.getElementById("foundryChatMessages");
  const sysPromptInput = document.getElementById("chatSystemPrompt");
  const modelSelect = document.getElementById("chatModelSelect");
  const tempSlider = document.getElementById("chatTempSlider");
  const metricsRow = document.getElementById("chatMetricsRow");

  const query = queryInput.value.trim();
  if (!query) return;

  // Add User bubble
  chatMessages.innerHTML += `
    <div class="chat-bubble bubble-user">${query}</div>
  `;
  queryInput.value = "";
  chatMessages.scrollTop = chatMessages.scrollHeight;

  chatHistory.push({ role: "user", content: query });

  try {
    const res = await fetch("/api/foundry/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: chatHistory,
        model: modelSelect ? modelSelect.value : "gpt-4o",
        temperature: parseFloat(tempSlider ? tempSlider.value : 0.7),
        system_prompt: sysPromptInput ? sysPromptInput.value : ""
      })
    });
    const data = await res.json();

    lastAssistantSpeech = data.response.replace(/[\*#_`]/g, "");

    // Format Markdown bolding
    const formatted = data.response
      .replace(/\n\n/g, "<br><br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/•/g, "&bull;");

    chatMessages.innerHTML += `
      <div class="chat-bubble bubble-assistant">${formatted}</div>
    `;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    chatHistory.push({ role: "assistant", content: data.response });

    if (metricsRow) {
      metricsRow.innerHTML = `
        <span>Latency: <strong>${data.latency_ms} ms</strong> (${data.provider})</span>
        <span>Prompt Toks: ${data.usage.prompt_tokens} | Comp Toks: ${data.usage.completion_tokens}</span>
      `;
    }
  } catch (err) {
    console.error("Chat error:", err);
  }
}

/* ----------------------------------------------------
   4B. SINGLE-AGENT SOLUTION
---------------------------------------------------- */
function initFoundryAgent() {
  const btnRun = document.getElementById("btnRunAgent");
  const goalInput = document.getElementById("agentGoalInput");
  const timeline = document.getElementById("agentTimelineContainer");
  const ansBox = document.getElementById("agentFinalAnswerBox");
  const ansContent = document.getElementById("agentFinalAnswerContent");

  if (btnRun && goalInput) {
    btnRun.addEventListener("click", async () => {
      const goal = goalInput.value.trim();
      if (!goal) return;

      timeline.innerHTML = `
        <div class="timeline-item">
          <div class="timeline-dot dot-thought"></div>
          <div class="timeline-card">
            <strong style="color:var(--accent-purple);">PLANNING</strong>
            <div style="font-size:0.84rem; color:var(--text-secondary);">Agent is analyzing goal and choosing tool sequence...</div>
          </div>
        </div>
      `;
      ansBox.style.display = "none";

      try {
        const res = await fetch("/api/foundry/agent", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ goal })
        });
        const data = await res.json();

        timeline.innerHTML = "";
        data.execution_steps.forEach(st => {
          let dotClass = "dot-thought";
          let badgeText = "THOUGHT";
          let badgeColor = "var(--accent-purple)";

          if (st.type === "action") {
            dotClass = "dot-action";
            badgeText = `ACTION: [${st.tool}]`;
            badgeColor = "var(--accent-blue)";
          } else if (st.type === "observation") {
            dotClass = "dot-observation";
            badgeText = "OBSERVATION";
            badgeColor = "var(--success)";
          }

          let innerHtml = `<strong style="color:${badgeColor}; font-size:0.82rem;">Step ${st.step} • ${badgeText}</strong>`;
          if (st.content) {
            innerHtml += `<div style="font-size:0.84rem; color:var(--text-primary); margin-top:0.2rem;">${st.content}</div>`;
          }
          if (st.arguments) {
            innerHtml += `<div style="font-size:0.8rem; font-family:monospace; background:rgba(0,0,0,0.3); padding:0.3rem 0.5rem; border-radius:4px; margin-top:0.3rem;">Args: ${JSON.stringify(st.arguments)}</div>`;
          }
          if (st.observation) {
            innerHtml += `<div style="font-size:0.84rem; color:var(--success); margin-top:0.3rem;">↳ <em>${st.observation}</em></div>`;
          }

          timeline.innerHTML += `
            <div class="timeline-item">
              <div class="timeline-dot ${dotClass}"></div>
              <div class="timeline-card">${innerHtml}</div>
            </div>
          `;
        });

        // Final Answer
        ansBox.style.display = "block";
        ansContent.innerHTML = data.final_answer.replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

      } catch (err) {
        console.error("Agent run error:", err);
      }
    });
  }
}

/* ----------------------------------------------------
   5. VISION & IMAGE STUDIO (WEEK 4)
---------------------------------------------------- */
function initVisionStudio() {
  const btnAnalyze = document.getElementById("btnAnalyzeVision");
  const presetSelect = document.getElementById("visionPresetSelect");
  const questionInput = document.getElementById("visionQuestionInput");
  const uploadInput = document.getElementById("visionUploadInput");

  let uploadedBase64 = null;

  if (uploadInput) {
    uploadInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          uploadedBase64 = reader.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  if (btnAnalyze) {
    btnAnalyze.addEventListener("click", async () => {
      const presetId = presetSelect ? presetSelect.value : "sample_invoice";
      const question = questionInput ? questionInput.value.trim() : "";

      try {
        const res = await fetch("/api/vision/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            preset_id: presetId,
            question: question || null,
            image_data: uploadedBase64
          })
        });
        const data = await res.json();

        document.getElementById("visionCaptionTitle").textContent = data.image_name || "Visual Scene Overview";
        document.getElementById("visionCaptionText").textContent = data.caption || "";

        const pills = document.getElementById("visionObjectsPills");
        pills.innerHTML = "";
        data.detected_objects.forEach(obj => {
          pills.innerHTML += `
            <span class="badge badge-info">
              ${obj.label} <small>(${Math.round(obj.confidence * 100)}%)</small>
            </span>
          `;
        });

        document.getElementById("visionVqaAnswerText").textContent = data.vqa_answer || "Visual inspection complete.";

      } catch (err) {
        console.error("Vision analyze error:", err);
      }
    });
  }

  // Generative Artwork (DALL-E 3)
  const btnGen = document.getElementById("btnGenerateVisual");
  const promptInput = document.getElementById("genImagePrompt");
  const styleSelect = document.getElementById("genImageStyle");
  const aspectSelect = document.getElementById("genImageAspect");
  const canvasWrapper = document.getElementById("genImageCanvasWrapper");

  if (btnGen && promptInput) {
    btnGen.addEventListener("click", async () => {
      const prompt = promptInput.value.trim();
      if (!prompt) return;

      canvasWrapper.innerHTML = `<div style="color:var(--text-secondary);"><i class="fa-solid fa-spinner fa-spin"></i> Rendering neural canvas...</div>`;

      try {
        const res = await fetch("/api/vision/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt,
            style: styleSelect ? styleSelect.value : "Azure Blueprint",
            aspect_ratio: aspectSelect ? aspectSelect.value : "16:9"
          })
        });
        const data = await res.json();
        canvasWrapper.innerHTML = data.svg_image;
      } catch (err) {
        console.error("Image gen error:", err);
      }
    });
  }
}

/* ----------------------------------------------------
   6. CONTENT UNDERSTANDING (WEEK 4)
---------------------------------------------------- */
function initContentUnderstanding() {
  const btnDoc = document.getElementById("btnRunDocumentExtraction");
  const btnAudio = document.getElementById("btnRunAudioExtraction");

  if (btnDoc) {
    btnDoc.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/content-understanding/document", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();

        document.getElementById("docExtractResultBox").style.display = "block";
        document.getElementById("docExtractStatusBadge").textContent = data.validation.status;

        const grid = document.getElementById("docFieldsGrid");
        grid.innerHTML = "";
        for (const [k, v] of Object.entries(data.extracted_fields)) {
          grid.innerHTML += `
            <div style="background:var(--bg-card); padding:0.5rem 0.8rem; border-radius:4px;">
              <span style="color:var(--text-muted); text-transform:uppercase; font-size:0.75rem;">${k.replace("_", " ")}</span>:
              <strong style="color:var(--accent-blue);">${v.value}</strong>
            </div>
          `;
        }

        const tbody = document.querySelector("#docLineItemsTable tbody");
        tbody.innerHTML = "";
        data.line_items.forEach(item => {
          tbody.innerHTML += `
            <tr>
              <td>${item.item}</td>
              <td>${item.description}</td>
              <td>${item.qty}</td>
              <td>$${item.unit_price.toFixed(2)}</td>
              <td><strong>$${item.total.toFixed(2)}</strong></td>
            </tr>
          `;
        });
      } catch (err) {
        console.error("Doc extract error:", err);
      }
    });
  }

  if (btnAudio) {
    btnAudio.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/content-understanding/audio", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();

        document.getElementById("audioExtractResultBox").style.display = "block";

        const list = document.getElementById("audioUtterancesList");
        list.innerHTML = "";
        data.utterances.forEach(u => {
          list.innerHTML += `
            <div style="background:var(--bg-card); padding:0.5rem 0.8rem; border-radius:4px; font-size:0.8rem;">
              <span style="color:var(--accent-blue); font-weight:600;">[${u.time_range}] ${u.speaker}:</span>
              <span>${u.text}</span>
            </div>
          `;
        });

        const actionsBox = document.getElementById("audioActionItemsList");
        actionsBox.innerHTML = data.action_items.map(a => `• <strong>${a.speaker}</strong>: ${a.action}`).join("<br>");

      } catch (err) {
        console.error("Audio extract error:", err);
      }
    });
  }
}

/* ----------------------------------------------------
   7. CAPSTONE ASSISTANT (SEC 3.3.1)
---------------------------------------------------- */
function initCapstoneAssistant() {
  const preview = document.getElementById("capstoneDocPreviewText");
  const btnSend = document.getElementById("btnSendCapstoneQuery");
  const queryInput = document.getElementById("capstoneQueryInput");
  const messagesBox = document.getElementById("capstoneChatMessages");
  const quickBtns = document.querySelectorAll(".capstone-quick-btn");

  // Load sample invoice text into preview
  fetch("/static/samples/sample_invoice.txt")
    .then(r => r.text())
    .then(t => {
      if (preview) preview.textContent = t;
    })
    .catch(() => {});

  quickBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const q = btn.getAttribute("data-q");
      if (queryInput) {
        queryInput.value = q;
        sendCapstoneQuery();
      }
    });
  });

  if (btnSend && queryInput) {
    btnSend.addEventListener("click", sendCapstoneQuery);
    queryInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendCapstoneQuery();
    });
  }

  async function sendCapstoneQuery() {
    const q = queryInput.value.trim();
    if (!q) return;

    messagesBox.innerHTML += `
      <div class="chat-bubble bubble-user">${q}</div>
    `;
    queryInput.value = "";
    messagesBox.scrollTop = messagesBox.scrollHeight;

    try {
      const res = await fetch("/api/capstone/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q })
      });
      const data = await res.json();

      const formatted = data.answer
        .replace(/\n\n/g, "<br><br>")
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

      const citationPill = data.citations && data.citations.length > 0
        ? `<div style="font-size:0.75rem; color:var(--accent-blue); margin-top:0.4rem;"><i class="fa-solid fa-bookmark"></i> Grounded in: ${data.citations.join(", ")}</div>`
        : "";

      messagesBox.innerHTML += `
        <div class="chat-bubble bubble-assistant">
          ${formatted}
          ${citationPill}
        </div>
      `;
      messagesBox.scrollTop = messagesBox.scrollHeight;

      const badge = document.getElementById("capstoneAuditBadge");
      if (badge) {
        badge.innerHTML = `<span class="badge badge-success">${data.responsible_ai_status} (${data.responsible_ai_score}/100)</span>`;
      }
    } catch (err) {
      console.error("Capstone query error:", err);
    }
  }
}

/* ----------------------------------------------------
   8. AI-901 PRACTICE EXAM ENGINE
---------------------------------------------------- */
let examQuestions = [];
let userSelections = {};

async function initExamEngine() {
  const container = document.getElementById("examQuestionsContainer");
  const answeredCount = document.getElementById("examAnsweredCounter");
  const btnSubmit = document.getElementById("btnSubmitExam");

  try {
    const res = await fetch("/api/exam/questions");
    const data = await res.json();
    examQuestions = data.questions || [];

    if (container) {
      container.innerHTML = "";
      examQuestions.forEach((q, idx) => {
        container.innerHTML += `
          <div class="card" id="qcard_${q.id}" style="margin-bottom: 1rem; border-left: 4px solid var(--accent-blue);">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem;">
              <span class="badge badge-info">Question ${idx + 1} of ${examQuestions.length}</span>
              <span style="font-size:0.78rem; color:var(--text-muted);">${q.subdomain}</span>
            </div>
            <p style="font-weight:600; font-size:0.95rem; margin-bottom:0.8rem; color:#ffffff;">${q.question}</p>
            <div class="exam-options-group" data-qid="${q.id}">
              ${q.options.map((opt, optIdx) => `
                <div class="exam-option-box" data-idx="${optIdx}">
                  <span style="width:22px; height:22px; border-radius:50%; background:var(--bg-card); display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700;">
                    ${String.fromCharCode(65 + optIdx)}
                  </span>
                  <span>${opt}</span>
                </div>
              `).join("")}
            </div>
            <div class="exam-explanation-box" id="expl_${q.id}" style="display:none; margin-top:0.8rem; padding:0.8rem; border-radius:var(--radius-sm); font-size:0.84rem;"></div>
          </div>
        `;
      });

      // Bind selection clicks
      document.querySelectorAll(".exam-options-group .exam-option-box").forEach(box => {
        box.addEventListener("click", () => {
          const group = box.closest(".exam-options-group");
          const qid = group.getAttribute("data-qid");
          const optIdx = parseInt(box.getAttribute("data-idx"));

          group.querySelectorAll(".exam-option-box").forEach(b => b.classList.remove("selected"));
          box.classList.add("selected");

          userSelections[qid] = optIdx;
          if (answeredCount) {
            answeredCount.textContent = `${Object.keys(userSelections).length} / ${examQuestions.length}`;
          }
        });
      });
    }
  } catch (err) {
    console.error("Exam load error:", err);
  }

  if (btnSubmit) {
    btnSubmit.addEventListener("click", async () => {
      const answeredTotal = Object.keys(userSelections).length;
      if (answeredTotal < examQuestions.length) {
        if (!confirm(`You have answered ${answeredTotal} of ${examQuestions.length} questions. Do you still want to submit and grade your exam?`)) {
          return;
        }
      }

      try {
        const res = await fetch("/api/exam/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ answers: userSelections })
        });
        const result = await res.json();

        // Reveal results card
        const resCard = document.getElementById("examResultsContainer");
        resCard.style.display = "block";
        resCard.scrollIntoView({ behavior: "smooth" });

        const banner = document.getElementById("examPassFailBanner");
        if (result.passed) {
          banner.innerHTML = `<span style="color:var(--success);"><i class="fa-solid fa-circle-check"></i> CONGRATULATIONS! CERTIFICATION PASSED</span>`;
        } else {
          banner.innerHTML = `<span style="color:var(--danger);"><i class="fa-solid fa-circle-xmark"></i> DID NOT PASS (Threshold: 700)</span>`;
        }

        document.getElementById("examScaledScoreText").textContent = `${result.scaled_score} / 1000 points (${result.correct_answers}/${result.total_questions} correct)`;

        // Domain breakdown
        const domainGrid = document.getElementById("examDomainStatsGrid");
        domainGrid.innerHTML = "";
        for (const [dName, dStat] of Object.entries(result.domain_breakdown)) {
          const badgeClass = dStat.percentage >= 70 ? "badge-success" : "badge-warning";
          domainGrid.innerHTML += `
            <div style="background:var(--bg-card); padding:1rem; border-radius:var(--radius-sm); border:1px solid var(--border-color);">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <strong style="font-size:0.86rem;">${dName}</strong>
                <span class="badge ${badgeClass}">${dStat.status}</span>
              </div>
              <div style="font-size:1.15rem; font-weight:800; color:var(--accent-blue);">${dStat.percentage}%</div>
              <div style="font-size:0.78rem; color:var(--text-muted);">${dStat.correct} of ${dStat.total} questions answered correctly</div>
            </div>
          `;
        }

        // Highlight questions and show explanations
        result.review_details.forEach(detail => {
          const group = document.querySelector(`.exam-options-group[data-qid="${detail.id}"]`);
          const explBox = document.getElementById(`expl_${detail.id}`);

          if (group) {
            const boxes = group.querySelectorAll(".exam-option-box");
            boxes.forEach((b, idx) => {
              b.classList.remove("selected");
              if (idx === detail.correct_choice) {
                b.classList.add("correct");
              }
              if (detail.user_choice !== null && idx === detail.user_choice && !detail.is_correct) {
                b.classList.add("incorrect");
              }
            });
          }

          if (explBox) {
            explBox.style.display = "block";
            const statColor = detail.is_correct ? "var(--success)" : "var(--danger)";
            const statIcon = detail.is_correct ? "fa-circle-check" : "fa-circle-xmark";
            explBox.style.background = detail.is_correct ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)";
            explBox.style.border = `1px solid ${statColor}`;
            explBox.innerHTML = `
              <strong style="color:${statColor};"><i class="fa-solid ${statIcon}"></i> ${detail.is_correct ? "Correct!" : "Incorrect"}</strong>
              <div style="margin-top:0.3rem; color:var(--text-primary);">${detail.explanation}</div>
            `;
          }
        });

      } catch (err) {
        console.error("Exam submit error:", err);
      }
    });
  }
}
