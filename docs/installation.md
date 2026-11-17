# Installation

## Requirements

- Python 3.9 or newer
- No third-party Python packages

The frontend uses browser-native HTML, CSS, and JavaScript. Node.js is not
required to run it.

## Start the application

From the repository root, open two terminals.

Terminal 1, start the proxy:

```powershell
py -3 -m servers.proxy_server
```

Terminal 2, start the frontend/API server:

```powershell
py -3 -m servers.frontend_server
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and enter a public HTTP or
HTTPS address, such as `https://example.com`. Stop each server with
<kbd>Ctrl</kbd>+<kbd>C</kbd>.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `TECHNETIUM_FRONTEND_PORT` | `8000` | Frontend HTTP listener port |
| `TECHNETIUM_PROXY` | `http://127.0.0.1:8080` | HTTP proxy URL used for destination requests |

The proxy currently listens on `127.0.0.1:8080`; its host and port are
configured by constants in `servers/proxy_server.py`.

## Run tests

From the repository root:

```powershell
py -3 -m unittest discover -v
```

The tests use only the Python standard library and do not require a live
destination website.

## Troubleshooting

- **The frontend cannot reach the proxy:** start the proxy first and confirm
  that port `8080` is available.
- **The frontend port is already in use:** set `TECHNETIUM_FRONTEND_PORT` to a
  free port before starting the frontend server.
- **A site is rejected:** only standard HTTP/HTTPS ports and public Internet
  destinations are permitted. Local/private destinations are intentionally
  blocked.
- **A page looks incomplete:** scripting, forms, embedded frames, and other
  dynamic behaviors are disabled in this prototype.
- **A module cannot be found:** run the commands from the repository root
  using `py -3 -m ...` as shown above.
