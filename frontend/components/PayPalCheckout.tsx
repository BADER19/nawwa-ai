import React, { useEffect } from 'react';

interface PayPalCheckoutProps {
  planId: string;
  onSuccess: (subscriptionId: string) => void;
  onError: (error: any) => void;
  onCancel: () => void;
}

declare global {
  interface Window {
    paypal: any;
  }
}

export default function PayPalCheckout({ planId, onSuccess, onError, onCancel }: PayPalCheckoutProps) {
  useEffect(() => {
    // Load PayPal SDK script
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID}&vault=true&intent=subscription`;
    script.async = true;

    script.onload = () => {
      if (window.paypal) {
        window.paypal.Buttons({
          createSubscription: function(data: any, actions: any) {
            return actions.subscription.create({
              plan_id: planId,
              application_context: {
                shipping_preference: 'NO_SHIPPING'
              }
            });
          },
          onApprove: function(data: any, actions: any) {
            console.log('Subscription approved:', data);
            onSuccess(data.subscriptionID);
          },
          onError: function(err: any) {
            console.error('PayPal error:', err);
            onError(err);
          },
          onCancel: function(data: any) {
            console.log('Subscription cancelled:', data);
            onCancel();
          }
        }).render('#paypal-button-container');
      }
    };

    document.body.appendChild(script);

    return () => {
      // Cleanup
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [planId, onSuccess, onError, onCancel]);

  return (
    <div>
      <div id="paypal-button-container"></div>
    </div>
  );
}