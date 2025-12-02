const terminalOutput = document.getElementById("terminal-output");
const terminalForm = document.getElementById("terminal-form");
const commandInput = document.getElementById("command-input");
const promptLabel = document.querySelector(".terminal-prompt");

// Chat mode state
let chatMode = false;
let sessionId = null;

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function linkify(text) {
  const escaped = escapeHtml(text);
  const urlPattern = /(https?:\/\/[^\s<]+)/g;
  const emailPattern = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
  return escaped
    .replace(urlPattern, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(emailPattern, '<a href="mailto:$1">$1</a>');
}

function getPromptText() {
  return chatMode ? "ai@benjamin:~$" : "visitor@benjamin:~$";
}

function updatePrompt() {
  if (promptLabel) {
    promptLabel.textContent = getPromptText();
  }
}

function appendEntry({ type, content, isAi = false }) {
  const entry = document.createElement("div");
  entry.className = `terminal-entry terminal-entry--${type}`;
  if (isAi) {
    entry.classList.add("terminal-entry--ai");
  }
  entry.innerHTML = linkify(content);
  terminalOutput.appendChild(entry);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function clearTerminal() {
  terminalOutput.innerHTML = "";
}

function startSpinner(label = "Thinking") {
  const frames = ["|", "/", "-", "\\"];
  const entry = document.createElement("div");
  entry.className = "terminal-entry terminal-entry--output terminal-entry--spinner";

  const icon = document.createElement("span");
  icon.className = "spinner-icon";
  icon.textContent = frames[0];

  const text = document.createElement("span");
  text.className = "spinner-text";
  text.textContent = ` ${label}…`;

  entry.appendChild(icon);
  entry.appendChild(text);
  terminalOutput.appendChild(entry);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;

  let frameIndex = 1;
  const interval = setInterval(() => {
    icon.textContent = frames[frameIndex % frames.length];
    frameIndex += 1;
  }, 120);

  return () => {
    clearInterval(interval);
    entry.remove();
  };
}

async function withSpinner(label, operation) {
  const stopSpinner = startSpinner(label);
  try {
    return await operation();
  } finally {
    stopSpinner();
  }
}

function enterChatMode() {
  chatMode = true;
  sessionId = sessionId || crypto.randomUUID();
  updatePrompt();
  if (commandInput) {
    commandInput.placeholder = "Ask me anything about Ben...";
  }
}

function exitChatMode() {
  chatMode = false;
  updatePrompt();
  if (commandInput) {
    commandInput.placeholder = "Type a command…";
  }
}

function showChatHelp() {
  appendEntry({
    type: "output",
    content:
      "Chat mode help:\n- Ask anything about Ben's background, skills, or projects.\n- Type 'help' to see this again.\n- Type 'exit' or 'end' to leave chat mode.",
  });
}

async function sendChatMessage(message) {
  appendEntry({ type: "input", content: `${getPromptText()} ${message}` });

  try {
    await withSpinner("Ben is thinking", async () => {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message, session_id: sessionId }),
      });

      const payload = await response.json();

      if (response.status === 429) {
        appendEntry({
          type: "error",
          content: payload.output || "Rate limit reached. Please wait a moment.",
        });
        return;
      }

      if (payload.session_id) {
        sessionId = payload.session_id;
      }

      if (payload.kind === "ai") {
        appendEntry({ type: "output", content: payload.output, isAi: true });
      } else if (payload.kind === "error") {
        appendEntry({ type: "error", content: payload.output });
      } else {
        appendEntry({ type: "output", content: payload.output });
      }
    });
  } catch (error) {
    console.error(error);
    appendEntry({
      type: "error",
      content: "Network error. Check your connection and try again.",
    });
  }
}

async function submitCommand(command) {
  // In chat mode, check for exit command first
  if (chatMode) {
    const normalized = command.toLowerCase();
    if (normalized === "exit" || normalized === "end") {
      appendEntry({ type: "input", content: `${getPromptText()} ${command}` });
      exitChatMode();
      appendEntry({
        type: "output",
        content: "Exited chat mode. Type 'help' to see available commands.",
      });
      return;
    }
    if (normalized === "help") {
      appendEntry({ type: "input", content: `${getPromptText()} ${command}` });
      showChatHelp();
      return;
    }
    // Send as chat message
    await sendChatMessage(command);
    return;
  }

  appendEntry({ type: "input", content: `${getPromptText()} ${command}` });

  try {
    await withSpinner("Working on it", async () => {
      const response = await fetch("/command", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ command }),
      });

      if (!response.ok) {
        appendEntry({
          type: "error",
          content: "Something went wrong. Please try again.",
        });
        return;
      }

      const payload = await response.json();

      switch (payload.kind) {
        case "text":
          appendEntry({ type: "output", content: payload.output });
          break;
        case "ai":
          appendEntry({ type: "output", content: payload.output, isAi: true });
          break;
        case "download":
          appendEntry({ type: "output", content: payload.output });
          if (payload.url) {
            window.open(payload.url, "_blank");
          }
          break;
        case "clear":
          clearTerminal();
          break;
        case "chat_start":
          appendEntry({ type: "output", content: payload.output });
          enterChatMode();
          break;
        case "chat_end":
          exitChatMode();
          appendEntry({ type: "output", content: payload.output });
          break;
        case "error":
        default:
          appendEntry({ type: "error", content: payload.output });
      }
    });
  } catch (error) {
    console.error(error);
    appendEntry({
      type: "error",
      content: "Network error. Check your connection and try again.",
    });
  }
}

if (terminalForm && commandInput && terminalOutput) {
  terminalForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const command = commandInput.value.trim();
    if (!command) {
      return;
    }
    submitCommand(command);
    commandInput.value = "";
  });

  // Show prompt automatically on load
  commandInput.focus();
  appendEntry({
    type: "output",
    content: "Type 'help' to explore available commands, or just ask me a question!",
  });
}
