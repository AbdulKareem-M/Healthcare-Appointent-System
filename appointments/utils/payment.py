import razorpay
import hmac
import hashlib
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def create_razorpay_client():
  """Create and return Razorpay client"""
  try:
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
  except Exception as e:
    logger.error(f"Error creating Razorpay client: {e}")
    raise RuntimeError(f"Failed to initialize Razorpay client: {str(e)}")

def create_payment_order(amount, currency='INR', receipt=None):
    """Create a Razorpay order"""
    client = create_razorpay_client()
    
    order_data = {
        'amount': int(amount * 100),  # Amount in paise
        'currency': currency,
        'receipt': receipt or f'appointment_{receipt}',
        'payment_capture': 1  # Auto capture payment
    }
    
    try:
        order = client.order.create(data=order_data)
        return order
    except Exception as e:
        print(f"Error creating Razorpay order: {e}")
        return None

def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """Verify Razorpay payment signature"""
    try:
        client = create_razorpay_client()
        
        # Generate signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return generated_signature == razorpay_signature
    except Exception as e:
        print(f"Error verifying payment signature: {e}")
        return False

def send_payment_confirmation_email(user_email, payment_details):
            """Send payment confirmation email to user"""
            try:
                # Here you would implement email sending logic
                # Using Django's email functionality or a third-party service
                # Example:
                # send_mail(
                #     subject='Payment Confirmation',
                #     message=f'Your payment of {payment_details["amount"]} was successful.',
                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     recipient_list=[user_email]
                # )
                pass
            except Exception as e:
                print(f"Error sending payment confirmation email: {e}")