const bridgeScript = `<script defer src="${location.origin}/js/page-bridge.js"></script>`;

export function renderPage(frame, pageHtml) {
  const policy = [
    "default-src 'none'",
    `img-src ${location.origin} data:`,
    `style-src 'unsafe-inline' ${location.origin}`,
    `font-src ${location.origin} data:`,
    `media-src ${location.origin}`,
    `script-src ${location.origin}`,
    "connect-src 'none'",
    "object-src 'none'",
    "frame-src 'none'",
    "form-action 'none'",
    "base-uri 'none'",
  ].join("; ");
  const securityMeta = `<meta http-equiv="Content-Security-Policy" content="${policy}">`;
  let documentHtml = pageHtml;

  if (/<head(?:\s[^>]*)?>/i.test(documentHtml)) {
    documentHtml = documentHtml.replace(/<head(?:\s[^>]*)?>/i, (head) => `${head}${securityMeta}`);
  } else {
    documentHtml = `${securityMeta}${documentHtml}`;
  }
  if (/<\/body\s*>/i.test(documentHtml)) {
    documentHtml = documentHtml.replace(/<\/body\s*>/i, `${bridgeScript}</body>`);
  } else {
    documentHtml += bridgeScript;
  }
  frame.srcdoc = documentHtml;
  frame.hidden = false;
}

export function showWelcome(welcome, frame, errorView) {
  welcome.hidden = false;
  frame.hidden = true;
  errorView.hidden = true;
  frame.removeAttribute("srcdoc");
}

export function showError(welcome, frame, errorView, title, message) {
  welcome.hidden = true;
  frame.hidden = true;
  frame.removeAttribute("srcdoc");
  errorView.hidden = false;
  document.querySelector("#error-title").textContent = title;
  document.querySelector("#error-message").textContent = message;
}