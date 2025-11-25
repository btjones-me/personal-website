const terminalOutput = document.getElementById("terminal-output");
const terminalForm = document.getElementById("terminal-form");
const commandInput = document.getElementById("command-input");

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

function appendEntry({ type, content }) {
  const entry = document.createElement("div");
  entry.className = `terminal-entry terminal-entry--${type}`;
  entry.innerHTML = linkify(content);
  terminalOutput.appendChild(entry);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function clearTerminal() {
  terminalOutput.innerHTML = "";
}

async function submitCommand(command) {
  appendEntry({ type: "input", content: `visitor@benjamin:~$ ${command}` });

  try {
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
      case "download":
        appendEntry({ type: "output", content: payload.output });
        if (payload.url) {
          window.open(payload.url, "_blank");
        }
        break;
      case "clear":
        clearTerminal();
        break;
      case "error":
      default:
        appendEntry({ type: "error", content: payload.output });
    }
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
    content: "Type 'help' to explore available commands.",
  });
}

