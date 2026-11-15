# Technetium

Technetium is a lightweight HTTP/HTTPS forward proxy with a localhost-only,
browser-like web viewer.

## Requirements

- Python 3.9 or newer
- No third-party Python packages

## Run

Open two terminals in the repository directory. Start the proxy first:

```powershell
py -3 servers\proxy_server.py
```

In the second terminal, start the frontend:

```powershell
py -3 servers\frontend_server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Enter a URL such as
`https://example.com`. The frontend listens on `127.0.0.1:8000`; the forward
proxy listens on `127.0.0.1:8080`.

The frontend proxy endpoint can be configured with `TECHNETIUM_PROXY` before
starting the frontend server. The frontend port can be changed with
`TECHNETIUM_FRONTEND_PORT`.

## Browser and safety notes

The frontend fetches pages and resources through the Technetium proxy. Its
API permits only HTTP(S) on ports 80 and 443, checks resolved addresses to
reject private/local destinations, rechecks redirect targets, and applies
response size and redirect limits. The proxy also rejects non-public
destination addresses. Website markup is sanitized and shown in a sandboxed
iframe; website JavaScript, forms, nested frames, and active SVG markup are
not enabled. Images and stylesheets are routed through the frontend API.