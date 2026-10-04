const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("input");
const chips = document.getElementById("chips");
const history = [];

function add(text, who, extra = "") {
  const el = document.createElement("div");
  el.className = "msg " + who + " " + extra;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

async function send(text) {
  add(text, "user");
  const typing = add("Typing...", "bot", "typing");
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history }),
    });
    const data = await res.json();
    typing.remove();
    const reply = data.reply || data.error || "Something went wrong.";
    add(reply, "bot");
    history.push({ role: "user", text }, { role: "bot", text: reply });
    document.getElementById("badge").textContent = data.source === "gemini" ? "Gemini" : "Offline mode";
  } catch (e) {
    typing.remove();
    add("Can't reach the server. Make sure app.py is running.", "bot");
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  send(text);
});

fetch("/api/config").then((r) => r.json()).then((cfg) => {
  document.title = cfg.name;
  document.getElementById("title").textContent = cfg.name;
  document.documentElement.style.setProperty("--accent", cfg.color);
  add(cfg.greeting, "bot");
  cfg.chips.forEach((c) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = c;
    b.onclick = () => send(c);
    chips.appendChild(b);
  });
});
