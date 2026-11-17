# Architecture

Technetium 0.1 is a localhost-operated browsing prototype composed of a
forward proxy, a frontend/API server, a small shared core package, and a
vanilla HTML/CSS/JavaScript client. It has no third-party runtime dependencies.

## Components

- **Proxy server (`servers/proxy_server.py`)** listens on `127.0.0.1:8080`.
  It accepts HTTP proxy requests and HTTPS `CONNECT` tunnels, relays bytes
  using sockets and `select`, and serves connections on daemon threads. It
  rejects destinations that resolve to non-public IP addresses.
- **Frontend server (`servers/frontend_server.py`)** listens on
  `127.0.0.1:8000` by default. It serves static frontend files and provides
  JSON page and resource endpoints. All destination fetches are sent through
  the configured Technetium proxy.
- **Core (`core/`)** contains HTTP request/response parsing, shared errors and
  configuration, and HTML metadata/link extraction. The frontend server uses
  core metadata extraction. The low-level proxy has not yet been refactored to
  use the core parser.
- **Frontend (`frontend/`)** provides browser controls, client-side navigation
  history, page rendering, and the purple browser interface.

## Request lifecycle

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend UI
    participant Front as Frontend server
    participant Proxy as Technetium proxy
    participant Web as Destination site

    User->>UI: Enter URL or choose a link
    UI->>Front: GET /api/browse?url=...
    Front->>Front: Validate scheme, port, and resolved addresses
    Front->>Proxy: HTTP request or HTTPS CONNECT via proxy
    Proxy->>Web: Forward request/tunnel
    Web-->>Proxy: Response
    Proxy-->>Front: Response bytes and headers
    Front->>Front: Follow validated redirects; parse metadata
    Front->>Front: Sanitize markup and rewrite supported assets
    Front-->>UI: JSON with status, HTML, and resolved links
    UI->>UI: Render in a sandboxed iframe
```

The HTTP and HTTPS flows differ at the proxy: it accepts HTTP requests in
absolute-form and forwards them to the destination in origin-form; HTTPS
requests use `CONNECT` to create a byte tunnel.

## Frontend/API communication

- `GET /` and other static paths serve files under `frontend/`.
- `GET /api/browse?url=<encoded-url>` fetches a page through the proxy and
  returns `url`, `status`, `content_type`, selected response `headers`,
  `title`, `description`, `canonical_url`, sanitized `html`, and resolved
  `links` (`text` and absolute `url`).
- `GET /api/resource?url=<encoded-url>` serves supported image, CSS, and font
  resources after validation. CSS resource URLs are rewritten to this endpoint.
- `GET /api/debug/logs?limit=<count>` returns a bounded local request log for
  the developer panel. Query values and URL credentials are redacted; response
  bodies and request headers are not recorded.

The browser UI sends anchor clicks back to its own frontend code, which
navigates using `/api/browse`; it does not navigate the top-level application
document to the destination. The click handler is a separate same-origin
frontend script because `srcdoc` inherits the host document's content security
policy.

The resource endpoint returns permissive CORS headers for supported static
assets so fonts can load from the sandboxed iframe's opaque origin. Destination
validation and supported resource types still apply; the JSON page API does
not enable cross-origin reads.

The developer panel opens from the **Dev** control or `Ctrl+Shift+D` and
provides Network, Console, and Page views. It reports frontend navigation
messages, page metadata, and recent page/resource fetches. It is an application
diagnostic view, not an interactive JavaScript console or remote-site debugger;
remote JavaScript remains disabled.

## Untrusted content boundaries

Fetched markup is sanitized and placed in an iframe with a sandbox that omits
same-origin permission. Remote scripts, forms, nested frames, active SVG
markup, and event-handler attributes are removed or blocked. A small
frontend-owned click handler supports navigation for sanitized links. A
content security policy restricts resources to the frontend resource API.

The frontend server binds to loopback, checks the request Host, permits only
HTTP/HTTPS on ports 80/443, rejects local/private DNS results, rechecks
redirects, and caps redirects and response sizes. The proxy also binds to
loopback and rejects non-public destination addresses. These controls are
appropriate for local development, not a substitute for a hardened,
multi-user deployment.

## Current boundaries

The first release target is intentionally limited. Page JavaScript is disabled;
forms and many dynamic-site behaviors are unsupported. The proxy currently
implements its own request-line and socket relay path rather than consuming
the shared core request/response parser. These are tracked in [TODO.md](../TODO.md).
