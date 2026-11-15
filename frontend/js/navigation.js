export function normalizeAddress(value) {
  const input = value.trim();
  if (!input) {
    throw new Error("Enter a website address to continue.");
  }
  if (/\s/.test(input)) {
    throw new Error("Enter a valid website address without spaces.");
  }

  const candidate = /^[a-z][a-z\d+.-]*:\/\//i.test(input)
    ? input
    : `https://${input}`;
  let url;
  try {
    url = new URL(candidate);
  } catch {
    throw new Error("That website address doesn't look valid.");
  }
  if (!["http:", "https:"].includes(url.protocol) || !url.hostname) {
    throw new Error("Only HTTP and HTTPS website addresses are supported.");
  }
  return url.href;
}

export class NavigationHistory {
  #items = [];
  #index = -1;

  get current() {
    return this.#items[this.#index] ?? "";
  }

  get canGoBack() {
    return this.#index > 0;
  }

  get canGoForward() {
    return this.#index >= 0 && this.#index < this.#items.length - 1;
  }

  push(url) {
    this.#items = this.#items.slice(0, this.#index + 1);
    this.#items.push(url);
    this.#index = this.#items.length - 1;
  }

  replace(url) {
    if (this.#index < 0) {
      this.push(url);
      return;
    }
    this.#items[this.#index] = url;
  }

  moveBack() {
    if (!this.canGoBack) return "";
    this.#index -= 1;
    return this.current;
  }

  moveForward() {
    if (!this.canGoForward) return "";
    this.#index += 1;
    return this.current;
  }
}