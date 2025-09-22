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
  Calendar, 
  Plus, 
  Edit, 
  X,
  CheckCircle,
  AlertCircle,
  CreditCard,
  RefreshCw,
  DollarSign,
  Clock
} from 'lucide-react';

interface Subscription {
  id: string;
  plan_name: string;
  amount: number;
  billing_cycle: string;
  status: string;
  start_date: string;
  end_date?: string;
  next_billing_date?: string;
  payment_method_id?: string;
  created_at: string;
}

interface SubscriptionCreate {
  plan_name: string;
  amount: number;
  billing_cycle: string;
  start_date: string;
  end_date?: string;
  payment_method_id?: string;
}

interface PaymentMethod {
  id: string;
  type: string;
  card_last_four?: string;
  card_brand?: string;
  is_default: boolean;
}

export const Subscriptions: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<SubscriptionCreate>({
    plan_name: '',
    amount: 0,
    billing_cycle: 'monthly',
    start_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchSubscriptions();
    fetchPaymentMethods();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      const response = await fetch('/api/v1/financial/subscriptions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSubscriptions(data);
      } else {
        toast.error('Failed to fetch subscriptions');
      }
    } catch (error) {
      toast.error('Error fetching subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const fetchPaymentMethods = async () => {
    try {
      const response = await fetch('/api/v1/financial/payment-methods', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPaymentMethods(data);
      }
    } catch (error) {
      console.error('Error fetching payment methods');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingId 
        ? `/api/v1/financial/subscriptions/${editingId}`
        : '/api/v1/financial/subscriptions';
      
      const method = editingId ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingId ? 'Subscription updated' : 'Subscription created');
        setShowAddForm(false);
        setEditingId(null);
        resetForm();
        fetchSubscriptions();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save subscription');
      }
    } catch (error) {
      toast.error('Error saving subscription');
    }
  };

  const handleCancel = async (id: string) => {
    if (!confirm('Are you sure you want to cancel this subscription?')) return;

    try {
      const response = await fetch(`/api/v1/financial/subscriptions/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast.success('Subscription cancelled');
        fetchSubscriptions();
      } else {
        toast.error('Failed to cancel subscription');
      }
    } catch (error) {
      toast.error('Error cancelling subscription');
    }
  };

  const startEdit = (subscription: Subscription) => {
    setEditingId(subscription.id);
    setFormData({
      plan_name: subscription.plan_name,
      amount: subscription.amount,
      billing_cycle: subscription.billing_cycle,
      start_date: subscription.start_date,
      end_date: subscription.end_date,
      payment_method_id: subscription.payment_method_id
    });
    setShowAddForm(true);
  };

  const resetForm = () => {
    setFormData({
      plan_name: '',
      amount: 0,
      billing_cycle: 'monthly',
      start_date: new Date().toISOString().split('T')[0]
    });
    setEditingId(null);
    setShowAddForm(false);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: X },
      expired: { color: 'bg-gray-100 text-gray-800', icon: Clock },
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon size={12} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">Loading subscriptions...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Subscriptions</h2>
        <Button 
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          Add Subscription
        </Button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>
              {editingId ? 'Edit Subscription' : 'Add Subscription'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="plan_name">Plan Name</Label>
                  <Input
                    id="plan_name"
                    placeholder="Premium Plan"
                    value={formData.plan_name}
                    onChange={(e) => setFormData({...formData, plan_name: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="amount">Amount (₹)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    placeholder="999.00"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="billing_cycle">Billing Cycle</Label>
                  <Select 
                    value={formData.billing_cycle} 
                    onValueChange={(value) => setFormData({...formData, billing_cycle: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="quarterly">Quarterly</SelectItem>
                      <SelectItem value="yearly">Yearly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="end_date">End Date (Optional)</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={formData.end_date || ''}
                    onChange={(e) => setFormData({...formData, end_date: e.target.value || undefined})}
                  />
                </div>

                <div>
                  <Label htmlFor="payment_method_id">Payment Method</Label>
                  <Select 
                    value={formData.payment_method_id || ''} 
                    onValueChange={(value) => setFormData({...formData, payment_method_id: value === '' ? undefined : value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select payment method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">No payment method</SelectItem>
                      {paymentMethods.map((method) => (
                        <SelectItem key={method.id} value={method.id}>
                          {method.type} {method.card_last_four && `•••• ${method.card_last_four}`}
                          {method.is_default && ' (Default)'}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit">
                  {editingId ? 'Update' : 'Create'} Subscription
                </Button>
                <Button type="button" variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Subscriptions List */}
      <div className="grid gap-4">
        {subscriptions.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <RefreshCw className="mx-auto mb-4 text-gray-400" size={48} />
              <p className="text-gray-500">No subscriptions found</p>
            </CardContent>
          </Card>
        ) : (
          subscriptions.map((subscription) => (
            <Card key={subscription.id} className="relative">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg">{subscription.plan_name}</h3>
                      {getStatusBadge(subscription.status)}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <DollarSign size={16} />
                        <span>{formatCurrency(subscription.amount)} / {subscription.billing_cycle}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Calendar size={16} />
                        <span>Started: {new Date(subscription.start_date).toLocaleDateString()}</span>
                      </div>
                      
                      {subscription.next_billing_date && (
                        <div className="flex items-center gap-2">
                          <Clock size={16} />
                          <span>Next billing: {new Date(subscription.next_billing_date).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>

                    {subscription.end_date && (
                      <div className="mt-2 text-sm text-gray-500">
                        Ends: {new Date(subscription.end_date).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    {subscription.status === 'active' && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => startEdit(subscription)}
                        >
                          <Edit size={16} />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCancel(subscription.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Cancel
                        </Button>
                      </>
                    )}
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