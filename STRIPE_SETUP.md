# Stripe Billing Integration Setup Guide

This guide will help you set up Stripe billing for InstantViz in **under 15 minutes**.

---

## 🎯 Quick Overview

The billing system includes:
- ✅ 4 subscription tiers (Free, Pro, Team, Enterprise)
- ✅ Usage tracking & enforcement
- ✅ Stripe Checkout integration
- ✅ Customer Portal for subscription management
- ✅ Webhook handlers for automated billing events

---

## Step 1: Create a Stripe Account

1. Go to https://dashboard.stripe.com/register
2. Create an account (it's free!)
3. Complete the basic setup

---

## Step 2: Get Your API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your **Secret Key** (starts with `sk_test_`)
3. Update `infra/.env`:
   ```env
   STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_KEY_HERE
   ```

---

## Step 3: Create Products & Prices

### Create Pro Plan ($19/month):

1. Go to https://dashboard.stripe.com/test/products
2. Click **"+ Add product"**
3. Fill in:
   - **Name**: Pro Plan
   - **Description**: 500 visualizations/month
   - **Price**: $19.00 USD
   - **Billing period**: Monthly
4. Click **"Save product"**
5. Copy the **Price ID** (starts with `price_`)
6. Update `infra/.env`:
   ```env
   STRIPE_PRO_MONTHLY_PRICE_ID=price_YOUR_PRO_ID_HERE
   ```

### Create Pro Plan Annual ($190/year):

1. In the same product, click **"Add another price"**
2. Fill in:
   - **Price**: $190.00 USD
   - **Billing period**: Yearly
3. Copy the **Price ID**
4. Update `infra/.env`:
   ```env
   STRIPE_PRO_YEARLY_PRICE_ID=price_YOUR_PRO_YEARLY_ID_HERE
   ```

### Create Team Plan ($49/month):

1. Click **"+ Add product"**
2. Fill in:
   - **Name**: Team Plan
   - **Description**: 2,500 visualizations/month, up to 5 team members
   - **Price**: $49.00 USD
   - **Billing period**: Monthly
3. Copy the **Price ID**
4. Update `infra/.env`:
   ```env
   STRIPE_TEAM_MONTHLY_PRICE_ID=price_YOUR_TEAM_ID_HERE
   ```

### Create Team Plan Annual ($490/year):

1. Add another price:
   - **Price**: $490.00 USD
   - **Billing period**: Yearly
2. Copy the **Price ID**
3. Update `infra/.env`:
   ```env
   STRIPE_TEAM_YEARLY_PRICE_ID=price_YOUR_TEAM_YEARLY_ID_HERE
   ```

---

## Step 4: Set Up Webhooks (For Production)

### Local Development (Using Stripe CLI):

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Run:
   ```bash
   stripe listen --forward-to localhost:18001/stripe/webhook
   ```
3. Copy the webhook secret (starts with `whsec_`)
4. Update `infra/.env`:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
   ```

### Production (Stripe Dashboard):

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click **"+ Add endpoint"**
3. Enter your URL: `https://yourdomain.com/stripe/webhook`
4. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
   - `checkout.session.completed`
5. Copy the **Signing secret**
6. Update `.env` with the secret

---

## Step 5: Rebuild & Test

```bash
cd infra
docker compose down
docker compose up -d --build
```

### Test the API:

```bash
# Check subscription info (should show "free" tier)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:18001/subscription/subscription-info
```

---

## 🎯 How It Works

### 1. User Flow:

1. **Free user** signs up → Gets 50 visualizations/month
2. **Hits limit** → Receives 429 error with upgrade prompt
3. **Clicks upgrade** → Redirected to Stripe Checkout
4. **Completes payment** → Webhook updates their tier to Pro/Team
5. **Usage resets** → Counter set to 0, gets new limit (500 or 2,500)

### 2. Usage Tracking:

- Every `/visualize` request increments `usage_count`
- System checks `subscription_tier` and `usage_count` before processing
- Resets automatically every 30 days from `usage_reset_date`

### 3. Tier Limits:

| Tier | Visualizations | Workspaces | Price |
|------|----------------|------------|-------|
| Free | 50/month | 3 | $0 |
| Pro | 500/month | Unlimited | $19/mo |
| Team | 2,500/month | Unlimited | $49/mo |
| Enterprise | Unlimited | Unlimited | Custom |

---

## 🔗 API Endpoints

### For Frontend Integration:

#### Get Available Plans
```http
GET /subscription/plans
```

#### Create Checkout Session
```http
POST /subscription/create-checkout-session
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "plan": "pro_monthly",
  "success_url": "http://localhost:8082/app?success=true",
  "cancel_url": "http://localhost:8082/app?canceled=true"
}
```

**Response:**
```json
{
  "session_id": "cs_test_...",
  "url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

#### Get Subscription Info
```http
GET /subscription/subscription-info
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "tier": "pro",
  "status": "active",
  "usage_count": 45,
  "usage_limit": 500,
  "usage_percentage": 9.0,
  "usage_reset_date": "2025-02-01T00:00:00",
  "features": ["all_visualizations", "celebrity_images", "exports", "priority_support"],
  "has_stripe_subscription": true
}
```

#### Create Customer Portal Session (Manage Subscription)
```http
POST /subscription/create-portal-session
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "return_url": "http://localhost:8082/app"
}
```

---

## 🛠️ Troubleshooting

### Issue: "Missing stripe-signature header"
**Solution:** Webhook secret mismatch. Re-run `stripe listen` and copy the new secret.

### Issue: "User has no Stripe customer ID"
**Solution:** User needs to create a checkout session first. Customer ID is created automatically.

### Issue: Usage not resetting
**Solution:** Check `usage_reset_date` in database. It auto-resets after 30 days.

### Issue: Tier not updating after payment
**Solution:**
1. Check webhook logs: `docker logs infra-backend-1 | grep webhook`
2. Ensure webhook secret matches
3. Test with `stripe trigger customer.subscription.created`

---

## 📊 Database Schema

New fields added to `users` table:

```sql
subscription_tier VARCHAR(20) DEFAULT 'free'
stripe_customer_id VARCHAR(255)
stripe_subscription_id VARCHAR(255)
subscription_status VARCHAR(50) DEFAULT 'active'
usage_count INTEGER DEFAULT 0
usage_reset_date TIMESTAMP
trial_ends_at TIMESTAMP
```

---

## 🚀 Going to Production

1. **Switch to Live Mode** in Stripe Dashboard
2. Get **Live API Keys** (start with `sk_live_`)
3. Create **Live Products** (same as test mode)
4. Update `.env` with live keys
5. Set up **Production Webhook** with your domain
6. Enable **Stripe Tax** (optional, but recommended)
7. Configure **Email Receipts** in Stripe settings

---

## 💡 Next Steps

### Frontend Integration:

1. **Add "Upgrade" button** when user hits limit
2. **Redirect to Stripe Checkout** using the checkout session URL
3. **Show usage meter** in the UI
4. **Add "Manage Billing" link** to Customer Portal

### Example Frontend Code:

```typescript
// Upgrade button handler
async function handleUpgrade(plan: string) {
  const response = await fetch('/subscription/create-checkout-session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      plan: plan,
      success_url: window.location.origin + '/app?success=true',
      cancel_url: window.location.origin + '/app?canceled=true'
    })
  });

  const { url } = await response.json();
  window.location.href = url; // Redirect to Stripe Checkout
}
```

---

## ✅ Testing Checklist

- [ ] Free user can create 50 visualizations
- [ ] 51st visualization returns 429 error
- [ ] Checkout session creates successfully
- [ ] Payment succeeds in Stripe test mode (use card `4242 4242 4242 4242`)
- [ ] Webhook updates user tier to Pro/Team
- [ ] Usage count resets to 0 after upgrade
- [ ] Pro user can create 500 visualizations
- [ ] Customer Portal loads successfully

---

## 📞 Need Help?

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Test Cards**: https://stripe.com/docs/testing
- **Webhook Testing**: https://stripe.com/docs/webhooks/test

---

**You're all set! 🎉**

Run `docker compose up -d --build` and your billing system is live!
