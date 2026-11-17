import { NavigationHistory, normalizeAddress } from "./navigation.js";
import { renderPage, showError, showWelcome } from "./renderer.js";
import { DeveloperTools } from "./debugger.js";

const addressInput = document.querySelector("#address-input");
const welcomeInput = document.querySelector("#welcome-input");
const addressForm = document.querySelector("#address-form");
const welcomeForm = document.querySelector("#welcome-form");
const backButton = document.querySelector("#back-button");
const forwardButton = document.querySelector("#forward-button");
const refreshButton = document.querySelector("#refresh-button");
const retryButton = document.querySelector("#retry-button");
const welcome = document.querySelector("#welcome");
const frame = document.querySelector("#page-frame");
const errorView = document.querySelector("#error-view");
const statusBar = document.querySelector(".page-status");
const statusLabel = document.querySelector("#status-label");
const currentAddress = document.querySelector("#current-address");
const loadingBar = document.querySelector("#loading-bar");

const history = new NavigationHistory();
const developerTools = new DeveloperTools();
let activeRequest = 0;

function updateControls() {
  backButton.disabled = !history.canGoBack;
  forwardButton.disabled = !history.canGoForward;
}

function setLoading(loading) {
  statusBar.classList.toggle("loading", loading);
  statusLabel.textContent = loading ? "Loading" : "Ready";
  loadingBar.style.width = loading ? "" : "0";
}

function setCurrentUrl(url) {
  addressInput.value = url;
  currentAddress.textContent = url;
  currentAddress.title = url;
}

async function navigate(value, mode = "push") {
  let url;
  try {
    url = normalizeAddress(value);
  } catch (error) {
    developerTools.log(`Address rejected: ${error.message}`, "error");
    showError(welcome, frame, errorView, "Check the website address", error.message);
    return;
  }

  developerTools.log("Navigation requested");
  const requestId = ++activeRequest;
  welcome.hidden = true;
  errorView.hidden = true;
  frame.hidden = true;
  statusLabel.textContent = "Connecting";
  currentAddress.textContent = url;
  currentAddress.title = url;
  setLoading(true);

  try {
    const response = await fetch(`/api/browse?url=${encodeURIComponent(url)}`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    const result = await response.json();
    if (requestId !== activeRequest) return;
    if (result.error || !result.html) {
      throw new Error(result.error || `The server returned HTTP ${response.status}.`);
    }

    const finalUrl = result.url || url;
    if (mode === "push") history.push(finalUrl);
    else history.replace(finalUrl);
    setCurrentUrl(finalUrl);
    renderPage(frame, result.html);
    developerTools.setPage(result);
    developerTools.log(`Page loaded with HTTP ${result.status}`);
    statusLabel.textContent = `HTTP ${result.status}`;
    updateControls();
  } catch (error) {
    if (requestId !== activeRequest) return;
    developerTools.log(`Navigation failed: ${error.message}`, "error");
    showError(
      welcome,
      frame,
      errorView,
      "Unable to reach this website",
      error instanceof TypeError
        ? "The frontend server could not be reached. Make sure both Technetium servers are running."
        : error.message,
    );
    statusLabel.textContent = "Navigation failed";
    currentAddress.textContent = url;
  } finally {
    if (requestId === activeRequest) setLoading(false);
  }
}

addressForm.addEventListener("submit", (event) => {
  event.preventDefault();
  navigate(addressInput.value);
});

welcomeForm.addEventListener("submit", (event) => {
  event.preventDefault();
  addressInput.value = welcomeInput.value;
  navigate(welcomeInput.value);
});

backButton.addEventListener("click", () => {
  const previous = history.moveBack();
  if (previous) navigate(previous, "replace");
  updateControls();
});

forwardButton.addEventListener("click", () => {
  const next = history.moveForward();
  if (next) navigate(next, "replace");
  updateControls();
});

refreshButton.addEventListener("click", () => {
  if (history.current) navigate(history.current, "replace");
});

retryButton.addEventListener("click", () => {
  navigate(history.current || addressInput.value, "replace");
});

window.addEventListener("message", (event) => {
  if (event.source !== frame.contentWindow || !event.data
      || event.data.type !== "technetium:navigate"
      || typeof event.data.url !== "string") {
    return;
  }
  let destination;
  try {
    destination = new URL(event.data.url);
  } catch {
    return;
  }
  if (!["http:", "https:"].includes(destination.protocol)) return;
  navigate(destination.href);
});

window.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "l") {
    event.preventDefault();
    addressInput.focus();
    addressInput.select();
  }
  if (event.key === "Enter" && document.activeElement === addressInput) {
    event.preventDefault();
    navigate(addressInput.value);
  }
});

showWelcome(welcome, frame, errorView);
updateControls();