import React, { useEffect, useState } from 'react';
import { AlertTriangle, XCircle, Check, Clock, CreditCard } from 'lucide-react';
import { api } from '../lib/api';

// Comprehensive TypeScript interface for customer plan data
interface CustomerPlan {
  tier: 'FREE' | 'PRO' | 'TEAM' | 'ENTERPRISE';
  status: 'active' | 'trialing' | 'past_due' | 'canceled' | 'suspended';
  usage_count: number;
  usage_limit: number | null; // null means unlimited
  usage_reset_date: string; // ISO 8601
  features: string[];
  has_stripe_subscription: boolean;

  // Optional fields for different states
  trial_end_date?: string; // ISO 8601, for trialing status
  payment_retry_date?: string; // ISO 8601, for past_due status
  cancellation_date?: string; // ISO 8601, for canceled status
  suspension_reason?: string; // for suspended status
}

// State machine types
type PlanState = 'active_free' | 'active_paid' | 'trialing' | 'past_due' | 'canceled_grace' | 'suspended';

interface BadgeConfig {
  text: string;
  color: string;
  background: string;
}

interface CtaConfig {
  label: string;
  action: () => void;
  variant: 'primary' | 'secondary' | 'danger';
}

// Helper function to determine plan state from API data
function determinePlanState(plan: CustomerPlan): PlanState {
  if (plan.status === 'suspended') return 'suspended';
  if (plan.status === 'past_due') return 'past_due';
  if (plan.status === 'trialing') return 'trialing';
  if (plan.status === 'canceled') return 'canceled_grace';
  if (plan.status === 'active' && plan.tier === 'FREE') return 'active_free';
  if (plan.status === 'active' && plan.tier !== 'FREE') return 'active_paid';
  return 'active_free'; // fallback
}

// State machine: Badge configuration based on plan state
function getBadgeConfig(state: PlanState, plan: CustomerPlan): BadgeConfig {
  switch (state) {
    case 'active_free':
      return { text: 'Active', color: '#ffffff', background: '#10b981' };
    case 'active_paid':
      return { text: 'Active', color: '#ffffff', background: '#10b981' };
    case 'trialing':
      return { text: 'Trial Active', color: '#ffffff', background: '#3b82f6' };
    case 'past_due':
      return { text: 'Payment Failed', color: '#ffffff', background: '#ef4444' };
    case 'canceled_grace':
      return { text: 'Canceled', color: '#ffffff', background: '#f59e0b' };
    case 'suspended':
      return { text: 'Suspended', color: '#ffffff', background: '#6b7280' };
  }
}

// State machine: CTA configuration based on plan state
function getCtaConfig(state: PlanState, plan: CustomerPlan): CtaConfig | null {
  switch (state) {
    case 'active_free':
      return {
        label: 'Upgrade Plan',
        action: () => window.location.href = '/pricing',
        variant: 'primary'
      };
    case 'active_paid':
      return {
        label: 'Manage Billing',
        action: async () => {
          try {
            const response = await api.post('/subscription/create-portal-session', {
              return_url: window.location.origin + '/dashboard'
            });
            window.location.href = response.data.url;
          } catch (err) {
            alert('Failed to open billing portal');
          }
        },
        variant: 'secondary'
      };
    case 'trialing':
      return {
        label: 'Subscribe Now',
        action: () => window.location.href = '/pricing',
        variant: 'primary'
      };
    case 'past_due':
      return {
        label: 'Update Payment Method',
        action: async () => {
          try {
            const response = await api.post('/subscription/create-portal-session', {
              return_url: window.location.origin + '/dashboard'
            });
            window.location.href = response.data.url;
          } catch (err) {
            alert('Failed to open billing portal');
          }
        },
        variant: 'danger'
      };
    case 'canceled_grace':
      return {
        label: 'Reactivate Subscription',
        action: () => window.location.href = '/pricing',
        variant: 'primary'
      };
    case 'suspended':
      return null; // No action available for suspended accounts
  }
}

export default function UserDashboard() {
  const [plan, setPlan] = useState<CustomerPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscriptionInfo();
  }, []);

  const fetchSubscriptionInfo = async () => {
    try {
      setLoading(true);
      const response = await api.get('/subscription/subscription-info');
      // Transform API response to match CustomerPlan interface
      const apiData = response.data;
      const transformedPlan: CustomerPlan = {
        tier: apiData.tier.toUpperCase(),
        status: apiData.status,
        usage_count: apiData.usage_count,
        usage_limit: typeof apiData.usage_limit === 'number' ? apiData.usage_limit : null,
        usage_reset_date: apiData.usage_reset_date,
        features: apiData.features || [],
        has_stripe_subscription: apiData.has_stripe_subscription || false,
        trial_end_date: apiData.trial_end_date,
        payment_retry_date: apiData.payment_retry_date,
        cancellation_date: apiData.cancellation_date,
        suspension_reason: apiData.suspension_reason
      };
      setPlan(transformedPlan);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch subscription info:', err);
      setError(err.response?.data?.detail || 'Failed to load subscription info');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoDate: string, relative: boolean = true) => {
    const date = new Date(isoDate);
    if (!relative) {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    }

    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMs < 0) return 'Resetting soon';
    if (diffHours < 1) return 'Resets in less than 1h';
    if (diffHours < 24) return `Resets in ${diffHours}h`;
    if (diffDays === 1) return 'Resets tomorrow';
    return `Resets in ${diffDays} days`;
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'FREE':
        return '#6b7280';
      case 'PRO':
        return '#3b82f6';
      case 'TEAM':
        return '#8b5cf6';
      case 'ENTERPRISE':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage < 70) return '#10b981'; // neutral green
    if (percentage < 90) return '#f59e0b'; // warning orange
    return '#ef4444'; // danger red
  };

  const calculateUsagePercentage = (count: number, limit: number | null): number => {
    if (limit === null) return 0; // unlimited
    if (limit === 0) return 100; // edge case
    return Math.min((count / limit) * 100, 100);
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{
          display: 'inline-block',
          width: '32px',
          height: '32px',
          border: '3px solid #e5e7eb',
          borderTop: '3px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite'
        }} />
        <p style={{ marginTop: '16px', fontSize: '14px', color: '#6b7280' }}>Loading subscription info...</p>
        <style jsx>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{
          maxWidth: '400px',
          margin: '0 auto',
          padding: '16px',
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          color: '#991b1b',
          marginBottom: '20px'
        }}>
          {error}
        </div>
        <button
          onClick={fetchSubscriptionInfo}
          style={{
            padding: '10px 20px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!plan) return null;

  // Determine current state from plan data
  const currentState = determinePlanState(plan);
  const badgeConfig = getBadgeConfig(currentState, plan);
  const ctaConfig = getCtaConfig(currentState, plan);
  const usagePercentage = calculateUsagePercentage(plan.usage_count, plan.usage_limit);
  const usageColor = getUsageColor(usagePercentage);
  const tierColor = getTierColor(plan.tier);

  // Determine if upgrade panel should be shown
  const showUpgradePanel = ['active_free', 'trialing', 'canceled_grace'].includes(currentState);

  return (
    <div style={{
      padding: '32px 16px',
      maxWidth: '1040px',
      margin: '0 auto'
    }}>
      {/* Header */}
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '28px',
          fontWeight: 600,
          color: '#111827',
          margin: '0 0 8px 0'
        }}>
          Account Dashboard
        </h1>
        <p style={{
          fontSize: '14px',
          color: '#6b7280',
          margin: 0
        }}>
          Manage your subscription and monitor usage
        </p>
      </header>

      {/* Current Plan Card */}
      <section
        aria-labelledby="current-plan-heading"
        style={{
          background: 'white',
          border: `1px solid ${tierColor}`,
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}
      >
        {/* Plan Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '24px',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div>
            <h2
              id="current-plan-heading"
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                margin: '0 0 8px 0'
              }}
            >
              Current Plan
            </h2>
            <div style={{
              fontSize: '32px',
              fontWeight: 700,
              color: tierColor,
              lineHeight: 1
            }}>
              {plan.tier}
            </div>
          </div>

          {/* Dynamic Badge */}
          <div
            role="status"
            aria-label={`Plan status: ${badgeConfig.text}`}
            style={{
              padding: '6px 14px',
              background: badgeConfig.background,
              color: badgeConfig.color,
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.3px'
            }}
          >
            {badgeConfig.text}
          </div>
        </div>

        {/* Usage Section */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            marginBottom: '12px'
          }}>
            <h3 style={{
              fontSize: '14px',
              fontWeight: 600,
              color: '#111827',
              margin: 0
            }}>
              Daily AI Requests
            </h3>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '13px',
              color: '#6b7280'
            }}>
              <Clock size={14} strokeWidth={1.5} />
              <span>{formatDate(plan.usage_reset_date, true)}</span>
            </div>
          </div>

          {/* Progress Bar with ARIA */}
          <div
            role="progressbar"
            aria-valuenow={plan.usage_count}
            aria-valuemin={0}
            aria-valuemax={plan.usage_limit || undefined}
            aria-label={`${plan.usage_count} of ${plan.usage_limit || 'unlimited'} AI requests used today`}
            style={{
              width: '100%',
              height: '10px',
              background: '#e5e7eb',
              borderRadius: '5px',
              overflow: 'hidden',
              marginBottom: '10px'
            }}
          >
            <div style={{
              width: plan.usage_limit ? `${usagePercentage}%` : '0%',
              height: '100%',
              background: usageColor,
              transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s ease',
              borderRadius: '5px'
            }} />
          </div>

          {/* Usage Text */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '13px',
            color: '#4b5563'
          }}>
            <span>
              <strong style={{ fontWeight: 600, color: '#111827' }}>
                {plan.usage_count.toLocaleString()}
              </strong>
              {' '}AI requests today
            </span>
            <span style={{ fontWeight: 500 }}>
              {plan.usage_limit === null ? 'Unlimited' : `${plan.usage_limit.toLocaleString()} limit`}
            </span>
          </div>

          {/* Usage Warnings (70-90% and 90%+) */}
          {plan.usage_limit !== null && usagePercentage >= 70 && usagePercentage < 90 && (
            <div
              role="alert"
              style={{
                marginTop: '12px',
                padding: '12px 14px',
                background: '#fffbeb',
                border: '1px solid #fcd34d',
                borderRadius: '8px',
                fontSize: '13px',
                color: '#92400e',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px'
              }}
            >
              <AlertTriangle size={16} strokeWidth={2} style={{ flexShrink: 0, marginTop: '1px', color: '#f59e0b' }} />
              <span>
                You've used <strong>{usagePercentage.toFixed(0)}%</strong> of your daily limit.
                {plan.tier === 'FREE' && ' Upgrade to PRO for unlimited AI requests!'}
              </span>
            </div>
          )}

          {plan.usage_limit !== null && usagePercentage >= 90 && (
            <div
              role="alert"
              style={{
                marginTop: '12px',
                padding: '12px 14px',
                background: '#fef2f2',
                border: '1px solid #fca5a5',
                borderRadius: '8px',
                fontSize: '13px',
                color: '#991b1b',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px'
              }}
            >
              <XCircle size={16} strokeWidth={2} style={{ flexShrink: 0, marginTop: '1px', color: '#ef4444' }} />
              <span>
                {usagePercentage >= 100
                  ? "You've reached your daily AI limit. Quota resets tomorrow. Upgrade for unlimited access!"
                  : `You've used ${usagePercentage.toFixed(0)}% of your daily limit. You're close to running out.`}
              </span>
            </div>
          )}
        </div>

        {/* Features */}
        <div style={{ marginBottom: ctaConfig ? '20px' : '0' }}>
          <h3 style={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#111827',
            margin: '0 0 12px 0'
          }}>
            Plan Features
          </h3>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {plan.features.map((feature, idx) => (
              <span
                key={idx}
                style={{
                  padding: '6px 12px',
                  background: '#f3f4f6',
                  borderRadius: '16px',
                  fontSize: '12px',
                  color: '#374151',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontWeight: 500
                }}
              >
                <Check size={13} strokeWidth={2.5} style={{ color: '#10b981', flexShrink: 0 }} />
                {feature.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>

        {/* State-Aware CTA Button */}
        {ctaConfig && (
          <button
            onClick={ctaConfig.action}
            aria-label={ctaConfig.label}
            style={{
              width: '100%',
              padding: '12px 20px',
              background: ctaConfig.variant === 'primary' ? '#3b82f6' :
                         ctaConfig.variant === 'danger' ? '#ef4444' : 'transparent',
              color: ctaConfig.variant === 'secondary' ? '#3b82f6' : '#ffffff',
              border: ctaConfig.variant === 'secondary' ? '1px solid #3b82f6' : 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseEnter={(e) => {
              if (ctaConfig.variant === 'primary') {
                e.currentTarget.style.background = '#2563eb';
              } else if (ctaConfig.variant === 'danger') {
                e.currentTarget.style.background = '#dc2626';
              } else {
                e.currentTarget.style.background = '#eff6ff';
              }
            }}
            onMouseLeave={(e) => {
              if (ctaConfig.variant === 'primary') {
                e.currentTarget.style.background = '#3b82f6';
              } else if (ctaConfig.variant === 'danger') {
                e.currentTarget.style.background = '#ef4444';
              } else {
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <CreditCard size={16} strokeWidth={2} />
            {ctaConfig.label}
          </button>
        )}

        {/* Suspended State Message */}
        {currentState === 'suspended' && (
          <div
            role="alert"
            style={{
              padding: '14px',
              background: '#f9fafb',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '13px',
              color: '#374151',
              textAlign: 'center'
            }}
          >
            <strong>Account Suspended:</strong> {plan.suspension_reason || 'Please contact support for assistance.'}
          </div>
        )}
      </section>

      {/* Smart Upgrade Panel (only for active_free, trialing, canceled_grace) */}
      {showUpgradePanel && (
        <section
          aria-labelledby="upgrade-heading"
          style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            borderRadius: '12px',
            padding: '28px 24px',
            color: 'white',
            textAlign: 'center',
            marginTop: '20px'
          }}
        >
          <h2
            id="upgrade-heading"
            style={{
              margin: '0 0 12px 0',
              fontSize: '22px',
              fontWeight: 700,
              lineHeight: 1.3
            }}
          >
            {currentState === 'active_free' && 'Unlock More Power'}
            {currentState === 'trialing' && 'Continue with Pro Features'}
            {currentState === 'canceled_grace' && 'Reactivate Your Subscription'}
          </h2>
          <p style={{
            margin: '0 0 24px 0',
            fontSize: '14px',
            opacity: 0.95,
            lineHeight: 1.5,
            maxWidth: '480px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            {currentState === 'active_free' && 'Get unlimited AI requests, unlock all features, and supercharge your productivity.'}
            {currentState === 'trialing' && `Your trial ends ${plan.trial_end_date ? `on ${formatDate(plan.trial_end_date, false)}` : 'soon'}. Subscribe now to keep all features.`}
            {currentState === 'canceled_grace' && 'Your subscription was canceled but you still have access. Reactivate to continue enjoying premium features.'}
          </p>
          <button
            onClick={() => window.location.href = '/pricing'}
            aria-label="View pricing plans"
            style={{
              padding: '13px 36px',
              background: 'white',
              color: '#3b82f6',
              border: 'none',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 14px rgba(0,0,0,0.2)';
            }}
          >
            {currentState === 'active_free' && 'View Plans'}
            {currentState === 'trialing' && 'Subscribe Now'}
            {currentState === 'canceled_grace' && 'Reactivate Plan'}
          </button>
        </section>
      )}

      {/* State-Specific Info Banners */}
      {currentState === 'past_due' && plan.payment_retry_date && (
        <div
          role="alert"
          style={{
            marginTop: '20px',
            padding: '16px',
            background: '#fef2f2',
            border: '1px solid #fca5a5',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#991b1b'
          }}
        >
          <strong>Payment Failed:</strong> We'll retry your payment on {formatDate(plan.payment_retry_date, false)}.
          Please update your payment method to avoid service interruption.
        </div>
      )}

      {currentState === 'canceled_grace' && plan.cancellation_date && (
        <div
          role="alert"
          style={{
            marginTop: '20px',
            padding: '16px',
            background: '#fffbeb',
            border: '1px solid #fcd34d',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#92400e'
          }}
        >
          <strong>Subscription Canceled:</strong> Your access will end on {formatDate(plan.cancellation_date, false)}.
          Reactivate anytime before then to continue.
        </div>
      )}
    </div>
  );
}
