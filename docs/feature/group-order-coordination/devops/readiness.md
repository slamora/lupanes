# DEVOPS Readiness — group-order-coordination v1

**Wave**: DEVOPS | **Date**: 2026-06-16

This is a feature inside an existing Django app maintained by a single volunteer. No new
infrastructure is required. This note records the platform constraints DELIVER must respect
so the change ships green through the existing pipeline.

## Existing pipeline (must stay green)

- **CI**: `.github/workflows/django.yml` runs `python manage.py test` on push/PR to `main`,
  matrix Python 3.10 + 3.11. CI copies `.env.example` → `.env` before running.
- **Lint**: pre-commit runs `flake8` (max-line-length 120; `migrations/`, `tests/`, `static/`
  excluded) plus trailing-whitespace / EOF / yaml / large-file hooks.
- **Tests**: Django `TestCase`, no pytest. New tests live in the app test module(s).

## Readiness checklist for DELIVER

1. **New setting `GROUP_ORDER_NOTIFY_EMAIL`** (the socios recipient for the D3 order-open
   email) MUST declare a sensible default in `proj/settings.py` (e.g. `socios@lupierra.es`)
   read via django-environ. Because CI only has `.env.example`, the default must make CI pass
   without requiring a new `.env` key. Also add the key to `.env.example` for documentation.
2. **Email test isolation**: the project email backend is `post_office.EmailBackend`, which
   *enqueues* mail — `mail.outbox` is NOT auto-populated. D3 email assertions MUST use
   `@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")`.
3. **Order-open email is fire-and-forget**: send after commit, catch broadly, log, and degrade
   to a warning message. A mail failure must never roll back order creation (US-07 sad path).
4. **Migration `0004` is additive** (three new tables, no data migration, no changes to
   existing tables) → safe to apply forward with zero downtime; trivially reversible.
5. **No new runtime dependencies.** No changes to `requirements*.txt`, Docker, or gunicorn.
6. **flake8**: keep new lines ≤ 120 chars; migrations are auto-excluded.

## Observability / rollback

- Rollback = `migrate lupanes 0003` (drops the three new tables) + revert the deploy. No data
  in existing tables is touched, so rollback is safe.
- Sentry (already wired) will capture any unhandled exception in the new views; the order-open
  email failure path logs a warning rather than erroring.

## Outstanding (carried from DISCOVER/DISCUSS)

- **D9 pre-DELIVER mockup review** — human gate with Gloria/Marta/Didier; cannot run in an
  autonomous session. Remains OUTSTANDING before production rollout. The running feature serves
  as the mockup. Does not block merging the implementation branch for review.
- **V1 roster validation** (~30 min) before any notification-volume scaling decision.
