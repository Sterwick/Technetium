# Technetium

**A local proxy-powered browsing experiment.**

Technetium is an actively developed project exploring a custom web-viewing
experience built around its own HTTP proxy. Rather than handing a destination
page directly to the browser UI, the frontend server fetches it through the
Technetium proxy and returns sanitized content, metadata, and resolved links
for the interface to navigate.

> **Development status:** Technetium 0.1 is in preparation. This repository
> contains an early working prototype; the 0.1 release is not complete.

The dedicated Technetium website is **coming soon**. It is not online yet, and
no public URL has been announced. More information and project resources will
be shared there after launch.

## What works today

- A loopback-only forward proxy with HTTP forwarding and HTTPS `CONNECT`.
- A separate local frontend/API server that fetches pages through that proxy.
- A purple browser interface with address entry, back/forward, refresh,
  loading feedback, and error states.
- A local developer panel for page metadata, frontend messages, and proxied
  page/resource request status and timing.
- Basic HTML sanitization, isolated iframe rendering, relative-link handling,
  redirect following, and proxied image/CSS/font resources.
- Core HTTP request/response parsing and HTML metadata/link extraction.

The prototype has important limitations: page scripts, forms, nested frames,
and active SVG are disabled; the proxy and core parser are not yet fully
integrated; and end-to-end browser/proxy test coverage is still in progress.
See the [roadmap](docs/roadmap.md) and [TODO](TODO.md) for current status.

## Quick start

**Requirements:** Python 3.9 or newer. There are no third-party runtime
dependencies.

From the repository root, start the proxy in one terminal:

```powershell
py -3 -m servers.proxy_server
```

Start the frontend server in a second terminal:

```powershell
py -3 -m servers.frontend_server
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) and try
`https://example.com`. The frontend binds to `127.0.0.1:8000`; the proxy binds
to `127.0.0.1:8080`. Use <kbd>Ctrl</kbd>+<kbd>C</kbd> in each terminal to stop
the servers.

For detailed setup and configuration, see [Installation](docs/installation.md).

## Project structure

```text
core/       Shared HTTP parsing, metadata extraction, configuration, and tests
servers/    Local forward proxy and frontend/API server
frontend/   Browser interface: HTML, CSS, and JavaScript
tests/      Frontend server, sanitization, and URL validation tests
docs/       Architecture, installation, development, and roadmap
```

## Documentation

- [Architecture and request lifecycle](docs/architecture.md)
- [Installation and configuration](docs/installation.md)
- [Development workflow and API contract](docs/development.md)
- [Roadmap](docs/roadmap.md)
- [Implementation checklist](TODO.md)

## Tests

Run the standard-library test suite from the repository root:

```powershell
py -3 -m unittest discover -v
```

Tests do not require a live website.

## Safety and scope

Both servers are intended for local development and bind to loopback. The
frontend API restricts destinations to public HTTP/HTTPS sites on standard
ports, revalidates redirects, and enforces size limits. Website content is
untrusted: scripts and active markup are restricted and pages are shown in a
sandboxed frame. These prototype safeguards are not a claim of production
readiness or a hardened multi-user proxy.

## License

No license file is currently present. Licensing remains an open release
preparation item; until one is added, do not assume the project is
open-source-licensed.
