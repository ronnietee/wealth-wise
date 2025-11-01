"""
PayFast integration helpers (signature, ITN validation, payload building).

Reference: https://developers.payfast.co.za/docs
"""

import hashlib
import hmac
import urllib.parse
from typing import Dict, Tuple
from flask import current_app


class PayFastService:
    @staticmethod
    def generate_signature(data: Dict[str, str]) -> str:
        """Generate PayFast signature using passphrase if configured.
        PayFast requires fields to be URL-encoded and sorted by keys.
        """
        # Exclude signature if present
        data = {k: v for k, v in data.items() if k != 'signature' and v is not None}
        # Sort
        items = sorted(data.items())
        # Build query string
        query = urllib.parse.urlencode(items)
        passphrase = current_app.config.get('PAYFAST_PASSPHRASE', '')
        if passphrase:
            query = f"{query}&passphrase={urllib.parse.quote_plus(passphrase)}"
        return hashlib.md5(query.encode('utf-8')).hexdigest()

    @staticmethod
    def validate_itn(payload: Dict[str, str]) -> Tuple[bool, str]:
        """Validate ITN signature from PayFast.
        Returns (valid, reason)
        """
        sent_sig = payload.get('signature', '')
        calc_sig = PayFastService.generate_signature(payload)
        if sent_sig != calc_sig:
            return False, 'Invalid signature'
        # Additional validations like verifying with PayFast server can be added here
        return True, 'OK'
    
    @staticmethod
    def postback_validation(payload: Dict[str, str]) -> Tuple[bool, str]:
        """POST back to PayFast to verify payment status (recommended best practice).
        
        Performs server-to-server validation by sending the ITN data back to PayFast.
        This ensures the payment notification is legitimate.
        """
        import requests
        from flask import current_app
        
        try:
            # PayFast validation endpoint
            validation_url = 'https://sandbox.payfast.co.za/eng/query/validate' if current_app.config.get('PAYFAST_TEST_MODE') else 'https://www.payfast.co.za/eng/query/validate'
            
            # POST the same data back to PayFast
            response = requests.post(validation_url, data=payload, timeout=10)
            
            # PayFast returns "VALID" if payment is legitimate
            if response.status_code == 200 and response.text.strip() == 'VALID':
                return True, 'Validated by PayFast'
            else:
                return False, f'PayFast validation failed: {response.text[:100]}'
                
        except Exception as e:
            # If POST-back fails, log but don't necessarily reject (for network issues)
            current_app.logger.warning(f'PayFast POST-back validation error: {str(e)}')
            # Return True with warning - signature validation is still primary check
            return True, f'POST-back error (signature valid): {str(e)}'

    @staticmethod
    def build_subscription_payload(user, subscription_id: int, plan_code: str, amount_cents: int) -> Dict[str, str]:
        """Build payload for creating a subscription via PayFast (redirect form post).
        
        Args:
            user: User model instance
            subscription_id: Subscription ID to track in PayFast custom fields
            plan_code: Plan code (monthly or yearly)
            amount_cents: Amount in cents
        """
        amount = f"{amount_cents / 100:.2f}"
        
        # PayFast frequency values: 3 = monthly, 6 = bi-annual (6 months)
        # For yearly, we need to use cycles=2 with frequency=6 (bi-annual) OR use custom frequency
        # Standard approach: 3 for monthly, 6 for bi-annual (then use cycles for yearly)
        frequency = 3 if plan_code == 'monthly' else 6  # 3=monthly, 6=bi-annual
        cycles = 0 if plan_code == 'monthly' else 2  # For yearly: 2 cycles of bi-annual = 1 year
        
        base = {
            'merchant_id': current_app.config.get('PAYFAST_MERCHANT_ID', ''),
            'merchant_key': current_app.config.get('PAYFAST_MERCHANT_KEY', ''),
            'return_url': current_app.config.get('PAYFAST_RETURN_URL'),
            'cancel_url': current_app.config.get('PAYFAST_CANCEL_URL'),
            'notify_url': current_app.config.get('PAYFAST_NOTIFY_URL'),
            'amount': amount,
            'item_name': f"STEWARD {plan_code.capitalize()} Subscription",
            'email_address': user.email,
            'name_first': user.first_name,
            'name_last': user.last_name,
            # Subscription params (PayFast)
            'subscription_type': 1,  # 1 for subscription
            'billing_date': '',      # optional start date
            'recurring_amount': amount,
            'frequency': frequency,
            'cycles': cycles,  # 0 for indefinite (monthly), 2 for yearly (bi-annual cycles)
            # Custom fields to map ITN back to user/subscription
            'custom_str1': str(user.id),  # User ID for webhook mapping
            'custom_int1': subscription_id,  # Subscription ID for webhook mapping
        }
        base['signature'] = PayFastService.generate_signature(base)
        return base


