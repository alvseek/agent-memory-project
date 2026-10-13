# ADR-025: Hermod Grows a Guarded, Hosted Shape and a Deployment of Its Own

**Date**: 2026-10-12

**Status**: Accepted

**Extends**: ADR-024 (*The Artifact-Generation Family Leaves the Overlay, and the Overlay Gets a Served Form*), which this supersedes on one point: `hermod-server` is no longer local-mode only.

---

## Problem

ADR-024 gave the overlay a served form and deliberately kept it local: `hermod-server` carried no issuer, no audience, no public base URL and no mode field, on the argument that a field which exists is a field that can be set wrong. Its config said so in one line — *hosting Hermod would mean porting Munnin's `build_auth` and its loopback guards, not flipping a flag here*.

That leaves a client that cannot install markdown unable to reach the overlay from anywhere but the machine that holds the repository. The framework's whole served story is "a client connects the memory core and the coding layer"; today only the memory half can be connected remotely. Separately, `hermod-server` has no deployment at all: no image, no release pipeline, and no repository holding the instance the way `munnin-deploy` holds Munnin's.

## Decision

**We decided to**: give `hermod-server` the token verification ADR-024 declined, as a port of Munnin's Logto resource-server shape including the tenant that token resolves to (**corrected by [ADR-027](2026-10-13-hermod-store-is-valaskjalf-records.md)**: this ADR ports the shape *minus* its tenancy, and Hermod now resolves a tenant from the verified token exactly as Munnin does, because the rows it reads are the memory store's), and to deploy it on the same box as Munnin through a new private umbrella, `hermod-deploy`, in the shape `munnin-deploy` already established.

The MCP face is verified exactly when an issuer is configured, and `/health` is never verified. One release pipeline builds the image in the public product repo and a second deploys an immutable tag from the private one. The two repos' boundary is unchanged: the dependency still runs one way, from `hermod-deploy` to `hermod-server`, and nothing in the product names the deployment.

**Why we chose this:**
- The exposure is real and specific. The MCP face serves the overlay's procedures *and* the project store, read **and write**, so a hosted Hermod with no guard would let anyone read a project's internal context and rewrite it. The store's content is the framework's own operating knowledge; the procedures are public, the store is not.
- The port is smaller than it sounds, and smaller still for the reason ADR-024 gave: Munnin already solved discovery, audience binding and the TLS-proxy redirect trap, and each of those fixes is a comment explaining a failure that cost a session. Re-deriving them here would be paying for them twice.
- Hosting is what makes the served form *useful*. A served overlay that only answers on the box that holds the repository duplicates the markdown install rather than replacing it.

## What to Build (Requirements)

- `hermod-server`: Logto JWKS verification in front of the mounted MCP face, ported from Munnin — `LogtoAuthProvider` (derived OIDC paths, pinned `scopes_supported`, `set_mcp_path` binding the verifier's audience), the RFC 9728 protected-resource document served from the **root**, and the path normaliser that keeps a spec-following client's no-slash `/mcp` from being answered with an http:// redirect behind a TLS proxy. `/health` stays on the parent app and therefore stays open.
- **No mode switch.** Verification follows the issuer's presence; with no issuer, the existing loopback guards apply and refuse any configuration that would leave the server reachable from elsewhere. This is a deliberate divergence from Munnin's `MUNNIN_AUTH`, which exists because Munnin's laptop shape means something Hermod's cannot (one constant tenant), and because a switch has two plausible defaults that fail differently: one refuses the documented local run, the other can leave a configured issuer unused.
- The product carries the build half: a `Dockerfile` (serving the overlay submodule as read-only content, as Munnin serves `control-files`), a `.dockerignore`, a local `compose.yaml`, and `.github/workflows/build-image.yml` publishing `ghcr.io/alvseek/hermod` tagged by short commit SHA.
- New private repo `hermod-deploy`: `hermod-server` vendored as a submodule, Kamal config at `config/deploy.yml`, a manual `deploy.yml` workflow running `kamal setup|deploy|rollback --skip-push`, and a README recording the topology.

**Success Criteria:**
- A request to `/mcp` with no token is refused 401; the same request with a token the issuer minted is served; `/health` answers both ways.
- The bare `/mcp` path answers the guard rather than a redirect, with redirects disabled in the client.
- The protected-resource document answers at the root path the 401 advertises, carrying the resource identifier.
- A public base URL with no issuer refuses to start, and so does a non-loopback bind with no issuer.
- `hermod-deploy` pins a commit of `hermod-server` and deploys a tag its CI published.

## Alternatives Rejected

- **Deploy it open.** The store tools write. An open endpoint is a public writable copy of every project's context, not merely a leaked document.
- **A single static bearer token instead of Logto.** Cheaper by an afternoon and wrong for the fleet: a token that is not tied to an issuer has no expiry, no revocation, and no second party who can hold it; and every other hosted surface here already trusts Logto.
- **Deploy with the port unpublished (SSH tunnel only).** Keeps the server genuinely local, which is honest but not what "deploy this" asks for; the point of the hosted shape is the client that cannot install markdown, and such a client cannot open a tunnel.
- **A mode switch mirroring `MUNNIN_AUTH`.** Adds a state that can be set wrong while buying nothing: Hermod has no tenant for the local shape to resolve differently.
- **Keep the auth out of the product and terminate it in the deploy.** It cannot be done there. Token verification has to run in front of the MCP transport, which lives in the app; a reverse proxy can hold a static credential but cannot verify a Logto token's audience against a resource identifier.
- **Let the deploy repo carry the Dockerfile.** The image is built by the public repo's CI from public source; the private repo holds only the instance, which is the split ADR-024's cousins already set.

---

**Full context**: the deployment's own record is [`hermod-deploy`](https://github.com/alvseek/hermod-deploy) (private), which pins this repo's product as a submodule.
