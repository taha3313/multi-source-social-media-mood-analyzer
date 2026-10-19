# Deployment

The setup follows Quranic Shazam's split API/frontend layout: locked dependencies, Make targets, two Dockerfiles, Compose, CI and a Render Blueprint. It does not copy that project's service identities, domain, credentials or deployment hooks.

## Render

`render.yaml` defines a Docker API in Frankfurt and a static frontend. The API explicitly uses the free plan; the frontend has no paid compute plan. No database, paid disk or worker is provisioned. Both services request native deployment after CI passes, including both Docker image builds. This configuration has not been proven live for this repository.

1. Run `make check` and `docker compose build` locally.
2. Validate with `render blueprints validate render.yaml` when the Render CLI is installed. JSON Schema validation alone cannot verify workspace-specific constraints.
3. Commit and push the changes to the GitHub repository. Render cannot read local files.
4. Open [Create Blueprint](https://dashboard.render.com/blueprint/new?repo=https://github.com/taha3313/multi-source-social-media-mood-analyzer), connect the GitHub repository and review the resources.
5. Supply credentials in Render's secret prompts. At least one source must have valid credentials; unused source values may remain empty. Never commit actual credentials.
6. Confirm the assigned service URLs. Update frontend `VITE_API_URL` and backend `CORS_ORIGINS` if Render assigns different names or you add a custom domain. Rebuild the frontend after URL changes.
7. Apply the Blueprint and monitor each deployment to `live`. Verify the exact deployed commit, `/health`, frontend assets and a real topic analysis. Watch model-loading memory and request duration.
8. On a subsequent change, verify that passing GitHub checks actually triggers a Render deployment. CI passing alone does not prove deployment. If native triggers fail, diagnose the integration before adding an optional hook fallback; hooks are secrets.

## Memory and cold starts

The API imports model libraries and downloads/loads both models only when an analysis starts. Health probes remain lightweight. This makes startup possible without preloading models, but **does not prove analysis fits Render's free 512 MB RAM**. PyTorch, a RoBERTa emotion model, MiniLM and batching may exceed that budget. Do not describe this Blueprint as a verified free inference deployment until real analysis succeeds under that limit.

Measure peak memory with `docker stats` during a credentialed request, and test with a 512 MB container limit before release. If it fails, reduce/quantize models or move inference to an explicitly chosen hosted provider; changing to a paid plan is a separate decision. Free Render storage is ephemeral, so model downloads can recur. Compose has a persistent model-cache volume; Render deliberately has no paid disk.

One analysis is admitted at a time per process; another receives 503. Only one Uvicorn worker is used to avoid duplicate models. The request remains synchronous from the client's perspective. Fetch timeouts do not cancel underlying blocking threads; a job queue and stricter provider budgets remain future work.

`/health` reports liveness, model load state and which source credentials are present. It does not certify valid credentials, provider availability, download success or inference quality. A failed provider currently can appear as an empty result; see the feature review before treating charts as reliable monitoring.

## Local Docker

`make docker-up` creates example env files when absent. Set credentials in `backend/.env`. The frontend is on loopback port 8080 and API on loopback port 8000. `make docker-down` retains the named model cache; `docker compose down -v` removes it.

## Dependency maintenance

Backend dependencies are defined in `backend/pyproject.toml`, pinned transitively in `uv.lock` and mirrored in `requirements.txt` for pip users. Update them deliberately with `uv lock --project backend --upgrade`, rerun checks, then regenerate the compatibility file:

```bash
uv export --project backend --frozen --no-dev --no-hashes --no-emit-project --emit-index-url --output-file backend/requirements.txt
```

Docker uses uv 0.8.22 and the frozen lock. PyTorch comes from its explicit CPU wheel index. GPU execution requires a separately tested dependency/image configuration.

## Other observed follow-up work

The existing frontend dependency tree reports 19 npm audit advisories (1 low, 5 moderate, 13 high). No automatic major-version upgrades were applied as part of deployment scaffolding. Review the affected direct/transitive paths before a public release. Vite also reports a main JavaScript chunk above 500 kB; split chart/UI dependencies when optimizing load performance.
