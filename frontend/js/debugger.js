export class DeveloperTools {
  constructor() {
    this.toggleButton = document.querySelector("#debug-toggle");
    this.panel = document.querySelector("#debug-panel");
    this.networkList = document.querySelector("#debug-network-list");
    this.consoleList = document.querySelector("#debug-console-list");
    this.pageInfo = document.querySelector("#debug-page-info");
    this.tabs = [...document.querySelectorAll("[data-debug-tab]")];
    this.panes = {
      network: document.querySelector("#debug-network-pane"),
      console: document.querySelector("#debug-console-pane"),
      page: document.querySelector("#debug-page-pane"),
    };
    this.consoleEntries = [];
    this.page = null;
    this.activeTab = "network";
    this.open = false;
    this.refreshing = false;
    this.refreshTimer = null;

    this.toggleButton.addEventListener("click", () => this.setOpen(!this.open));
    document.querySelector("#debug-close").addEventListener("click", () => this.setOpen(false));
    this.tabs.forEach((tab) => {
      tab.addEventListener("click", () => this.showTab(tab.dataset.debugTab));
    });
    this.showTab(this.activeTab);

    window.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.shiftKey
          && event.key.toLowerCase() === "d") {
        event.preventDefault();
        this.setOpen(!this.open);
      } else if (event.key === "Escape" && this.open) {
        this.setOpen(false);
      }
    });
  }

  setOpen(open) {
    this.open = open;
    this.panel.hidden = !open;
    this.toggleButton.setAttribute("aria-expanded", String(open));
    if (open) {
      this.refreshNetwork();
      this.refreshTimer = window.setInterval(() => this.refreshNetwork(), 1500);
    } else if (this.refreshTimer !== null) {
      window.clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  showTab(name) {
    if (!this.panes[name]) return;
    this.activeTab = name;
    this.tabs.forEach((tab) => {
      const active = tab.dataset.debugTab === name;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", String(active));
    });
    Object.entries(this.panes).forEach(([paneName, pane]) => {
      pane.hidden = paneName !== name;
    });
  }

  log(message, level = "info") {
    this.consoleEntries.push({
      time: new Date().toLocaleTimeString(),
      message: String(message),
      level,
    });
    this.consoleEntries = this.consoleEntries.slice(-100);
    if (this.activeTab === "console") this.renderConsole();
  }

  setPage(page) {
    this.page = {
      URL: page.url,
      Status: page.status,
      "Content type": page.content_type,
      Title: page.title,
      Description: page.description,
      "Canonical URL": page.canonical_url,
      Links: page.links?.length ?? 0,
    };
    if (this.activeTab === "page") this.renderPage();
  }

  async refreshNetwork() {
    if (this.refreshing) return;
    this.refreshing = true;
    try {
      const response = await fetch("/api/debug/logs?limit=100", { cache: "no-store" });
      if (!response.ok) throw new Error(`Debug endpoint returned HTTP ${response.status}`);
      const result = await response.json();
      this.renderNetwork(result.entries ?? []);
    } catch (error) {
      this.log(`Network log unavailable: ${error.message}`, "error");
    } finally {
      this.refreshing = false;
    }
  }

  renderNetwork(entries) {
    this.networkList.replaceChildren();
    if (!entries.length) {
      this.networkList.append(this.emptyMessage("No requests recorded yet."));
      return;
    }

    for (const entry of entries) {
      const row = document.createElement("div");
      row.className = "debug-network-row";
      const status = entry.status ?? "ERR";
      const cells = [
        entry.kind ?? "request",
        String(status),
        `${entry.duration_ms ?? 0} ms`,
        entry.content_type ?? entry.error ?? "",
        entry.url ?? "",
      ];
      cells.forEach((value, index) => {
        const cell = document.createElement("span");
        cell.textContent = value;
        if (index === 1) {
          cell.className = "debug-status";
          if (entry.error || (typeof status === "number" && status >= 400)) {
            cell.classList.add("is-error");
          }
        } else if (index === 4) {
          cell.className = "debug-url";
          cell.title = value;
        }
        row.append(cell);
      });
      this.networkList.append(row);
    }
  }

  renderConsole() {
    this.consoleList.replaceChildren();
    if (!this.consoleEntries.length) {
      this.consoleList.append(this.emptyMessage("No console messages yet."));
      return;
    }

    for (const entry of this.consoleEntries) {
      const row = document.createElement("div");
      row.className = `debug-console-entry${entry.level === "error" ? " is-error" : ""}`;
      const time = document.createElement("span");
      time.className = "debug-console-time";
      time.textContent = entry.time;
      const message = document.createElement("span");
      message.className = "debug-console-message";
      message.textContent = entry.message;
      row.append(time, message);
      this.consoleList.append(row);
    }
  }

  renderPage() {
    this.pageInfo.replaceChildren();
    if (!this.page) {
      const term = document.createElement("dt");
      term.textContent = "Page";
      const description = document.createElement("dd");
      description.textContent = "No page loaded";
      this.pageInfo.append(term, description);
      return;
    }

    for (const [label, value] of Object.entries(this.page)) {
      if (value === undefined || value === null || value === "") continue;
      const term = document.createElement("dt");
      term.textContent = label;
      const description = document.createElement("dd");
      description.textContent = String(value);
      this.pageInfo.append(term, description);
    }
  }

  emptyMessage(text) {
    const message = document.createElement("p");
    message.className = "debug-empty";
    message.textContent = text;
    return message;
  }
}
