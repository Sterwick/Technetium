# Development

## Repository organization

```text
core/       Shared HTTP parsing, metadata extraction, configuration, and tests
servers/    Local forward proxy and frontend/API server
frontend/   Browser interface (HTML, CSS, JavaScript)
docs/       Architecture, installation, development, and roadmap
tests/      Frontend server, URL validation, and sanitization tests
```

The core modules are independently tested in `core/tests/`. The proxy server
is a standalone socket-based server; integration with the shared parser remains
an open task.

## Workflow

1. Make a focused change in the component that owns the behavior.
2. Add a regression test for behavior or safety boundaries affected.
3. Run all standard-library tests:

   ```powershell
   py -3 -m unittest discover -v
   ```

4. For interactive checks, start both servers as described in
   [installation](installation.md) and browse public HTTP/HTTPS pages.
5. Update [TODO.md](../TODO.md) and the relevant documentation when behavior
   or limitations change.

## Conventions

- Keep the runtime dependency-free unless a demonstrated need justifies a
  dependency.
- Keep server responsibilities separate: the proxy transports requests; the
  frontend server serves the application and its page/resource API.
- Keep services bound to loopback for local development.
- Validate destinations before every request, including redirects and assets.
- Treat retrieved markup and headers as untrusted. Keep content isolated from
  the application origin and avoid exposing local APIs to page content.
- Document behavior that is actually implemented; mark future work as planned.

## Frontend/API contract

The frontend calls `GET /api/browse?url=<encoded-url>` and expects JSON
containing the final URL, HTTP status, content type, selected headers, page
metadata, sanitized HTML, and absolute links. Resource URLs in sanitized HTML
are rewritten to `GET /api/resource?url=<encoded-url>`. Both endpoints validate
destinations and use the Technetium proxy for outbound requests.

When changing this contract, update the API tests, frontend rendering code,
and [architecture documentation](architecture.md) together.

## Developer panel

Open **Dev** in the browser toolbar or press `Ctrl+Shift+D`. Network shows
recent page and resource requests with status, content type, and elapsed time.
Console shows navigation messages and errors; Page shows metadata for the
current document. Debug logs are kept in a bounded in-memory buffer, omit
response bodies and headers, and redact URL credentials and query values.
This tool does not evaluate JavaScript in fetched pages.
