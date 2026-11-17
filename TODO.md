# TODO

Items are checked only when the corresponding behavior is present and
verified. This list tracks the current prototype and the remaining work for
the 0.1 target; 0.1 is not yet complete.

## Core functionality

- [x] Define request and response data models and parse HTTP/1.0 and HTTP/1.1
      headers in `core/`.
- [x] Extract HTML titles, descriptions, canonical URLs, and resolved links.
- [ ] Integrate the core request parser into the proxy request handling path.
- [ ] Add shared URL normalization and validation helpers used consistently by
      both servers.
- [ ] Add core tests for malformed headers, URL edge cases, and `<base>` link
      resolution.

## Proxy server

- [x] Keep the proxy listener bound to `127.0.0.1`.
- [x] Handle HTTP proxy requests and HTTPS `CONNECT` tunnels with socket relay.
- [x] Resolve destinations and reject non-public addresses.
- [ ] Verify request methods, headers, bodies, and response forwarding with
      automated local integration tests.
- [ ] Add correct handling for half-closed sockets, timeouts, and partial
      writes under concurrent connections.
- [ ] Confirm header forwarding and connection cleanup on malformed and
      interrupted requests.
- [ ] Replace remaining placeholder CDN substitution behavior with a clear
      supported/unsupported decision.

## Frontend server

- [x] Serve frontend files on a loopback-only HTTP listener.
- [x] Provide `/api/browse` JSON and `/api/resource` resource endpoints.
- [x] Route destination fetches through the Technetium proxy.
- [x] Validate schemes, standard ports, public destinations, redirects, and
      response-size limits.
- [x] Return status, content type, selected headers, metadata, sanitized HTML,
      and resolved links.
- [x] Restrict resource forwarding to supported image, CSS, and font types.
- [ ] Add automated tests that verify the actual proxy transport is used and
      redirect targets are revalidated.
- [ ] Improve error reporting for disconnected proxy and destination timeouts.
- [ ] Align frontend URL validation and frontend-server validation rules.

## Frontend

- [x] Provide a responsive browser-like interface with address input, back,
      forward, refresh, loading, and error states.
- [x] Keep page rendering in a sandboxed iframe and route supported links
      through the frontend API.
- [x] Rewrite supported CSS and image resources to the frontend resource API.
- [x] Apply a dark purple Technetium theme.
- [x] Add a local developer panel with page metadata, frontend messages, and
      proxied page/resource request diagnostics.
- [ ] Verify navigation history behavior for failures, redirects, and rapid
      successive requests.
- [ ] Decide whether scripting or form submission belongs in 0.1; keep it
      disabled until a safe and tested design exists.
- [ ] Improve rendering compatibility for malformed or document-fragment HTML.

## Integration

- [ ] Integrate core parsing, metadata, and errors into both server workflows
      where appropriate.
- [ ] Test a complete UI-to-frontend-to-proxy-to-origin request for HTTP and
      HTTPS.
- [ ] Test a redirect chain and a relative-link navigation through the UI.
- [ ] Test image and stylesheet loading through the proxy resource endpoint.
- [ ] Confirm all docs and startup instructions match the final entry points.

## Testing

- [x] Add unit tests for core request/response parsing and metadata.
- [x] Add frontend URL validation, sanitizer, and mocked API endpoint tests.
- [x] Add local socket-based proxy tests for basic HTTP forwarding and CONNECT
      byte relaying.
- [ ] Add proxy tests for malformed requests, request bodies, timeout behavior,
      and concurrent clients.
- [ ] Add redirect, resource, timeout, and response-size API tests.
- [ ] Add browser-level tests for address submission, link clicks, history,
      loading, and errors.
- [ ] Run the complete test suite on each supported Python version.

## Documentation

- [x] Document the current architecture and request lifecycle.
- [x] Document local installation, configuration, and test commands.
- [x] Document development workflow and API contract.
- [x] Publish a roadmap that distinguishes current functionality from plans.
- [x] Announce that the project website is coming soon without inventing a URL.
- [ ] Review docs after the core/proxy integration is complete.

## Release preparation

- [ ] Decide and document the project license and add its license file.
- [ ] Define a versioning and changelog policy before tagging a release.
- [ ] Verify clean startup and graceful shutdown instructions on supported
      platforms.
- [ ] Complete integration and browser-level tests.
- [ ] Review the security boundaries before describing 0.1 as release-ready.
- [ ] Mark 0.1 complete only after the release acceptance criteria pass.

## Future improvements

- [ ] Evaluate broader asset and document support without weakening isolation.
- [ ] Improve accessibility, browser controls, and user-facing diagnostics.
- [ ] Consider packaging and optional configuration only after the 0.1 workflow
      is stable.
- [ ] Assess non-local deployment only as a separate security-reviewed effort.
