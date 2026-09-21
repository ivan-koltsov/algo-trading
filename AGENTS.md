# Agent Instructions & Guidelines

## Git Branch & Environment Deployment Workflow

### 1. Environments Architecture

| Environment | Git Branch | Cloud Render Services | URL Profile | Environment Indicator |
| :--- | :--- | :--- | :--- | :--- |
| **Production** | `main` | `algo-trading-api-prod`<br>`algo-trading-ui-prod` | `APP_ENV=production`<br>`VITE_APP_ENV=production` | `🟢 PROD` badge |
| **Development / Preview** | `dev` | `algo-trading-api-dev`<br>`algo-trading-ui-dev` | `APP_ENV=development`<br>`VITE_APP_ENV=development` | `🟡 DEV` badge |
| **Local Host** | `dev` | Local FastAPI (`:8001`)<br>Local Vite (`:3000`) | `APP_ENV=development`<br>`VITE_APP_ENV=development` | `🟡 DEV` badge |

---

### 2. Branch Protection & Pre-Commit Hook

1. **Active Feature Development**:
   - Always perform feature development, bug fixes, and tests on the `dev` branch.
   - **NEVER** commit directly to `main` or `master`.
   - A pre-commit hook in `.githooks/pre-commit` is active (`core.hooksPath = .githooks`) and will block any direct commit attempt to `main` or `master`.

2. **Testing & Verification**:
   - Verify changes on `dev` locally (API on `http://localhost:8001`, UI on `http://localhost:3000`).
   - Run linter/build checks:
     - `cd ui && npm run build`
     - Backend tests: `PYTHONPATH=. ./.venv/bin/python -m unittest discover -s api/tests -p "test_*.py"`

3. **Promoting from Dev to Production**:
   - Once changes are verified on `dev`, push `dev` to `origin/dev`.
   - The Dev Render environment automatically redeploys for preview.
   - Create a Pull Request from `dev` to `main`.
   - After review (and automated CodeRabbit review), merge the PR into `main` to trigger automated deployment to the Production Render environment.
