# Onboarding Flow Documentation

## Overview

The STEWARD onboarding process guides new users through account creation, preference setup, and payment method configuration. The flow is designed to be secure, user-friendly, and compliant with PCI DSS requirements.

## Onboarding Steps

### Step 1: Personal Information
- First Name (required)
- Last Name (required)
- Email Address (required, validated for uniqueness)
- Username (optional)
- Country (required, dropdown selection)
- Preferred Name (optional)

**Validation:**
- Real-time email uniqueness check
- Real-time username uniqueness check (if provided)
- Form validation before proceeding

### Step 2: Password Setup
- Password (required, min 8 chars, must include uppercase, lowercase, number, special character)
- Confirm Password (required, must match)

**Features:**
- Real-time password strength indicator
- Password confirmation matching validation
- Visual feedback for requirements

### Step 3: Referral Source
- How did you hear about us? (required, radio buttons)
- Options: Social Media, Friend/Family, Search Engine, Advertisement, Other
- If "Other" selected, additional text field appears

### Step 4: Currency and Categories
- Currency Selection (required, dropdown)
- Default Categories Selection (checkboxes)
  - User can select from predefined categories with subcategories
  - Custom categories can be added dynamically
  - Parent categories automatically include their subcategories

**Features:**
- Visual category cards with icons
- Expandable subcategory lists
- Custom category/subcategory creation
- Selected categories saved to user profile

### Step 5: Trial Information & Payment Setup
- **Information Display Only** (no form fields)
- Trial information box explaining:
  - 30-day free trial enrollment
  - No charges during trial period
  - Automatic subscription after trial ends
  - Upgrade/cancel options via Settings
- Security information about PayFast payment processing

**Navigation:**
- Back button (returns to Step 4)
- "Get Started" button (completes onboarding)

## Complete Onboarding Process

### Frontend Flow

1. **User completes Steps 1-4:**
   - All data collected and validated client-side
   - Data stored in `formData` object

2. **User reaches Step 5:**
   - Sees trial information and security messaging
   - Clicks "Get Started" button

3. **Account Creation:**
   - Frontend sends `POST /api/onboarding/complete` with collected data
   - Backend creates user account
   - Backend sets up initial categories
   - Backend starts trial subscription

4. **Payment Redirect:**
   - If subscriptions enabled, backend returns PayFast payload
   - Frontend automatically creates POST form to PayFast
   - User redirected to PayFast hosted payment page
   - User enters card details on PayFast's secure platform

5. **Return to Application:**
   - PayFast redirects back to `PAYFAST_RETURN_URL` (success) or `PAYFAST_CANCEL_URL` (cancelled)
   - User sees appropriate message and can continue to dashboard

### Backend Flow (`/api/onboarding/complete`)

1. **Input Validation:**
   - Validates all required fields
   - Checks email/username uniqueness
   - Validates password strength

2. **User Creation:**
   - Creates new User record
   - Hashes password securely
   - Sets initial user preferences

3. **Category Setup:**
   - Creates selected categories and subcategories
   - Links custom categories to user

4. **Trial Subscription:**
   - Seeds default subscription plans if needed
   - Starts trial via `SubscriptionService.start_trial()`
   - Sets `trial_start` and `trial_end` dates
   - Sets user status to `trial`
   - Sends trial started email

5. **PayFast Payload Generation:**
   - Builds PayFast subscription payload with:
     - Initial amount: `0.00` (saves payment method, no charge)
     - Billing date: Trial end date
     - Recurring amount: Full subscription price
   - Returns payload in response for frontend redirect

6. **Email Verification:**
   - Creates email verification token
   - Sends verification email to user

7. **Response:**
   - Returns success status
   - Includes PayFast payload if subscriptions enabled
   - Includes email verification status

## Security Features

### Payment Security
- **No card data collection:** Payment details never collected in our forms
- **PayFast hosted payment page:** All card details entered on PayFast's PCI DSS Level 1 compliant platform
- **Payment deferral:** Initial amount set to `0.00`, billing deferred until trial ends
- **Secure webhooks:** All PayFast notifications validated with signatures

### Data Security
- Passwords hashed using secure algorithms
- Email verification required for account activation
- CSRF protection on all form submissions
- Input validation on both client and server side

## Configuration

### Environment Variables

```bash
# Subscription Settings
SUBSCRIPTIONS_ENABLED=true              # Enable subscription features
ENFORCE_PAYMENT_AFTER_TRIAL=false      # Block users after trial (production: true)
TRIAL_DAYS=30                          # Trial period length

# PayFast Settings
PAYFAST_MERCHANT_ID=your_merchant_id
PAYFAST_MERCHANT_KEY=your_merchant_key
PAYFAST_PASSPHRASE=your_passphrase     # Recommended for production
PAYFAST_TEST_MODE=true                 # Use sandbox for testing
PAYFAST_RETURN_URL=http://localhost:5000/payfast/return
PAYFAST_CANCEL_URL=http://localhost:5000/payfast/cancel
PAYFAST_NOTIFY_URL=http://localhost:5000/api/subscriptions/webhook/payfast
```

## Error Handling

### Client-Side Validation
- Real-time field validation
- Visual error indicators
- Disabled buttons until validation passes
- Clear error messages

### Server-Side Validation
- Duplicate email/username checks
- Password strength validation
- Required field validation
- Error responses with clear messages

### Payment Errors
- PayFast cancellation handled gracefully
- User can continue with trial and set up payment later
- Clear messaging about payment status

## User Experience Considerations

### Progress Indication
- Progress bar shows current step
- Step counter (e.g., "Step 1 of 5")
- Clear visual feedback

### Navigation
- Back button on all steps except first
- Forward validation prevents skipping steps
- Can navigate back to edit previous steps

### Loading States
- Button text changes during submission ("Creating Account...")
- Disabled buttons during processing
- Error messages displayed clearly

## Related Files

### Frontend
- `templates/onboarding.html` - Onboarding template
- `static/js/onboarding.js` - Onboarding flow logic
- `static/css/style.css` - Styling for onboarding steps

### Backend
- `src/routes/api/__init__.py` - `/api/onboarding/complete` endpoint
- `src/services/subscription_service.py` - Trial management
- `src/services/payfast_service.py` - PayFast integration
- `src/services/auth_service.py` - User creation and validation
- `src/services/email_service.py` - Email notifications

## Testing

### Manual Testing Checklist

1. **Step 1 (Personal Info):**
   - [ ] Valid email accepted
   - [ ] Duplicate email rejected
   - [ ] Duplicate username rejected (if provided)
   - [ ] Required fields enforced

2. **Step 2 (Password):**
   - [ ] Password strength validation works
   - [ ] Password confirmation matching works
   - [ ] Weak passwords rejected

3. **Step 3 (Referral):**
   - [ ] Selection required
   - [ ] "Other" option shows text field

4. **Step 4 (Categories):**
   - [ ] Categories can be selected
   - [ ] Custom categories can be added
   - [ ] Currency selection works

5. **Step 5 (Trial Info):**
   - [ ] Information displays correctly
   - [ ] "Get Started" button works
   - [ ] Account creation succeeds
   - [ ] PayFast redirect occurs
   - [ ] Payment setup completes

6. **Post-Onboarding:**
   - [ ] Trial started correctly
   - [ ] Email verification sent
   - [ ] User can access dashboard
   - [ ] Payment method saved (no charge)

### Test Scenarios

**Scenario 1: Complete Onboarding with Payment**
1. Complete all 5 steps
2. Verify account created
3. Verify redirected to PayFast
4. Enter test card details
5. Verify redirected back
6. Verify trial active, payment method saved

**Scenario 2: Cancel Payment Setup**
1. Complete steps 1-4
2. Click "Get Started"
3. Redirected to PayFast
4. Cancel payment setup
5. Verify returned with appropriate message
6. Verify trial still active
7. Verify can set up payment later from Settings

**Scenario 3: Email Verification**
1. Complete onboarding
2. Verify email sent
3. Click verification link
4. Verify account activated

## Troubleshooting

### Common Issues

**"Email already exists"**
- User tries to sign up with existing email
- Solution: User should use different email or reset password

**"Payment setup cancelled"**
- User cancels on PayFast page
- Solution: User can continue with trial and set up payment later from Settings

**"Trial started email sent multiple times"**
- Previously occurred if payment details were checked multiple times
- **Fixed:** Email now sent once when trial starts during onboarding

**"No button on Step 5"**
- Navigation buttons not showing
- **Fixed:** Step 5 now properly displays "Get Started" button

## Future Enhancements

1. **Progressive Web App (PWA):**
   - Offline support for form completion
   - Save progress and resume later

2. **Social Signup:**
   - Google/Apple sign-in options
   - Skip password setup for social accounts

3. **Onboarding Skip:**
   - Option to complete basic onboarding and add details later
   - Simplified flow for returning users

---

**Last Updated**: December 2024
**Status**: ✅ Production-ready

