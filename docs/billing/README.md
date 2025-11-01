# Billing and Subscriptions

This guide explains how subscriptions are configured, how trials and gating work, how to integrate PayFast, and how to test the flows end-to-end.

- Default pricing: Monthly R35, Yearly R400
- Trial: 30 days (configurable)
- Gateway: PayFast (South Africa) — reference docs: https://developers.payfast.co.za/docs

## Contents
- Configuration and environment variables
- Data model and migrations
- Trial rules and gating behavior
- API endpoints and usage
- PayFast integration notes
- Testing scenarios
- Operational tasks and tips

---

## Configuration and environment variables

Configure via `.env` (see `env.example`):

- SUBSCRIPTIONS_ENABLED=true
- ENFORCE_PAYMENT_AFTER_TRIAL=false
- TRIAL_DAYS=30
- DEFAULT_CURRENCY=ZAR
- PAYFAST_MERCHANT_ID=your_id
- PAYFAST_MERCHANT_KEY=your_key
- PAYFAST_PASSPHRASE=your_passphrase  # recommended
- PAYFAST_TEST_MODE=true
- PAYFAST_RETURN_URL=http://localhost:5000/payfast/return
- PAYFAST_CANCEL_URL=http://localhost:5000/payfast/cancel
- PAYFAST_NOTIFY_URL=http://localhost:5000/api/subscriptions/webhook/payfast

Key flags
- SUBSCRIPTIONS_ENABLED: Master kill-switch for all subscription logic. If false, gating never blocks.
- ENFORCE_PAYMENT_AFTER_TRIAL: If false, users can continue after trial without blocking (dev mode). If true, expired trial blocks access unless subscription is active.
- TRIAL_DAYS: Trial length assigned at signup or when starting a trial.

---

## Data model and migrations

Schema additions:
- User fields (table `user`)
  - trial_start, trial_end
  - subscription_status (trial|active|past_due|cancelled|inactive)
  - subscription_plan (monthly|yearly)
  - next_billing_at, auto_renew
  - payfast_token, payfast_subscription_id
  - billing_currency (default ZAR)

- New tables (in `src/models/subscription.py`)
  - `subscription_plan` (code, name, price_cents, currency, interval, active)
  - `subscription` (user_id, plan_code, status, period window, payfast_subscription_id)
  - `payment` (user_id, subscription_id, amount_cents, currency, status, gateway_reference)

Migration
- File: `migrations/versions/7b2f3a1c2c1e_add_subscriptions.py`
- Apply with: `flask db upgrade` (ensure `FLASK_APP=app.py`)

---

## Trial rules and gating behavior

Decorator: `subscription_required` (in `src/auth/__init__.py`)
- Applied to core API routes (budget, categories, accounts, transactions)
- Behavior:
  - If `SUBSCRIPTIONS_ENABLED=false`: allow all requests
  - If `ENFORCE_PAYMENT_AFTER_TRIAL=false`: allow even after trial expiry (for development/testing)
  - If enforcement true: allow when status is `active` or trial still valid; otherwise block with HTTP 402

Trial assignment
- On signup (`POST /api/onboarding/complete`) a trial is started automatically if subscriptions are enabled.
- Explicit trial start also available via `POST /api/subscriptions/start`.

---

## API endpoints and usage

Base URL prefix: `/api/subscriptions`

- GET `/plans`
  - Seeds default plans if missing and returns active plans.
  - Response: list of `{ code, name, price_cents, currency, interval }`

- POST `/start` (auth required)
  - Body: `{ "plan": "monthly" | "yearly" }` (default: monthly)
  - Starts a trial for the user; returns trial metadata and a PayFast subscription payload to POST from the frontend.

- GET `/status` (auth required)
  - Returns `{ status, plan, trial_end, allowed, reason }` where `allowed` indicates gating evaluation.

- POST `/webhook/payfast`
  - PayFast ITN webhook endpoint. Validates signature; extend to map payment to user/subscription and mark as paid/active.

- POST `/toggle-enforcement`
  - Body: `{ "enabled": true|false }`
  - Toggles `ENFORCE_PAYMENT_AFTER_TRIAL` at runtime (non-persistent across restarts).

Other affected endpoints
- Core APIs (`/api/budget/*`, `/api/categories/*`, `/api/accounts/*`, `/api/transactions/*`) are now protected by `subscription_required`.

---

## PayFast integration notes

Reference: https://developers.payfast.co.za/docs

Service: `src/services/payfast_service.py`
- Signature generation uses MD5 of sorted URL-encoded fields with optional `passphrase` appended (PayFast requirement).
- ITN (`/webhook/payfast`) validates the signature. You should also implement server-side validation as per PayFast’s best practices (e.g., POST back validation), and verify `merchant_id`, amounts, and status.
- Subscription payload builder returns fields for a redirect/form POST to PayFast including `notify_url`.

Important
- Frequency/cycles must match PayFast subscription docs. Adjust `frequency` mapping for monthly/yearly as per official values in `build_subscription_payload`.
- Include identifiers (e.g., user id) in `custom_str1`/`custom_int1` to associate ITN with a specific user/subscription.

---

## Testing scenarios

Local prerequisites
- `FLASK_APP=app.py`, dependencies installed, and database migrated.

Scenarios
1) Trial flow (no enforcement)
   - Set `SUBSCRIPTIONS_ENABLED=true`, `ENFORCE_PAYMENT_AFTER_TRIAL=false`.
   - Sign up or call `POST /api/subscriptions/start` with `{ "plan": "monthly" }`.
   - Verify `GET /api/subscriptions/status` shows `status=trial`, `allowed=true`.
   - After trial end (manually set `trial_end` to past), verify `allowed` remains true.

2) Trial flow (with enforcement)
   - Set `ENFORCE_PAYMENT_AFTER_TRIAL=true`.
   - If trial expired, calls to protected endpoints should return 402.

3) PayFast redirect test (sandbox)
   - Use `/api/subscriptions/start` response `payfast` object to create a frontend form POST to PayFast sandbox.
   - Complete a test payment; ensure ITN hits `/api/subscriptions/webhook/payfast`.
   - Extend webhook to find user/subscription by `custom_str1` or reference and mark `Payment` as `paid`; call `SubscriptionService.activate_subscription`.

4) Webhook signature validation
   - Post a sample ITN payload with correct/incorrect signature; expect 200/400 respectively.

---

## Operational tasks and tips

- Seed plans: `SubscriptionService.seed_default_plans()` or call `GET /api/subscriptions/plans`.
- Toggle paywall: `POST /api/subscriptions/toggle-enforcement` with `{ "enabled": true }`.
- Migrations: `flask db upgrade` / `flask db downgrade -1`.
- Logs: check server console for ITN validation results and onboarding trial setup logs.

---

## File map

- Config: `src/config/__init__.py` (env flags and PayFast settings)
- Models: `src/models/subscription.py`, `src/models/user.py`
- Services: `src/services/subscription_service.py`, `src/services/payfast_service.py`
- Routes: `src/routes/api/subscriptions.py`, gating in `src/auth/__init__.py`, applied in core API routes
- Migration: `migrations/versions/7b2f3a1c2c1e_add_subscriptions.py`

---

## Roadmap

- Map PayFast ITN to users via custom fields and persist gateway references
- Implement subscription cancel/pause endpoints
- Add UI for managing plan and card details; confirm PayFast tokenization/redirect flows
- Add admin reporting for payments and subscription states
