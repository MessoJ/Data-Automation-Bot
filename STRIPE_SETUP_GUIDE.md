# ?? Stripe Payment Integration Setup Guide

This guide will walk you through implementing the complete Stripe payment integration for your e-commerce data automation platform.

## ?? Prerequisites

- Stripe account (https://stripe.com)
- Python environment with Flask
- SSL certificate for production webhooks

## ?? Step 1: Stripe Account Setup

### Create Products in Stripe Dashboard

1. **Log into Stripe Dashboard**
   - Go to https://dashboard.stripe.com
   - Navigate to Products ? Create Product

2. **Create Three Pricing Plans:**

   **Starter Plan**
   - Name: "E-commerce Data Automation - Starter"
   - Price: $99.00 USD
   - Billing: Monthly
   - Copy the Price ID (starts with `price_`)

   **Professional Plan**
   - Name: "E-commerce Data Automation - Professional"
   - Price: $199.00 USD
   - Billing: Monthly
   - Copy the Price ID

   **Enterprise Plan**
   - Name: "E-commerce Data Automation - Enterprise"
   - Price: $399.00 USD
   - Billing: Monthly
   - Copy the Price ID

3. **Get API Keys**
   - Navigate to Developers ? API Keys
   - Copy your Publishable Key (`pk_test_` for test, `pk_live_` for production)
   - Copy your Secret Key (`sk_test_` for test, `sk_live_` for production)

## ?? Step 2: Webhook Configuration

1. **Create Webhook Endpoint**
   - Go to Developers ? Webhooks
   - Click "Add endpoint"
   - Endpoint URL: `https://yourdomain.com/api/stripe/webhook`
   - Select events:
     - `checkout.session.completed`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
     - `customer.subscription.trial_will_end`
     - `customer.subscription.deleted`

2. **Get Webhook Secret**
   - After creating, click on the webhook
   - Reveal webhook signing secret
   - Copy the secret (starts with `whsec_`)

## ?? Step 3: Environment Configuration

Create or update your `.env` file:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Stripe Price IDs (from Step 1)
STRIPE_STARTER_PRICE_ID=price_1234567890abcdef
STRIPE_PROFESSIONAL_PRICE_ID=price_0987654321fedcba
STRIPE_ENTERPRISE_PRICE_ID=price_1122334455aabbcc

# Application Secret
SECRET_KEY=your_super_secret_key_for_production
```

## ?? Step 4: Install Dependencies

Update your requirements.txt and install:

```bash
pip install stripe==7.11.0
pip install -r requirements.txt
```

## ?? Step 5: Test the Integration

### Local Testing

1. **Start your Flask application:**
   ```bash
   python run_web.py
   ```

2. **Access the landing page:**
   ```
   http://localhost:5000/landing
   ```

3. **Test trial signup:**
   - Click "Start Free Trial" on any pricing plan
   - Fill out the modal with test email
   - Verify trial creation in Stripe dashboard

### Stripe Test Cards

Use these test cards for testing:

- **Successful payment:** `4242 4242 4242 4242`
- **Declined payment:** `4000 0000 0000 0002`
- **3D Secure required:** `4000 0027 6000 3184`

## ?? Step 6: Production Deployment

### SSL Certificate
Ensure your production domain has a valid SSL certificate (required for webhooks).

### Environment Variables
```bash
# Production Stripe Keys
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret

# Production Price IDs
STRIPE_STARTER_PRICE_ID=price_live_starter_id
STRIPE_PROFESSIONAL_PRICE_ID=price_live_professional_id
STRIPE_ENTERPRISE_PRICE_ID=price_live_enterprise_id
```

### Webhook Security
The webhook endpoint automatically verifies signatures to ensure requests come from Stripe.

## ?? Step 7: Monitor and Manage

### Stripe Dashboard Monitoring
- Monitor subscriptions in Stripe Dashboard
- View revenue metrics and analytics
- Manage customer disputes and refunds
- Track trial conversions

### Application Monitoring
- Check webhook event processing logs
- Monitor subscription status updates
- Track trial signup conversion rates
- Monitor payment success/failure rates

## ??? Step 8: Customization Options

### Custom Trial Lengths
Modify trial duration in `web/app.py`:
```python
subscription = stripe.Subscription.create(
    # ...
    trial_period_days=7,  # Change from 14 to 7 days
    # ...
)
```

### Custom Success/Cancel URLs
Update redirect URLs in checkout session:
```python
checkout_session = stripe.checkout.Session.create(
    # ...
    success_url='https://yourdomain.com/welcome?session_id={CHECKOUT_SESSION_ID}',
    cancel_url='https://yourdomain.com/pricing',
    # ...
)
```

### Email Notifications
Add customer email notifications for:
- Trial started
- Trial ending soon (3 days before)
- Payment successful
- Payment failed

## ?? Troubleshooting

### Common Issues

**1. Webhook Not Receiving Events**
- Verify webhook URL is accessible
- Check SSL certificate validity
- Verify webhook secret in environment

**2. Payment Failed**
- Check Stripe logs for error details
- Verify API keys are correct
- Ensure prices are in correct currency

**3. Trial Not Starting**
- Verify price IDs in environment
- Check customer creation logic
- Review Stripe dashboard for errors

### Debug Mode
Enable Stripe debug mode in development:
```python
import stripe
stripe.log = 'debug'  # Enable debug logging
```

## ?? Success Metrics

### Key Metrics to Track
- **Trial Signup Rate**: Visitors ? Trial signups
- **Trial Conversion Rate**: Trials ? Paid subscriptions
- **Monthly Recurring Revenue (MRR)**: Track growth
- **Churn Rate**: Monitor subscription cancellations
- **Customer Lifetime Value (CLV)**: Average revenue per customer

### Analytics Integration
Consider integrating with:
- Google Analytics for conversion tracking
- Mixpanel for user behavior analysis
- Stripe's built-in analytics

## ?? Congratulations!

You now have a complete Stripe payment integration with:
- ? 14-day free trials (no credit card required)
- ? Secure subscription management
- ? Automatic billing and invoicing
- ? Webhook event handling
- ? Customer portal for self-service
- ? Production-ready security

Your e-commerce data automation platform is ready to start generating recurring revenue!

## ?? Support

If you need help with the implementation:
- Check Stripe documentation: https://stripe.com/docs
- Review webhook event logs in Stripe dashboard
- Contact Stripe support for payment processing issues