# Contributing
- Create feature branches from `main`.
- Write clear commit messages (Conventional Commits recommended).
- Open a PR with a short summary and how to test.


## Added Sample Branch Workflow
-----------------------------------------

- The **`main`** branch contains stable, working code.
- All new work should be developed in a dedicated **feature branch**:
  ```bash
  git checkout -b feature/short-description

## Running Lint and Tests Locally

Before committing code, verify everything passes:

```bash
ruff check .
pytest -q