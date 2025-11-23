# Contributing to Zeta Reason

Thanks for your interest in improving Zeta Reason! This guide keeps contributions consistent and smooth.

## How to Contribute
- **Issues first**: Open a GitHub issue for bugs/feature requests. Clearly describe the problem, expected behavior, and repro steps.
- **Branching**: Create a feature branch from `main` (e.g., `feature/my-change`).
- **Coding standards**: Follow existing patterns and keep changes minimal and focused. Add comments sparingly for non-obvious logic.

## Setup
1. Clone the repo and install deps:
   - Backend: `cd backend && python -m venv venv && source venv/bin/activate && pip install -e .`
   - Frontend: `cd frontend && npm install`
2. Configure API keys in `backend/.env` as needed for provider tests.

## Before You Commit
- **Backend**: `pytest`; optional: `ruff check .` and `mypy zeta_reason/`
- **Frontend**: `npm run lint` and `npm run type-check`; run relevant UI/unit tests if present.
- Remove local artifacts (experiments, screenshots, cache) from commits.

## Pull Requests
- Keep PRs scoped; one logical change per PR.
- Include a short summary, screenshots if UI-facing, and mention any new config/env needs.
- Ensure CI passes (tests/lint/type-check).

## Code of Conduct
Be respectful and constructive. Disagreements are fine; disrespect is not.

## Security
Do not commit secrets or API keys. Report security issues privately via email: a4santho@uwaterloo.ca.
