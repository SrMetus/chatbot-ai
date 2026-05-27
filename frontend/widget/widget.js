/**
 * Luna Chat Widget — embeddable chatbot for any business.
 *
 * Include via a <script> tag with data-* attributes:
 *   data-client-id  — Client ID (default "1")
 *   data-api-url    — Backend base URL (default "http://localhost:8000")
 *
 * The widget fetches its branding config (primary_color, bot_name,
 * subtitle, welcome_message) from the /widget-config endpoint and
 * renders a floating chat bubble with full responsive and accessible
 * behaviour.
 */
(function () {
  var script = document.currentScript;
  var clientId = script && script.getAttribute("data-client-id") || "1";
  var apiUrl = script && script.getAttribute("data-api-url") || "http://localhost:8000";

  var primaryColor = "#1a5276";
  var botName = "Luna";
  var subtitle = "Asistente Virtual";
  var welcomeMessage = null;
  var sessionId = crypto.randomUUID ? crypto.randomUUID() : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) { var r = Math.random() * 16 | 0, v = c === "x" ? r : r & 3 | 8; return v.toString(16); });
  var isOpen = false;
  var isWaiting = false;
  var configLoaded = false;
  var welcomeShown = false;
  var root = null;
  var btn = null;
  var windowEl = null;
  var messagesEl = null;
  var inputEl = null;
  var typingEl = null;
  var loadingEl = null;

  function _el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) { for (var k in attrs) { if (k === "className") e.className = attrs[k]; else if (k === "style" && typeof attrs[k] === "object") { for (var sk in attrs[k]) e.style[sk] = attrs[k][sk]; } else e.setAttribute(k, attrs[k]); } }
    if (children) { for (var i = 0; i < children.length; i++) { var c = children[i]; if (typeof c === "string") e.appendChild(document.createTextNode(c)); else if (c) e.appendChild(c); } }
    return e;
  }

  function _get(path) {
    return fetch(apiUrl + path).then(function (r) { if (!r.ok) return r.json().then(function(e){throw new Error(e.detail||'Error '+r.status)}); return r.json(); });
  }

  function _post(path, body) {
    return fetch(apiUrl + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then(function (r) { if (!r.ok) return r.json().then(function(e){throw new Error(e.detail||'Error '+r.status)}); return r.json(); });
  }

  function fetchConfig() {
    loadingEl = _el("div", { id: "lw-loading", style: { position: "fixed", bottom: "24px", right: "24px", zIndex: "999999" } });
    var spinner = _el("div", { style: { width: "24px", height: "24px", border: "3px solid #e0e0e0", borderTopColor: "#1a5276", borderRadius: "50%", animation: "lwSpin .6s linear infinite" } });
    loadingEl.appendChild(spinner);
    document.body.appendChild(loadingEl);

    _get("/api/v1/clients/" + clientId + "/widget-config").then(function (data) {
      primaryColor = data.primary_color || primaryColor;
      botName = data.bot_name || botName;
      subtitle = data.subtitle || subtitle;
      welcomeMessage = data.welcome_message !== undefined && data.welcome_message !== null ? data.welcome_message : null;
      if (data.is_active === false) {
        if (loadingEl && loadingEl.parentNode) loadingEl.parentNode.removeChild(loadingEl);
        console.warn("Luna Chat: widget is inactive for client " + clientId);
        return;
      }
      configLoaded = true;
      if (loadingEl && loadingEl.parentNode) loadingEl.parentNode.removeChild(loadingEl);
      buildWidget();
    }).catch(function () {
      if (loadingEl && loadingEl.parentNode) loadingEl.parentNode.removeChild(loadingEl);
      configLoaded = true;
      buildWidget();
    });
  }

  function toggle() {
    isOpen = !isOpen;
    windowEl.classList.toggle("lw-open", isOpen);
    btn.classList.toggle("lw-hidden", isOpen);
    if (isOpen && !welcomeShown) {
      welcomeShown = true;
      addMessage(welcomeMessage || ("\u00A1Hola! Soy " + botName + ", tu asistente virtual. \u00BFEn qu\u00E9 puedo ayudarte?"), "bot");
    }
  }

  function addMessage(text, role) {
    var bubble = _el("div", { className: "lw-msg lw-msg-" + role });
    var textEl = _el("div", { className: "lw-msg-text" });
    textEl.textContent = text;
    bubble.appendChild(textEl);
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    isWaiting = true;
    typingEl.classList.add("lw-typing-visible");
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    isWaiting = false;
    typingEl.classList.remove("lw-typing-visible");
  }

  function handleSubmit(text) {
    if (!text || !text.trim() || isWaiting) return;
    var msg = text.trim();
    inputEl.value = "";
    addMessage(msg, "user");
    showTyping();
    _post("/api/v1/chat/" + clientId, { message: msg, session_id: sessionId }).then(function (data) {
      hideTyping();
      addMessage(data.message || "Sin respuesta.", "bot");
    }).catch(function () {
      hideTyping();
      addMessage("Lo siento, ocurrió un error. Intenta de nuevo o escribe tu consulta de otra forma.", "bot");
    });
  }

  function buildWidget() {
    root = _el("div", { id: "luna-widget-root" });

    var css = document.createElement("style");
    css.textContent = "\
@keyframes lwSpin{to{transform:rotate(360deg)}}\
#luna-widget-root{font-family:Georgia,'Times New Roman',serif;z-index:999999;}\
#lw-btn{position:fixed;bottom:24px;right:24px;width:60px;height:60px;border-radius:50%;border:none;background:" + primaryColor + ";color:#fff;font-size:26px;cursor:pointer;box-shadow:0 4px 20px rgba(0,0,0,0.25);transition:transform .25s ease,opacity .25s ease,box-shadow .25s ease;display:flex;align-items:center;justify-content:center;z-index:999999;padding:0;line-height:1;}\
#lw-btn:hover{transform:scale(1.08);box-shadow:0 6px 28px rgba(0,0,0,0.35);}\
#lw-btn:active{transform:scale(0.95);}\
#lw-btn.lw-hidden{opacity:0;transform:scale(0.8);pointer-events:none;}\
#lw-window{position:fixed;bottom:24px;right:24px;width:370px;height:560px;border-radius:16px;background:#fff;box-shadow:0 8px 40px rgba(0,0,0,0.18);display:flex;flex-direction:column;overflow:hidden;z-index:999998;opacity:0;transform:translateY(16px) scale(0.96);transition:opacity .28s ease,transform .28s ease;pointer-events:none;overscroll-behavior:contain;}\
#lw-window.lw-open{opacity:1;transform:translateY(0) scale(1);pointer-events:auto;}\
.lw-header{background:" + primaryColor + ";color:#fff;padding:16px 20px;display:flex;align-items:center;gap:10px;flex-shrink:0;}\
.lw-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}\
.lw-header-info{flex:1;min-width:0;}\
.lw-header-name{font-weight:700;font-size:15px;letter-spacing:0.3px;}\
.lw-header-sub{font-size:11px;opacity:0.8;margin-top:1px;}\
.lw-close{background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:0;width:44px;height:44px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:background .2s;}\
.lw-close:hover{background:rgba(255,255,255,0.2);}\
.lw-close:focus-visible{outline:2px solid #fff;outline-offset:2px;}\
.lw-messages{flex:1;overflow-y:auto;padding:16px 16px 8px;display:flex;flex-direction:column;gap:10px;background:#fafafa;}\
.lw-msg{display:flex;max-width:82%;animation:lwFadeIn .25s ease;}\
.lw-msg.lw-msg-user{align-self:flex-end;}\
.lw-msg.lw-msg-bot{align-self:flex-start;}\
.lw-msg-text{padding:10px 14px;border-radius:14px;font-size:14px;line-height:1.5;word-wrap:break-word;}\
.lw-msg-user .lw-msg-text{background:" + primaryColor + ";color:#fff;border-bottom-right-radius:4px;}\
.lw-msg-bot .lw-msg-text{background:#eaeaea;color:#1a1a1a;border-bottom-left-radius:4px;}\
.lw-typing{display:flex;align-items:center;gap:10px;padding:8px 16px;opacity:0;transition:opacity .2s;flex-shrink:0;height:0;overflow:hidden;}\
.lw-typing.lw-typing-visible{opacity:1;height:auto;padding:8px 16px;}\
.lw-typing-dots{display:flex;gap:4px;}\
.lw-typing-dot{width:8px;height:8px;border-radius:50%;background:#bbb;animation:lwBounce 1.2s infinite;}\
.lw-typing-dot:nth-child(2){animation-delay:.2s;}\
.lw-typing-dot:nth-child(3){animation-delay:.4s;}\
.lw-typing-label{font-size:12px;color:#888;font-style:italic;}\
.lw-input-wrap{display:flex;align-items:center;border-top:1px solid #e8e8e8;padding:10px 12px;background:#fff;flex-shrink:0;gap:8px;}\
.lw-input{border:none;flex:1;font-size:14px;padding:8px 4px;font-family:Georgia,'Times New Roman',serif;color:#1a1a1a;background:transparent;touch-action:manipulation;}\
.lw-input:focus-visible{outline:2px solid " + primaryColor + ";outline-offset:2px;border-radius:2px;}\
.lw-input::placeholder{color:#aaa;font-style:italic;}\
.lw-send{width:44px;height:44px;border-radius:50%;border:none;background:" + primaryColor + ";color:#fff;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:background .2s,transform .15s;padding:0;}\
.lw-send:hover{filter:brightness(1.1);}\
.lw-send:focus-visible{outline:2px solid " + primaryColor + ";outline-offset:2px;}\
.lw-send:active{transform:scale(0.9);}\
.lw-powered{text-align:center;font-size:10px;color:#bbb;padding:4px 0;flex-shrink:0;letter-spacing:0.5px;}\
@keyframes lwFadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}\
@keyframes lwBounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}\
@media(prefers-reduced-motion:reduce){#lw-window,#lw-btn,.lw-msg{animation:none;transition:none;}}\
@media(max-width:480px){\
#lw-btn{bottom:16px;right:16px;width:56px;height:56px;font-size:24px;}\
#lw-window{bottom:0;right:0;left:0;top:0;width:100%;height:100%;border-radius:0;}\
.lw-messages{padding:12px 12px 4px;}\
.lw-msg{max-width:88%;}\
.lw-header{padding:14px 16px;padding-top:calc(14px + env(safe-area-inset-top,0px));}\
.lw-input-wrap{padding-bottom:calc(10px + env(safe-area-inset-bottom,0px));}\
}";
    document.head.appendChild(css);

    btn = _el("button", { id: "lw-btn", "aria-label": "Abrir chat" });
    btn.innerHTML = "<span aria-hidden=\"true\">\uD83D\uDCAC</span>";
    btn.addEventListener("click", toggle);
    root.appendChild(btn);

    windowEl = _el("div", { id: "lw-window" });

    var header = _el("div", { className: "lw-header" });
    var avatar = _el("div", { className: "lw-avatar", "aria-hidden": "true" });
    avatar.textContent = "\uD83E\uDD16";
    var info = _el("div", { className: "lw-header-info" });
    var nameEl = _el("div", { className: "lw-header-name" });
    nameEl.textContent = botName;
    var subEl = _el("div", { className: "lw-header-sub" });
    subEl.textContent = subtitle;
    info.appendChild(nameEl);
    info.appendChild(subEl);
    var closeBtn = _el("button", { className: "lw-close", "aria-label": "Cerrar chat" });
    closeBtn.innerHTML = "<span aria-hidden=\"true\">\u2715</span>";
    closeBtn.addEventListener("click", toggle);
    header.appendChild(avatar);
    header.appendChild(info);
    header.appendChild(closeBtn);
    windowEl.appendChild(header);

    messagesEl = _el("div", { className: "lw-messages" });
    windowEl.appendChild(messagesEl);

    typingEl = _el("div", { className: "lw-typing" });
    var dots = _el("div", { className: "lw-typing-dots" });
    dots.appendChild(_el("span", { className: "lw-typing-dot" }));
    dots.appendChild(_el("span", { className: "lw-typing-dot" }));
    dots.appendChild(_el("span", { className: "lw-typing-dot" }));
    typingEl.appendChild(dots);
    var label = _el("span", { className: "lw-typing-label" });
    label.textContent = botName + " est\u00E1 escribiendo\u2026";
    typingEl.appendChild(label);
    windowEl.appendChild(typingEl);

    var inputWrap = _el("div", { className: "lw-input-wrap" });
    inputEl = _el("input", { className: "lw-input", type: "text", placeholder: "Escribe tu mensaje\u2026", "aria-label": "Mensaje", autocomplete: "off" });
    var sendBtn = _el("button", { className: "lw-send", "aria-label": "Enviar" });
    sendBtn.innerHTML = "<span aria-hidden=\"true\">\u25B6</span>";
    function onSubmit() { handleSubmit(inputEl.value); }
    sendBtn.addEventListener("click", onSubmit);
    inputEl.addEventListener("keydown", function (e) { if (e.key === "Enter") onSubmit(); });
    inputWrap.appendChild(inputEl);
    inputWrap.appendChild(sendBtn);
    windowEl.appendChild(inputWrap);

    var powered = _el("div", { className: "lw-powered" });
    powered.textContent = "LUNA CHAT";
    windowEl.appendChild(powered);

    root.appendChild(windowEl);
    document.body.appendChild(root);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen) toggle();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fetchConfig);
  } else {
    fetchConfig();
  }
})();
