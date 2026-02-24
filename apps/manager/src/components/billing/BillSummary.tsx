/**
 * BillSummary Component
 * Displays itemized services list, subtotal, GST, total, loyalty points
 * with print/share options
 */

import React from 'react';
import { Printer, Share2, Receipt } from 'lucide-react';
import { Button, Card, CardHeader, CardTitle, CardContent, Badge } from '@salon-flow/ui';
import { formatCurrency } from '@salon-flow/shared';
import type { BillItem, PaymentMethodType } from '../../types/billing';

interface BillSummaryProps {
  items: BillItem[];
  subtotal: number;
  gstAmount: number;
  gstPercent: number;
  grandTotal: number;
  loyaltyPoints: number;
  membershipDiscount?: number;
  manualAdjustment?: number;
  paymentMethod?: PaymentMethodType;
  customerName?: string;
  customerPhone?: string;
  invoiceNumber?: string;
  createdAt?: string;
  showActions?: boolean;
  onPrint?: () => void;
  onShare?: () => void;
}

export const BillSummary: React.FC<BillSummaryProps> = ({
  items,
  subtotal,
  gstAmount,
  gstPercent,
  grandTotal,
  loyaltyPoints,
  membershipDiscount = 0,
  manualAdjustment = 0,
  paymentMethod,
  customerName,
  customerPhone,
  invoiceNumber,
  createdAt,
  showActions = true,
  onPrint,
  onShare,
}) => {
  const handlePrint = () => {
    if (onPrint) {
      onPrint();
    } else {
      window.print();
    }
  };

  const handleShare = async () => {
    if (onShare) {
      onShare();
      return;
    }

    // Default share behavior - create WhatsApp message
    const billText = `
*Salon Flow Invoice*
${invoiceNumber ? `Invoice: ${invoiceNumber}` : ''}
${customerName ? `Customer: ${customerName}` : ''}
${customerPhone ? `Phone: ${customerPhone}` : ''}

*Services:*
${items.map(item => `• ${item.serviceName} - ${formatCurrency(item.overridePrice ?? item.servicePrice)}`).join('\n')}

Subtotal: ${formatCurrency(subtotal)}
GST (${gstPercent}%): ${formatCurrency(gstAmount)}
${membershipDiscount > 0 ? `Membership Discount: -${formatCurrency(membershipDiscount)}\n` : ''}
${manualAdjustment !== 0 ? `Adjustment: ${formatCurrency(manualAdjustment)}\n` : ''}
*Grand Total: ${formatCurrency(grandTotal)}*

Loyalty Points Earned: ${loyaltyPoints}

Thank you for visiting! 💇
    `.trim();

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Salon Flow Invoice',
          text: billText,
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    } else if (customerPhone) {
      // Fallback to WhatsApp
      const whatsappUrl = `https://wa.me/${customerPhone.replace(/\D/g, '')}?text=${encodeURIComponent(billText)}`;
      window.open(whatsappUrl, '_blank');
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Receipt className="h-5 w-5" />
          Bill Summary
        </CardTitle>
        {showActions && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              className="h-8"
            >
              <Printer className="h-4 w-4 mr-1" />
              Print
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
              className="h-8"
            >
              <Share2 className="h-4 w-4 mr-1" />
              Share
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Invoice Info */}
        {(invoiceNumber || createdAt) && (
          <div className="flex justify-between text-sm text-gray-500 pb-2 border-b">
            {invoiceNumber && <span>#{invoiceNumber}</span>}
            {createdAt && <span>{new Date(createdAt).toLocaleString()}</span>}
          </div>
        )}

        {/* Customer Info */}
        {customerName && (
          <div className="text-sm pb-2 border-b">
            <p className="font-medium">{customerName}</p>
            {customerPhone && <p className="text-gray-500">{customerPhone}</p>}
          </div>
        )}

        {/* Services List */}
        <div className="space-y-2">
          {items.map((item, index) => (
            <div key={`${item.serviceId}-${index}`} className="flex justify-between items-start">
              <div className="flex-1">
                <p className="font-medium text-sm">{item.serviceName}</p>
                <p className="text-xs text-gray-500">by {item.staffName}</p>
                {item.overridePrice !== undefined && item.overridePrice < item.servicePrice && (
                  <Badge variant="secondary" className="text-xs mt-1">
                    {Math.round((1 - item.overridePrice / item.servicePrice) * 100)}% off
                  </Badge>
                )}
              </div>
              <div className="text-right">
                {item.overridePrice !== undefined && item.overridePrice < item.servicePrice ? (
                  <div>
                    <p className="text-sm line-through text-gray-400">
                      {formatCurrency(item.servicePrice)}
                    </p>
                    <p className="font-medium text-green-600">
                      {formatCurrency(item.overridePrice)}
                    </p>
                  </div>
                ) : (
                  <p className="font-medium">{formatCurrency(item.servicePrice)}</p>
                )}
                {item.quantity > 1 && (
                  <p className="text-xs text-gray-500">×{item.quantity}</p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Totals */}
        <div className="border-t pt-3 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Subtotal</span>
            <span>{formatCurrency(subtotal)}</span>
          </div>

          {membershipDiscount > 0 && (
            <div className="flex justify-between text-sm text-green-600">
              <span>Membership Discount</span>
              <span>-{formatCurrency(membershipDiscount)}</span>
            </div>
          )}

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">GST ({gstPercent}%)</span>
            <span>{formatCurrency(gstAmount)}</span>
          </div>

          {manualAdjustment !== 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adjustment</span>
              <span className={manualAdjustment < 0 ? 'text-green-600' : ''}>
                {manualAdjustment < 0 ? '-' : '+'}{formatCurrency(Math.abs(manualAdjustment))}
              </span>
            </div>
          )}

          <div className="flex justify-between font-semibold text-lg border-t pt-2">
            <span>Grand Total</span>
            <span className="text-purple-600">{formatCurrency(grandTotal)}</span>
          </div>
        </div>

        {/* Loyalty Points */}
        {loyaltyPoints > 0 && (
          <div className="bg-purple-50 rounded-lg p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">⭐</span>
              <span className="text-sm font-medium text-purple-700">
                Loyalty Points Earned
              </span>
            </div>
            <span className="font-bold text-purple-600">+{loyaltyPoints}</span>
          </div>
        )}

        {/* Payment Method */}
        {paymentMethod && (
          <div className="text-sm text-gray-500 flex items-center gap-2">
            <span>Payment:</span>
            <Badge variant="outline">
              {paymentMethod === 'upi' && '📱 UPI'}
              {paymentMethod === 'cash' && '💵 Cash'}
              {paymentMethod === 'card' && '💳 Card'}
              {paymentMethod === 'wallet' && '👛 Wallet'}
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default BillSummary;
