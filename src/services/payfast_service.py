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
    def build_subscription_payload(user, plan_code: str, amount_cents: int) -> Dict[str, str]:
        """Build payload for creating a subscription via PayFast (redirect form post)."""
        amount = f"{amount_cents / 100:.2f}"
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
            # Subscription params (PayFast) – frequency and cycles
            'subscription_type': 1,  # 1 for subscription
            'billing_date': '',      # optional start date
            'recurring_amount': amount,
            'frequency': 3 if plan_code == 'monthly' else 6,  # 3=monthly, 6=bi-annual, 6 used as placeholder; adjust per docs
            'cycles': 0,  # 0 for indefinite
        }
        base['signature'] = PayFastService.generate_signature(base)
        return base


