# Local validation — 2026-10-19

## Passed

- Frontend `npm run lint` and `npm run build`.
- Browser dashboard rendering. The pre-existing `react-loadly` integration caused repeated hook errors; replacing it with a local loading component removed those errors.
- Backend correctness lint using the existing local Ruff executable and this project's configuration.
- All 10 backend checks in a temporary Python 3.10 environment using system packages plus cached source-client/test dependencies. These include model-free health, missing credentials, input limits, CORS and the single-post/negative-score regression. This is smoke coverage, not verification of the locked Python 3.11 environment.
- Real local HTTP calls: `/health` returned 200 with models unloaded and no sources configured; `/analyze` returned the expected missing-credentials 503.
- `uv lock --check --project backend`.
- `docker compose config --quiet`.
- `render.yaml` against Render's current public JSON Schema using `check-jsonschema`.
- `git diff --check`.

## Incomplete

- The full locked Python installation was interrupted after more than ten minutes of slow downloads. `make check` therefore did not complete in that environment.
- Full Docker image builds were interrupted during base-image downloads; both BuildKit and the legacy builder were attempted. Container startup, Nginx proxying and inference under a container memory limit remain unverified.
- The Render CLI is not installed; platform/workspace-aware Blueprint validation was not run.
- No source credentials were supplied, so live provider collection, model inference, model accuracy and quota usage were not tested.
- At the time of this local validation, no commit, push or Render deployment had occurred. CI includes both Docker image builds for remote validation.

Temporary application servers and build/download attempts were stopped after verification. Local example env files contain no credentials and are ignored by Git.
