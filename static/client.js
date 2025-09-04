// Client-side JavaScript for agent run visualization with colored prompt sections
let lastEventCount = 0;

async function fetchEvents() {
  try {
    const res = await fetch(window.location.pathname + "/events");
    const events = await res.json();
    
    // Only render if new events
    if (events.length > lastEventCount) {
      render(events);
      lastEventCount = events.length;
    }
  } catch (error) {
    console.error("Error fetching events:", error);
  }
}

function last(arr, pred) { 
  const filtered = arr.filter(pred); 
  return filtered[filtered.length - 1]; 
}

function renderPromptSections(sections) {
  // Define the correct order of sections and their display names
  const sectionOrder = [
    { key: "system_role", name: "1. System Role" },
    { key: "approach_guidelines", name: "2. Approach & Guidelines" },
    { key: "available_tools", name: "3. Available Tools" },
    { key: "user_task", name: "4. User's Task" },
    { key: "conversation_history", name: "5. History (incl. tool responses)" },
    { key: "current_state", name: "6. Current State" }
  ];
  
  const container = document.getElementById("prompt-sections");
  container.innerHTML = "";
  
  // Render sections in the correct order
  for (const section of sectionOrder) {
    const content = sections[section.key];
    if (content && content.trim()) {  // Only render non-empty sections
      const sectionDiv = document.createElement("div");
      sectionDiv.className = `prompt-section section-${section.key}`;
      
      const labelDiv = document.createElement("div");
      labelDiv.className = "prompt-section-label";
      labelDiv.textContent = section.name;
      
      const contentPre = document.createElement("pre");
      contentPre.className = "prompt-section-content";
      contentPre.textContent = content;
      
      sectionDiv.appendChild(labelDiv);
      sectionDiv.appendChild(contentPre);
      container.appendChild(sectionDiv);
    }
  }
}

function render(events) {
  // Find latest relevant events
  const modelReq = last(events, e => e.type === "model_request");
  const modelRes = last(events, e => e.type === "model_result");
  const stepStarted = last(events, e => e.type === "step_started");
  
  // Get tool calls and results for current step
  const currentStep = stepStarted ? stepStarted.step : 0;
  const toolCalls = events.filter(e => e.type === "tool_call" && e.step === currentStep);
  const toolResults = events.filter(e => e.type === "tool_result" && e.step === currentStep);

  // Update step number
  document.getElementById("step-num").textContent = currentStep || "–";
  
  // Update prompt - either with sections or fallback to raw text
  if (modelReq) {
    if (modelReq.prompt_sections) {
      // Render color-coded sections
      renderPromptSections(modelReq.prompt_sections);
    } else if (modelReq.prompt) {
      // Fallback to raw prompt text
      const fallback = document.getElementById("prompt-sections");
      fallback.innerHTML = `<pre id="prompt-text">${escapeHtml(modelReq.prompt)}</pre>`;
    }
  }

  // Update assistant response (shown BEFORE tool traces)
  const assistantText = document.getElementById("assistant-text");
  if (modelRes && modelRes.assistant_text) {
    assistantText.textContent = modelRes.assistant_text;
    assistantText.parentElement.style.display = "block";
  } else {
    assistantText.parentElement.style.display = "none";
  }

  // Update tool traces (shown AFTER assistant response)
  const tracesDiv = document.getElementById("tool-traces");
  if (toolCalls.length > 0) {
    tracesDiv.innerHTML = "";
    
    toolCalls.forEach(call => {
      const result = toolResults.find(r => r.name === call.name && r.step === call.step);
      
      const traceDiv = document.createElement("div");
      traceDiv.className = "trace";
      
      // Tool name
      const toolHead = document.createElement("div");
      toolHead.className = "tool-head";
      toolHead.textContent = `🔧 ${call.name}`;
      traceDiv.appendChild(toolHead);
      
      // Arguments
      const argsDiv = document.createElement("pre");
      argsDiv.className = "args";
      argsDiv.textContent = JSON.stringify(call.args, null, 2);
      traceDiv.appendChild(argsDiv);
      
      // Result
      if (result) {
        const resultDiv = document.createElement("pre");
        resultDiv.className = "result";
        
        if (result.ok) {
          resultDiv.textContent = "✅ " + (result.result_preview || JSON.stringify(result.result).slice(0, 500));
        } else {
          resultDiv.textContent = "❌ Error: " + (result.result_preview || result.error || "Unknown error");
          resultDiv.style.color = "#cc0000";
        }
        traceDiv.appendChild(resultDiv);
      } else {
        const pendingDiv = document.createElement("pre");
        pendingDiv.className = "result";
        pendingDiv.textContent = "⏳ (pending)";
        pendingDiv.style.fontStyle = "italic";
        traceDiv.appendChild(pendingDiv);
      }
      
      tracesDiv.appendChild(traceDiv);
    });
    
    tracesDiv.parentElement.style.display = "block";
  } else {
    // Hide tool traces section if no tools called
    if (tracesDiv.innerHTML === "" || tracesDiv.innerHTML === "(no tool calls yet)") {
      tracesDiv.parentElement.style.display = "none";
    }
  }
  
  // Check if run is complete
  const runCompleted = events.some(e => e.type === "run_completed");
  if (runCompleted) {
    const button = document.querySelector("#next-form button");
    button.textContent = "✓ Run complete";
    button.disabled = true;
    button.style.opacity = "0.5";
    button.style.cursor = "not-allowed";
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Handle form submission with AJAX
document.getElementById("next-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const button = e.target.querySelector("button");
  const originalText = button.textContent;
  button.textContent = "Running...";
  button.disabled = true;
  
  try {
    await fetch(e.target.action, { method: "POST" });
    
    // Re-enable after a short delay
    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 1000);
  } catch (error) {
    console.error("Error triggering next step:", error);
    button.textContent = originalText;
    button.disabled = false;
  }
});

// Start polling
setInterval(fetchEvents, 1000);
fetchEvents();