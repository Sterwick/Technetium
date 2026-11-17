document.addEventListener("click", (event) => {
  const target = event.target;
  const link = target && typeof target.closest === "function"
    ? target.closest("a[data-technetium-url]")
    : null;
  if (!link) return;

  const url = new URL(link.getAttribute("data-technetium-url"));
  if (url.protocol !== "http:" && url.protocol !== "https:") return;

  event.preventDefault();
  event.stopPropagation();
  parent.postMessage({ type: "technetium:navigate", url: url.href }, "*");
}, true);
