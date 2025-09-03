// Client-side JavaScript for agent run visualization
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
  
  // Update prompt
  const promptText = document.getElementById("prompt-text");
  if (modelReq && modelReq.prompt) {
    promptText.textContent = modelReq.prompt;
  }

  // Update tool traces
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
      toolHead.textContent = call.name;
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
          resultDiv.textContent = result.result_preview || JSON.stringify(result.result).slice(0, 500);
        } else {
          resultDiv.textContent = "Error: " + (result.result_preview || result.error || "Unknown error");
          resultDiv.style.color = "#cc0000";
        }
        traceDiv.appendChild(resultDiv);
      } else {
        const pendingDiv = document.createElement("pre");
        pendingDiv.className = "result";
        pendingDiv.textContent = "(pending)";
        pendingDiv.style.fontStyle = "italic";
        traceDiv.appendChild(pendingDiv);
      }
      
      tracesDiv.appendChild(traceDiv);
    });
  }

  // Update assistant response
  const assistantText = document.getElementById("assistant-text");
  if (modelRes && modelRes.assistant_text) {
    assistantText.textContent = modelRes.assistant_text;
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