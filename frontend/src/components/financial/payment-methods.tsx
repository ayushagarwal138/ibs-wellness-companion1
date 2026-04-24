'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'react-hot-toast';
import { 
  CreditCard, 
  Plus, 
  Trash2, 
  Edit, 
  Check, 
  X,
  Shield,
  Star,
  Calendar,
  AlertCircle
} from 'lucide-react';

interface PaymentMethod {
  id: string;
  type: string;
  card_last_four?: string;
  card_brand?: string;
  expiry_month?: number;
  expiry_year?: number;
  is_default: boolean;
  created_at: string;
}

interface PaymentMethodCreate {
  type: string;
  card_number?: string;
  card_brand?: string;
  expiry_month?: number;
  expiry_year?: number;
  cvv?: string;
  cardholder_name?: string;
  is_default?: boolean;
}

export const PaymentMethods: React.FC = () => {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<PaymentMethodCreate>({
    type: 'card',
    is_default: false
  });

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const fetchPaymentMethods = async () => {
    try {
      const response = await fetch('/api/v1/financial/payment-methods', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPaymentMethods(data);
      } else {
        toast.error('Failed to fetch payment methods');
      }
    } catch (error) {
      toast.error('Error fetching payment methods');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingId 
        ? `/api/v1/financial/payment-methods/${editingId}`
        : '/api/v1/financial/payment-methods';
      
      const method = editingId ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingId ? 'Payment method updated' : 'Payment method added');
        setShowAddForm(false);
        setEditingId(null);
        setFormData({ type: 'card', is_default: false });
        fetchPaymentMethods();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save payment method');
      }
    } catch (error) {
      toast.error('Error saving payment method');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this payment method?')) return;

    try {
      const response = await fetch(`/api/v1/financial/payment-methods/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        toast.success('Payment method deleted');
        fetchPaymentMethods();
      } else {
        toast.error('Failed to delete payment method');
      }
    } catch (error) {
      toast.error('Error deleting payment method');
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      const response = await fetch(`/api/v1/financial/payment-methods/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ is_default: true })
      });

      if (response.ok) {
        toast.success('Default payment method updated');
        fetchPaymentMethods();
      } else {
        toast.error('Failed to update default payment method');
      }
    } catch (error) {
      toast.error('Error updating payment method');
    }
  };

  const startEdit = (method: PaymentMethod) => {
    setEditingId(method.id);
    setFormData({
      type: method.type,
      card_brand: method.card_brand,
      expiry_month: method.expiry_month,
      expiry_year: method.expiry_year,
      is_default: method.is_default
    });
    setShowAddForm(true);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setShowAddForm(false);
    setFormData({ type: 'card', is_default: false });
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">Loading payment methods...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Payment Methods</h2>
        <Button 
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          Add Payment Method
        </Button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>
              {editingId ? 'Edit Payment Method' : 'Add Payment Method'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="type">Payment Type</Label>
                  <Select 
                    value={formData.type} 
                    onValueChange={(value) => setFormData({...formData, type: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="card">Credit/Debit Card</SelectItem>
                      <SelectItem value="upi">UPI</SelectItem>
                      <SelectItem value="netbanking">Net Banking</SelectItem>
                      <SelectItem value="wallet">Digital Wallet</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.type === 'card' && (
                  <>
                    {!editingId && (
                      <div>
                        <Label htmlFor="card_number">Card Number</Label>
                        <Input
                          id="card_number"
                          placeholder="1234 5678 9012 3456"
                          value={formData.card_number || ''}
                          onChange={(e) => setFormData({...formData, card_number: e.target.value})}
                          required
                        />
                      </div>
                    )}

                    <div>
                      <Label htmlFor="cardholder_name">Cardholder Name</Label>
                      <Input
                        id="cardholder_name"
                        placeholder="John Doe"
                        value={formData.cardholder_name || ''}
                        onChange={(e) => setFormData({...formData, cardholder_name: e.target.value})}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="expiry_month">Expiry Month</Label>
                      <Select 
                        value={formData.expiry_month?.toString()} 
                        onValueChange={(value) => setFormData({...formData, expiry_month: parseInt(value)})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Month" />
                        </SelectTrigger>
                        <SelectContent>
                          {Array.from({length: 12}, (_, i) => (
                            <SelectItem key={i + 1} value={(i + 1).toString()}>
                              {(i + 1).toString().padStart(2, '0')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="expiry_year">Expiry Year</Label>
                      <Select 
                        value={formData.expiry_year?.toString()} 
                        onValueChange={(value) => setFormData({...formData, expiry_year: parseInt(value)})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Year" />
                        </SelectTrigger>
                        <SelectContent>
                          {Array.from({length: 10}, (_, i) => {
                            const year = new Date().getFullYear() + i;
                            return (
                              <SelectItem key={year} value={year.toString()}>
                                {year}
                              </SelectItem>
                            );
                          })}
                        </SelectContent>
                      </Select>
                    </div>

                    {!editingId && (
                      <div>
                        <Label htmlFor="cvv">CVV</Label>
                        <Input
                          id="cvv"
                          placeholder="123"
                          maxLength={4}
                          value={formData.cvv || ''}
                          onChange={(e) => setFormData({...formData, cvv: e.target.value})}
                          required
                        />
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_default"
                  checked={formData.is_default}
                  onChange={(e) => setFormData({...formData, is_default: e.target.checked})}
                />
                <Label htmlFor="is_default">Set as default payment method</Label>
              </div>

              <div className="flex gap-2">
                <Button type="submit">
                  {editingId ? 'Update' : 'Add'} Payment Method
                </Button>
                <Button type="button" variant="outline" onClick={cancelEdit}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Payment Methods List */}
      <div className="grid gap-4">
        {paymentMethods.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <CreditCard className="mx-auto mb-4 text-gray-400" size={48} />
              <p className="text-gray-500">No payment methods added yet</p>
            </CardContent>
          </Card>
        ) : (
          paymentMethods.map((method) => (
            <Card key={method.id} className="relative">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <CreditCard className="text-blue-500" size={24} />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize">{method.type}</span>
                        {method.is_default && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Star size={12} />
                            Default
                          </Badge>
                        )}
                      </div>
                      {method.card_last_four && (
                        <p className="text-sm text-gray-500">
                          {method.card_brand} •••• {method.card_last_four}
                          {method.expiry_month && method.expiry_year && (
                            <span className="ml-2">
                              Expires {method.expiry_month.toString().padStart(2, '0')}/{method.expiry_year}
                            </span>
                          )}
                        </p>
                      )}
                      <p className="text-xs text-gray-400">
                        Added {new Date(method.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {!method.is_default && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSetDefault(method.id)}
                      >
                        Set Default
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEdit(method)}
                    >
                      <Edit size={16} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(method.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};