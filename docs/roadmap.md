# Roadmap

Technetium is actively under development. Version 0.1 is a target, not a
completed release. The project's dedicated website is coming soon; no public
website URL or launch date has been announced.

## 0.1 — initial functional release

- Make the loopback proxy's HTTP forwarding and HTTPS CONNECT paths reliable
  and test them end to end.
- Integrate the shared core parser and metadata extraction into the request
  lifecycle without duplicating parsing logic.
- Complete the browser workflow for redirects, link navigation, back/forward,
  and supported page assets.
- Keep page content isolated and document the limits of supported markup.
- Provide repeatable tests, local startup instructions, and accurate release
  documentation.

0.1 should not be called complete until core browsing and proxy behavior have
been verified together.

## Future 0.x releases

- Expand standards-compliant HTTP behavior and add robust connection handling.
- Improve resource support and rendering for common pages while preserving
  isolation.
- Add automated integration and browser-level regression tests.
- Improve diagnostics and user-facing explanations for blocked or failed
  requests.
- Establish release packaging and compatibility expectations.

## Longer-term possibilities

These are exploratory and are not commitments:

- A richer browsing interface and configurable privacy controls.
- More extensible metadata and navigation support.
- Additional deployment options beyond the local-development model, following
  a separate security review.
- Public project resources through the upcoming Technetium website.
