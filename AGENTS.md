# Agent Instructions & Guidelines

## Git Branch & Deployment Workflow

1. **Active Development Branch**:
   - Always perform feature development, bug fixes, and tests on the `dev` branch.
   - **NEVER** commit directly to `main` or `master`.
   - A pre-commit hook in `.githooks/pre-commit` is active (`core.hooksPath = .githooks`) and will block any direct commit attempt to `main` or `master`.

2. **Testing & Verification**:
   - Always verify and test changes on `dev` locally (API on `http://localhost:8001`, UI on `http://localhost:3000`).
   - Run linter/build checks:
     - `cd ui && npm run build`
     - Python syntax / endpoint verification.

3. **Promoting to Production**:
   - Once changes are verified on `dev`, push `dev` to `origin/dev`.
   - Create a Pull Request from `dev` to `main`.
   - After review (and automated CodeRabbit review), merge the PR to `main` to trigger automated deployment on Render.
