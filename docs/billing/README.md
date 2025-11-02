# Billing and Subscriptions

Complete guide for the STEWARD billing system, including PayFast integration, admin portal, and subscription management.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Admin Portal](#admin-portal)
4. [Data Model](#data-model)
5. [Subscription Flow](#subscription-flow)
6. [API Endpoints](#api-endpoints)
7. [PayFast Integration](#payfast-integration)
8. [Testing](#testing)
9. [Operations](#operations)

---

## Quick Start

1. **Configure environment variables** (see [Configuration](#configuration))
2. **Run migrations**: `flask db upgrade`
3. **Set admin credentials** (see [Admin Portal Setup](#admin-portal))
4. **Test subscription flow** (see [Testing](#testing))

---

## Configuration

### Environment Variables

Add to your `.env` file (see `env.example` for template):

#### Subscription Settings
```bash
SUBSCRIPTIONS_ENABLED=true              # Master switch for subscription features
ENFORCE_PAYMENT_AFTER_TRIAL=false      # Block users after trial expires (production: true)
TRIAL_DAYS=30                          # Trial period length in days
DEFAULT_CURRENCY=ZAR                   # Default billing currency
```

#### PayFast Settings
```bash
PAYFAST_MERCHANT_ID=your_merchant_id
PAYFAST_MERCHANT_KEY=your_merchant_key
PAYFAST_PASSPHRASE=your_passphrase     # Recommended for production
PAYFAST_TEST_MODE=true                 # Use sandbox for testing
PAYFAST_RETURN_URL=http://localhost:5000/payfast/return
PAYFAST_CANCEL_URL=http://localhost:5000/payfast/cancel
PAYFAST_NOTIFY_URL=http://localhost:5000/api/subscriptions/webhook/payfast
```

#### Admin Portal Credentials
```bash
ADMIN_USERNAME=admin                   # Admin login username
ADMIN_PASSWORD=your-secure-password   # REQUIRED - no default
```

### Configuration Flags

- **`SUBSCRIPTIONS_ENABLED`**: Master kill-switch. If `false`, all subscription gating is disabled.
- **`ENFORCE_PAYMENT_AFTER_TRIAL`**: 
  - `false` (dev mode): Users can continue using app after trial expires
  - `true` (production): Users with expired trials are blocked with HTTP 402
- **`TRIAL_DAYS`**: Length of trial period assigned at signup

---

## Admin Portal

### Access

- **URL**: `http://localhost:5000/admin`
- **Credentials**: Use `ADMIN_USERNAME` and `ADMIN_PASSWORD` from `.env`
- **Features**:
  - Dashboard with subscription and payment statistics
  - Subscription management page
  - Payment history and reporting
  - Process renewals manually
  - Toggle payment enforcement (with visual status indicator)

### Quick Setup

See **[ADMIN_SETUP.md](./ADMIN_SETUP.md)** for detailed admin portal setup instructions.

### Features

- **Dashboard**: Real-time stats for users, subscriptions, payments, and revenue
- **Subscription Management**: View all subscriptions with filtering by status/plan
- **Payment Management**: Complete payment history with statistics
- **Quick Actions**:
  - Process Renewals: Manually trigger subscription renewals
  - Toggle Payment Enforcement: Enable/disable blocking of expired trials (shows current state)

---

## Data Model

### User Table Extensions

Added to `user` table:
- `trial_start`, `trial_end` (DateTime)
- `subscription_status` (trial|active|past_due|cancelled|inactive)
- `subscription_plan` (monthly|yearly)
- `next_billing_at`, `auto_renew`
- `payfast_token`, `payfast_subscription_id`
- `billing_currency` (default: ZAR)
- `is_admin` (Boolean, for backward compatibility - admin uses credentials)

### Subscription Tables

**`subscription_plan`** (default plans):
- `code` (monthly, yearly)
- `name`, `price_cents`, `currency`, `interval`
- `active` (Boolean)

**`subscription`**:
- `user_id`, `plan_code`
- `status` (trial|active|past_due|cancelled|inactive)
- `started_at`, `current_period_start`, `current_period_end`
- `cancel_at`, `cancelled_at`
- `payfast_subscription_id`

**`payment`**:
- `user_id`, `subscription_id`
- `amount_cents`, `currency`, `status` (pending|paid|failed|refunded)
- `gateway`, `gateway_reference`
- `paid_at`, `created_at`

### Migrations

1. **Add subscriptions**: `migrations/versions/7b2f3a1c2c1e_add_subscriptions.py`
2. **Add admin role**: `migrations/versions/add_admin_role_to_user.py`

Apply with: `flask db upgrade`

---

## Subscription Flow

### 1. Trial Start (Onboarding)

**Automatic Trial Start During Signup:**
- User completes onboarding steps (personal info, password, referral, currency/categories)
- On Step 5: User sees trial information and clicks "Get Started"
- Account created via `POST /api/onboarding/complete`
- Trial automatically starts:
  - Sets `trial_start` and `trial_end` (trial_start + TRIAL_DAYS, default 30 days)
  - User status set to `trial`
  - Trial started email sent
- User immediately redirected to PayFast hosted payment page to save payment method
- **No charge occurs** - payment method saved for future billing

**Manual Trial Start:**
- User can also start trial manually: `POST /api/subscriptions/start` with `{ "plan": "monthly" | "yearly" }`
- Returns PayFast payload for payment setup (optional)

### 2. Payment Method Setup (PayFast)

**During Onboarding:**
- User redirected to PayFast's secure, PCI DSS Level 1 compliant payment page
- User enters card details directly on PayFast's platform (never touches our servers)
- PayFast saves payment method (tokenizes card) with:
  - Initial amount: `0.00` (no charge)
  - Billing date: Trial end date
  - Recurring amount: Full subscription amount
- PayFast redirects user back to our site
- Payment method is ready for automatic billing when trial ends

### 3. Subscription Activation (After Trial)

**Automatic Billing:**
- When trial period ends, PayFast automatically charges the recurring subscription amount
- PayFast sends ITN (Instant Transaction Notification) to webhook endpoint
- Webhook validates signature and POST-back with PayFast
- Payment recorded in `payment` table
- Subscription status changed from `trial` to `active`
- Subscription activated email sent

### 4. Renewals

- Automatic renewal processing via `POST /api/subscriptions/renewal/process`
- Designed for cron job execution (daily recommended)
- Extends subscription period based on plan interval
- Can be triggered manually from admin dashboard

### 5. Cancellation

- User can cancel: `POST /api/subscriptions/cancel`
- Options:
  - Immediate cancellation
  - Cancel at period end (continues until current period expires)
- Email notification sent

### 6. Upgrade/Downgrade

- **Upgrade**: `POST /api/subscriptions/upgrade` - Immediate with prorated billing
- **Downgrade**: `POST /api/subscriptions/downgrade` - Scheduled at period end
- Email notifications sent

---

## API Endpoints

### Public Endpoints

#### `GET /api/subscriptions/plans`
Returns list of available subscription plans.
- Seeds default plans if missing
- Response: `[{ code, name, price_cents, currency, interval }]`

#### `POST /api/subscriptions/webhook/payfast`
PayFast ITN webhook endpoint (public, but validates signature).
- Validates PayFast signature
- Performs POST-back validation with PayFast servers
- Maps payment to user/subscription
- Records payment and activates subscription
- Sends email notifications

### User Endpoints (Authentication Required)

#### `POST /api/subscriptions/start`
Start a trial subscription.
- Body: `{ "plan": "monthly" | "yearly" }`
- Returns PayFast redirect payload
- Sends trial started email

#### `GET /api/subscriptions/status`
Get current subscription status.
- Response: `{ status, plan, trial_end, allowed, reason }`

#### `POST /api/subscriptions/cancel`
Cancel subscription.
- Body: `{ "immediate": true|false }`
- Sends cancellation email

#### `POST /api/subscriptions/upgrade`
Upgrade to higher plan (immediate).
- Body: `{ "plan": "yearly" }`
- Adjusts billing period accordingly
- Sends upgrade email

#### `POST /api/subscriptions/downgrade`
Downgrade to lower plan (at period end).
- Body: `{ "plan": "monthly" }`
- Scheduled for end of current period
- Sends downgrade email

#### `POST /api/subscriptions/pause` / `POST /api/subscriptions/resume`
Pause or resume a subscription.

### Admin Endpoints (Admin Required)

#### `GET /api/subscriptions/admin/subscriptions`
Get all subscriptions with statistics.
- Returns: `{ subscriptions: [...], stats: { total, by_status, by_plan } }`

#### `GET /api/subscriptions/admin/payments`
Get all payments with statistics.
- Returns: `{ payments: [...], stats: { total, by_status, total_revenue_by_currency, by_gateway } }`

#### `GET /api/subscriptions/enforcement/status`
Get current payment enforcement status.
- Returns: `{ enforce_payment_after_trial, status }`

#### `POST /api/subscriptions/toggle-enforcement`
Toggle payment enforcement on/off.
- Toggles current state automatically
- Returns: `{ enforce_payment_after_trial, message }`

#### `POST /api/subscriptions/renewal/process`
Process subscription renewals (for cron jobs).
- Returns: `{ renewed: count, failed: [...] }`

---

## PayFast Integration

### Service Location

`src/services/payfast_service.py`

### Key Features

1. **Signature Generation**: MD5 hash of sorted URL-encoded fields + optional passphrase
2. **ITN Validation**: Validates PayFast signature from webhook payload
3. **POST-back Validation**: Server-to-server verification with PayFast (additional security layer)
4. **Subscription Payload**: Builds redirect form data for subscription checkout
5. **Payment Deferral**: Supports setting initial amount to `0.00` with future billing date
   - Used during trial periods to save payment method without charging
   - Billing date set to trial end date for automatic billing
   - Parameters: `defer_payment=True` and `billing_date=trial_end`

### Integration Flow

**Onboarding Flow (Automatic):**
1. User completes onboarding and clicks "Get Started"
2. Backend creates account and starts trial via `POST /api/onboarding/complete`
3. Backend builds PayFast subscription payload with:
   - Initial amount: `0.00` (saves payment method without charging)
   - Billing date: Trial end date (deferred payment)
   - Recurring amount: Full subscription price
4. Frontend automatically redirects user to PayFast hosted payment page
5. User enters card details on PayFast's secure platform
6. PayFast saves payment method and redirects back to `PAYFAST_RETURN_URL` or `PAYFAST_CANCEL_URL`
7. When trial ends, PayFast automatically charges recurring amount
8. PayFast sends ITN to `PAYFAST_NOTIFY_URL` when payment is processed
9. Webhook validates signature and POST-back, then activates subscription

**Manual Subscription Start:**
1. User calls `POST /api/subscriptions/start` with plan selection
2. Backend creates trial and returns PayFast payload (same structure as above)
3. Frontend can redirect to PayFast for payment setup
4. Same flow continues as onboarding

### Custom Fields

The integration includes custom fields for user/subscription mapping:
- `custom_str1`: User ID
- `custom_int1`: Subscription ID

These are used by the webhook to find the correct user/subscription when processing ITN.

### Testing

- Use PayFast sandbox: Set `PAYFAST_TEST_MODE=true`
- Test cards: See PayFast documentation for test card numbers
- ITN testing: PayFast sandbox dashboard can trigger test notifications

Reference: [PayFast Developer Docs](https://developers.payfast.co.za/docs)

---

## Testing

### Prerequisites

```bash
FLASK_APP=app.py
pip install -r requirements.txt
flask db upgrade
```

### Test Scenarios

#### 1. Trial Flow (No Enforcement)
```bash
# Set in .env
SUBSCRIPTIONS_ENABLED=true
ENFORCE_PAYMENT_AFTER_TRIAL=false

# Test
POST /api/subscriptions/start { "plan": "monthly" }
GET /api/subscriptions/status
# Should show: status="trial", allowed=true
# Even after trial_end expires, allowed should remain true
```

#### 2. Trial Flow (With Enforcement)
```bash
# Set in .env
ENFORCE_PAYMENT_AFTER_TRIAL=true

# Test expired trial
# Protected endpoints should return HTTP 402
```

#### 3. PayFast Sandbox Test
1. Start subscription via API
2. Use returned PayFast payload to redirect to PayFast sandbox
3. Complete test payment
4. Verify ITN received and subscription activated
5. Check email notifications sent

#### 4. Admin Portal
1. Configure admin credentials in `.env`
2. Access `/admin` and login
3. Verify dashboard loads with stats
4. Test toggle enforcement button (should show current state)
5. Test subscription and payment pages

---

## Operations

### Daily Tasks

#### Process Renewals (Cron Job)

**Automated setup is recommended.** See **[CRON_SETUP.md](./CRON_SETUP.md)** for complete setup instructions.

**Quick Setup (Linux/Unix):**
```bash
# 1. Make script executable
chmod +x scripts/renewals.sh

# 2. Test manually
./scripts/renewals.sh

# 3. Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /full/path/to/wealth-wise/scripts/renewals.sh >> /full/path/to/wealth-wise/logs/renewals.log 2>&1
```

**Quick Setup (Windows):**
1. Use Task Scheduler to run `scripts/process_renewals.py` daily at 2 AM
2. See [CRON_SETUP.md](./CRON_SETUP.md) for detailed Windows instructions

**Manual Testing:**
```bash
# Run the Python script directly
python scripts/process_renewals.py

# Or use curl (requires admin token)
curl -X POST http://localhost:5000/api/subscriptions/renewal/process \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Manual Operations

#### Seed Subscription Plans
```python
from src.services.subscription_service import SubscriptionService
SubscriptionService.seed_default_plans('ZAR')
```
Or call `GET /api/subscriptions/plans` (auto-seeds if missing).

#### Toggle Payment Enforcement
- Via Admin Portal: Click "Toggle Payment Enforcement" button (shows current state)
- Via API: `POST /api/subscriptions/toggle-enforcement`
- Note: Changes are in-memory only (resets on app restart; set in `.env` for persistence)

#### View Statistics
- Admin Dashboard: `/admin/dashboard`
- Subscriptions: `/admin/subscriptions`
- Payments: `/admin/payments`

### Email Configuration

Ensure `.env` has email settings:
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@steward.com
```

Email notifications are sent for:
- Trial started
- Trial ending (7 days before expiry)
- Payment success/failure
- Subscription activated/cancelled
- Plan upgrade/downgrade

---

## Access Control

### Subscription Gating

Protected endpoints use `@subscription_required` decorator:
- `/api/budget/*`
- `/api/categories/*`
- `/api/accounts/*`
- `/api/transactions/*`

**Behavior**:
1. If `SUBSCRIPTIONS_ENABLED=false`: Always allow
2. If `ENFORCE_PAYMENT_AFTER_TRIAL=false`: Allow even after trial expiry
3. If enforcement enabled:
   - Allow if status is `active` OR trial is still valid
   - Block with HTTP 402 if trial expired or subscription cancelled

### Admin Access

Protected with `@admin_required` decorator:
- Supports session-based auth (web portal)
- Supports JWT token auth (API/cron jobs)
- Backward compatible with user-based `is_admin` flag (for API tokens)

---

## File Structure

### Core Files
- **Config**: `src/config/__init__.py` - Environment variables and settings
- **Models**: `src/models/subscription.py`, `src/models/user.py`
- **Services**: 
  - `src/services/subscription_service.py` - Subscription business logic
  - `src/services/payfast_service.py` - PayFast integration
  - `src/services/email_service.py` - Email notifications
- **Routes**: 
  - `src/routes/api/subscriptions.py` - Subscription endpoints
  - `src/routes/admin.py` - Admin portal routes
  - `src/auth/__init__.py` - Auth decorators (`subscription_required`, `admin_required`)

### Templates
- `templates/admin/*` - Admin portal pages
- `templates/base_admin.html` - Admin base template
- `templates/settings.html` - User subscription management UI

### Migrations
- `migrations/versions/7b2f3a1c2c1e_add_subscriptions.py`
- `migrations/versions/add_admin_role_to_user.py`

---

## Troubleshooting

### Common Issues

**"Admin access not configured"**
- Ensure `ADMIN_PASSWORD` is set in `.env`
- Restart Flask app after adding credentials

**"Trial expired. Subscription required"**
- Check `ENFORCE_PAYMENT_AFTER_TRIAL` setting
- Set to `false` for development/testing
- User needs to start subscription if enforcement is enabled

**PayFast webhook not received**
- Verify `PAYFAST_NOTIFY_URL` is publicly accessible
- Check PayFast dashboard for ITN logs
- Ensure webhook endpoint validates signatures correctly

**Email notifications not sending**
- Verify email settings in `.env`
- Check SMTP server credentials
- Review server logs for email errors

**Subscription not activating after payment**
- Check webhook logs for ITN processing
- Verify POST-back validation is working
- Check that custom fields (user_id, subscription_id) are correctly mapped

---

## Security Best Practices

1. **Admin Credentials**: Use strong passwords, never commit to version control
2. **PayFast Passphrase**: Always set `PAYFAST_PASSPHRASE` in production
3. **HTTPS**: Use HTTPS for all PayFast URLs and webhooks in production
4. **Signature Validation**: All PayFast communications validate signatures
5. **POST-back Validation**: Additional server-to-server verification for webhooks
6. **Session Security**: Admin sessions expire after 24 hours
7. **Environment Variables**: Store all sensitive data in `.env` (not in code)

---

## Related Documentation

- **[PAYMENT_SECURITY.md](./PAYMENT_SECURITY.md)** - Payment security implementation and PCI compliance
- **[ONBOARDING_FLOW.md](./ONBOARDING_FLOW.md)** - Complete onboarding flow documentation
- **[ADMIN_SETUP.md](./ADMIN_SETUP.md)** - Detailed admin portal setup guide
- **[CRON_SETUP.md](./CRON_SETUP.md)** - Automated renewal processing setup guide
- **PayFast Docs**: https://developers.payfast.co.za/docs

---

**Last Updated**: December 2024
