# Deploying the Flask Portfolio App to Railway (Free Tier)

These steps focus on deploying the Flask app (`personal_website/portfolio/app.py`) to Railway using the free tier. The Streamlit dashboard is out of scope.

## Prerequisites
- Railway account (free tier).
- GitHub repo connected to Railway (recommended) or Railway CLI installed locally (`npm i -g @railway/cli`).
- Python 3.12 runtime supported by Railway Nixpacks (default is fine).
- Environment variables available: `PYDANTIC_AI_GATEWAY_API_KEY`, `LLM_MODEL` (optional override), and any others from `.env.example`.

## Project Setup on Railway
1) Create a new project in Railway.
2) Add a “GitHub Repo” service and select this repository, or create a “Blank” service and deploy via CLI from your local clone.
3) Set the service root (if prompted) to the repo root. Railway’s Python Nixpacks will detect `pyproject.toml` and install dependencies automatically.

## Runtime Command
- Entry point (web process):
  ```bash
  uv run flask --app personal_website.portfolio.app:app run --host 0.0.0.0 --port $PORT
  ```
  Railway sets `$PORT`; keep `0.0.0.0`. Using `uv run` ensures the virtual env is active from the lockfile.
- Alternatively, create a `Procfile` at repo root (optional but explicit):
  ```
  web: uv run flask --app personal_website.portfolio.app:app run --host 0.0.0.0 --port $PORT
  ```

## Environment Variables
Set these in the Railway service:
- `PYDANTIC_AI_GATEWAY_API_KEY` (required for LLM calls; without it, tests/LLM features may be skipped or limited).
- `LLM_MODEL` (optional; defaults to `gateway/google-vertex:gemini-2.5-pro`).
- Any overrides from `.env.example` (e.g., `DEBUG=false`, `LOG_LEVEL=INFO`, `LLM_MAX_INPUT_CHARS`, etc.).
Note: Never commit `.env`; manage secrets in Railway’s dashboard.

## Deploy via GitHub Integration (Recommended)
1) In Railway, enable deployments from the `main` branch.
2) Add a GitHub workflow (example `.github/workflows/deploy-railway.yml`) that runs tests before deploy:
   ```yaml
   name: Deploy to Railway
   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: astral-sh/uv@v2
           with:
             python-version: "3.12"
         - run: uv sync --extra dev
         - run: uv run pytest
         - uses: railwayapp/action@v2
           with:
             serviceId: ${{ secrets.RAILWAY_SERVICE_ID }}
             railwayToken: ${{ secrets.RAILWAY_TOKEN }}
   ```
   - Store `RAILWAY_TOKEN` and `RAILWAY_SERVICE_ID` as GitHub secrets (get them from Railway → “Deploy from CI” settings).
   - The action builds using Railway’s infra after tests pass.

## Deploy via Railway CLI (Manual Option)
1) Install CLI: `npm i -g @railway/cli`.
2) Login: `railway login`.
3) Link project: `railway link` (select the project and service).
4) Deploy: `railway up`.

## Free Tier Considerations
- Limited monthly runtime and network; app may sleep/idle between requests.
- Cold starts: expect a few seconds warmup; keep the app lightweight.
- Avoid unnecessary background processes; only the web process should run.
- Monitor usage in Railway dashboard to stay within limits.

## Health Checks
- Railway auto-exposes the web process. Confirm `/` returns 200 (portfolio command UI).
- Add a lightweight health endpoint if desired (e.g., `/healthz` returning JSON 200) to improve readiness checks.

## Optional Pre-Deploy Tests in CI
If you want to gate deploys on tests before the Railway action:
```yaml
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/uv@v2
        with:
          python-version: "3.12"
      - run: uv sync --extra dev
      - run: uv run pytest
      - uses: railwayapp/action@v2
        with:
          serviceId: ${{ secrets.RAILWAY_SERVICE_ID }}
          railwayToken: ${{ secrets.RAILWAY_TOKEN }}
```

## What you’ll see after deploy
- Railway will build the image from `pyproject.toml`, install deps, then start the `web` command.
- Once live, Railway shows a public URL; use that as your portfolio endpoint for the Flask app.

## Logfire in Deployment
- The app calls `logfire.configure()` and `logfire.instrument_pydantic_ai()` at import time. In production you need a valid Logfire token.
- Recommended: obtain a token via `uv run logfire auth` locally, then run `uv run logfire auth --print-token` (or read `~/.logfire/default.toml`) and store the token as `LOGFIRE_TOKEN` in Railway.
- Set `LOGFIRE_ENVIRONMENT` (optional) to tag the environment, e.g., `production`.
- If you use a non-default region/base URL, set `LOGFIRE_BASE_URL` to match the token’s region.
- No tokens or `.logfire` files should be committed; rely on Railway secrets for `LOGFIRE_TOKEN` (and optionally `LOGFIRE_BASE_URL`, `LOGFIRE_ENVIRONMENT`).
