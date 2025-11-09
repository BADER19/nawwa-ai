# Dashboard State Machine Documentation

## Overview
The Account Dashboard now uses a comprehensive state machine to adapt the UI based on the customer's plan status. This creates a dynamic, data-driven experience that changes based on the user's subscription state.

## State Machine States

### 1. **active_free**
**Trigger:** `status === 'active' && tier === 'FREE'`

**UI Behavior:**
- Badge: "Active" (green background #10b981)
- CTA Button: "Upgrade Plan" (primary blue)
- Upgrade Panel: **Visible** - "Unlock More Power"
- Usage Bar: Shows 10/10 limit with color coding

**User Journey:**
Free tier users see prominent upgrade messaging to convert them to paid plans.

---

### 2. **active_paid**
**Trigger:** `status === 'active' && tier !== 'FREE'`

**UI Behavior:**
- Badge: "Active" (green background #10b981)
- CTA Button: "Manage Billing" (secondary outline)
- Upgrade Panel: **Hidden**
- Usage Bar: Shows current usage with 70/90 thresholds

**User Journey:**
Paying customers can manage their subscription but don't see upgrade nags.

---

### 3. **trialing**
**Trigger:** `status === 'trialing'`

**UI Behavior:**
- Badge: "Trial Active" (blue background #3b82f6)
- CTA Button: "Subscribe Now" (primary blue)
- Upgrade Panel: **Visible** - "Continue with Pro Features" + trial end date
- Usage Bar: Shows trial usage limits

**User Journey:**
Trial users are encouraged to convert before their trial expires.

---

### 4. **past_due**
**Trigger:** `status === 'past_due'`

**UI Behavior:**
- Badge: "Payment Failed" (red background #ef4444)
- CTA Button: "Update Payment Method" (danger red)
- Upgrade Panel: **Hidden**
- Additional Banner: Shows payment retry date
- Usage Bar: May show limited access

**User Journey:**
Users with failed payments see urgent calls-to-action to update their payment method.

---

### 5. **canceled_grace**
**Trigger:** `status === 'canceled'`

**UI Behavior:**
- Badge: "Canceled" (orange background #f59e0b)
- CTA Button: "Reactivate Subscription" (primary blue)
- Upgrade Panel: **Visible** - "Reactivate Your Subscription"
- Additional Banner: Shows cancellation end date
- Usage Bar: Still shows access during grace period

**User Journey:**
Canceled users retain access until the billing period ends and are encouraged to reactivate.

---

### 6. **suspended**
**Trigger:** `status === 'suspended'`

**UI Behavior:**
- Badge: "Suspended" (gray background #6b7280)
- CTA Button: **None** (no action available)
- Upgrade Panel: **Hidden**
- Additional Message: Shows suspension reason
- Usage Bar: Shows suspended state

**User Journey:**
Suspended accounts have no self-service options and must contact support.

---

## Usage Bar Color Coding

The usage bar uses three distinct color states:

| Usage %      | Color   | Hex Code | Meaning              |
|--------------|---------|----------|----------------------|
| 0% - 69%     | Green   | #10b981  | Healthy usage        |
| 70% - 89%    | Orange  | #f59e0b  | Warning - approaching limit |
| 90% - 100%+  | Red     | #ef4444  | Danger - at or over limit |

**Thresholds changed from old implementation (50/80) to new (70/90) per requirements.**

---

## Accessibility Features

### ARIA Labels
- Progress bar: `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- Badge: `role="status"` with descriptive `aria-label`
- Alerts: `role="alert"` for warnings and errors
- Sections: `aria-labelledby` for semantic headings

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Focus states clearly visible
- Tab order follows logical reading order

### Screen Reader Support
- Semantic HTML5 elements (`<section>`, `<header>`, `<h1>`, `<h2>`, `<h3>`)
- Progress bars announce current/max values
- Dynamic content changes announced via alerts

---

## API Contract

### Expected Response from `/subscription/subscription-info`

```typescript
{
  tier: 'FREE' | 'PRO' | 'TEAM' | 'ENTERPRISE',
  status: 'active' | 'trialing' | 'past_due' | 'canceled' | 'suspended',
  usage_count: number,
  usage_limit: number | null, // null = unlimited
  usage_reset_date: string, // ISO 8601
  features: string[], // e.g., ['basic_shapes', 'community_support']
  has_stripe_subscription: boolean,

  // Optional fields for different states:
  trial_end_date?: string, // ISO 8601, for 'trialing'
  payment_retry_date?: string, // ISO 8601, for 'past_due'
  cancellation_date?: string, // ISO 8601, for 'canceled'
  suspension_reason?: string // for 'suspended'
}
```

---

## Implementation Details

### State Determination Function
```typescript
function determinePlanState(plan: CustomerPlan): PlanState {
  if (plan.status === 'suspended') return 'suspended';
  if (plan.status === 'past_due') return 'past_due';
  if (plan.status === 'trialing') return 'trialing';
  if (plan.status === 'canceled') return 'canceled_grace';
  if (plan.status === 'active' && plan.tier === 'FREE') return 'active_free';
  if (plan.status === 'active' && plan.tier !== 'FREE') return 'active_paid';
  return 'active_free'; // fallback
}
```

### Usage Calculation
```typescript
function calculateUsagePercentage(count: number, limit: number | null): number {
  if (limit === null) return 0; // unlimited
  if (limit === 0) return 100; // edge case
  return Math.min((count / limit) * 100, 100);
}
```

---

## Testing Checklist

To test all states, modify the backend response or use test accounts:

- [ ] **active_free**: Create account with FREE tier, status 'active'
- [ ] **active_paid**: Upgrade to PRO tier, status 'active'
- [ ] **trialing**: Start trial with status 'trialing', include trial_end_date
- [ ] **past_due**: Simulate failed payment with status 'past_due', include payment_retry_date
- [ ] **canceled_grace**: Cancel subscription with status 'canceled', include cancellation_date
- [ ] **suspended**: Suspend account with status 'suspended', include suspension_reason

### Edge Cases to Test

1. **Usage at exactly 70%**: Should show orange warning
2. **Usage at exactly 90%**: Should show red danger alert
3. **Usage over 100%**: Should cap bar at 100%, show disabled message
4. **Unlimited plan (usage_limit: null)**: Progress bar shows 0%, text says "Unlimited"
5. **Zero usage**: Bar empty, shows 0 visualizations
6. **Missing optional dates**: Falls back to "soon" for relative dates

---

## Design Specifications

### Typography
- Page Title: 28px, font-weight 600, color #111827
- Section Headings: 14px, font-weight 600, uppercase, letter-spacing 0.5px
- Plan Tier: 32px, font-weight 700, tier-specific color
- Body Text: 13-14px, font-weight 400-500, color #4b5563/#6b7280

### Color Palette
- **FREE Tier**: #6b7280 (gray)
- **PRO Tier**: #3b82f6 (blue)
- **TEAM Tier**: #8b5cf6 (purple)
- **ENTERPRISE Tier**: #ef4444 (red)

### Spacing
- Container max-width: 1040px
- Card padding: 24px
- Section margins: 20-32px
- Element gaps: 8-16px

### Responsive Behavior
- Desktop: Max 1040px centered container
- Mobile: Full width with 16px side padding
- Badge/Header: Flexbox wraps on narrow screens
- Feature pills: Wrap to multiple rows

---

## Zero Emojis Policy

All visual indicators use:
- **lucide-react** icons (Check, AlertTriangle, XCircle, Clock, CreditCard)
- Professional vector graphics
- Consistent sizing (13-16px) and stroke weight (1.5-2.5px)

**No Unicode emojis anywhere in the component.**
