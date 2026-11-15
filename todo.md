# TODO

- [x] Create the initial browser frontend
  - [x] Add a responsive dark-themed Technetium interface and address bar
  - [x] Add back, forward, refresh, loading status, and current URL display
  - [x] Add client-side navigation history and URL normalization
  - [x] Render fetched pages in a sandboxed iframe
  - [x] Route page link navigation through the frontend API
  - [x] Resolve page links, images, and stylesheets against the fetched page URL
  - [x] Show useful navigation errors
  - [ ] Revisit page JavaScript support; fetched scripts are currently removed/disabled

- [x] Implement the initial frontend server
  - [x] Serve frontend files on localhost
  - [x] Add a browser-facing JSON page API and resource endpoint
  - [x] Fetch through the Technetium proxy instead of making direct outbound requests
  - [x] Follow redirects while revalidating destinations
  - [x] Return page HTML, metadata, links, status, and selected headers
  - [x] Sanitize fetched HTML and rewrite supported resource URLs
  - [x] Restrict schemes, ports, and local/private destinations

- [x] Make the existing proxy import-safe and add basic destination checks
- [x] Document initial local launch instructions in `readme.md`
- [ ] Integrate with and review the core modules as they are developed
- [ ] Finish broader testing of links, resources, redirects, failures, and browser behavior
- [ ] Review and refine the initial implementation after core integration