// Client-side JavaScript for agent run visualization with colored prompt sections
let lastEventCount = 0;
let lastModelResponseStep = -1;

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

function renderPromptSections(sections, tokenCounts) {
  // Define the correct order of sections and their display names
  const sectionOrder = [
    { key: "system_role", name: "1. System Role" },
    { key: "user_task", name: "2. User's Request (Primary Objective)" },
    { key: "approach_guidelines", name: "3. Approach & Guidelines" },
    { key: "available_tools", name: "4. Available Tools" },
    { key: "conversation_history", name: "5. Conversation History & Previous Work" },
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
      let labelText = section.name;
      // Add token count if available
      if (tokenCounts && tokenCounts[section.key]) {
        labelText += ` (${tokenCounts[section.key]} tokens)`;
      }
      labelDiv.textContent = labelText;
      
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
  const compressionEvent = last(events, e => e.type === "history_compressed");
  
  // Get tool calls and results for current step
  const currentStep = stepStarted ? stepStarted.step : 0;
  const toolCalls = events.filter(e => e.type === "tool_call" && e.step === currentStep);
  const toolResults = events.filter(e => e.type === "tool_result" && e.step === currentStep);

  // Update step number
  document.getElementById("step-num").textContent = currentStep || "–";
  
  // Update prompt - either with sections or fallback to raw text
  if (modelReq) {
    if (modelReq.prompt_sections) {
      // Render color-coded sections with token counts
      renderPromptSections(modelReq.prompt_sections, modelReq.token_counts);
      
      // Update total token count
      if (modelReq.token_counts && modelReq.token_counts.total) {
        document.getElementById("total-tokens").textContent = modelReq.token_counts.total.toLocaleString();
      }
    } else if (modelReq.prompt) {
      // Fallback to raw prompt text
      const fallback = document.getElementById("prompt-sections");
      fallback.innerHTML = `<pre id="prompt-text">${escapeHtml(modelReq.prompt)}</pre>`;
    }
  }
  
  // Check if compression has been applied to this step
  if (compressionEvent && compressionEvent.step <= currentStep) {
    // Add a note about compression
    const stepLabel = document.getElementById("step-num");
    if (stepLabel && !stepLabel.textContent.includes("compressed")) {
      stepLabel.textContent = currentStep + " (history compressed)";
    }
  }

  // Update assistant response (shown BEFORE tool traces)
  const assistantText = document.getElementById("assistant-text");
  const assistantHeader = document.getElementById("assistant-header");
  
  // Always prioritize showing the model response if it exists and is for current step
  if (modelRes && modelRes.assistant_text && modelRes.step === currentStep) {
    // Show the complete LLM response, not just parsed tool calls
    assistantText.textContent = modelRes.assistant_text;
    
    // Check if this is a final response (no tool calls and contains completion keywords)
    const isFinalResponse = toolCalls.length === 0 && (
      modelRes.assistant_text.toLowerCase().includes("## final") ||
      modelRes.assistant_text.toLowerCase().includes("## conclusion") ||
      modelRes.assistant_text.toLowerCase().includes("## summary") ||
      modelRes.assistant_text.toLowerCase().includes("final answer:") ||
      modelRes.assistant_text.toLowerCase().includes("analysis complete")
    );
    
    if (isFinalResponse) {
      assistantHeader.textContent = "Final Agent Response";
      assistantHeader.style.color = "#28a745"; // Green color for final response
    } else {
      assistantHeader.textContent = "Agent response";
      assistantHeader.style.color = ""; // Reset to default color
    }
    
    assistantText.parentElement.style.display = "block";
  } else if (modelRes) {
    // If there's a model result but no assistant_text, still show it
    assistantText.textContent = "(Waiting for response...)";
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
  
  // Check if run is complete or if we need to re-enable the button
  const runCompleted = events.some(e => e.type === "run_completed");
  const button = document.querySelector("#next-form button");
  
  if (runCompleted) {
    button.textContent = "✓ Run complete";
    button.disabled = true;
    button.style.opacity = "0.5";
    button.style.cursor = "not-allowed";
    waitingForResponse = false;
  } else if (waitingForResponse && modelRes && modelRes.assistant_text && modelRes.step > lastModelResponseStep) {
    // We were waiting for a response and now have received a NEW one for the current step
    lastModelResponseStep = modelRes.step;
    
    // Check if this is a final response
    const isFinalResponse = toolCalls.length === 0 && (
      modelRes.assistant_text.toLowerCase().includes("## final") ||
      modelRes.assistant_text.toLowerCase().includes("## conclusion") ||
      modelRes.assistant_text.toLowerCase().includes("## summary") ||
      modelRes.assistant_text.toLowerCase().includes("final answer:") ||
      modelRes.assistant_text.toLowerCase().includes("analysis complete")
    );
    
    if (isFinalResponse) {
      // Don't re-enable the button for final responses
      button.textContent = "✓ Run complete";
      button.disabled = true;
      button.style.opacity = "0.5";
      button.style.cursor = "not-allowed";
    } else {
      // Re-enable the button for non-final responses
      button.textContent = "▶ Run next step";
      button.disabled = false;
      button.style.opacity = "";
      button.style.cursor = "";
    }
    waitingForResponse = false;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Track if we're waiting for a response
let waitingForResponse = false;

// Handle form submission with AJAX
document.getElementById("next-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const button = e.target.querySelector("button");
  const originalText = button.textContent;
  button.textContent = "Running...";
  button.disabled = true;
  waitingForResponse = true;
  
  try {
    await fetch(e.target.action, { method: "POST" });
    // Don't re-enable immediately - wait for the response to be received
  } catch (error) {
    console.error("Error triggering next step:", error);
    button.textContent = originalText;
    button.disabled = false;
    waitingForResponse = false;
  }
});

// Compress history function
async function compressHistory() {
  const btn = document.getElementById("compress-btn");
  const originalText = btn.textContent;
  btn.textContent = "Compressing...";
  btn.disabled = true;
  
  try {
    const response = await fetch(window.location.pathname + "/compress", { 
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    
    if (response.ok) {
      const data = await response.json();
      btn.textContent = "Compression requested";
      // Compression will happen before the next step
      setTimeout(() => {
        btn.textContent = originalText;
        btn.disabled = false;
      }, 2000);
      
      // Show message to user
      if (data.message) {
        console.log(data.message);
      }
    } else {
      btn.textContent = "Failed";
      setTimeout(() => {
        btn.textContent = originalText;
        btn.disabled = false;
      }, 2000);
    }
  } catch (error) {
    console.error("Error compressing history:", error);
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

// Make function available globally
window.compressHistory = compressHistory;

// Start polling
setInterval(fetchEvents, 1000);
fetchEvents();