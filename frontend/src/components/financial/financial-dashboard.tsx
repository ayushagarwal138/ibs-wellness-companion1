'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'react-hot-toast';
import { 
  DollarSign, 
  CreditCard, 
  FileText, 
  Repeat, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
  Eye
} from 'lucide-react';

// Import our financial components
import { PaymentMethods } from './payment-methods';
import { Subscriptions } from './subscriptions';
import { Invoices } from './invoices';

interface FinancialSummary {
  total_revenue: number;
  subscription_revenue: number;
  consultation_revenue: number;
  pending_payments: number;
  active_subscriptions: number;
  total_invoices: number;
  overdue_invoices: number;
}

interface Transaction {
  id: string;
  amount: number;
  type: string;
  status: string;
  description?: string;
  created_at: string;
}

interface RecentActivity {
  transactions: Transaction[];
  invoices: any[];
  subscriptions: any[];
}

export const FinancialDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity>({
    transactions: [],
    invoices: [],
    subscriptions: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFinancialData();
  }, []);

  const fetchFinancialData = async () => {
    try {
      // Fetch financial summary
      const summaryResponse = await fetch('/api/v1/financial/summary', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setSummary(summaryData);
      }

      // Fetch recent transactions
      const transactionsResponse = await fetch('/api/v1/financial/transactions?limit=5', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (transactionsResponse.ok) {
        const transactionsData = await transactionsResponse.json();
        setRecentActivity(prev => ({
          ...prev,
          transactions: transactionsData
        }));
      }

      // Fetch recent invoices
      const invoicesResponse = await fetch('/api/v1/financial/invoices?limit=5', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (invoicesResponse.ok) {
        const invoicesData = await invoicesResponse.json();
        setRecentActivity(prev => ({
          ...prev,
          invoices: invoicesData
        }));
      }

      // Fetch recent subscriptions
      const subscriptionsResponse = await fetch('/api/v1/financial/subscriptions?limit=5', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (subscriptionsResponse.ok) {
        const subscriptionsData = await subscriptionsResponse.json();
        setRecentActivity(prev => ({
          ...prev,
          subscriptions: subscriptionsData
        }));
      }

    } catch (error) {
      toast.error('Error fetching financial data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const getStatusBadge = (status: string, type: 'transaction' | 'invoice' | 'subscription' = 'transaction') => {
    const statusConfigs = {
      transaction: {
        pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
        completed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
        failed: { color: 'bg-red-100 text-red-800', icon: AlertCircle }
      },
      invoice: {
        draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
        sent: { color: 'bg-blue-100 text-blue-800', icon: Clock },
        paid: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
        overdue: { color: 'bg-red-100 text-red-800', icon: AlertCircle }
      },
      subscription: {
        active: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
        cancelled: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
        paused: { color: 'bg-yellow-100 text-yellow-800', icon: Clock }
      }
    };

    const typeConfig = statusConfigs[type];
    const config = (typeConfig as any)[status] || (typeConfig as any)['pending'] || { color: 'bg-gray-100 text-gray-800', icon: Clock };
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon size={12} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">Loading financial dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Financial Dashboard</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchFinancialData}>
            Refresh Data
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="payments">Payment Methods</TabsTrigger>
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Financial Summary Cards */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                      <p className="text-2xl font-bold">{formatCurrency(summary.total_revenue)}</p>
                    </div>
                    <div className="p-3 bg-green-100 rounded-full">
                      <TrendingUp className="text-green-600" size={24} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Pending Payments</p>
                      <p className="text-2xl font-bold">{formatCurrency(summary.pending_payments)}</p>
                    </div>
                    <div className="p-3 bg-yellow-100 rounded-full">
                      <Clock className="text-yellow-600" size={24} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Active Subscriptions</p>
                      <p className="text-2xl font-bold">{summary.active_subscriptions}</p>
                    </div>
                    <div className="p-3 bg-blue-100 rounded-full">
                      <Repeat className="text-blue-600" size={24} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Overdue Invoices</p>
                      <p className="text-2xl font-bold">{summary.overdue_invoices}</p>
                    </div>
                    <div className="p-3 bg-red-100 rounded-full">
                      <AlertCircle className="text-red-600" size={24} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Revenue Breakdown */}
          {summary && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Revenue Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Repeat size={16} className="text-blue-600" />
                        <span>Subscription Revenue</span>
                      </div>
                      <span className="font-semibold">{formatCurrency(summary.subscription_revenue)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <DollarSign size={16} className="text-green-600" />
                        <span>Consultation Revenue</span>
                      </div>
                      <span className="font-semibold">{formatCurrency(summary.consultation_revenue)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-2"
                      onClick={() => setActiveTab('invoices')}
                    >
                      <Plus size={16} />
                      Create Invoice
                    </Button>
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-2"
                      onClick={() => setActiveTab('subscriptions')}
                    >
                      <Repeat size={16} />
                      Manage Subscriptions
                    </Button>
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-2"
                      onClick={() => setActiveTab('payments')}
                    >
                      <CreditCard size={16} />
                      Payment Methods
                    </Button>
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-2"
                    >
                      <FileText size={16} />
                      View Reports
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Transactions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign size={20} />
                  Recent Transactions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentActivity.transactions.length === 0 ? (
                    <p className="text-gray-500 text-sm">No recent transactions</p>
                  ) : (
                    recentActivity.transactions.map((transaction) => (
                      <div key={transaction.id} className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-sm">{formatCurrency(transaction.amount)}</p>
                          <p className="text-xs text-gray-500">{transaction.type}</p>
                        </div>
                        {getStatusBadge(transaction.status, 'transaction')}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Recent Invoices */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText size={20} />
                  Recent Invoices
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentActivity.invoices.length === 0 ? (
                    <p className="text-gray-500 text-sm">No recent invoices</p>
                  ) : (
                    recentActivity.invoices.map((invoice) => (
                      <div key={invoice.id} className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-sm">{invoice.invoice_number}</p>
                          <p className="text-xs text-gray-500">{formatCurrency(invoice.total_amount)}</p>
                        </div>
                        {getStatusBadge(invoice.status, 'invoice')}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Recent Subscriptions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Repeat size={20} />
                  Recent Subscriptions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentActivity.subscriptions.length === 0 ? (
                    <p className="text-gray-500 text-sm">No recent subscriptions</p>
                  ) : (
                    recentActivity.subscriptions.map((subscription) => (
                      <div key={subscription.id} className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-sm">{subscription.plan_name}</p>
                          <p className="text-xs text-gray-500">{formatCurrency(subscription.amount)}</p>
                        </div>
                        {getStatusBadge(subscription.status, 'subscription')}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="payments">
          <PaymentMethods />
        </TabsContent>

        <TabsContent value="subscriptions">
          <Subscriptions />
        </TabsContent>

        <TabsContent value="invoices">
          <Invoices />
        </TabsContent>
      </Tabs>
    </div>
  );
};